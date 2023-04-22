from flask import Flask, request, jsonify, make_response
import mysql.connector
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import pytz

app = Flask(__name__)
app.config["SECRET_KEY"] = "LDblvz6FvtHHRbNCcsAIk6h3m51tdrGf"
app.config["DEBUG"]=True

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
        except:
            return jsonify({
                "data": "Token Invalid",
                "code": 403
            }), 403
        return f(*args, **kwargs)
    return decorator

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "",
    database = "flask_product",
    auth_plugin = "mysql_native_password"
)

@app.route("/login", endpoint="login", methods = ["POST"])
def login():
    try:
        data = request.json
        cursor = db.cursor()
        sql = "SELECT * FROM users WHERE username=%s"
        cursor.execute(sql, (data["username"],))
        user = cursor.fetchone()
        if user is None:
            return jsonify({
                "data": "Invalid username or password",
                "code": 401
            }), 401

        user_password = user[2]
        if check_password_hash(user_password, data['password']):
            token = jwt.encode({
                "user": data["username"],
                "exp": datetime.datetime.utcnow()+datetime.timedelta(minutes=30)
            }, app.config["SECRET_KEY"]).encode("UTF-8")
            return jsonify({
                "data": "Login Success",
                "token": token.decode("UTF-8"),
                "code": 200
            }), 200
        else:
            return jsonify({
                "data": "Login is Invalid",
                "code": 403
            }), 403
    except Exception as e:
        return jsonify({
            "data": str(e),
            "code": 500
        }), 500

@app.route("/register", endpoint="register", methods = ["POST"])
def register():
    try:
        data = request.json
        cursor = db.cursor()
        existing_users = "SELECT username FROM users WHERE username=%s"
        cursor.execute(existing_users, (data['username'],))
        row = cursor.fetchone()
        if row:
            return jsonify({
                "data": "Username already exists!",
                "code": 400
            }), 400

        hashed_password = generate_password_hash(data['password'])
        sql = "INSERT INTO users (id, username, password) VALUES (NULL, %s, %s)"
        value = (data['username'], hashed_password)
        cursor.execute(sql, value)
        db.commit()
        return jsonify({
            "data": "Register successfull",
            "code": 200
        }), 200
    except Exception as e:
        return jsonify({
            "data": str(e),
            "code": 500
        }), 500


@app.route("/products", endpoint="getProducts", methods=["GET"])
@token_required
def getProduct():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM products")
        result = []
        for i in cursor.fetchall():
            result.append({
                "id": i[0],
                "productName": i[1],
                "price": i[2]
            })
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
def getProductById(id):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
        data = cursor.fetchall()[0]
        result = {
            "id": data[0],
            "productName": data[1],
            "price": data[2]
        }
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
def insertProduct():
    try:
        data = request.json
        cursor = db.cursor()
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
def updateProductById(id):
    try:
        data = request.json
        cursor = db.cursor()
        sql = "UPDATE products SET productName = %s, price = %s WHERE id = %s"
        value = (data['productName'], data['price'], id)
        cursor.execute(sql, value)
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
        cursor.execute("DELETE FROM products WHERE id = %s", (id,))
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
