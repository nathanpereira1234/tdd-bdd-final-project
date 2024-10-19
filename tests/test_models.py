# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError  # Imported to test exceptions
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://postgres:postgres@localhost:5432/postgres"
    )


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_a_product(self):
        """It should Read a Product from the database"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        # Fetch newly created product
        new_product = Product.find(product.id)
        # Assert that red product matches the one that was just created
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a Product"""
        # Create a Product using ProductFactory
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        new_id = product.id
        self.assertIsNotNone(new_id)
        # Update description
        new_description = "This is an updated description XYAJSD76872"
        product.description = new_description
        # Update product in database
        product.update()
        # Assert that the id is the same as the original
        self.assertEqual(product.id, new_id)
        # Assert that description has been successfully updated
        self.assertEqual(product.description, new_description)

        # Fetch all products in the database
        all_products = Product.all()
        # Assert there's only 1 product
        self.assertEqual(len(all_products), 1)

        # Fetch updated product
        fetched_product = all_products[0]
        # Assert that the id is the same as the original
        self.assertEqual(fetched_product.id, new_id)
        # Assert that description has been successfully updated
        self.assertEqual(fetched_product.description, new_description)

        # Assert invalid id exception
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        # Call the create() method on the product to save it to the database.
        # Assert  if the length of the list returned by Product.all() is equal to 1,
        # to verify that after creating a product and saving it to the database, there is only one product in the system.
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Call the delete() method on the product object, to remove the product from the database.
        product.delete()
        # Assert if the length of the list returned by Product.all() is now equal to 0,
        # indicating that the product has been successfully deleted from the database.
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        # Assert if the products list is empty
        self.assertEqual(len(products), 0)
        # Use for loop to create five Product objects using a ProductFactory()
        # and call the create() method on each product to save them to the database.
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # Fetch all products from the database again using product.all()
        all_products = Product.all()
        # Assert if the length of the products list is equal to 5, to verify that the
        # five products created in the previous step have been successfully added to the database.
        self.assertEqual(len(all_products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        # Use a for loop to iterate over the products list and call the create() method
        for product in products:
            product.create()
        # Retrieve the name of the first product in the products list.
        test_name = products[0].name
        # Use a list comprehension to filter the products based on their name and then use len()
        # to calculate the length of the filtered list, and use the variable called count
        count = len([product for product in products if product.name == test_name])
        # Call the find_by_name() method on the Product class to retrieve products from the database
        name_match_products = Product.find_by_name(test_name)
        # Assert if the count of the found products matches the expected count.
        self.assertEqual(name_match_products.count(), count)
        # Use a for loop to iterate over the found products and assert that each product's name matches
        # the expected name, to ensure that all the retrieved products have the correct name.
        for product in name_match_products:
            self.assertEqual(product.name, test_name)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        # Use a for loop to iterate over the products list and call the create() method
        for product in products:
            product.create()
        # Retrieve the availability of the first product in the products list.
        availability = products[0].available
        # Use a list comprehension to filter the products based on their availability and then use len()
        # to calculate the length of the filtered list, and use the variable called count
        count = len([product for product in products if product.available == availability])
        # Call the find_by_availability() method on the Product class to retrieve products from
        # the database that have the specified availability.
        products_by_availability = Product.find_by_availability(availability)
        # Assert if the count of the found products matches the expected count.
        self.assertEqual(products_by_availability.count(), count)
        # Use a for loop to iterate over the found products and assert that each product's availability
        # matches the expected availability, to ensure that all the retrieved products have the correct availability.
        for product in products_by_availability:
            self.assertEqual(product.available, availability)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        # Use a for loop to iterate over the products list and call
        # the create() method on each product to save them to the database.
        for product in products:
            product.create()
        # Retrieve the category of the first product in the products list.
        category = products[0].category
        # Use a list comprehension to filter the products based on their category
        count = len([product for product in products if product.category == category])
        # Call the find_by_category() method on the Product class to retrieve products
        # from the database that have the specified category.
        products_by_category = Product.find_by_category(category)
        # Assert if the count of the found products matches the expected count.
        self.assertEqual(products_by_category.count(), count)
        # Use a for loop to iterate over the found products and assert that each product's
        # category matches the expected category
        for product in products_by_category:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """It should Find Products by Price"""
        products = ProductFactory.create_batch(10)
        # Use a for loop to iterate over the products list and call
        # the create() method on each product to save them to the database.
        for product in products:
            product.create()
        # Retrieve the price of the first product in the products list.
        price = products[0].price
        # Use a list comprehension to filter the products having equal price
        count = len([product for product in products if product.price == price])
        # Call the find_by_price() method on the Product class to retrieve products
        # from the database that have the specified price.
        products_by_price = Product.find_by_price(str(price))
        # Assert if the count of the found products matches the expected count.
        self.assertEqual(products_by_price.count(), count)
        # Use a for loop to iterate over the found products and assert that each product's
        # price matches the expected price
        for product in products_by_price:
            self.assertEqual(product.price, price)

    def test_a_product_deserialization(self):
        """Should deserialize a Product from a dictionary"""
        # Create a ProductFactory
        test_product = ProductFactory()
        test_dict = test_product.serialize()

        # Assert that deserialization works
        product = Product()
        product.deserialize(test_dict)
        self.assertEqual(product.name, test_product.name)

        # Assert invalid availability exception
        product_dict = test_dict
        product_dict["available"] = "Not a boolean"
        self.assertRaises(DataValidationError, product.deserialize, product_dict)

        # Assert attribute error exception
        product_dict = test_dict
        product_dict["category"] = None
        self.assertRaises(DataValidationError, product.deserialize, product_dict)

        # Assert missing deserialization dict key
        self.assertRaises(DataValidationError, product.deserialize, {"missing_key": 0})

        # Assert invalid deserialization input type
        self.assertRaises(DataValidationError, product.deserialize, "Not a valid dictionary")

