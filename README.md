# Mobile RFID Reader

Welcome to the documentation for the Mobile RFID Reader. This documentation is divided into two main sub-sections, namely **Drone-Inventory App** and **Unmanned Aerial Vehicle (UAV) Setup/Configuration**. 

This projects situates itself as a high-level "proof-of-concept." The ultimate goal of this project is to show that scanning RFID-enabled inventory from a UAV is feasible and can provide tremendous performance benefits for both inventory managers as well as in-field workers.

The project utilizes a Bebop 2 drone as the base and utilizes a variety of sensors to detect RFID enabled inventory as well as its approximate location (see the "Unmanned Aerial Vehicle (UAV) Setup/Configuration" for additional details). All of this data is made accessible to users via the Drone-Inventory App. Viewing scanned inventory, flight control as well as inventory management can all be performed using the Drone-Inventory App.

(This documentation was formatted with Markdown and therefore a Markdown reader is recommended!)

### Authors:
[Jason Elting](mailto:elting.2@wright.edu "elting.2@wright.edu"), [Jameson Morgan](mailto:morgan.219@wright.edu "morgan.219@wright.edu"), [Zia Anwar](mailto:anwar.3@wright.edu "anwar.3@wright.edu") and [Kiran Wani](mailto:wani.4@wright.edu "wani.4@wright.edu")

### GitHub:

https://github.com/morgan219/wsu-team-projects (restricted)

### License:
The MIT License

Copyright 2018 Jason Elting, Jameson Morgan, Zia Anwar and Kiran Wani

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Notice:

<em>This project was developed for Team Projects I & II (CEG 4980/4981 or EE 4910/4920) at Wright State University (WSU) during the Fall 2017 and Spring 2018 semesters. All aspects of this project remain the intellectual property of Wright State University and this project's authors (named above).</em>

<br>

## Drone-Inventory App
The Drone-Inventory App is the graphical user interface (GUI) for the Mobile RFID Reader project. The application operates on port 8000 and is accessible through the following URL or IP:

* URL: http://team21.cs.wright.edu:8000/rfid/api/v1/inventory

* IP: 130.108.78.45:8000/rfid/api/v1/inventory

The application is password protected and uses the HTTPAuth login process. Only users with valid username/password combinations are allowed to access the Drone-Inventory App. NOTE: The drone utilizes a special username/password combination for accessing the application.

### Returned Inventory Display:
By default, the returned inventory database is deleted after an application refresh. In addition, a user can utilize the "Delete" button to simply clear all entries returned. This **will not** delete the items from the inventory database but simply "clears" the returned inventory screen.

### Database Configuration:
- id, unique-autoincrementer, integer
- title, title of inventory item, string type
- tag, tag number of inventory item, string type
- location, location information for inventory item, text type

### API:
The application is based upon a REST API with data being passed in via HTTP GET and POST requests. Data is passed in using using the HTTP form format (application/x-www-urlencoded) and is retrieved using `request.form['tag_id']` from within the Flask application.

<pre>
+___________________________________________________________________________________+________+____________________________________________________________________________________________+
| URL                                                                               | TYPE   | Parameters                       | Result                                                  |
+===================================================================================+========+==================================+=========================================================+
| http://team21.cs.wright.edu:8000/rfid/api/v1/flight                               | GET    | None                             | Shows flight control page                               | 
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/about                                | GET    | None                             | Shows about page for project                            |
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/inventory                            | GET    | None                             | Shows the inventory returned page                       |
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/inventory                            | POST   | None                             | Posts inventory (tag, name, location) to main database  |
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/database                             | GET    | None                             | Shows the database management page                      |
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/inventory/get                        | POST   | tag (type:text)                  | Retrieves specific item (by tag) from inventory returned|
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/database/get                         | POST   | tag (type:text)                  | Retrieves specific item (by tag) from main database     |
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/inventory/posttag                    | POST   | tag (type:text)                  | Posts inventory (tag, name, location) to returned       |
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/inventory/update                     | POST   | title, tag, location (types:text)| Updates inventory (tag, name, location) in main database|
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/inventory/delete                     | POST   | tag (type:text)                  | Deletes inventory (tag, name, location) in main database|
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/inventory/delete_returned_inventory  | POST   | None                             | Clears inventory (tag, name, location) from returned    |
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/inventory/getDatabase                | GET    | None                             | Returns the main database for backup purposes           |
+-----------------------------------------------------------------------------------+--------+----------------------------------+---------------------------------------------------------+
| http://team21.cs.wright.edu:8000/rfid/api/v1/keepAlive (COMING SOON!)             | GET    | None                             | Keep alive used for checking communication with Pi      |
+___________________________________________________________________________________+________+__________________________________+_________________________________________________________+
</pre>

### Sample API Calls (using curl):
Only items which exist in the main database will be displayed. In other words, if a scanned tag does not exist within the main database, it will not be displayed to the user. The UAV scanning application should utilize an HTTP POST request in order to pass this information to the application. An example 'curl' call is included below for reference.

Display Scanned Item <br>
`curl -u <username>:<password> -d "tag=<tag_number>" -X POST http://team21.cs.wright.edu:8000/rfid/api/v1/inventory/posttag`

Create Inventory Item <br>
`curl -u <username>:<password> -d "tag=<tag_number>&title=<title>&location=<location>" -X POST http://team21.cs.wright.edu:8000/rfid/api/v1/inventory`

### API NOTES:

* Only unique tags are accepted during creation. If a user inputs a tag which already exists within the main database, a friendly error message will result. If a user tries to display the same tag to the user, an error will result.
* The .../posttag url should be used for displaying the current scanned inventory, however, please note that it simply checks for a valid entry in the main database and displays it. Therefore, in order to properly update the location please call .../update url with the updated location prior to calling the .../posttag url. This will ensure that the displayed tag utilizes the most recent location.
* Updating the inventory can take up to three parameters, namely the title tag and location. If the title is left out, it simply updates the the location.

### RFID Reader:
The reader used for this project is the sparkfun M6E Nano. This reader is based upon one of th ThingMagic RFID readers and therefore can utilize the ThingMagic Python Wrapper Library (https://github.com/gotthardp/python-mercuryapi). We utilized this library for our project. To install the ThingMagic Python Wrapper Library, simply follow the installation instructions located on the repositories GitHub page.

### Scanning RFID Tags:
The scanning of RFID tags occurs through the `scan_rfid.py` file. The following settings are configurable and are modified in-code:

* `runtime`: specifies how long to scan for tags, by default 10 seconds
* `region`: specifies the geographical region, by default NA2
* `protocol`: specifies the rfid type, by default GEN2 for EPC Gen. 2
* `power`: specifies power in centi-decibles, by default 1900
* `credentials`: specifies the login credentials to the Drone-Inventory App, format: username:password
* `posturl`: specifies the URL that should be used to POST tags to
* `antenna`: specifies which antenna to use, defaults to 1

<br>

## Unmanned Aerial Vehicle (UAV) Setup/Configuration
### Current Hardware: 
![alt text](https://i.imgur.com/0dPaKkW.jpg "Hardware")
