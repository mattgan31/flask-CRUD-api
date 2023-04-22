from flask import Flask, request, jsonify, make_response
import mysql.connector
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "LDblvz6FvtHHRbNCcsAIk6h3m51tdrGf"

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({
                "data": "Token Required",
                "code": 403
            }), 403

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({
                "data": "Token Expired",
                "code": 403
            }), 403
        except jwt.exceptions.InvalidTokenError:
            return jsonify({
                "data": "Token Invalid",
                "code": 403
            }), 403

        return f(*args, **kwargs)
    return decorator

db = mysql.connector.connect(
    host = "127.0.0.1",
    user = "root",
    passwd = "",
    database = "flask_product",
    auth_plugin = "mysql_native_password"
)

@app.route("/login",endpoint="login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "data": "Username and password are required",
                "code": 400
            }), 400

        cursor = db.cursor()
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({
                "data": "Invalid username or password",
                "code": 401
            }), 401

        user_password = user[2]
        if not check_password_hash(user_password, password):
            return jsonify({
                "data": "Invalid username or password",
                "code": 401
            }), 401

        token = jwt.encode({
            "user": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config["SECRET_KEY"])

        return jsonify({
            "data": "Login Success",
            "token": token,
            "code": 200
        }), 200

    except Exception as e:
        return jsonify({
            "data": str(e),
            "code": 500
        }), 500


@app.route("/register", endpoint="register", methods=["POST"])
def register():
    try:
        data = request.json
        cursor = db.cursor()

        # check if username already exists
        existing_users = "SELECT username FROM users WHERE username=%s"
        cursor.execute(existing_users, (data['username'],))
        if cursor.fetchone():
            return jsonify({
                "data": "Username already exists!",
                "code": 400
            }), 400

        # hash the password and insert new user into the database
        hashed_password = generate_password_hash(data['password'])
        insert_user = "INSERT INTO users (id, username, password) VALUES (NULL, %s, %s)"
        values = (data['username'], hashed_password)
        cursor.execute(insert_user, values)
        db.commit()

        return jsonify({
            "data": "Registration successful",
            "code": 200
        }), 200

    except Exception as e:
        return jsonify({
            "data": str(e),
            "code": 500
        }), 500


@app.route("/products", endpoint="getProducts", methods=["GET"])
@token_required
def get_products():
    try:
        cursor = db.cursor()

        # get all products
        cursor.execute("SELECT * FROM products")
        result = [{"id": i[0], "productName": i[1], "price": i[2]} for i in cursor.fetchall()]

        return jsonify({
            "data": result, 
            "code": 200
            }), 200
    
    except Exception as e:
        return jsonify({
            "data": str(e),
            "code": 500
            }), 500

@app.route("/products/<int:id>", endpoint="getProductByID", methods=["GET"])
@token_required
def get_product_by_id(id):
    try:
        cursor = db.cursor()

        # get product by id
        cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
        data = cursor.fetchall()[0]
        result = {"id": data[0], "productName": data[1], "prdatace": data[2]}

        return jsonify({
            "data": result, 
            "code": 200
            }), 200
    
    except Exception as e:
        return jsonify({
            "data": str(e), 
            "code": 500 
            }), 500

@app.route("/products", endpoint="insertProduct", methods=['POST'])
@token_required
def insert_product():
    try:
        data = request.json
        cursor = db.cursor()

        # insert data products
        sql = "INSERT INTO products (id, productName, price) VALUES (NULL, %s, %s)"
        value = (data['productName'], data['price'])
        cursor.execute(sql, value)
        db.commit()

        return jsonify({
            "data": "1 Record Inserted", 
            "code": 200
            }), 200
    
    except Exception as e:
        return jsonify({
            "data": str(e), 
            "code": 500
            }), 500

@app.route("/products/<int:id>", endpoint="updateProductById", methods=["PUT"])
@token_required
def update_product_by_id(id):
    try:
        data = request.json
        cursor = db.cursor()

        # update data product by id
        sql = "UPDATE products SET productName = %s, price = %s WHERE id = %s"
        value = (data['productName'], data['price'], id)
        cursor.execute(sql, value)

        # check if id not found
        if cursor.rowcount == 0:
            return jsonify({
                "data": "No product with the given ID was found",
                "code": 404
            }), 404
        db.commit()

        return jsonify({
            "data": "1 Record Affected",
            "code": 200
        }), 200
    
    except Exception as e:
        return jsonify({
            "data": str(e),
            "code": 500
        }), 500

@app.route("/products/<int:id>", endpoint="deleteProductByID", methods=["DELETE"])
@token_required
def deleteProductById(id):
    try:
        cursor = db.cursor()

        # delete data products by id
        cursor.execute("DELETE FROM products WHERE id = %s", (id,))
        
        # check if id not found
        if cursor.rowcount == 0:
            return jsonify({
                "data": "No product with the given ID was found",
                "code": 404
            }), 404
        db.commit()

        return jsonify({
            "data": "1 Record Deleted",
            "code": 200
        }), 200
    
    except Exception as e:
        return jsonify({
            "data": str(e),
            "code": 500
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
