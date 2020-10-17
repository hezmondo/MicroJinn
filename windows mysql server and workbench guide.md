### Installing mysql server and workbench in windows

**mysql server**

Go to the Oracle MySQL download website:	https://dev.mysql.com/downloads You may need to register, but this is simple and free.

I chose the small web based MSI this time - mysql-installer-web-community-8.0.21.0.msi this app allows you to install mysql server and workbench.

Open the mysql msi app and install just myql server (Community Server 8.0.21) X64 - incredibly quick and simple.
  
I chose development machine to use the least of the PC resources and accepted the splash creen with localhost 3306.

You will be asked to set a password for root.  **If so, use a reasonable password for root and write it down - eg Pete123456P!** 

At this point, I opted to set up a non-root user (say peter) with typical DB admin privileges and to set a strong password - simple and quick.

You will use this non-root user and password for mjinn in the essential start up file myconfig.py 

**mysql workbench**

Open (or continue to use) the same mysql msi app and now add workbench from applications/workbench latest X64 and install it - quick and easy.

When starting workbench, you can either edited the offered root connection to use your non-root username, or create a second connection to use that. 
In either case, click to test the connection **without putting the password in first** and then put your password in and click to save it.  
Bingo - very easy and quick, so I will now remove all the stuff about how hard this used to be.

### Problems in importing mysql functions and procedures from another installation

Currently, you may get some or all of these errors, but **NB:- all the tables will very likely have imported fine**, before the error, when it gets to procedures and functions:

1.  ERROR 1231 (42000) at line 1454: Variable 'sql_mode' can't be set to the value of 'NO_AUTO_CREATE_USER'

2.  ERROR because MySQL dumps functions containing text such as this: CREATE DEFINER=`root`@`localhost` FUNCTION

3.  ERROR because MySQL dumps functions containing text such as this: SET TIME ZONE =

To get around this, first use Notepad++ or any text editor to replace the text strings in your extracted mjinn dump file as follows:

replace DEFINER=`root`@`localhost` with "" 
replace NO_AUTO_CREATE_USER with ""

Now remove these problem lines from the very end of your sql dump file:

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

if you get an error mentioning log_bin_trust_function_creators, open a query window in workbench and run this query:

    set log_bin_trust_function_creators = 1;

Call Hez if you are struggling.  One workaround: 

Create two sql dump files, one being just all the tables, named TablesDump, and the other being just the teeny user table along with the functions and procedures, named UserFuncProcDump

The TablesDump sql dump file should import fine as it is.  Now it is easier to edit the small FuncProcDump sql file as set out above, to remove the offending text and then do data import in workbench.  

Dirty but job done and works fine. 
    
All that follows is just here in case you might ever need it

### Basic localhost mysql commands in the mysql console

Login to the mysql server from the command line with the following command:

    mysql -u root -p

I have specified the user root with the -u flag, and then used the -p flag so MySQL prompts for a password. Enter your current password to complete the login.

You should now be at a MySQL prompt that looks very similar to this:

    mysql>

To create a database named fitness type the following command:

    Create database fitness;

To view the database you’ve created issue the following command:

    show databases;

Now create a user with the name hezmo, and the password test123test!

    CREATE USER 'hezmondo'@'localhost' IDENTIFIED BY 'test123test!';

In just one command you’ve created your first MySQL user. However, this user won’t be able to do anything with MySQL until they are granted additional privileges. In fact, they won’t even be able to login without additional permissions.


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

    GRANT CREATE ON *.* TO 'hezmondo'@'localhost';

Or maybe grant all permissions and also grant access:

    GRANT ALL PRIVILEGES ON *.* TO 'hezmondo'@'localhost' WITH GRANT OPTION;

When finished making your permission changes, it’s good practice to reload all the privileges with the flush command!

    FLUSH PRIVILEGES;

To show permissions for a MySQL User:

    SHOW GRANTS FOR 'hezmondo'@'localhost';


To import and export sql dumps or sql files, best use full path file names.  

To execute a sql file on the desktop:

    use db_name;
    source ~/Desktop/fitnessdump.sql;

To dump a backup file to the desktop:

    mysqldump fitness > ~/Desktop/fitnessdump2.sql;

Or try this in the terminal:

Remember where your SQL file is. If your SQL file is in the Desktop folder/directory then go the desktop directory and enter the command like this:

    mysql -u hezmondo -p Hez815918H fitness < ~/Desktop/fitnessdump.sql


Eventually I discovered that MySQL server is now set up to restrict access to localhost only by default, for security reasons. It seems extraordinary to me that I had to resort to this level of arcane skullduggery to change that:

    sudo nano etc/mysql/mysql.conf.d/mysqld.cnf

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


