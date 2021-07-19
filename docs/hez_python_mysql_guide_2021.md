# Hez python, mysql server and workbench installation guide - updated by Hez 17th July 2021:

**Windows**

install latest python 64 bit for lulu or 3.7.9 32 bit for jinn - tick all users, choose location eg C:\Program files(86)\Python37

Download the small msi installer for myql (for jinn stick with 8.0.24)

Install myql server, mysql workbench and mysql python connector, all 8.0.24 64 bit, using SHA authentication and setting a strong password for root such as JxxxYxxx14!
At the same time, you might as well add a user eg hezm at the same time, with dba admin privileges and strong password such as YxxxJxxx14!

Start up workbench and create schema lulu and/or yoda and/or mfit 

NB if you have password problems, you might need to open a mysql console: open cmd prompt as administrator an do this to get into mysql console:

	cd C:\Program Files\MySQL\MySQL Server 8.0\bin

	mysql -u root -p

Enter password: JxxxYxxx14!

Now follow mysql console instructions included below in linux setup


**python_jinn for Windows**

open a command window as administrator

for Lulu, install the required python dependencies using pip -r with a text filefrom C:\flask\mjinn:

	pip install -r lulu_dependencies.txt
	
or for Jinn, best install the required python dependencies individually and carefully:

	pip install pyqt5==5.12.2
	pip install PyQtWebEngine==5.12.1
	pip install mysql-connector-python
	pip install dateutils
	pip install openpyxl
	pip install python-docx

NB - to make it all work, you must get the drivers for Qt_5.12.2 from hez or from thecodemonkey86 and place libmysql.dll in C:\Windows, C:\Windows\system32 and C:\jinn\code\DLLs and then place qsqlmysql.dll in C:\Program Files(86)\Python37\Lib\site-packages\PyQt5\Qt5\plugins\sqldrivers\

 	cd  C:\jinn	
	python code/home.py --version
	python code/home.py




**Linux**

Install latest mysql:

	sudo apt-get update -y
	sudo apt-get install mysql-server
	sudo mysql_secure_installation

set a strong password for root such as YxxxJxxx14!

Now enter the mysql console with this command using your password for root:

	sudo mysql

**Once in the mysql console in a terminal or command window:**

now we create a new user named hezm:

	CREATE USER 'hezm'@'localhost' IDENTIFIED WITH mysql_native_password BY 'YxxxJxxx14!';

Grant all permissions to hezm and also grant access:

	GRANT ALL PRIVILEGES ON *.* TO 'hezm'@'localhost' WITH GRANT OPTION;

When finished making your permission changes, it’s good practice to reload all the privileges with the flush command!

	FLUSH PRIVILEGES;

To show permissions for a MySQL User:

	SHOW GRANTS FOR 'hezm'@'localhost';

now we can create an empty database:

	CREATE SCHEMA mjinn; 

To import and export sql dumps or sql files, best use full path file names.

To execute a sql file on the desktop:

	use mfit;	
	source ~/Desktop/fitnessdump.sql;

To dump a backup file to the desktop:

	mysqldump fitness > ~/Desktop/fitnessdump2.sql;

To exit mysql console:

	exit;

**to install workbench in linux**

install workbench from the KDE software application manager (which contains snap apps) or:

	sudo snap install mysql-workbench_community

We now need to change from kwallet to gnome keyring:

	sudo apt-get update -y	
	sudo apt install gnome-keyring

Now uninstall kwallet using the software application manager.

We have installed MySQLWorkbench as a Snap package and want to store the database password(s) in the Gnome Passwords & Keys facility.
However, a Snap package is sandboxed; it is not by default allowed to access this service. When we choose "Store in keychain" MySQLWorkbench is blocked by AppArmor.
You need to enter a command to allow this package to access the service. The command is:

	sudo snap connect mysql-workbench-community:password-manager-service :password-manager-service

now restart and try again to add a connection for hezm, which should now work fine


**python_jinn for Linux**

for Lulu just 

	cd C:\flask\mjinn
	pip install -r lulu_dependencies.txt

For Jinn, your linux may well have pyqt5 and possibly PyQtWebEngine already installed, but otherwise:

Install these python dependencies using apt_get:

	sudo apt-get install python3-pyqt5
	sudo apt-get install python3-pyqt5.qtsql
	sudo apt-get install libqt5sql5-mysql

and these using pip3

	pip3 install PyQtWebEngine
	pip3 install dateutils
	pip3 install openpyxl
	pip3 install python-docx
	pip3 install mysql-connector-python

then check versions and start Jinn

	python3 /home/richard/Jinn/Code/home.py --version
	python3 /home/richard/Jinn/Code/home.py

