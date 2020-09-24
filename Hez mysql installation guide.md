# Linux mysql installation guide - updated by Hez 24th September 2020:

### Install Linux (Ubuntu):	

In Windows, download your chosen Linux install (eg Ubuntu 20.04) as an ISO image (about 2.5GB)

In Windows, create USB boot stick using Rufus (a teeny free downoad exe file) and the downloaded ISO image

On the PC to be converted to Linux: boot from the USB Linux boot stick, choosing to **overwrite existing OS**.

Installing without wifi or LAN connected works fine. Likewise tick to receive online updates works fine as well

As Ubuntu installs, if asked, choose your location, UK keyboard, your user name and a password for sudo. I suggest a short one, such as **pete**. I chose **login automatically**.

At end of the installation, restart and leave the Linux PC for a few minutes to come to.

Once online, use the software updater to update Linux, LibreOffice, etc.  One such download was 252MB and it took about 15 minutes to fully update. 

On the newly installed Linux PC which has been updated and is now online: 

### Install MySQL Server and MySQL Workbench in Ubuntu 20.04

Open a terminal on the desktop, in the home folder or anywhere and execute these commands:
 
	sudo apt-get install mysql-server 
	
	sudo mysql_secure_installation

You may be asked to set a password for root.  **If so, use a reasonable password for root and write it down - eg Hez123456H!** 

You will be asked a series of questions: I said no to validate passwords and yes to everything else

### If you want to use MySQL workbench on this PC:  

Now, in Ubuntu 20.04, **MySQL workbench is available to install through the software app on LHS taskbar**, so install it from there

After workbench is installed, start workbench by clicking the **show applications** button at bottom left and search for **work..**.

### I had problems connecting to mysql server and to workbench using the correct root password I set at installation, so here is how to get into MySQL server as root if you do not know your password:

	sudo mysql -u root
	
	=> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Hez654321H!';
	
	sudo service mysql restart

You should now be able to connect from workbench to the mysql server as root, using your new password

I read somewhere that you should **not really use root to connect to MySQL server**. It is good practice to create a new user (such as hez or roger) with typical DBA privileges and a suitable password, to use to connect from Jinn and into workbench.

You can create a new user and set privileges in workbench, or see my separate mysql shell guide.

Run this query to create the empty mjinn schema:

	CREATE SCHEMA mjinn 

Refresh the **schemas** area on left in the schemas tab to see your new empty database mjinn.	

There are a few issues in importing mysql 5.7 sql dump files into mysql 8.  My favoured solution is to create two sql dump files from 5.7, one being just all the tables named TablesDump and the other being the user table along with the functions and procedures named UserFuncProc

The TablesDump sql dump file should import fine as it is.  The UserFuncProc dump file will need editing in a text editor such as Notepad++ so as to:

1. Replace all occurrences of DEFINER=`root`@`localhost` with a blank field and 

2. Replace all occurrences of NO_AUTO_CREATE_USER, with a blank field

Now run this query in workbench:

    SET GLOBAL log_bin_trust_function_creators = 1

Now the UserFuncProc sql dump file should import fine

So, after refreshing, you should now see all the tables and all the functions and procedures.