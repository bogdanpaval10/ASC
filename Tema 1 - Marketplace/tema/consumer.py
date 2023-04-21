"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    my_loop = bool
    sleep_time = int

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """

        super(Consumer, self).__init__(**kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.my_loop = True
        self.sleep_time = 0
        self.kwargs = kwargs

    def new_cart(self):
        """
        It creates a new cart.
        """

        with self.marketplace.locker_all_carts:
            cart_id = self.marketplace.new_cart()  # se creeaza un nou consumator

        return cart_id

    def run(self):
        for curr_cart in self.carts:  # se parcurge lista de operatii pt consumator
            cart_id = self.new_cart()
            for parse in curr_cart:
                for _ in range(0, parse.get("quantity")):
                    self.my_loop = True
                    while self.my_loop:  # se incearca adaugarea produselor cerute
                        if parse.get("type") == "add":
                            if self.marketplace.add_to_cart(cart_id, parse.get("product")) is False:
                                # nu s-a putut adauga produsul in cos, asteapta
                                self.sleep_time = self.retry_wait_time
                            else:
                                self.my_loop = False    # a fost adaugat cu succes
                                break
                        elif parse.get("type") == "remove": # se sterge produsul din cos
                            self.marketplace.remove_from_cart(cart_id, parse.get("product"))
                            self.my_loop = False
                            break
                        else:
                            self.my_loop = False    # nu este o comanda valida
                            break
                        sleep(self.sleep_time)

            with self.marketplace.sem_order:    # se publica comanda
                self.marketplace.place_order(cart_id)

