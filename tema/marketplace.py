"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import unittest
import logging
from time import gmtime
from logging.handlers import RotatingFileHandler
from threading import Lock


class TestMarketplace(unittest.TestCase):
    """
    Class that is testing Marketplace's function correctness.
    Should be run separately, before any actual use of Marketplace
    """

    def setUp(self):
        # Initialize instance of class Marketplace for all tests
        self.marketplace = Marketplace(5)

    def test_register_producer(self):
        """
        Tests if some first calls of register_producer generate different expected id's
        """
        for i in range(1, 100):
            self.assertEqual(self.marketplace.register_producer(), i)

    def test_new_cart(self):
        """
        Tests if some first calls of new_cart generate different expected id's
        """
        for i in range(1, 100):
            self.assertEqual(self.marketplace.new_cart(), i)

    def test_publish(self):
        """
        Checks if dictionary is well filled with data and publish correctly returns for
        queue size of 5, 9 producers, items as ints 1 : 5
        """
        producers = []
        # Publish alternatively
        for i in range(1, 10):
            producers.append(self.marketplace.register_producer())
            self.assertTrue(self.marketplace.publish(producers[i - 1], 1))
            self.assertEqual(
                self.marketplace.producer_lists[producers[i - 1]]['products'], [[-1, 1]]
            )

        # Publish for each consumer rest of items to fill their queue
        for i in range(1, 10):
            expected_list = [[-1, 1]]
            for j in range(2, 6):
                self.assertTrue(self.marketplace.publish(producers[i - 1], j))
                expected_list.append([-1, j])
                self.assertEqual(
                    self.marketplace.producer_lists[producers[i - 1]]['products'], expected_list
                )

        # Try to publish one more item to check if it fails since queue is full
        expected_list = []
        for i in range(1, 6):
            expected_list.append([-1, i])
        for i in range(1, 10):
            self.assertFalse(self.marketplace.publish(producers[i - 1], 6))
            self.assertEqual(
                self.marketplace.producer_lists[producers[i - 1]]['products'], expected_list
            )

    def test_add_to_cart(self):
        """
        Tests 2 consumers adding items from 2 producers, both failed adds and successful ones
        """
        # Get some producers and fill up their queues with some items
        producers = [self.marketplace.register_producer(), self.marketplace.register_producer()]
        for i in range(1, 3):
            for j in range(1, 5):
                self.marketplace.publish(producers[i - 1], j)

        # Test some consumer add_to_cart operations that should succeed and some that should fail
        consumers = [self.marketplace.new_cart(), self.marketplace.new_cart()]
        self.assertTrue(self.marketplace.add_to_cart(consumers[0], 1))
        self.assertTrue(self.marketplace.add_to_cart(consumers[0], 2))

        self.assertTrue(self.marketplace.add_to_cart(consumers[1], 1))
        self.assertTrue(self.marketplace.add_to_cart(consumers[1], 3))

        self.assertTrue(self.marketplace.add_to_cart(consumers[0], 3))
        self.assertTrue(self.marketplace.add_to_cart(consumers[0], 4))

        self.assertTrue(self.marketplace.add_to_cart(consumers[1], 4))

        self.assertFalse(self.marketplace.add_to_cart(consumers[0], 1))
        self.assertFalse(self.marketplace.add_to_cart(consumers[0], 3))
        self.assertFalse(self.marketplace.add_to_cart(consumers[1], 4))

        # Check internal data structures used
        self.assertEqual(
            self.marketplace.producer_lists[producers[0]]['products'],
            [[1, 1], [1, 2], [2, 3], [1, 4]]
        )
        self.assertEqual(
            self.marketplace.producer_lists[producers[1]]['products'],
            [[2, 1], [-1, 2], [1, 3], [2, 4]]
        )

        self.assertEqual(
            self.marketplace.carts_in_use[consumers[0]],
            [1, 2, 3, 4]
        )
        self.assertEqual(
            self.marketplace.carts_in_use[consumers[1]],
            [1, 3, 4]
        )

    def test_remove_from_cart(self):
        """
        Tests 2 consumers removing some items from their carts
        The implementation of tested function doesn't check if there is actually an item to remove
        """
        # Get some producers and fill up their queues with some items
        producers = [self.marketplace.register_producer(), self.marketplace.register_producer()]
        for i in range(1, 3):
            for j in range(1, 5):
                self.marketplace.publish(producers[i - 1], j)

        # Add some items to consumers so we can remove some
        consumers = [self.marketplace.new_cart(), self.marketplace.new_cart()]
        self.marketplace.add_to_cart(consumers[0], 1)
        self.marketplace.add_to_cart(consumers[0], 2)
        self.marketplace.add_to_cart(consumers[0], 4)
        self.marketplace.add_to_cart(consumers[1], 1)
        self.marketplace.add_to_cart(consumers[1], 3)
        self.marketplace.add_to_cart(consumers[1], 4)
        self.marketplace.add_to_cart(consumers[0], 3)

        # Test removing items
        self.marketplace.remove_from_cart(consumers[0], 1)
        self.marketplace.remove_from_cart(consumers[0], 3)
        self.marketplace.remove_from_cart(consumers[1], 1)
        self.marketplace.remove_from_cart(consumers[1], 4)
        self.marketplace.remove_from_cart(consumers[1], 3)

        # Check internal data structures used
        self.assertEqual(
            self.marketplace.producer_lists[producers[0]]['products'],
            [[-1, 1], [1, 2], [-1, 3], [1, 4]]
        )
        self.assertEqual(
            self.marketplace.producer_lists[producers[1]]['products'],
            [[-1, 1], [-1, 2], [-1, 3], [-1, 4]]
        )

        self.assertEqual(
            self.marketplace.carts_in_use[consumers[0]],
            [2, 4]
        )
        self.assertEqual(
            self.marketplace.carts_in_use[consumers[1]],
            []
        )

    def test_place_order(self):
        """
        Tests 2 consumers removing some items from their carts
        The implementation of tested function doesn't check if there is actually an item to remove
        """
        # Get some producers and fill up their queues with some items
        producers = [self.marketplace.register_producer(), self.marketplace.register_producer()]
        for i in range(1, 3):
            for j in range(1, 5):
                self.marketplace.publish(producers[i - 1], j)

        # Add some items to consumers so we can remove some
        consumers = [self.marketplace.new_cart(), self.marketplace.new_cart()]
        self.marketplace.add_to_cart(consumers[0], 1)
        self.marketplace.add_to_cart(consumers[0], 2)
        self.marketplace.add_to_cart(consumers[1], 1)
        self.marketplace.add_to_cart(consumers[1], 3)
        self.marketplace.add_to_cart(consumers[0], 3)

        # Test placing orders
        self.assertEqual(
            self.marketplace.place_order(consumers[0]),
            [1, 2, 3]
        )
        self.assertEqual(
            self.marketplace.place_order(consumers[1]),
            [1, 3]
        )

        # Check internal data structures used
        self.assertEqual(
            self.marketplace.producer_lists[producers[0]]['products'],
            [[-1, 4]]
        )
        self.assertEqual(
            self.marketplace.producer_lists[producers[1]]['products'],
            [[-1, 2], [-1, 4]]
        )

        self.assertEqual(
            self.marketplace.carts_in_use[consumers[0]],
            []
        )
        self.assertEqual(
            self.marketplace.carts_in_use[consumers[1]],
            []
        )


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        @type queue_size_per_producer: Int
        @param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        # Max items in queue for each producer
        self.queue_size_per_producer = queue_size_per_producer

        # Dictionary of all producer's items, key=id, value=a dictionary with a 'lock':Lock()
        # and 'products':a list of products (each product is actually a list of 2 elements:
        # the id of the cart that reserved that product and the product type itself)
        self.producer_lists = {}
        # A lock used for the before-mentioned dictionary, needed so no insert while iterating
        # through it are possible (even though multiple insertions would have been possible since
        # they are atomic)
        self.producer_lists_lock = Lock()
        # The counter used to generate id's for the producers, since many may call this at a time,
        # the lock above is used to also guard this (when id is generated, a dictionary entry is
        # created)
        self.producer_ids = 0

        # Dictionary with consumer carts, simply mapping cart_id (int) to a list of products
        self.carts_in_use = {}
        # Lock used for giving away cart id_s (concurrency on incrementing and reading an int)
        self.carts_lock = Lock()
        # The counter used to generate id's for the consumers
        self.cart_ids = 0

        # Lock used for printing (in Consumer module)
        self.print_lock = Lock()

        # Logger object for use in every method
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler('marketplace.log', maxBytes=32768, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.Formatter.converter = gmtime
        self.logger.addHandler(handler)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.logger.info('register_producer is called')

        # Concurrent field writing protected by lock (also adding to iterable dictionary)
        with self.producer_lists_lock:
            self.producer_ids += 1
            self.producer_lists[self.producer_ids] = {'lock': Lock(), 'products': []}
            producer_id = self.producer_ids

        self.logger.info('register_producer returned %s', producer_id)
        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        @type producer_id: String
        @param producer_id: producer id

        @type product: Product
        @param product: the Product that will be published in the Marketplace

        returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.logger.info('publish is called by producer %s with product %s',
                         producer_id, product)
        success = False

        # Protect each consumer's own list with a lock when changing elements and iterating through
        with self.producer_lists[producer_id]['lock']:
            # Add given element only if there is enough space marking it as available(cart_id=-1),
            # return accordingly
            if len(self.producer_lists[producer_id]['products']) < self.queue_size_per_producer:
                self.producer_lists[producer_id]['products'].append([-1, product])
                success = True

        self.logger.info('publish was called by producer %s with product %s and returned %s',
                         producer_id, product, success)
        return success

    def new_cart(self):
        """
        Creates a new cart for the consumer

        returns an int representing the cart_id
        """
        self.logger.info('new_cart is called')

        # Concurrent field writing protected by lock
        with self.carts_lock:
            self.cart_ids += 1
            self.carts_in_use[self.cart_ids] = []
            cart_id = self.cart_ids

        self.logger.info('new_cart returned %s', cart_id)
        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        @type cart_id: Int
        @param cart_id: id cart

        @type product: Product
        @param product: the product to add to cart

        returns True or False. If the caller receives False, it should wait and then try again
        """
        self.logger.info('add_to_cart is called by consumer %s with product %s',
                         cart_id, product)
        success = False

        # Iteration through dictionary should be synchronized with respect to inserting keys
        with self.producer_lists_lock:
            for producer_dict in self.producer_lists.values():
                if success:
                    break
                # List changing of some elements should also be synchronized
                with producer_dict['lock']:
                    for item in producer_dict['products']:
                        # Mark item as reserved, add to own cart and stop searching
                        if item[0] == -1 and item[1] == product:
                            item[0] = cart_id
                            self.carts_in_use[cart_id].append(product)
                            success = True
                            break

        self.logger.info('add_to_cart was called by consumer %s with product %s and returned %s',
                         cart_id, product, success)
        return success

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        @type cart_id: Int
        @param cart_id: id cart

        @type product: Product
        @param product: the product to remove from cart
        """
        self.logger.info('remove_from_cart is called by consumer %s with product %s',
                         cart_id, product)

        # Remove item from consumer's cart
        self.carts_in_use[cart_id].remove(product)

        # Mark item from first occurrence in any producer
        # Iteration through dictionary should be synchronized with respect to inserting keys
        done = False
        with self.producer_lists_lock:
            for producer_dict in self.producer_lists.values():
                if done:
                    break
                # List changing of some elements should also be synchronized
                with producer_dict['lock']:
                    for item in producer_dict['products']:
                        # Mark item as available by resetting id
                        if item[0] == cart_id and item[1] == product:
                            item[0] = -1
                            done = True
                            break

        self.logger.info('remove_from_cart was called by consumer %s with product %s',
                         cart_id, product)

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        @type cart_id: Int
        @param cart_id: id cart
        """
        self.logger.info('place_order is called by consumer %s', cart_id)

        # Get list of items in cart and reset it
        final_cart_items = self.carts_in_use[cart_id]
        self.carts_in_use[cart_id] = []

        # For every item actually delete it from producer
        for item in final_cart_items:
            # Iteration through dictionary should be synchronized with respect to inserting keys
            with self.producer_lists_lock:
                for producer_dict in self.producer_lists.values():
                    # List changing of some elements should also be synchronized
                    with producer_dict['lock']:
                        # Remove item and continue for the next item (break) if found
                        if [cart_id, item] in producer_dict['products']:
                            producer_dict['products'].remove([cart_id, item])
                            break

        self.logger.info('place_order was called by consumer %s and returned %s',
                         cart_id, final_cart_items)
        return final_cart_items
