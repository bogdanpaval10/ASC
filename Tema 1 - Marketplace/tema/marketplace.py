"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock, Semaphore, currentThread
import logging
from logging.handlers import RotatingFileHandler
import time


logging.basicConfig(filename="marketplace.log", level=logging.INFO)
logging.Formatter.converter = time.gmtime


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        self.queue_size_per_producer = queue_size_per_producer
        self.producers_lists = {}  # fiecare producator are lista lui de produse
        self.all_products = []  # elemente de tipul tuplu (produs, id_producator)
                                                # -> toate produsele din magazin
        self.all_carts = []  # fiecare carucior are lista cu produsele din el
        self.nr_producers = 0  # nr total de producatori
        self.nr_products = 0  # nr total de produse din magazin
        self.nr_carts = 0  # nr total de cosuri (consumatori)

        self.locker_nr_producers = Lock()  # folosit cand se adauga un producator nou
        self.locker_all_carts = Lock()  # folosit cand se adauga un cart nouz
        self.sem_order = Semaphore(1)  # folosit la plasarea comenzii
        self.locker_insert_del = Lock()  # folosit la add/remove

        self.loggy = logging.getLogger()
        handler = RotatingFileHandler("marketplace.log", maxBytes=100000, backupCount=20)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        self.loggy.addHandler(handler)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        producer_id = self.nr_producers
        try:
            self.loggy.info("At the beginning of register_producer.")
            self.nr_producers = self.nr_producers + 1  # se adauga noul producator
            self.producers_lists[producer_id] = []  # lista cu produsele producatorului cu prod_id
        except ValueError:
            self.loggy.info("ERROR: There have been an error, register_producer function!")
        finally:
            self.loggy.info("Successfully registered the producer %s.", str(producer_id))

        return str(producer_id)

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        if int(producer_id) > self.nr_producers:  # daca producatorul nu exista (id mai mare)
            self.loggy.info("ERROR: The producer %s doesn't exist to add %s.", producer_id,
                                                                                 str(product))
            return False

        self.loggy.info("At the beginning of publish %s %s.", producer_id, str(product))
        # se verifica daca mai este loc pt acest produs
        if len(self.producers_lists[int(producer_id)]) < self.queue_size_per_producer:
            # se adauga produsul in lista producatorului
            self.producers_lists[int(producer_id)].append(product)
            # se adauga produsul in lista magazinului
            self.all_products.append((product, int(producer_id)))
            self.nr_products = self.nr_products + 1
            self.loggy.info("Successfully published the product %s, from %s.", str(product),
                                                                                 producer_id)
            return True

        self.loggy.info("Full!")  # lista este plina, nu se poate adauga
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """

        cart_id = self.nr_carts
        try:
            self.loggy.info("At the beginning of new_cart.")
            self.nr_carts = self.nr_carts + 1  # se adauga noul cart (consumator)
            self.all_carts.append([])  # lista pt a stoca produsele din cosul cart_id
        except ValueError:
            self.loggy.info("ERROR: There have been an error creating the new cart!")
        finally:
            self.loggy.info("Successfully added the cart %s.", str(cart_id))

        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        if int(cart_id) > self.nr_carts:  # daca cosul nu exista (are id > nr total de cosuri)
            self.loggy.info("ERROR: The cart %s doesn't exist to add %s.", str(cart_id),
                                                                             str(product))
            return False

        self.loggy.info("At the beginning of add_to_cart %s %s.", str(cart_id), str(product))
        with self.locker_insert_del:
            my_bool = False
            for curr_product in self.all_products:  # se parcurg toate produsele din magazin
                if curr_product[0] is product:  # am gasit produsul cautat
                    my_bool = True
                    # sterge produsul din magazin si il adauga in cosul consumatorului cart_id
                    self.all_products.remove(curr_product)
                    self.all_carts[cart_id].append(curr_product)
                    self.nr_products = self.nr_products - 1
                    break

            if my_bool is True:  # produsul exista in magazin
                for curr_producer in range(self.nr_producers):
                    if product in self.producers_lists[curr_producer]:
                        # s-a gasit cui ii apartine produsul cerut si sterge produsul din
                        self.producers_lists[curr_producer].remove(product)  # lista producatorului
                        break
                self.loggy.info("Successfully added the product %s in %s.", str(product),
                                                                              str(cart_id))
            else:
                self.loggy.info("ERROR: The product %s doesn't exist in %s.", str(product),
                                                                                str(cart_id))

        return my_bool

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """

        if int(cart_id) > self.nr_carts:  # daca cosul nu exista (are id > nr total de cosuri)
            self.loggy.info("ERROR: The cart %s doesn't exist to be removed %s.", str(cart_id),
                                                                                    str(product))
            return None

        self.loggy.info("At the beginning of remove_from_cart %s %s.", str(cart_id),
                                                                         str(product))
        my_bool = False
        # parcurge lista cu produsele consumatorului cart_id
        for curr_prods in self.all_carts[cart_id]:
            curr_product = curr_prods[0]  # tipul produsului
            curr_producer = curr_prods[1]  # id-ul producatorului
            if curr_product is product:  # s-a gasit produsul cautat in cosul consumatorului
                with self.locker_insert_del:
                    self.all_carts[cart_id].remove(curr_prods)  # sterge produsul din cos
                    self.all_products.append(curr_prods)  # adauga produs inapoi in magazin
                    # adauga produsul in lista cui l-a produs
                    self.producers_lists[curr_producer].append(product)
                    self.nr_products = self.nr_products + 1
                my_bool = True
                break

        self.loggy.info("Successfully removed the product %s from %s.", str(product),
                                                                          str(cart_id))
        if my_bool is True:  # nu a fost gasit produsul in cos
            self.loggy.info("ERROR: The product %s doesn't exist in %s.", str(product),
                                                                            str(cart_id))

        return None

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        if int(cart_id) > self.nr_carts:  # daca cosul nu exista (are id > nr total de cosuri)
            self.loggy.info("ERROR: The cart %s doesn't exist to be ordered.", str(cart_id))
            return None

        self.loggy.info("At the beginning of place_order %s.", str(cart_id))
        list_order = []  # se formeaza o lista cu produsele din cos
        try:
            # se parcurge lista cu produsele consumatorului cart_id
            for curr_cart in self.all_carts[cart_id]:
                # adauga doar produsul (nu si id producator - este tuplu)
                list_order.append(curr_cart[0])
                print(f"{currentThread().getName()} bought {str(curr_cart[0])}")
            for curr_cart in self.all_carts[cart_id]:  # se sterg produsele din cos
                self.remove_from_cart(cart_id, curr_cart[0])
        except ValueError:
            self.loggy.info("ERROR: There have been an error placing the order!")
        finally:
            self.loggy.info("Successfully placed the order %s.", str(cart_id))

        return list_order
