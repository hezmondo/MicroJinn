### Basic start up guide for installing mjinn - last updated 17 Aug 2020

### It is assumed that you have already installed MySql Server and MySql Workbench using my separate guide and that
### you have already installed Python 3.7 (you will already have this installed in Ubuntu 20.04 or Mint 20)


### It is very easy (10 minutes) to install flask etc using a terminal in Linux or Powershell in Windows:

In Linux, simplest may be to install pip3:

	sudo apt install python3-pip
	
	pip3 install flask
	
	pip3 install flask-sqlalchemy
	
	pip3 install flask-migrate
	
	pip3 install flask-login
	
	pip3 install flask-mail
	
	pip3 install flask-pymysql
	
	pip3 install flask-bootstrap
	pip install flask-wtf

	sudo apt-get install python3-flask (Linux) or pip install flask (Windows)

	sudo apt-get install python3-flask-sqlalchemy (Linux) or pip install flask-sqlalchemy (Windows)

	sudo apt-get install python3-flask-migrate (Linux) or pip install flask-migrate (Windows)

	sudo apt-get install python3-flask-login (Linux) or pip install flask-login (Windows)

	sudo apt-get install python3-flask-mail (Linux) or pip install flask-mail (Windows)

	sudo apt-get install python3-flask-pymysql (Linux) or pip install flask-mysql (Windows)

	python3 -m pip install flask-bootstrap (Linux) or pip install flask-bootstrap (Windows)

	python3 -m pip install flask-wtf (Linux) or pip install flask-wtf (Windows)
	
	python3 -m pip install email_validator (Linux) or pip install email_validator (Windows)

	python3 -m pip install PyJWT (Linux - already in Ubuntu 20.04) or pip install PyJWT (Windows)
	
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


	
