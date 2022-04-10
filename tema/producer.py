"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Thread
from time import sleep


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time

    def run(self):
        # Register yourself in the market
        producer_id = self.marketplace.register_producer()

        # Keep publishing products according to pattern:
        # count times each product, redo whole list after it's done, indefinitely
        while True:
            for product in self.products:
                for _ in range(product[1]):
                    # Keep try publishing, wait republish time if you fail
                    while not self.marketplace.publish(producer_id, product[0]):
                        sleep(self.republish_wait_time)
                    # After publishing wait defined time (might also simulate production time)
                    sleep(product[2])
