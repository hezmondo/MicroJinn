from flask import Blueprint, render_template, send_from_directory
from app.main.backup import mbackup_database, mget_backup_path, mrestore_database

backup_bp = Blueprint('backup_bp', __name__)

@backup_bp.route('/backup_database', methods=['GET', 'POST'])
# @login_required
def backup_database():
    file_name, backup_database_output = mbackup_database()

    return render_template('backup_database.html', file_name=file_name, backup_database_output=backup_database_output)


@backup_bp.route('/restore_database', methods=['GET', 'POST'])
# @login_required
def restore_database():
    backup_files, restore_database_output, message = mrestore_database()

    return render_template('restore_database.html', backup_files=backup_files,
                           restore_database_output=restore_database_output, message=message)


@backup_bp.route('/sqldumps/<path:filename>', methods=['GET', 'POST'])
# @login_required
def sqldumps(filename):
    backup_path = mget_backup_path()
    # page has: <a href="{{ url_for('backup_bp.sqldumps', filename=backup_file.name) }}">{{ backup_file.name }}</a>
    # this function sends the file from the directory as a download "attachment" (i.e. needs to be saved)
    return send_from_directory(directory=backup_path, filename=filename, as_attachment=True)
