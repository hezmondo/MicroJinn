### Install mysql Server in Ubuntu 20.04 - last updated 25 Dec 2020

Open a terminal on the desktop, in the home folder or anywhere and execute these commands:
 
	sudo apt-get install mysql-server 
	
	sudo mysql_secure_installation

You may be asked to set a password for root.  **If so, use a reasonable password for root and write it down - eg heZ1234567!** 

You may be asked a series of questions: I said no to validate passwords and yes to everything else

### Install mysql workbench in Ubuntu 20.04

Workbench is now available to install using the Ubuntu software app

After workbench is installed, start workbench by clicking the **show applications** button at bottom left and search for **work..**.

### I had problems connecting workbench to mysql server using the correct root password:

One issue is mysql server may not configure so as to allow workbench to connect as root.  If so, please follow the mmjinn guide for mysql console and maria, where you will learn how to configure mysql server in a terminal

Another issue is if you have installed MySQLWorkbench as a Snap package. You want to store the database password(s) in the Gnome Passwords & Keys facility. However, a Snap package is sandboxed; it is not by default allowed to access this service. When you choose "Store in keychain" MySQLWorkbench is blocked by AppArmor. You need to enter a command to allow this package to access the service. The command is:

    sudo snap connect mysql-workbench-community:password-manager-service :password-manager-service

### Problems in importing mysql functions and procedures from one installation to another

You may get some or all of these errors, but **NB:- all the tables will very likely have imported fine**, before the error when it gets to procedures and functions:

1.  ERROR 1231 (42000) at line 1454: Variable 'sql_mode' can't be set to the value of 'NO_AUTO_CREATE_USER'

2.  ERROR because MySQL dumps functions containing text such as this: CREATE DEFINER=`root`@`localhost` FUNCTION

3.  ERROR because MySQL dumps functions containing text such as this: SET TIME ZONE =

It is simple to get around this in linux by running these commands in a terminal opened in the folder containing your sql dump file eg "mydump.sql" - this will replace the problem text with ""
  
	sed -i 's/NO_AUTO_CREATE_USER//' mydump.sql 
	sed -i 's/DEFINER=`root`@`localhost`//' mydump.sql 

You may also need to remove any lines from the very end of your sql dump file containing the text "TIME ZONE".

Lastly you may get an error mentioning log_bin_trust_function_creators.  If so, either in mysql console or in workbench, run this:

    set global log_bin_trust_function_creators = 1; 

Now try the import again and you should be good to go

**Hez favoured simple solution to data import issues:**
 
Create two sql dump files, one being just all the tables, named TablesDump, and the other being just the teeny user table along with the functions and procedures, named UserFuncProcDump

The TablesDump sql dump file should import fine as it is.  Now it is easier to edit the small FuncProcDump sql file as set out above, to remove the offending text and then do data import in workbench.  

So, after refreshing, you should now see all the tables and all the functions and procedures.
    
**Feel free to check out the mjinn guide for mysql console and maria**
