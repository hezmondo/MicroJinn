### basic start up guide for installing mjinn - last updated 25 Dec 2020

### install mysql server and mysql workbench using the mysql server and workbench installation guide
 
**Now install Python 3.7, 3.8 or 3.9 (already in Linux). Easy and quick to install in Windows - https://www.python.org/downloads/**

It is then very easy (10 minutes) to install flask and other dependencies using a terminal in Linux or Powershell in Windows:

**In Linux, simplest may be to install pip3** 

	sudo apt install python3-pip

and then use pip3 to install these dependencies:
	
	pip3 install flask
	
	pip3 install flask-sqlalchemy
	
	pip3 install flask-migrate
	
	pip3 install flask-login
	
	pip3 install flask-mail
	
	pip3 install flask-pymysql
	
	pip3 install flask-bootstrap
	
	pip3 install flask-wtf
	
	pip3 install email_validator
	
	pip3 install PyJWT (requirements already satisfied)
	
	pip3 install cryptography
	
	pip3 install xhtml2pdf

    pip3 install flask-table

**In Windows, pip is already installed, so just do the same pip installs as above but use pip instead of pip3**
	
### Now download the mjinn code from the github repo, maintaining the directory structure.  

### Edit the file named samplemyconfig.py to insert your mysql user name and password details, then rename as myconfig.py

Starting the flask server can be done by executing python mjinn.py in windows or python3 mjinn.py in Linux

The app will only start if:

1. The mjinn schema exists in mysql
2. myconfig.py is properly configured with a valid mysql username and password
3. all dependencies have been installed
4. the mjinn schema has been populated sufficiently - please see the new mjinn user guide and my new mysql server and workbench installation guide

 
### How to set up to edit/run/debug mjinn in PyCharm (available as software app on all Linux platforms and also on Windows):

File > Open ..., select mjinn directory.  That loads it as a project.

Run > Edit Configurations ....  Find the Before launch near bottom of tab, click the green "+" beneath it.

Select desired Browser, for Url enter: http://127.0.0.1:5000/

Now you can run/debug from PyCharm, and it will open a new browser window for your app each time automatically.  Output/debug messages go to PyCharm Console tab.


### How to install Chrome in Ubuntu 20.04:  In a terminal:

First install the gdebi and wget packages. By using gdebi to install Google Chrome browser we also ensure that any possible package prerequisites are met during the installation:
	
	sudo apt install gdebi-core wget

now download the Google Chrome browser pack:

	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
	
Now use gdebi command to install the prevously downloaded Google Chrome package: 

	sudo gdebi google-chrome-stable_current_amd64.deb
	
Now go to apps and you will see Chrome available


	
