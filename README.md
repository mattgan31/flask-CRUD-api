# About this Project
This repo is a result of my learning about Python Flask Basic, basically this backend app included Auth, JWT with timer, and Basic CRUD Features

## How to use ?

- First, you can create MySQL database with name `flask_product` or whatever you want (You must edit dbname in the script).
- You must create 2 table use with the next Query

Query for Users table:
```sql
    CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);
```
Query for Products table:
```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    productName VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
);
```
- Next, you need to install some modules used in this project
```sh
pip install flask mysql.connector
```

- Now you can run the project use
```sh
py app.py
```
or
```sh
python3 app.py
```

## Endpoints

### POST /register
Request:
```
POST /register
Content-Type: application/json

{
    "username": "Your username",
    "password": "your_password"
}
```

Response:
```json
{
    "code": 200,
    "data": "Register successfull"
}
```

### POST /login

Request:
```
POST /login
Content-Type: application/json

{
    "username": "Your username",
    "password": "your_password"
}
```

Response:
```json
{
    "code": 200,
    "data": "Login Success",
    "token": "token_generated"
}
```

### POST /products

Request:
```
POST /products
Content-Type: application/json

{
    "productName": "Product Name",
    "price": 100000
}
```
Response:
```json
{
    "code": 200,
    "data": "1 Record Inserted"
}
```

### GET /products

Request:
```
GET /products
```
Response:
```json
{
    "code": 200,
    "data": [
        {
            "id": 1,
            "price": "100000.00",
            "productName": "Product Name 1"
        },
        {
            "id": 2,
            "price": "200000.00",
            "productName": "Product Name 2"
        },
        {
            "id": 3,
            "price": "300000.00",
            "productName": "Product Name 3"
        }
    ]
}
```

### GET /products/{id}

Request:
```
GET /products/1
```
Response:
```json
{
    "code": 200,
    "data": {
        "id": 1,
        "price": "1000000.00",
        "productName": "Product Name"
    }
}
```
### PUT /products/{id}

Request:
```
PUT /products/1
{
    "productName": "Product Name",
    "price": 10000000
}
```

Response:
```json
{
    "code": 200,
    "data": "1 Record Affected"
}
```

### DELETE /products/{id}

Request:
```
DELETE /products/1
```

Response:
```json
{
    "code": 200,
    "data": "1 Record Deleted"
}
```
