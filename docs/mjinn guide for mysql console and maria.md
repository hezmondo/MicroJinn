### running mysql commands in linux terminal or windows mysql console - last updated 25 Dec 2020

These instructions are for linux but most of this works fine in a powershell window in Windows

Open a terminal anywhere 

**if you cannot get into MySQL 8.0 as root (unknown) password, see latest advice below**

I read somewhere that you should **not really use root to connect to MySQL server**. It is good practice to create a new user (such as peter or roger) with typical DBA privileges and a suitable password, to use to connect from Jinn and into workbench.

Login to the MySQL server as root from the command line with the following command:

    mysql -u root -p

I have specified the user root with the -u flag, and then used the -p flag so MySQL prompts for a password. Enter your current password to complete the login.

You should now be at a MySQL prompt that looks very similar to this:

    mysql>

To create a database named yoda type the following command:

    Create database yoda;

To view the database you’ve created issue the following command:

    show databases;

Now create a user with the name hezm, and the password test123test!

    CREATE USER 'hezm'@'localhost' IDENTIFIED BY 'test123test!';

In just one command you’ve created your first MySQL user and set a password. However, this user won’t be able to do anything with MySQL until they are granted additional privileges. In fact, they won’t even be able to login without additional permissions.

To see a list of MySQL users, including the host they’re associated with:

    SELECT User,Host FROM mysql.user;

The basic syntax for granting permissions is:

    GRANT permission ON database.table TO 'user'@'localhost';

Here is a short list of commonly used permissions :

ALL – Allow complete access to a specific database. If a database is not specified, then allow complete access to the entirety of MySQL.
CREATE – Allow a user to create databases and tables.
DELETE – Allow a user to delete rows from a table.
DROP – Allow a user to drop databases and tables.
EXECUTE – Allow a user to execute stored routines.
GRANT OPTION – Allow a user to grant or remove another user’s privileges.
INSERT – Allow a user to insert rows from a table.
SELECT – Allow a user to select data from a database.
SHOW DATABASES- Allow a user to view a list of all databases.
UPDATE – Allow a user to update rows in a table.

To grant CREATE permissions for all databases * and all tables * use the following command:

    GRANT CREATE ON *.* TO 'hezm'@'localhost';

Or maybe grant all permissions and also grant access:

    GRANT ALL PRIVILEGES ON *.* TO 'hezm'@'localhost' WITH GRANT OPTION;

When finished making your permission changes, it’s good practice to reload all the privileges with the flush command!

    FLUSH PRIVILEGES;

To show permissions for a MySQL User:

    SHOW GRANTS FOR 'hezm'@'localhost';

To import and export sql dumps or sql files, best use full path file names.  

To execute a sql file on the desktop:

    use db_name;
    source ~/Desktop/fitnessdump.sql;

To dump a backup file to the desktop:

    mysqldump newbase > ~/Desktop/newbasedump2.sql;

Or try this in the terminal:

Remember where your SQL file is. If your SQL file is in the Desktop folder/directory then go the desktop directory and enter the command like this:

    mysql -u hezm -p test123test! newbase < ~/Desktop/newbasedump.sql

Eventually I discovered that MySQL server is now set up to restrict access to localhost only by default, for security reasons. It seems extraordinary to me that I had to resort to this level of arcane skullduggery to change that:

    sudo nano etc/mysql/mysql.conf.d/mysqld.cnf


### Problems in importing mysql functions and procedures using a mysql dump created in workbench by another user

The import of functions and procedures seems to fail every time.  Assuming you are trying to import a single sql file containing all the functions and procedures, 
you first need to replace all occurrences of  CREATE DEFINER=**** FUNCTION with CREATE FUNCTION and then remove all occurrences of NO_AUTO_CREATE_USER within the whole sql file. 
The import of functions and procedures will probably still fail with an error mentioning "log_bin_trust_function_creators".  
If so, either in mysql console or in workbench, run this command/query:  set global log_bin_trust_function_creators = 1; and then try again.  
That setting only lasts for the workbench setting

**Hez favoured simple solution to data import issues:**
 
Create two sql dump folders, one being just all the tables, named TablesDump, and the other being just the teeny user table along with the functions and procedures, named UserFuncProcDump

The TablesDump sql dump file should import fine as it is.  Now it is easier to edit the small FuncProcDump sql file as set out above, to remove the offending text and then do data import in workbench.  

So, after refreshing, you should now see all the tables and all the functions and procedures.

### If you need to get into MySQL server as root and you do not know your password:

**For mysql server prior to 8**: open a terminal anywhere and execute these commands to either set for the first time, or to re-set a new password for root. **I suggest you use a reasonable password for root and write it down - eg Pete123456P** 

	sudo mysql -u root
	
	=> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Pete123456P';
	
	sudo service mysql restart

