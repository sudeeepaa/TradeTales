from flask import Flask
from Routes.LoginApi import login_app  # Import the Blueprint
from Routes.ProductsAPI import product_app
from flask_cors import CORS
app = Flask(__name__)
app.register_blueprint(login_app)  # Register the blueprint
app.register_blueprint(product_app)
CORS(app)
if __name__ == '__main__':
    app.run(debug=True)
