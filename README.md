## Tea Online Shop

This project was developed using Python 3.9, Flask web framework, and SQLite. 

The system API will allow customers to search for products sold at the website and buy purchase them while updating the order status and at each stage of the purchasing journey. Products are sold both by the website itself and several third-party sellers as part of the website’s marketplace. Third-party sellers can be individuals or organisations, and once they have registered as a seller, they maintain their own product catalogue, pricing and storefront. If a product is temporarily out of stock, then then it will be marked as unavailable.
#How to Start
1- Install the packages in your own virtual environment using the $ pip3 install -r requirements.txt

2- Start the server using python app.py command while in the project root directory. Once the server is running, the web app can be accessed by navigating to http://127.0.0.1:5000 in a web browser.

3- Use the CLI commands if needed to create a new database, and import the test data

Create the database tables flask db_create

Delete the database records flask db_drop

Import the test data flask db_seed

| Email               | Password            | Role                |
| ------------------- | ------------------- | ------------------- |
| admin@email.com     | password            | Admin               |
| seller@seller.com   | Password            | Individual Seller   |
| customer@store.com  | Password            | Customer            |

4- The system has only REST APIs, so you'll need to use REST Client such as Postman to be able to login and use the application commands
## REST API
All data is sent and recieved as JSON.
The API contains the following resources:

| Resource                       | Methods                 |
| -------------------------      | ----------------------- |
| /login                         | POST                    | 
| /register                      | POST                    |
| /add_product                   | POST                    | 
| /product_details/<product_id>  | GET                     | 
| /product_details/search        | POST                    | 


POST /login` allows users to log in by sending their email and password body form data request. This request
will return a JSON web token which must be sent with add product request.

Post /register allows users to register by sending their email and password via body form data request.

POST /add_product allows users with the authentication token to add new products by passing all of the product information in the body form data request.

GET /product_details/<product_id> allows users to retrieve the product full details by passing the product Id in the URL.

POST /product_details/search allows users to search for a product by a word that matches any other word in the product name by passing the keyword in the body form data request as product_name.

## Tests
Kindly view the screenshots folder to view the queries and database structure, the imported data is a proof that the classes and relationships are well implemented, however the app is missing the ability to render the pages and make the queries to join the data tables.

### References
- LinkedIn. 2021. Building RESTful APIs with Flask Online Class | LinkedIn Learning, formerly Lynda.com. [online] Available at: https://www.linkedin.com/learning/building-restful-apis-with-flask.
- Richard Taujenis. 2021. Flask Web application One to Many database relationship with CRUD operation | Nerd For Tech. [online] Available at: https://medium.com/nerd-for-tech/one-to-many-database-relationship-crud-with-postgresql-and-flask-part-1-6f87fb574b7c.
- YouTube. 2021. Python Flask Tutorial - Blog project - YouTube. [online] Available at: https://www.youtube.com/playlist?list=PLe4mIUXfbIqaLWrzsSDQAAK3_NQB1jBZZ.
