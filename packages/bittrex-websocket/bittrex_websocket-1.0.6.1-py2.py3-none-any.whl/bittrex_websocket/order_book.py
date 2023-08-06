#!/usr/bin/python
# -*- coding: utf-8 -*-

# bittrex_websocket/order_book.py
# Stanislav Lazarov

from bittrex_websocket import BittrexSocket, BittrexMethods
from .constants import EventTypes
from time import sleep


class OrderBook(BittrexSocket):
    def __init__(self, url=None, retry_timeout=None, max_retries=None):
        super(OrderBook, self).__init__(url, retry_timeout, max_retries)
        self.order_books = {}

    def control_queue_handler(self):
        while True:
            event = self.control_queue.get()
            if event is not None:
                if event.type == EventTypes.CONNECT:
                    self._handle_connect()
                elif event.type == EventTypes.SUBSCRIBE:
                    self._handle_subscribe(event)
                elif event.type == EventTypes.RECONNECT:
                    self._handle_reconnect(event.error_message)
                elif event.type == EventTypes.CLOSE:
                    self.connection.conn.close()
                    break
                self.control_queue.task_done()

    def on_public(self, msg):
        # Create entry for the ticker in the trade_history dict
        if msg['invoke_type'] == BittrexMethods.SUBSCRIBE_TO_EXCHANGE_DELTAS:
            ticker = msg['M']
            if ticker not in self.order_books:
                self.query_exchange_state([ticker])
                self.order_books[ticker] = {'l': 1}
            else:
                print('lol')
