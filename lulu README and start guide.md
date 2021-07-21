### lulu start up guide - last updated 21 July 2021 

Current Hez office PC is running: 

>- mysql server and workbench 8.0.25 - 64 bit
> 
>- python 3.9.5 - 64 bit


>1. install mysql server and mysql workbench using the mysql server and workbench installation guide - 5 mins

>2. install Python 3.9.5 and pip - in Windows, download exe file here [PyPi](https://www.python.org/downloads/) - 3 mins  
>
>- in windows, remember to tick for all users and for pip. I chose location C:\Program files\Python39
>
>- in Linux, you may need to install pip3 with `sudo apt install python3-pip`

>3. Install flask and other python dependencies - 3 mins
>
>- Open a terminal or command window or powershell window **as administrator - very important** and 
>-  in windows execute `pip install -r lulu_dependencies.txt`
>-  or in linux execute	`pip3 install -r lulu_dependencies.txt`

>4. Download the mjinn code folder or get a copy from Hez - be careful to maintain the directory structure
	
>5. Edit the file mjinn/samplemyconfig.py to insert your mysql user name and password details and save as `myconfig.py`

>6. You can start the flask server by opening a terminal or command window or powershell in C:\mjinn and
>    
>-  in windows execute `python mjinn.py`
>-  or in linux execute	`python3 mjinn.py`

>  The app will only start if:
>
>-  The mjinn schema exists in mysql and has been populated sufficiently - please see the new data install guide below
>- myconfig.py is properly configured with a valid mysql username and password
>- all python dependencies have been installed

###Instructions for advanced users and programmers:

>We normally run mjinn as a development server in debug mode.  Here is the relevant line at the end of mjinn.py:
>
>- if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)

>How to set up to edit/run/debug mjinn in PyCharm (available as software app on all Linux platforms and also on Windows):
>
>- File > Open > select mjinn directory. That loads it as a project.
>
>- Run > Edit Configurations > Select Flask/mjinn.py > defaults should be fine - use python interpreter
>
>- Find the Before launch near bottom of tab > click the green "+" beneath it > select desired Browser, for Url enter: http://127.0.0.1:5000/
>
>- Now you can run/debug from PyCharm, and it will open a new browser window for your app each time automatically. 
>
>- Output/debug messages will go to the PyCharm Console tab.
>
>- If you wish to run mjinn as a test server on a PC and access it from another (eg android) device, use this line:
>- app.run(host='0.0.0.0', debug=False, use_debugger=False, use_reloader=False, passthrough_errors=True)
 
 
###New data installation guide - how to set up and populate the schema for the first time

>1. In workbench, drop the mjinn schema if it exists and 'create schema mjinn' to create an empty schema
>
>2. Delete the Flask/mjinn/migrations table, if it exists
>
>3. Open a terminal/command window/powershell window in Flask/mjinn and execute these commands:
>- flask db init
>- flask db migrate
>- flask db upgrade
>
>4. In workbench, make sure you have your yoda schema present with all your live yoda/jinn data and then run the following mysql queries in workbench to populate the tables and routines:
>- Run `start_pop_routines.sql` to set up the functions and procedures
>- Run `start_pop_basic_tables.sql` to populate several tables which have largely static data.  Several of these tables will need to be edited by the new user to suit his or her preferences
>- Run `start_pop_rent_external.sql` to populate the rent_external and manager_external tables with your yoda/jinn data
>- Run `start_pop_income_tables.sql` to populate the income tables with your yoda/jinn data
>- Run `start_pop_money_tables.sql` to populate the money tables with your yoda/jinn data
>- Run `start_pop_rentplus_tables.sql` to populate the agent, rent, and other tables with your yoda/jinn data
	
