### Basic start up guide for installing mjinn - last updated 24 Sep 2020

### It is assumed that you have already installed MySql Server and MySql Workbench using my separate guide and that
### you have already installed Python 3.7 or 3.8 (you will already have this installed in Ubuntu 20.04 or Mint 20)


### It is very easy (10 minutes) to install flask etc using a terminal in Linux or Powershell in Windows:

In Linux, simplest may be to install pip3 and use that:

	sudo apt install python3-pip
	
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
	
	pip3 install xhtml2pdf


In Windows, pip is already installed, so exactly the same but use pip instead of pip3

	pip install flask
	
	pip install flask-sqlalchemy
	
	pip install flask-migrate
	
	pip install flask-login
	
	pip install flask-mail
	
	pip install flask-pymysql
	
	pip install flask-bootstrap
	
	pip install flask-wtf
	
	pip install email_validator
	
	pip install PyJWT (requirements already satisfied)
	
	pip install xhtml2pdf
	
	
### Download the whole of the repo maintaining the directory structure.  

### Edit file named samplemyconfig.py to insert your user name and password setup details, then alter file name to myconfig.py

### How to set up to edit/run/debug mjinn in PyCharm (available as software app on all Linux platforms):

File > Open ..., select Fitness directory.  That loads it as a project.

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


	
