import os
import datetime
import re
import subprocess
import sys
import tempfile

from flask import current_app, request
from sqlalchemy import engine
from sqlalchemy.engine import url

import app


# Infer the root path from the run file in the project root (e.g. mjinn.py)
fn = getattr(sys.modules['__main__'], '__file__')
root_path = os.path.abspath(os.path.dirname(fn))
# Backup directory is `sqldumps` sub-directory
backup_path = os.path.join(root_path, "sqldumps")

def mget_backup_path():
    return backup_path


def mget_SQLAlchemy_engine() -> engine.Engine:
    # return the SQLAlchemy `Engine` bound into the current session
    return app.db.session.bind


def mget_SQLAlchemy_engine_url() -> url.URL:
    # return the parsed `URL` object from the current SQLAlchemy engine
    return mget_SQLAlchemy_engine().url


def post_process_backup_output_file(result_file, final_output_file):
    # Be careful about line endings when postprocessing mysqldump --resultfile=... output under Windows
    # as per https://dev.mysql.com/doc/refman/5.7/en/mysqldump.html#option_mysqldump_result-file
    # > This option should be used on Windows to prevent newline \n characters from being converted
    # > to \r\n carriage return/newline sequences.
    # In any case, the SQL dump can and does contain binary characters (e..g from PDF dumps)
    # so we must do all of this in binary mode
    reDefiner = ""
    with open(result_file, "rb") as inp:
        with open(final_output_file, "wb") as outp:
            for line in inp:
                # get rid of the CREATE DEFINER=user@host which mysqldump puts in for functions/procedures
                # as these would prevent restore if that user does not exist
                line = re.sub(rb"^(\s*CREATE\s+)DEFINER\s*=\s*\S+", rb"\1", line, flags=re.IGNORECASE)
                outp.write(line)


def backup_file_list():
    # class for showing (selected) file information
    class FileInfo:
        def __init__(self):
            self.name = ""
            self.size = 0
            self.mtime = 0
            self.datetime = ""

    # find the existing backup files, and put them into `restore_files` table
    if not os.path.isdir(backup_path):
        raise FileNotFoundError(f"Backup directory does not exist: {backup_path}")
    backup_files = []
    # populate `backup_files` with all ".sql" files
    with os.scandir(backup_path) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file():
                if entry.name.lower().endswith('.sql'):
                    stat_result = entry.stat()
                    file_info = FileInfo()
                    file_info.name = entry.name
                    file_info.size = stat_result.st_size
                    file_info.mtime = datetime.datetime.fromtimestamp(stat_result.st_mtime)
                    file_info.datetime = file_info.mtime.strftime("%d-%b-%Y %H:%M")
                    backup_files.append(file_info)
    # sort by modification time, reversed, so that most recent at top
    backup_files.sort(key=lambda fi: fi.mtime, reverse=True)

    return backup_files


def mbackup_database():
    backup_database_output = ""
    file_name = ""
    if request.method == "POST":
        # options for the backup
        class Options:
            verbose = False
            add_drop_database = False
            include_routines = True
            post_process_output = True

        result_file = ""
        try:
            if not os.path.isdir(backup_path):
                raise FileNotFoundError(f"Backup directory does not exist: {backup_path}")
            # get the database credentials
            # ultimately this comes from `SQLALCHEMY_DATABASE_URI`
            _url = mget_SQLAlchemy_engine_url()
            db_host = _url.host
            db_name = _url.database
            db_user = _url.username
            db_password = _url.password
            # Getting current datetime to create the separate backup file name like "2018-08-17_12-34".
            now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            # `result_file` will be the output file from the mysqldump
            # `final_output_file` will be the final backup file
            # which may have been preprocessed from `result_file` to remove stuff...
            final_output_file = os.path.join(backup_path, f"{db_name}-{now_str}.sql")
            if Options.post_process_output:
                fd, result_file = tempfile.mkstemp(".sql", "databasebackup_")
                os.close(fd)
            else:
                result_file = final_output_file
            # if we are going to postprocess the output
            # we must pass a temporary file to script for result-file and then postprocess that to the final output file
            # Note that we must do it this way (e.g. not to stdout) and must be careful how we do it because of Windows:
            # https://dev.mysql.com/doc/refman/5.7/en/mysqldump.html#option_mysqldump_result-file
            # > This option should be used on Windows to prevent newline \n characters from being converted
            # > to \r\n carriage return/newline sequences.
            # get the mysqldump executable
            # this can be changed in "myconfig.py", e.g. to provide the full path if not on PATH, etc.
            mysqldump_executable = current_app.config.get('MYSQLDUMP_EXECUTABLE', 'mysqldump')
            # build the mysqldump command
            dumpcmd = [mysqldump_executable]
            if Options.verbose:
                dumpcmd.append("--verbose")
            if Options.add_drop_database:
                dumpcmd.append("--add-drop-database")
            if Options.include_routines:
                dumpcmd.append("--routines")
            dumpcmd.extend([
                f"--host={db_host}",
                f"--user={db_user}",
                f"--result-file={result_file}",
                "--databases", db_name])
            backup_database_output += f"Executing OS command: {dumpcmd}\n"

            # copy current process enviorment variables...
            environ = os.environ.copy()
            # ...and put password into sub-process environment variable
            # else mysqldump: [Warning] Using a password on the command line interface can be insecure.
            environ["MYSQL_PWD"] = db_password
            # run the `mysqldump` sub-process, capturing output
            completed_process = subprocess.run(dumpcmd, env=environ, capture_output=True, text=True)
            if completed_process.stdout is not None:
                backup_database_output += completed_process.stdout
            if completed_process.stderr is not None:
                backup_database_output += completed_process.stderr
            exit_code = completed_process.returncode
            if exit_code == 0:
                file_name = f"{db_name}-{now_str}.sql"
                backup_database_output += "OS command executed successfully\n"
                if Options.post_process_output:
                    # now do the postprocessing on the output
                    post_process_backup_output_file(result_file, final_output_file)
                backup_database_output += f"Backup placed in file: {final_output_file}\n"
            else:
                backup_database_output += f"OS command reported unsuccessful, exit code {exit_code}\n"
        except Exception as ex:
            backup_database_output += f"***Exception: {str(ex)}"
        finally:
            if Options.post_process_output:
                if result_file:
                    os.unlink(result_file)

    return file_name, backup_database_output


