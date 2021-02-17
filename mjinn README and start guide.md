### basic start up guide for installing mjinn - last updated 16 Feb 2021

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

We normally run mjinn as a development server in debug mode.  Here is the relevant line at the end of mjinn.py:

if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)

If you wish to run mjinn as a test server on a PC and access it from another (eg android) device, use this line:

    app.run(host='0.0.0.0', debug=False, use_debugger=False, use_reloader=False, passthrough_errors=True)
 


	
