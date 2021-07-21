from flask import render_template, Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric
import os
from datetime import datetime
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

# flask and SQLAlchemy configuration
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret-sauce'  # change this IRL

# initialising database, and authentication
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


# CLI commands to create, seed, and drop the database
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


@app.cli.command('db_seed')
def db_seed():
    test_user = User(email='admin@admin.com',
                     password='admin')
    # add seller as website owner
    test_seller = Seller(email='seller@seller.com',
                         password='Password', seller_type=0)

    # add seller as third-party individual
    test_seller_individual = Seller(email='individual@seller.com',
                                    password='Password', seller_type=1)

    # add seller as third-party organisation
    test_seller_org = Seller(email='org@seller.com',
                             password='Password', seller_type=2)
    # add warehouse staff
    test_staff = WarehouseStaff(email='staff@store.com',
                                password='Password', staff_id=56)
    # add a customer user
    test_customer = Customer(email='customer@store.com',
                             password='Password', shipping_info='Abbey Road, London')
    # adding payment details
    test_pay_details = Paymentdetails(payment_type='PayPal', auth_token='000111000', customer=test_customer)

    # adding products
    Earl = Product(product_name='Earl Grey Cream Tea',
                   product_description='A smooth blend with vanilla overtones',
                   product_quantity='200',
                   product_price=15,
                   product_warehouse_location='E24',
                   product_status=True,
                   )

    Jasmine = Product(product_name='Jasmine Tea',
                      product_description='Jasmine Teas are an indulgent treat for all the senses and can be enjoyed at any time of the day.',
                      product_quantity='89',
                      product_price=19,
                      product_warehouse_location='K29',
                      product_status=True,
                      )

    Assam = Product(product_name='Assam Tea - Loose Leaf',
                    product_description='The Assam Tea blend from English Tea Store is a strong tea, and makes a '
                                        'great start to the day',
                    product_quantity='20',
                    product_price=12,
                    product_warehouse_location='Z12',
                    product_status=True,
                    )

    Buckingham = Product(product_name='Buckingham Palace Garden Party Tea',
                         product_description='Perfect for afternoon settings',
                         product_quantity='45',
                         product_price=18,
                         product_warehouse_location='G07',
                         product_status=True,
                         )
    # adding orders, order history and payment
    test_order = Order(customer=test_customer, order_status=0, quantity=10, order_items=Earl)
    test_order2 = Order(customer=test_customer, order_status=2, quantity=2, order_items=Buckingham)
    test_orderHistory = OrderHistory(order_status=0, order_id=test_order)
    test_orderHistory2 = OrderHistory(order_status=0, order_id=test_order2)
    test_payment = Payment(order_id=test_order2, status=1, total=645)

    db.session.add(test_user)
    db.session.add(test_seller)
    db.session.add(test_seller_individual)
    db.session.add(test_seller_org)
    db.session.add(test_staff)
    db.session.add(test_pay_details)
    db.session.add(test_customer)

    db.session.add(Earl)
    db.session.add(Assam)
    db.session.add(Buckingham)

    db.session.add(test_order)
    db.session.add(test_order2)
    db.session.add(test_orderHistory)
    db.session.add(test_orderHistory2)
    db.session.add(test_payment)

    db.session.commit()
    print('Database seeded!')


# setting up the application routing
@app.route('/')
def hello_world():
    return 'This is a REST API application'


# retrieve all products end point
@app.route('/products', methods=['GET'])
def products():
    products_list = Product.query.all()
    result = products_schema.dump(products_list)
    return jsonify(result)


# user registration end point
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exists.'), 409
    else:
        password = request.form['password']
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully."), 201


# user login and authentication end point
@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login succeeded!", access_token=access_token)
    else:
        return jsonify(message="Bad email or password"), 401


# retreive a product by the product Id
@app.route('/product_details/<int:product_id>', methods=["GET"])
def product_details(product_id: int):
    product = Product.query.filter_by(product_id=product_id).first()
    if product:
        result = product_schema.dump(product)
        return jsonify(result)
    else:
        return jsonify(message="That product does not exist"), 404


# search for a product by the product name
@app.route('/products/search', methods=['POST'])
def search_product():
    product_name2 = request.form['product_name']

    product = Product.query.filter(Product.product_name.contains(product_name2)).all()
    if product:
        result = products_schema.dump(product)
        return jsonify(result)
    else:
        return jsonify(message="That product does not exist"), 404


