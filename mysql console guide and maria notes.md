### Basic localhost mysql commands in the terminal and in a windows mysql console

These instructions are for Linux but most of this works fine in a powershell window in Windows

Open a terminal anywhere, **if you cannot get into MySQL 8.0 as root (unknown) password, see latest advice below**

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


### How to use sed to clean up a MySQL dump created in workbench rather than one created by the wonderful Jinn backup utility created by JB 

If you attempt to import sql dump created in workbench you may get one or all of these errors:

ERROR 1231 (42000) at line 1454: Variable 'sql_mode' can't be set to the value of 'NO_AUTO_CREATE_USER'

ERROR because MySQL dumps functions containing text such as this: CREATE DEFINER=`root`@`localhost` FUNCTION

Run these commands in a terminal opened in the folder containing your sql dump file eg "mydump.sql"
  
	sed -i 's/NO_AUTO_CREATE_USER//' mydump.sql 
	sed -i 's/DEFINER=`root`@`localhost`//' mydump.sql 

If you get an error because of text containing SET TIME_ZONE=, then I suggest you remove this line, which is a few lines up from the very end of the sql file.  I will ask JB if sed can do this.


### If you still get a problem importing dump files, you may need to do this:

Login to the MySQL shell (see detailed instructions above) and run this command:

    set log_bin_trust_function_creators = 1; 


### If you need to get into MySQL server as root and you do not know your password:

It seems that in Ubuntu 18.04, Mint 19 and Ubuntu 20.04, you cannot log onto the MySQL server as root in Workbench without first opening a terminal anywhere and executing these commands to either set for the first time, or to re-set a new password for root. **I suggest you use a reasonable password for root and write it down - eg Pete123456P** 

	sudo mysql -u root
	
	=> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Pete123456P';
	
	sudo service mysql restart

It seems clear that this function (and the soluction above) was removed in MySQL 8.0.11

First option - if you in skip-grant-tables mode

in mysqld_safe:

    UPDATE mysql.user SET authentication_string=null WHERE User='root';
    FLUSH PRIVILEGES;
    exit;

and then, in terminal:

    mysql -u root

in mysql:

ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'yourpasswd';

Second option - not in skip-grant-tables mode

just in mysql:

    ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'yourpasswd';

posts on this problem:

For in SKIP-GRANT-TABLES mode - sudo /usr/local/mysql/bin/mysqld_safe --skip-grant-tables . Works for 8.0.1

I got ERROR 1146 (42S02): Table 'mysql.role_edges' doesn't exist so I had to do a mysql_upgrade -u root after I set the root password to null for this to work.

I had to use mysql_native_password instead of caching_sha2_password for this to work: ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'yourpasswd';. Not sure why

### Old advice for MyQL before 8.0  to set password to Pete123456P: 

	sudo mysql -u root
	
	=> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Pete123456P';
	
	sudo service mysql restart

    
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


