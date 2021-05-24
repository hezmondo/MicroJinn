**How to install Kubuntu OS to run from a USB Flash Drive**

https://www.fosslinux.com/2404/installing-a-updatable-manjaro-linux-on-a-usb-flash-drive.htm

https://www.fosslinux.com/10212/how-to-install-a-complete-ubuntu-on-a-usb-flash-drive.htm

latest very detailed:

https://askubuntu.com/questions/1217832/how-to-create-a-full-install-of-ubuntu-20-04-to-usb-device-step-by-step



**mysql**

Install mysql 8.0.23:

	sudo apt-get update -y
	sudo apt-get install mysql-server
	sudo mysql_secure_installation

set a full strength 10 character password for root with one or more special characters

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

Now we can create an empty database:

    create schema mjinn;

To import and export sql dumps or sql files, best use full path file names.

To execute a sql file on the desktop:

	use mfit;
	source ~/Desktop/fitnessdump.sql;

To dump a backup file to the desktop:

	mysqldump fitness > ~/Desktop/fitnessdump2.sql;

To exit mysql console:

	exit;


To dump a backup file to the desktop in a terminal:

Remember where your SQL file is. If your SQL file is in the Desktop folder/directory then go the desktop directory and enter the command like this:

	mysql -u hezmondo -p YxxxJxxx14! fitness < ~/Desktop/fitnessdump.sql


**workbench**

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


**chrome**

First install the gdebi and wget packages. By using gdebi to install Google Chrome browser we also ensure that any possible package prerequisites are met during the installation:
	
	sudo apt install gdebi-core wget

now download the Google Chrome browser pack:

	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
	
Now use gdebi command to install the prevously downloaded Google Chrome package: 

	sudo gdebi google-chrome-stable_current_amd64.deb
	
Now go to apps and you will see Chrome available

**python and pip**

now install pip3 if not already installed in your linux:

	sudo apt install python3-pip


**running Lulu or Jinn**

for Lulu just 

	cd flask
	pip install -r lulu_dependencies.txt

For Jinn, your linux may have pyqt5 and possibly PyQtWebEngine already installed, but otherwise:

Install these python dependencies using apt_get:

	sudo apt-get install python3-pyqt5
	sudo apt-get install python3-pyqt5.qtsql
	sudo apt-get install libqt5sql5-mysql

and then these using pip3

    pip3 install PyQtWebEngine
    pip3 install dateutils
	pip3 install openpyxl
	pip3 install python-docx
	pip3 install mysql-connector-python

	python3 /home/richard/Jinn/Code/home.py --version
	python3 /home/richard/Jinn/Code/home.py

**fdisk**

Before deleting a partition, run the following command to list the partition scheme

	fdisk -l
	
Note: The number 1 in /dev/sdb1 indicates the partition number. Make a note of the number of the partition you intend to delete

To select a disk, run the following command:

	sudo fdisk /dev/sdb
	
To delete partition, run the d command in the fdisk command-line utility

The partition is automatically selected if there are no other partitions on the disk. If the disk contains multiple partitions, select a partition by typing its number

The terminal prints out a message confirming that the partition is deleted

Reload the partition table to verify that the partition has been deleted. To do so, run the p command

Run the w command to write and save changes made to the disk



**linux useful commands**

    history > bash_history.txt
suggest change to desired directory, so can be addressed as . (dot).

    cd ~/Jinn/Data

find all files downward which are symbolic links, and `ls` them [safe!]
    
    find . -type l -ls

find all files downward which are symbolic links, and delete them [dangerous!!]

    find . -type l -delete

find all files downward which are symbolic links, and move them to your trash [a bit safer?]

    find . -type l -exec gio trash "{}" \;

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


### Finding out about your hardware and OS:

list all hardware:

    sudo lshw -short

list OS details:

    lsb_release -a

liat full details for RAM:

    sudo dmidecode --type memory

list disk drives:

    sudo lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL


### Emergency Linux stuff (for freezes, etc)