**For mysql server 8 on**:
First option using skip-grant-tables mode

In order to skip the grant tables and reset the root password, we must first stop the MySQL service. Enter your Linux password if prompted.

    sudo /etc/init.d/mysql stop

Ensure the directory /var/run/mysqld exists and correct owner set.

    sudo mkdir /var/run/mysqld

    sudo chown mysql /var/run/mysqld

Now start MySQL with the --skip-grant-tables option. The & is required here.

    sudo mysqld_safe --skip-grant-tables&

You should see something similar to this:

[1] 1283
user@server:~$ 2019-02-12T11:15:59.872516Z mysqld_safe Logging to syslog.
2019-02-12T11:15:59.879527Z mysqld_safe Logging to '/var/log/mysql/error.log'.
2019-02-12T11:15:59.922502Z mysqld_safe Starting mysqld daemon with databases from /var/lib/m
    sudo service mysql stop

Now press ENTER to return to the Linux BASH prompt.

You can now log in to the MySQL root account without a password.

    sudo mysql --user=root mysql

Once logged in, you will see the mysql> prompt.

    UPDATE mysql.user SET authentication_string=null WHERE User='root';

    flush privileges;

Replace your_password_here with your own. (Generate a strong password here)

    ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password_here';

Flush privileges again.

    flush privileges;

Exit MySQL with "exit".

Now make sure all MySQL processes are stopped before starting the service again.

    sudo killall -u mysql

If you see a message similar to below, press ENTER to continue.

2020-05-30T07:23:38.547616Z mysqld_safe mysqld from pid file /var/lib/mysql/ubuntu.pid ended

Now start MySQL again.

    sudo /etc/init.d/mysql start

Log in to MySQL again and you should now be prompted for a password.

    sudo mysql -p -u root

Enter your MySQL root password. If correct, you should see something like:

Welcome to the MySQL monitor.

Now you are good to go!

posts on this problem:

For in SKIP-GRANT-TABLES mode - sudo /usr/local/mysql/bin/mysqld_safe --skip-grant-tables . Works for 8.0.1

I got ERROR 1146 (42S02): Table 'mysql.role_edges' doesn't exist so I had to do a mysql_upgrade -u root after I set the root password to null for this to work.

I had to use mysql_native_password instead of caching_sha2_password for this to work: ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'yourpasswd';. Not sure why



### Configure remote access to MySQL / MariaDB Databases

This brief tutorial shows students and new users how to configure remote access to MySQL or MariaDB database servers on Ubuntu 18.04 systems. When configured correctly, you will be able to connect to the database servers from a remote system on the same network.

If the server is connected directory to the Internet, you may able able to access it from anywhere around the world where Internet access is available.. however, opening up your database servers directly to the internet is not recommended.

In our next post, we’ll update this tutorial to show you how to enable secure the connection to the database server via SSL so that no one can intercept the communications and analyze the data between the server and the client computers.

When you’re ready to setup remote database access, please continue below.

By default, MySQL or MariaDB only listens for connections from the localhost. All remote access to the server is denied by default. To enable remote access, run the commands below to open MySQL/MariaDB configuration file.

	sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

on MariaDB server, the file may live below

	sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf

Then make the below change below from:

	bind-address                              = 127.0.0.1

To

	bind-address                               = 0.0.0.0

After making the change above, save the file and run the commands below to restart the server.

	sudo systemctl restart mysql.service

	sudo systemctl restart mariadb.service

To verify that the change happens, run the commands below

	sudo netstat -anp | grep 3306

and you should find the result that looks like the one below

	tcp       0      0 0.0.0.0:3306          0.0.0.0:*        LISTEN         3213/mysqld

Now the server is setup to listen to all IP addresses but individual IP needs to be explicitly configure to connect to a database.

To enable a client to connect to a database, you must grant access to the remote server.

For example, if you wish for a client computer with IP address 192.168.1.5 to connect to a database called wpdatabase as user wpuser, then run the commands below after logging onto the database server.

    GRANT ALL ON wpdatabase.* TO 'wpuser@192.168.1.5' IDENTIFIED BY 'new password here';

After running the commands above, you should be able to access the server from the client computer with that assigned IP.
To connect to the server from the IP, run the commands below

    sudo mysql -uroot -pdatabaseuser_password -h server hostname or IP address

That’s it! You’ve successfully configured a remote access to MySQL/MariaDB database server.

You may want to open Ubuntu Firewall to allow IP address 192.168.1.5 to connect on port 3306.

    sudo ufw allow from 192.168.1.5 to any port 3306   