def mrestore_database():
    # get the avialable backup files into the table for selection
    backup_files = backup_file_list()
    restore_database_output = ""
    # Testing Sams modal messaging system with feedback from restore
    message = ""
    if request.method == "POST":
        # options for the restore
        class Options:
            verbose = False
            comments = True
            # see e.g. https://dev.mysql.com/doc/refman/5.7/en/stored-programs-logging.html
            # this command is needed if e.g. some SQL functions are not declared `DETERMINISTIC`
            # as of 19/02/2021 all necessary functions have now been marked `DETERMINISTIC`
            # so this is not needed, but it is unclear whetehr it may be in the future
            # init_command = 'SET GLOBAL log_bin_trust_function_creators = 1;'
            init_command = None

        try:
            # get the database credentials
            # ultimately this comes from `SQLALCHEMY_DATABASE_URI`
            _url = mget_SQLAlchemy_engine_url()
            db_host = _url.host
            db_name = _url.database
            db_user = _url.username
            db_password = _url.password
            selected_file = request.form.get("select_file")
            if not selected_file:
                raise ValueError("No file selected to restore from")
            restore_path = os.path.join(backup_path, selected_file)
            if not os.path.isfile(restore_path):
                raise FileNotFoundError(f"Restore file does not exist: {restore_path}")
            file_handle = open(restore_path, 'rb')
            # get the mysql executable
            # this can be changed in "myconfig.py", e.g. to provide the full path if not on PATH, etc.
            mysql_executable = current_app.config.get('MYSQL_EXECUTABLE', 'mysql')
            # build the mysql command
            restorecmd = [mysql_executable]
            if Options.verbose:
                restorecmd.append("--verbose")
            if Options.comments:
                restorecmd.append("--comments")
            if Options.init_command:
                restorecmd.append(f"--init-command={Options.init_command}")
            restorecmd.extend([
                f"--host={db_host}",
                f"--user={db_user}"])
            restore_database_output += f"Executing OS command: {restorecmd}\n"

            # copy current process enviorment variables...
            environ = os.environ.copy()
            # ...and put password into sub-process environment variable
            # else mysql: [Warning] Using a password on the command line interface can be insecure.
            environ["MYSQL_PWD"] = db_password
            # run the `mysql` sub-process, capturing output
            completed_process = subprocess.run(restorecmd, env=environ, stdin=file_handle, capture_output=True, text=True)
            if completed_process.stdout is not None:
                restore_database_output += completed_process.stdout
            if completed_process.stderr is not None:
                restore_database_output += completed_process.stderr
            exit_code = completed_process.returncode
            if exit_code == 0:
                restore_database_output += "OS command executed successfully\n"
                restore_database_output += f"Backup restored from file: {restore_path}\n"
                message = "Restore successful!"
            else:
                restore_database_output += f"OS command reported unsuccessful, exit code {exit_code}\n"
                message = f"Restore failed with exit code: {exit_code}\n"
        except Exception as ex:
            restore_database_output += f"***Exception: {str(ex)}"
            message = f"Restore failed with exception: {str(ex)}"

    return backup_files, restore_database_output, message

