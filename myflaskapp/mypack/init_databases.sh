#!/bin/bash

echo "Begin Init Process"

echo "Removing Old Databases"
sudo rm rfid.db
sudo rm returned.db

sudo sqlite3 rfid.db < schema.sql
echo "Created Main Database"

sudo sqlite3 returned.db <schema.sql
echo "Created Returned Inventory Database"

sudo chmod 777 rfid.db
sudo chmod 777 returned.db
echo "Adjusted File Access"

echo "Complete!"
