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

        self.producer_lists = {}
        self.producer_lists_lock = Lock()
        self.producer_ids = 0

        self.carts_in_use = {}
        self.carts_lock = Lock()
        self.cart_ids = 0

        self.print_lock = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.producer_lists_lock:
            self.producer_ids += 1
            self.producer_lists[self.producer_ids] = {'lock': Lock(), 'products': []}
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
        with self.producer_lists[producer_id]['lock']:
            if len(self.producer_lists[producer_id]['products']) < self.queue_size_per_producer:
                self.producer_lists[producer_id]['products'].append([-1, product])
                return True
            return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        returns an int representing the cart_id
        """
        with self.carts_lock:
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
        for producer_dict in self.producer_lists.values():
            with producer_dict['lock']:
                for item in producer_dict['products']:
                    if item[0] == -1 and item[1] == product:
                        item[0] = cart_id
                        self.carts_in_use[cart_id].append(product)
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
        self.carts_in_use[cart_id].remove(product)
        with self.producer_lists_lock:
            for producer_dict in self.producer_lists.values():
                with producer_dict['lock']:
                    for item in producer_dict['products']:
                        if item[0] == cart_id and item[1] == product:
                            item[0] = -1
                            return

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        @type cart_id: Int
        @param cart_id: id cart
        """
        final_cart_items = self.carts_in_use[cart_id]
        self.carts_in_use[cart_id] = []
        for item in final_cart_items:
            with self.producer_lists_lock:
                for producer_dict in self.producer_lists.values():
                    with producer_dict['lock']:
                        if [cart_id, item] in producer_dict['products']:
                            producer_dict['products'].remove([cart_id, item])
                            break

        return final_cart_items
