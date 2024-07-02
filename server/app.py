#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify, json
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurants_list = [
        {"id": restaurant.id, "name": restaurant.name, "address": restaurant.address}
        for restaurant in restaurants
    ]
    return make_response({"restaurants": restaurants_list}, 200)


@app.route('/restaurants/<int:id>', methods=['GET'])
def restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        response_body = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [rp.pizza_id for rp in restaurant.restaurant_pizzas]  
        }
     
        response_status = 200
    else:
        response_body = {"error": f"Restaurant {id} not found"}
        response_status = 404

    return make_response(jsonify(response_body), response_status)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    # restaurant = Restaurant.query.get(id)
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": f"Restaurant not found"}), 404
    
  
@app.route('/pizzas', methods = ['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_list = [
        {'id': pizza.id,
         'name': pizza.name,
         'ingredients':pizza.ingredients

         }
         for pizza in pizzas
    ]
    return jsonify(pizzas_list), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizzas():
    data = request.get_json()
    try:
        price = data.get('price')
        if price is None or price < 1 or price > 30:
            raise ValueError('validation errors')
        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id'],
        )

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        response = make_response(json.dumps(new_restaurant_pizza.to_dict()), 201)
    except ValueError as e:
        response = make_response(json.dumps({'errors': [str(e)]}), 400)
    except Exception as e:
        response = make_response(json.dumps({'errors': ['An unexpected error occurred']}), 500)

    response.headers['Content-type'] = 'application/json'
    return response

if __name__ == "__main__":
    app.run(port=5555, debug=True)