# add a new product by authenticated seller or website owner
@app.route('/add_product', methods=['POST'])
@jwt_required()
def add_product():
    product_name = request.form['product_name']
    test = Product.query.filter_by(product_name=product_name).first()
    if test:
        return jsonify("There is already a product by that name"), 409
    else:
        product_description = request.form['product_description']
        product_quantity = request.form['product_quantity']
        product_price = int(request.form['product_price'])
        product_warehouse_location = request.form['product_warehouse_location']
        product_status = int(request.form['product_status'])

        new_product = Product(product_name=product_name,
                              product_description=product_description,
                              product_quantity=product_quantity,
                              product_price=product_price,
                              product_warehouse_location=product_warehouse_location,
                              product_status=product_status)

        db.session.add(new_product)
        db.session.commit()
        return jsonify(message="You added a Product"), 201


"""User table in database. Stores user information"""

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    type = db.Column(db.String(20))
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'user'
    }


"""Customer inheritance from user to store the customer information and relationships with other tables such as 
payment details """

class Customer(User):
    shipping_info = db.Column(db.String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }

"""Warehouse staff inheritance from user to store the customer information and relationships with other tables such as 
staff id and permission to search for the product location and update the order status """
class WarehouseStaff(User):
    staff_id = db.Column(db.Integer)
    __mapper_args__ = {
        'polymorphic_identity': 'Warehouse Staff'
    }

"""Seller inheritance from user to store the seller information and create relatioships to create their own market 
place with products listing and manage the inventory """
class Seller(User):
    seller_type = db.Column(db.Integer)
    __mapper_args__ = {
        'polymorphic_identity': 'Seller'
    }

"""Market Place Table to store the market place information of the seller and organise the products"""
class MarketPlace(db.Model):
    __tablename__ = 'marketPlace'

    marketPlace_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))


"""Products Table to all of the products information"""
class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.String(500), nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)
    product_warehouse_location = db.Column(db.String(500), nullable=False)
    product_status = db.Column(db.Boolean, default=True, nullable=False)
    __mapper_args__ = dict(polymorphic_identity='Product')

"""Order Table to store all of the orders and status relationships"""
class Order(db.Model):
    __tablename__ = 'order'

    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order_status = db.Column(db.Integer)
    quantity = db.Column(db.Integer, nullable=False)
    prodcts_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))

    # Relationship
    customer = db.relationship('User', foreign_keys=customer_id)
    order_items = db.relationship("Product", foreign_keys=prodcts_id)
    __mapper_args__ = dict(polymorphic_identity='Order')

"""Order History Table to store all of the orders updates and to log the order status"""
class OrderHistory(db.Model):
    __tablename__ = 'orderHistory'
    orderHistories_id = db.Column(db.Integer, primary_key=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_status = db.Column(db.Integer, nullable=False)
    order = db.Column(db.Integer, db.ForeignKey('order.order_id'))

    # Relationship
    order_id = db.relationship("Order", foreign_keys=order)
    __mapper_args__ = dict(polymorphic_identity='OrderHistory')

"""Payments Table to store all of the initiated payments and track status, linked with the orders"""
class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    status = db.Column(db.String(20), nullable=False)
    total = db.Column(db.Numeric(12, 2))

    # Relationships
    order_id = db.relationship("Order", foreign_keys=order)
    __mapper_args__ = dict(polymorphic_identity='Payments')


"""Allowing customers to store their payment methods by using an authentication token that will be retrieved from third-party payment gateway providers"""
class Paymentdetails(db.Model):
    __tablename__ = 'paymentDetails'
    method_id = db.Column(db.Integer, primary_key=True)
    payment_type = db.Column(db.String(20), nullable=False)
    auth_token = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    customer = db.relationship('User', foreign_keys=customer_id)

"""User Schema used for the serialization/deserialization of the users data"""
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')

"""Product Schema used for the serialization/deserialization of the product data"""
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('product_id', 'product_name', 'product_description', 'product_price', 'product_quantity',
                  'product_warehouse_location', 'product_status')

"""Initialise User Schema"""
user_schema = UserSchema()
users_schema = UserSchema(many=True)

"""Initialise Product Schema"""
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


if __name__ == '__main__':
    app.run()
