### Install mysql Server

**Ubuntu 20.04**

Open a terminal on the desktop, in the home folder or anywhere and execute these commands:
 
	sudo apt-get install mysql-server 
	
	sudo mysql_secure_installation

You may be asked to set a password for root.  **If so, use a reasonable password for root and write it down - eg Pete123456P** 

You will be asked a series of questions: I said no to validate passwords and yes to everything else

**Windows**

The basic mysql server installation is now pretty straightforward. Go to the Oracle MySQL download website:	https://dev.mysql.com/downloads/mysql/ You may need to register, but 
this is simple and free.

Download either the the small web based msi or the full msi suitable for your PC. Current is MySQL Community Server 8.0.21.  The msi will allow you to install workbench at the same time, if you wish.

I chose development machine to use the least of the PC resources.

You may be asked to set a password for root.  **If so, use a reasonable password for root and write it down - eg Pete123456P** 

You will be asked a series of questions: I said no to validate passwords and yes to everything else

If asked, accept the default 3306 TCP/IP settings.

### Install mysql workbench

**Ubuntu 20.04**

Workbench is now available to install using the Ubuntu software app

After workbench is installed, start workbench by clicking the **show applications** button at bottom left and search for **work..**.

**Windows**

This is now offered along with mysql server in the msi from Oracle, as explained above.

### Install mysql workbench and configure a user for mysql server

It is quite likely that you will fail to connect to workbench, for either one or both of these problems:

1. It seems that you cannot log onto the MySQL server as root in Workbench, so open a terminal, command prompt or powershell window and execute these commands to either set for the first time, or re-set a new password for root **I suggest you use a reasonable password for root and write it down - eg Pete123456P** 

in terminal or command prompt

	sudo mysql -u root

This will put you in the mysql console, so now execute this command
	
	mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Pete123456P';
	
now you need to exit the mysql console

	mysql> exit	
	
now back in terminal

	sudo service mysql restart

or in windows:

First, open the Run window by using the Windows+R keyboard

Second, type services.msc and press Enter:

Third, select the MySQL service and click the restart button.


2. In Ubuntu 20.04, even after setting correct permissions, I got a horrible error message when trying to enter the password in the only place available, which is "Store in keychain".  Unbelievably, the solution I found was to go back to the terminal and enter this command:

	sudo snap connect mysql-workbench-community:password-manager-service :password-manager-service

**Anyway, hopefully you can now log in to Workbench either as root with password Pete123456P or with your new user and password**   

It is good practice to create a new user (such as peter or roger) to use to connect to mysql server from Jinn or mjinn or workbench.

I therefore recommend you use workbench to set up a new user withwith typical DBA privileges and a suitable password.  If you have problems with workbench, or you do not have workbench, jump to ### Basic localhost mysql commands in the terminal and using mysql console below.

### Problems in importing functions and procedures from MySQL 5.7 to MySQL 8

You will likely get some or all of these errors, but you may wish to note that all the tables will very likely import fine, before the error when it gets to procedures and functions:

1.  ERROR 1231 (42000) at line 1454: Variable 'sql_mode' can't be set to the value of 'NO_AUTO_CREATE_USER'

2.  ERROR because MySQL dumps functions containing text such as this: CREATE DEFINER=`root`@`localhost` FUNCTION

2.  ERROR because MySQL dumps functions containing text such as this: SET TIME ZONE =

In linux, run these commands in a terminal opened in the folder containing your sql dump file eg "mydump.sql" - this will replace the problem text with ""
  
	sed -i 's/NO_AUTO_CREATE_USER//' mydump.sql 
	sed -i 's/DEFINER=`root`@`localhost`//' mydump.sql 

Now login to the mysql console (see instructions above and below) and run this command:

    set log_bin_trust_function_creators = 1; 

In windows, use Notepad++ or any text editor to repace DEFINER=`root`@`localhost` with "" and to replace NO_AUTO_CREATE_USER with "" in your extracted mjinn dump file.

Call Hez if you are struggling.

Hez simple solution: dump just one small table and all functions and procedures, manually edit the sql dump file to remove the offending text and then do data import in workbench.  Dirty but job done and works fine. 
    
All that follows is just here in case we ever need it

### Basic localhost mysql commands in the terminal and mysql console

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


