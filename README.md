# CS50 Web Project 1
[CS50 Web Programming with Python and JavaScript](https://www.edx.org/course/cs50s-web-programming-with-python-and-javascript)

# Student Name
[Hiroshi Igarashi](https://www.facebook.com/hiroshibook)

# application.py  
This is a main program of this book review application.
After receving HTTP request from users, the identified method attempts to access to data source, and pass data to the template file.

# layout.html
This html file is an outter layout of this book review site.

# index.html  
This is a login page for bookreview site.
If you don't have an account, you can click the link for registaion page.

# registration.html
This is a html file in order for new users to create thier account.

# user_account.html
This html file is a page which shows user account , and users can change their account infomation.

# mypage.html
After loggin a book review site, mypage.html is a home page for users.
They can browze recent book reviews and the book review they wrote in the past.

# search.html
This is a page for seaching books. Users can input ISBN, book title, and author as parameters for SQL query.

# booklist.html
This page shows the result of book search SQL query.
There is a view button to open the book.

# bookdetail.html
This page shows book information and bookreviews.
users can write thier book reviwew and also they can edit their review when they want to change it.

# write_bookreview.html
Users can write their bookreview in this page.

# edit_bookreview.html
Users can edit their bookreview in this page and also they can delete their bookreivew.

# delete_bookreview.html
After deleting bookreview , this pages appears to let users know that the deletion operation is successfull.

# error.html
If an error occurs , this page shows error messages.

# nav.tpl
This is a navigation bar template.

# Tables
## users table
This table stores user account. 
Primary key is user_id column.

## books table
This table stores book data. 
Primary key is isbn column.

## bookreviews table
This table stores bookreviews. 
Primary key is composed of isbn and user_id column. 

# Logging feature
In ./log/ directoy, this app creates bookreview_app.log so that developeres can track down bugs.

# Frontend frameworks / JavaScript libraries
- bootstrap4
- Chart.js
- jQuery DataTables

# Basic Concept about data registration
When registring and editing data, This app requires three steps.
First, this app sends the registration page to users and inputting and editing data is allowed.
When this app recevies data from users, data validations is executed.(Ex. password is correct or not)
If the data is invalid, input page is resent to users.
If the data is valid, confirmation page is generated and sent to users.
Second, conformation is required to review the input data. if users want to change input data, they can go back to the previous page by pressing back button on web browser. 
Finally, when input data is sent to the server, the sql for insertion or update is created and executed.

