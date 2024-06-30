from models import Restaurant, RestaurantPizza, Pizza
from app import app, db
from faker import Faker


class TestApp:
    '''Flask application in app.py'''

    def test_restaurants(self):
        """retrieves restaurants with GET request to /restaurants"""
        with app.app_context():
            fake = Faker()
            restaurant1 = Restaurant(name=fake.name(), address=fake.address())
            restaurant2 = Restaurant(name=fake.name(), address=fake.address())
            db.session.add_all([restaurant1, restaurant2])
            db.session.commit()

            response = app.test_client().get('/restaurants')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json
            restaurants = Restaurant.query.all()

            assert [restaurant['id'] for restaurant in response] == [restaurant.id for restaurant in restaurants]
            assert [restaurant['name'] for restaurant in response] == [restaurant.name for restaurant in restaurants]
            assert [restaurant['address'] for restaurant in response] == [restaurant.address for restaurant in restaurants]
            for restaurant in response:
                assert 'restaurant_pizzas' not in restaurant

    def test_restaurants_id(self):
        '''retrieves one restaurant using its ID with GET request to /restaurants/<int:id>.'''

        with app.app_context():
            fake = Faker()
            restaurant = Restaurant(name=fake.name(), address=fake.address())
            db.session.add(restaurant)
            db.session.commit()

            response = app.test_client().get(f'/restaurants/{restaurant.id}')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json
            assert response['id'] == restaurant.id
            assert response['name'] == restaurant.name
            assert response['address'] == restaurant.address
            assert 'restaurant_pizzas' in response

    def test_returns_404_if_no_restaurant_to_get(self):
        '''returns an error message and 404 status code with GET request to /restaurants/<int:id> by a non-existent ID.'''

        with app.app_context():
            response = app.test_client().get('/restaurants/0')
            assert response.status_code == 404
            assert response.content_type == 'application/json'
            assert response.json.get('error') == "Restaurant not found"

    def test_deletes_restaurant_by_id(self):
        '''deletes restaurant with DELETE request to /restaurants/<int:id>.'''

        with app.app_context():
            fake = Faker()
            restaurant = Restaurant(name=fake.name(), address=fake.address())
            db.session.add(restaurant)
            db.session.commit()

            response = app.test_client().delete(f'/restaurants/{restaurant.id}')
            assert response.status_code == 204

            result = Restaurant.query.filter(Restaurant.id == restaurant.id).one_or_none()
            assert result is None

    def test_returns_404_if_no_restaurant_to_delete(self):
        '''returns an error message and 404 status code with DELETE request to /restaurants/<int:id> by a non-existent ID.'''

        with app.app_context():
            response = app.test_client().delete('/restaurants/0')
            assert response.status_code == 404
            assert response.json.get('error') == "Restaurant not found"

    def test_pizzas(self):
        """retrieves pizzas with GET request to /pizzas"""
        with app.app_context():
            fake = Faker()
            pizza1 = Pizza(name=fake.name(), ingredients=fake.sentence())
            pizza2 = Pizza(name=fake.name(), ingredients=fake.sentence())
            db.session.add_all([pizza1, pizza2])
            db.session.commit()

            response = app.test_client().get('/pizzas')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json

            pizzas = Pizza.query.all()

            assert [pizza['id'] for pizza in response] == [pizza.id for pizza in pizzas]
            assert [pizza['name'] for pizza in response] == [pizza.name for pizza in pizzas]
            assert [pizza['ingredients'] for pizza in response] == [pizza.ingredients for pizza in pizzas]
            for pizza in response:
                assert 'restaurant_pizzas' not in pizza

    def test_creates_restaurant_pizzas(self):
        '''creates one restaurant_pizzas using a pizza_id, restaurant_id, and price with a POST request to /restaurant_pizzas.'''

        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients=fake.sentence())
            restaurant = Restaurant(name=fake.name(), address=fake.address())
            db.session.add(pizza)
            db.session.add(restaurant)
            db.session.commit()

            # delete if existing in case price differs
            restaurant_pizza = RestaurantPizza.query.filter_by(
                pizza_id=pizza.id, restaurant_id=restaurant.id).one_or_none()
            if restaurant_pizza:
                db.session.delete(restaurant_pizza)
                db.session.commit()

            response = app.test_client().post('/restaurant_pizzas', json={
                "price": 3,
                "pizza_id": pizza.id,
                "restaurant_id": restaurant.id,
            })

            assert response.status_code == 201
            assert response.content_type == 'application/json'
            response = response.json
            assert response['price'] == 3
            assert response['pizza_id'] == pizza.id
            assert response['restaurant_id'] == restaurant.id
            assert response['id']
            assert response['pizza']
            assert response['restaurant']

            query_result = RestaurantPizza.query.filter(
                RestaurantPizza.restaurant_id == restaurant.id, RestaurantPizza.pizza_id == pizza.id).first()
            assert query_result.price == 3

    def test_400_for_validation_error(self):
        '''returns a 400 status code and error message if a POST request to /restaurant_pizzas fails.'''

        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients=fake.sentence())
            restaurant = Restaurant(name=fake.name(), address=fake.address())
            db.session.add(pizza)
            db.session.add(restaurant)
            db.session.commit()

            # Test with price not in 1..30
            response = app.test_client().post('/restaurant_pizzas', json={
                "price": 0,
                "pizza_id": pizza.id,
                "restaurant_id": restaurant.id,
            })
            assert response.status_code == 400
            assert response.json['errors'] == ["validation errors: Price must be between 1 and 30"]

            response = app.test_client().post('/restaurant_pizzas', json={
                "price": 31,
                "pizza_id": pizza.id,
                "restaurant_id": restaurant.id,
            })
            assert response.status_code == 400
            assert response.json['errors'] == ["validation errors: Price must be between 1 and 30"]

    def test_get_restaurant_pizzas(self):
        '''retrieves all restaurant_pizzas with GET request to /restaurant_pizzas.'''

        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients=fake.sentence())
            restaurant = Restaurant(name=fake.name(), address=fake.address())
            restaurant_pizza = RestaurantPizza(price=15, pizza=pizza, restaurant=restaurant)
            db.session.add(pizza)
            db.session.add(restaurant)
            db.session.add(restaurant_pizza)
            db.session.commit()

            response = app.test_client().get('/restaurant_pizzas')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json
            assert len(response) > 0
            
            # Check the first item in the response
            assert response[0]['price'] == 15
            assert response[0]['pizza_id'] == pizza.id
            assert response[0]['restaurant_id'] == restaurant.id
            assert 'pizza' in response[0]
            assert 'restaurant' in response[0]

            # Make sure that the pizza and restaurant info is included in the response
            assert response[0]['pizza']['id'] == pizza.id
            assert response[0]['pizza']['name'] == pizza.name
            assert response[0]['pizza']['ingredients'] == pizza.ingredients
            assert response[0]['restaurant']['id'] == restaurant.id
            assert response[0]['restaurant']['name'] == restaurant.name
            assert response[0]['restaurant']['address'] == restaurant.address

    def test_get_pizza_by_id(self):
        '''retrieves one pizza with GET request to /pizzas/<int:id>.'''

        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients=fake.sentence())
            db.session.add(pizza)
            db.session.commit()

            response = app.test_client().get(f'/pizzas/{pizza.id}')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json
            assert response['id'] == pizza.id
            assert response['name'] == pizza.name
            assert response['ingredients'] == pizza.ingredients

    def test_patch_pizza(self):
        '''updates a pizza with PATCH request to /pizzas/<int:id>.'''

        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients=fake.sentence())
            db.session.add(pizza)
            db.session.commit()

            response = app.test_client().patch(f'/pizzas/{pizza.id}', json={
                "name": "Updated Pizza",
                "ingredients": "Updated Ingredients",
            })

            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response = response.json
            assert response['id'] == pizza.id
            assert response['name'] == "Updated Pizza"
            assert response['ingredients'] == "Updated Ingredients"

    def test_delete_pizza(self):
        '''deletes a pizza with DELETE request to /pizzas/<int:id>.'''

        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients=fake.sentence())
            db.session.add(pizza)
            db.session.commit()

            response = app.test_client().delete(f'/pizzas/{pizza.id}')
            assert response.status_code == 204
            assert Pizza.query.get(pizza.id) is None
