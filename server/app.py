#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

@app.route("/")
def home():
    return "<h1>Welcome to the Restaurant-Pizza Management System</h1>"

@app.route("/restaurants", methods=["GET", "POST"])
def handle_restaurants():
    if request.method == "GET":
        all_restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict(exclude=["restaurant_pizzas"]) for restaurant in all_restaurants]), 200

    if request.method == "POST":
        data = request.get_json()
        new_restaurant = Restaurant(
            name=data.get("name"),
            address=data.get("address")
        )
        db.session.add(new_restaurant)
        db.session.commit()
        return jsonify(new_restaurant.to_dict()), 201

@app.route("/restaurants/<int:restaurant_id>", methods=["GET", "PATCH", "DELETE"])
def handle_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    if request.method == "GET":
        return jsonify(restaurant.to_dict()), 200

    if request.method == "PATCH":
        data = request.get_json()
        for key, value in data.items():
            setattr(restaurant, key, value)
        db.session.commit()
        return jsonify(restaurant.to_dict()), 200

    if request.method == "DELETE":
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

@app.route("/pizzas", methods=["GET", "POST"])
def handle_pizzas():
    if request.method == "GET":
        all_pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict(exclude=["restaurant_pizzas"]) for pizza in all_pizzas]), 200

    if request.method == "POST":
        data = request.get_json()
        new_pizza = Pizza(
            name=data.get("name"),
            ingredients=data.get("ingredients")
        )
        db.session.add(new_pizza)
        db.session.commit()
        return jsonify(new_pizza.to_dict()), 201

@app.route("/pizzas/<int:pizza_id>", methods=["GET", "PATCH", "DELETE"])
def handle_pizza(pizza_id):
    pizza = Pizza.query.get(pizza_id)
    if not pizza:
        return jsonify({"error": f"Pizza {pizza_id} not found"}), 404

    if request.method == "GET":
        return jsonify(pizza.to_dict()), 200

    if request.method == "PATCH":
        data = request.get_json()
        for key, value in data.items():
            setattr(pizza, key, value)
        db.session.commit()
        return jsonify(pizza.to_dict()), 200

    if request.method == "DELETE":
        db.session.delete(pizza)
        db.session.commit()
        return '', 204

@app.route("/restaurant_pizzas", methods=["GET", "POST"])
def handle_restaurant_pizzas():
    if request.method == "GET":
        all_restaurant_pizzas = RestaurantPizza.query.all()
        return jsonify([rp.to_dict() for rp in all_restaurant_pizzas]), 200

    if request.method == "POST":
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data.get("price"),
                restaurant_id=data.get("restaurant_id"),
                pizza_id=data.get("pizza_id")
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return jsonify(new_restaurant_pizza.to_dict()), 201
        except ValueError as error:
            return jsonify({"errors": [f"Validation error: {error}"]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
