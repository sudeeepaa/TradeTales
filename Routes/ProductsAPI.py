from flask import Flask, request, jsonify, Blueprint
from DBUtility.DataBase import Database  # Assuming Database class exists for DB connection

product_app = Blueprint('product_app', __name__)


@product_app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    query = """
        INSERT INTO products (name, description, price, stock_quantity, category) 
        VALUES (%s, %s, %s, %s, %s) RETURNING product_id;
    """
    product_id = Database.execute_query(query,
                                        (data['name'], data['description'], data['price'],
                                         data['stock_quantity'], data['category']), fetch=True)

    return jsonify({'message': 'Product added successfully', 'product_id': product_id}), 201


# Get All Products
@product_app.route('/products', methods=['GET'])
def get_products():
    query = "SELECT * FROM products;"
    products = Database.execute_query(query)
    return jsonify(products)


# Get Product by ID
@product_app.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    query = "SELECT * FROM products WHERE product_id = %s;"
    product = Database.execute_query(query, (product_id,))
    if product:
        return jsonify(product[0])  # Since it's a list, return the first item
    return jsonify({'message': 'Product not found'}), 404


# Update Product
@product_app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    query = """
        UPDATE products SET name = %s, description = %s, price = %s, stock_quantity = %s, category = %s
        WHERE product_id = %s RETURNING product_id;
    """
    updated_product = Database.execute_query(query,
                                             (data['name'], data['description'], data['price'],
                                              data['stock_quantity'], data['category'], product_id), fetch=True)
    if updated_product:
        return jsonify({'message': 'Product updated successfully'})
    return jsonify({'message': 'Product not found'}), 404


# Delete Product
@product_app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    query = "DELETE FROM products WHERE product_id = %s RETURNING product_id;"
    deleted_product = Database.execute_query(query, (product_id,), fetch=True)
    if deleted_product:
        return jsonify({'message': 'Product deleted successfully'})
    return jsonify({'message': 'Product not found'}), 404

