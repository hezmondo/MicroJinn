### basic start up guide for installing lulu - last updated 8 May 2021 for mysql server and workbench 8.0.24, python 3.9.4 all 64 bit

### install mysql server and mysql workbench using the mysql server and workbench installation guide
 
**Now install Python 3.9.4 (already in Linux) and pip. 

**Easy 3 minutes python install in Windows -download exe file from https://www.python.org/downloads/**

NB - remember to tick for all users and for pip and I chose location C:\Program files\Python39

**In Linux, you may need to install pip3** 

	sudo apt install python3-pip

Easy 2 minutes to install flask and other dependencies

first save these dependencies as lulu_dependencies.txt:

flask
flask-sqlalchemy
flask-migrate
flask-login
flask-mail
flask-pymysql
flask-bootstrap
flask-wtf
email_validator
PyJWT
cryptography
xhtml2pdf
flask-table
flask-caching

now open a terminal in Linux or a Powershell in Windows **as administrator**

in Windows, if you pip install not as administrator, all your dependencies get installed in C:\users\richard\appdate\roaming.
You end up with these in C:\Program files\Python39\Lib\site-packages. 

now in windows execute:

	pip install -r lulu_dependencies.txt

or in linux execute:

	pip3 install -r lulu_dependencies.txt
	
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


**How to set up to edit/run/debug mjinn in PyCharm (available as software app on all Linux platforms and also on Windows):**

File > Open > select mjinn directory. That loads it as a project.

Run > Edit Configurations > Select Flask/mjinn.py > defaults should be fine - use python interpreter

Find the Before launch near bottom of tab > click the green "+" beneath it > select desired Browser, for Url enter: http://127.0.0.1:5000/

Now you can run/debug from PyCharm, and it will open a new browser window for your app each time automatically. 

Output/debug messages will go to the PyCharm Console tab.


If you wish to run mjinn as a test server on a PC and access it from another (eg android) device, use this line:

    app.run(host='0.0.0.0', debug=False, use_debugger=False, use_reloader=False, passthrough_errors=True)
 


	
