### Install mysql Server in Ubuntu 20.04

Open a terminal on the desktop, in the home folder or anywhere and execute these commands:
 
	sudo apt-get install mysql-server 
	
	sudo mysql_secure_installation

You may be asked to set a password for root.  **If so, use a reasonable password for root and write it down - eg Pete123456P** 

You will be asked a series of questions: I said no to validate passwords and yes to everything else

### Install mysql workbench in Ubuntu 20.04

Workbench is now available to install using the Ubuntu software app

After workbench is installed, start workbench by clicking the **show applications** button at bottom left and search for **work..**.

When starting workbench, you can either edit the offered root connection to your non-root username, or create a second connection to use that. 
In either case, click to test the connection **without putting the password in first** and then put your password in and click to save it.  

### I had problems connecting to mysql server and to workbench using the correct root password I set at installation, so here is how to get into MySQL server as root if you do not know your password:

	sudo mysql -u root
	
	=> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Hez654321H!';
	
	sudo service mysql restart

You should now be able to connect from workbench to the mysql server as root, using your new password

I understand that you should **not really use root to connect to MySQL server**. It is good practice to create a new user (such as hez or roger) with typical DBA privileges and a suitable password, to use to connect from Jinn and into workbench.

You can create a new user and set privileges in workbench, or see my separate mysql console guide.

Run this query to create the empty mjinn schema:

	CREATE SCHEMA mjinn 

Refresh the **schemas** area on left in the schemas tab to see your new empty database mjinn.	

### Problems in importing mysql functions and procedures from one installation to another

You may get some or all of these errors, but **NB:- all the tables will very likely have imported fine**, before the error when it gets to procedures and functions:

1.  ERROR 1231 (42000) at line 1454: Variable 'sql_mode' can't be set to the value of 'NO_AUTO_CREATE_USER'

2.  ERROR because MySQL dumps functions containing text such as this: CREATE DEFINER=`root`@`localhost` FUNCTION

3.  ERROR because MySQL dumps functions containing text such as this: SET TIME ZONE =

It is simple to get around this:

In linux, run these commands in a terminal opened in the folder containing your sql dump file eg "mydump.sql" - this will replace the problem text with ""
  
	sed -i 's/NO_AUTO_CREATE_USER//' mydump.sql 
	sed -i 's/DEFINER=`root`@`localhost`//' mydump.sql 

Now remove these problem lines from the very end of your sql dump file:

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

Now login to the mysql console (see instructions above and below) and run this command:

    set log_bin_trust_function_creators = 1; 

Now try the import again and if still stuck, try the following solution and/or call Hez if you are struggling.

**Hez favoured simple solution to data import issues:**
 
Create two sql dump files, one being just all the tables, named TablesDump, and the other being just the teeny user table along with the functions and procedures, named UserFuncProcDump

The TablesDump sql dump file should import fine as it is.  Now it is easier to edit the small FuncProcDump sql file as set out above, to remove the offending text and then do data import in workbench.  

So, after refreshing, you should now see all the tables and all the functions and procedures.
    
**Feel free to check out my new mysql console guide and maria notes**
