# trackyourgoods
Udacity Project 3

## Setup
1 - Clone Vagrant <br>
2 - Install dependencies (SQLAlchemy, dict2xml, flask-seasurf) <br>
3 - Setup Database (run database_setup.py) <br>
3a - Insert dummy data by running (dummyclosetdata.py) <br>
3b - May have to change username in dummyclosetdata.py <br>
4 - Run project_tyg.py <br>
5 - Navigate to localhost:/5000/index <br>

## Extra Credit Applied
1 - XML files can be found: <br>
1a) http://localhost:5000/closet/[closet_id]/collection_XML <br>
2 - Image files read and view on page <br>
2a) Uploaded Image files found at  http://localhost:5000/closet/[closet_id]/items/ <br>
3 - Image Upload/Edit found in appropriate files  <br>
3a) Click on three dots under image to edit or delete an image <br>
4 - CSRF implemented in appropriate HTML files using Seasurf <br>

## 
-- Login found on left toolbar (click upper left menubar and arrow down)
-- Delete/Edit items found by clicking three dot menu bars near each closet/item
-- Adding new closets/items can be done by hitting button on bottom right
