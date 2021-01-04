### Installing mysql server and workbench in windows - last updated 25 Dec 2020

**mysql server**

Go to the Oracle MySQL download website:	https://dev.mysql.com/downloads You may need to register, but this is simple and free.

I chose the small web based MSI this time - mysql-installer-web-community-8.0.21.0.msi this app allows you to install mysql server and workbench.

Open the mysql msi app and install just myql server (Community Server 8.0.21) X64 - incredibly quick and simple.
  
I chose development machine to use the least of the PC resources and accepted the splash creen with localhost 3306.

You will be asked to set a password for root.  **If so, use a reasonable password for root and write it down - eg heZ1234567H!** 

At this point, I opted to set up a non-root user (say hezm) with typical DB admin privileges and to set a strong password - simple and quick.

You will use this non-root user and password in the essential start up file myconfig.py to connect to mjinn.

**mysql workbench**

Open (or continue to use) the same mysql msi app and now add workbench from applications/workbench latest X64 and install it - quick and easy.

When starting workbench, you can either edit the offered root connection to your non-root username, or create a second connection to use that. 
In either case, click to test the connection **without putting the password in first** and then put your password in and click to save it.  

### I had problems connecting workbench to mysql server using the correct root password:

One issue is mysql server may not configure so as to allow workbench to connect as root.  If so, please follow the mmjinn guide for mysql console and maria, where you will learn how to configure mysql server in a terminal

Another issue is if you have installed MySQLWorkbench as a Snap package. You want to store the database password(s) in the Gnome Passwords & Keys facility. However, a Snap package is sandboxed; it is not by default allowed to access this service. When you choose "Store in keychain" MySQLWorkbench is blocked by AppArmor. You need to enter a command to allow this package to access the service. The command is:

    sudo snap connect mysql-workbench-community:password-manager-service :password-manager-service

### Problems in importing mysql functions and procedures from one installation to another

You may get some or all of these errors, but **NB:- all the tables will very likely have imported fine**, before the error when it gets to procedures and functions:

1.  ERROR 1231 (42000) at line 1454: Variable 'sql_mode' can't be set to the value of 'NO_AUTO_CREATE_USER'

2.  ERROR because MySQL dumps functions containing text such as this: CREATE DEFINER=`root`@`localhost` FUNCTION

3.  ERROR because MySQL dumps functions containing text such as this: SET TIME ZONE =

It is simple to get around this in windows by opening the offeding sql file (should be named routines) in notepad++ and replace the problem text with ""
  
	replace "/NO_AUTO_CREATE_USER//" with "" 
	replace "/DEFINER=`root`@`localhost`//"  with ""

You may also need to remove any lines from the very end of your sql dump file containing the text "TIME ZONE".

Lastly you may get an error mentioning log_bin_trust_function_creators.  If so, either in mysql console or in workbench, run this:

    set global log_bin_trust_function_creators = 1; 

Now try the import again and you should be good to go

**Hez favoured simple solution to data import issues:**
 
Create two sql dump files, one being just all the tables, named TablesDump, and the other being just the teeny user table along with the functions and procedures, named UserFuncProcDump

The TablesDump sql dump file should import fine as it is.  Now it is easier to edit the small FuncProcDump sql file as set out above, to remove the offending text and then do data import in workbench.  

So, after refreshing, you should now see all the tables and all the functions and procedures.
    
**Feel free to check out the mjinn guide for mysql console and maria**
