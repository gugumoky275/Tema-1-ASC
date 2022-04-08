"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock


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
        self.queue_size_per_producer = queue_size_per_producer
        self.producer_ids = 0
        self.cart_ids = 0
        self.producer_ids_lock = Lock()
        self.cart_ids_lock = Lock()

        # A dictionary where key is producer id (int), value is a list of tuples:
        # (locked?, cart_id_that_locked, product)
        self.marketplace_items = {}

        # A dictionary where key is cart id (int), value is the list of products
        self.carts_in_use = {}

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        # Return next available id from self field, multiple producers can call this,
        # so it needs to be synchronized
        with self.producer_ids_lock:
            self.producer_ids += 1
            return self.producer_ids

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        @type producer_id: String
        @param producer_id: producer id

        @type product: Product
        @param product: the Product that will be published in the Marketplace

        returns True or False. If the caller receives False, it should wait and then try again.
        """
        # Add product to corresponding producer list
        # Each producer has a unique id so each have their own lists, no race condition
        # Also list appends and pops are atomic, so no need to use locks here
        if len(self.marketplace_items[producer_id][2]) < self.queue_size_per_producer:
            self.marketplace_items[producer_id][2].append(product)
            return True
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        returns an int representing the cart_id
        """
        # Return next available id from self field, multiple consumers can call this,
        # so it needs to be synchronized
        with self.cart_ids_lock:
            self.cart_ids += 1
            self.carts_in_use[self.cart_ids] = []
            return self.cart_ids

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        @type cart_id: Int
        @param cart_id: id cart

        @type product: Product
        @param product: the product to add to cart

        returns True or False. If the caller receives False, it should wait and then try again
        """
        for curr_producer_list in self.marketplace_items.values():
            for offered_product in curr_producer_list:
                if offered_product == product:
                    return True
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        @type cart_id: Int
        @param cart_id: id cart

        @type product: Product
        @param product: the product to remove from cart
        """
        pass

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        @type cart_id: Int
        @param cart_id: id cart
        """
        pass
