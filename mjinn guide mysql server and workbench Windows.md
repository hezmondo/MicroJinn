### Installing mysql server and workbench in windows

**mysql server**

Go to the Oracle MySQL download website:	https://dev.mysql.com/downloads You may need to register, but this is simple and free.

I chose the small web based MSI this time - mysql-installer-web-community-8.0.21.0.msi this app allows you to install mysql server and workbench.

Open the mysql msi app and install just myql server (Community Server 8.0.21) X64 - incredibly quick and simple.
  
I chose development machine to use the least of the PC resources and accepted the splash creen with localhost 3306.

You will be asked to set a password for root.  **If so, use a reasonable password for root and write it down - eg Pete123456P!** 

At this point, I opted to set up a non-root user (say peter) with typical DB admin privileges and to set a strong password - simple and quick.

You will use this non-root user and password in the essential start up file myconfig.py to connect to mjinn.

**mysql workbench**

Open (or continue to use) the same mysql msi app and now add workbench from applications/workbench latest X64 and install it - quick and easy.

When starting workbench, you can either edit the offered root connection to your non-root username, or create a second connection to use that. 
In either case, click to test the connection **without putting the password in first** and then put your password in and click to save it.  

**if you cannot get into MySQL 8.0 as root (password unknown or not recognised) see my new mysql console guide and maria notes**


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

Now try the import again and if still stuck, try the following solution and/or call Hez if you are struggling.

**Hez favoured simple solution to data import issues:**
 
Create two sql dump files, one being just all the tables, named TablesDump, and the other being just the teeny user table along with the functions and procedures, named UserFuncProcDump

The TablesDump sql dump file should import fine as it is.  Now it is easier to edit the small FuncProcDump sql file as set out above, to remove the offending text and then do data import in workbench.  

Dirty but job done and works fine. 
    
**Feel free to check out my new mysql console guide and maria notes**