Use ctrl + alt + F1 to switch to terminal,
login.
run sudo service lightdm stop , lightdm and xserver should be stopped now 
(check with ctrl + alt + F7 , which is your current xorg session, 
it should not show any desktop now)
do your things.
run sudo service lightdm start to start lightdm and xorg again.

If it locks up completely, you can REISUB it, which is a safer alternative to just 
cold rebooting the computer.

REISUB by:

While holding Alt and the SysReq (Print Screen) keys, type REISUB.

R:  Switch to XLATE mode
E:  Send Terminate signal to all processes except for init
I:  Send Kill signal to all processes except for init
S:  Sync all mounted file-systems
U:  Remount file-systems as read-only
B:  Reboot

REISUB is BUSIER backwards, as in "The System is busier than it should be", 
if you need to remember it. 
Or mnemonically - R eboot; E ven; I f; S ystem; U tterly; B roken.


### finding files

If you're trying to find files, don't use ls. Use the find command.

find /usr -name '[prs]*'

If you don't want to search the entire tree under /usr, do this:

find /usr -maxdepth 1 -name '[prs]*'


### ps command

ps -ef | grep mysql  ssee explanation below

-e and -f are options to the ps command, and pipes take the output of one command and pass it as the input to another. Here is a full breakdown of this command:

 ps - list processes
 -e - show all processes, not just those belonging to the user
 -f - show processes in full format (more detailed than default)
 command 1 | command 2 - pass output of command 1 as input to command 2
 grep find lines containing a pattern
 processname - the pattern for grep to search for in the output of ps -ef

So altogether

ps -ef | grep mysql

means: look for lines containing processname in a detailed overview/snapshot of all current processes, and display those lines


### sudo apt-get install v package manager

sudo apt update
sudo apt upgrade
sudo apt-get install -f
sudo apt autoremove
apt list --upgradeable
apt-cache search pyqt5
sudo gedit sources.list "gives approved repositories"
sudo gedit /etc/apt/sources.list "allows you to add a repository"

apt list --upgradable
sudo gedit /etc/apt/sources.list
sudo apt update
sudo apt upgrade
sudo apt-get install -f

In some cases where I got Cannot locate package, I found the package on the Ubuntu packages web site which states: If you are running Ubuntu, it is strongly suggested to use a package manager like aptitude or synaptic to download and install packages, instead of doing so manually via this website. You can try manually adding any of the listed mirrors by adding a line to your /etc/apt/sources.list using gedit...  I added:

deb http://security.ubuntu.com/ubuntu trusty-security main
deb http://de.archive.ubuntu.com/ubuntu/ubuntu trusty main


### Sample levels of PyQt and Sip, etc

hezmondo@hezmondo-boatPC:~/Jinn/HezJinn$ python3 home.py --version
Python version: 3.5.2 (default, Nov 17 2016, 17:05:23) 
[GCC 5.4.0 20160609]
PyQt version: 5.5.1
Qt version: 5.5.1
SIP version: 4.17


### not sure what this was:

cd ~root
wget http://files.directadmin.com/services/debian_7.0_64/libmysqlclient.so.18
mv libmysqlclient.so.18 /usr/lib/x86_64-linux-gnu/
cd /usr/lib/x86_64-linux-gnu
chmod 755 libmysqlclient.so.18
ldconfig


### Installing partimage

sudo apt-get install partimage

sudo partimage


### Bash history

cat ~/.bash_history


??

**Lenovo hardware issues Dec 2018**

Determine the chipset
1. First you need to determine the exact chipset. Like this:

Launch a terminal window.

Use copy/paste to transfer the following word into the terminal:

lsusb

Press Enter.

Now you should see one line that approximately resembles the following output (example from my own computer):

Bus 002 Device 007: ID **0bda:818b** Realtek Semiconductor Corp.

The combination of characters and numbers that I've made red, is the unique ID of your Realtek chipset. Use Google to find out which chipset it is. The solution differs for every chipset.
