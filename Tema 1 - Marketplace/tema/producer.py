"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import string
from threading import Thread
from time import sleep


class Producer(Thread):
    """
    Class that represents a producer.
    """

    my_loop = bool
    sleep_time = int
    id_producer = string

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

        super(Producer, self).__init__(**kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.my_loop = True
        self.sleep_time = 0
        self.kwargs = kwargs
        with self.marketplace.locker_nr_producers:  # se adauga un nou producator
            self.id_producer = self.marketplace.register_producer()

    def run(self):
        while self.my_loop:  # produce la infinit, pana se respecta ultima conditie si se opreste
            for curr_product in self.products:  # se parcurge lista cu produse
                # (id, qty, sleep_time) = curr_product -> pt a intelege fiecare parametru
                for _ in range(0, curr_product[1]):  # se adauga cantitatea ceruta
                    if self.marketplace.publish(self.id_producer, curr_product[0]) is True:
                        # adauga in marketplace un produs + sleep dupa adaugare
                        self.sleep_time = curr_product[2]
                    else:
                        # sleep pt ca este plin, asteapta sa se consume
                        self.sleep_time = self.republish_wait_time
                    sleep(self.sleep_time)

            if self.marketplace.nr_producers == 0:
                # daca nu mai sunt producatori, se opreste productia
                self.my_loop = False

