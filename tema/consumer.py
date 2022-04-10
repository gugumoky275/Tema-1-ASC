"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Thread, Lock
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        @type carts: List
        @param carts: a list of add and remove operations

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type retry_wait_time: Time
        @param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.printing_lock = Lock()

    def run(self):
        # Get your customer id (cart_id, even though you have more sets of operations)
        cart_id = self.marketplace.new_cart()

        # Get each set of operations before placing an order (here called cart) and
        # for each of respective action's count do that action without waiting additionally.
        # When adding to cart check if market has respective product, if not retry after
        # retry_wait_time
        for cart in self.carts:
            for action in cart:
                for _ in range(action['quantity']):
                    if action['type'] == 'add':
                        while not self.marketplace.add_to_cart(cart_id, action['product']):
                            sleep(self.retry_wait_time)
                    elif action['type'] == 'remove':
                        self.marketplace.remove_from_cart(cart_id, action['product'])
            cart_product_list = self.marketplace.place_order(cart_id)
            # Print items, use a lock (two should not speak at the same time)
            with self.marketplace.print_lock:
                for product in cart_product_list:
                    print(self.name, 'bought', product)
