from flask import request
from flask_socketio import join_room, leave_room, emit

from main.services.binance_service import BinanceService


class WebSocketHandler:
    """ doc string for WebSocketHandler """

    def __init__(self, socket_io):
        super(WebSocketHandler, self).__init__()
        self.socket_io = socket_io
        self.binance_service = BinanceService()
        self.registerHandlers()

    def registerHandlers(self):
        connected_clients = []

        @self.socket_io.on('connect')
        def handle_connect(methods=['GET', 'POST']):
            print('Client Connected : ' + request.sid)
            join_room(request.sid)
            emit('hello', 'Hello from server', room=request.sid)
            connected_clients.append(request.sid)
            # room = session.get('room')
            # join_room(room)
            # print("room = " + str(room))
            print(connected_clients)

        @self.socket_io.on('disconnect')
        def handle_disconnect(methods=['GET', 'POST']):
            print('Client Disconnected : ' + request.sid)
            leave_room(request.sid)
            connected_clients.remove(request.sid)
            print(connected_clients)

        @self.socket_io.on('hi')
        def handle_message(methods=['GET', 'POST']):
            print('hi : ' + request.sid)

        @self.socket_io.on('message')
        def handle_message(message, methods=['GET', 'POST']):
            print('received : ' + str(message) + ' from ' + request.sid)

        @self.socket_io.on('symbol_ticker')
        def handle_message(symbol, methods=['GET', 'POST']):
            print('Requested ticker for : ' + str(symbol) + ' from ' + request.sid)
            price = self.binance_service.getSymbolTicker(symbol)
            response = {
                "symbol": symbol,
                "price": price
            }
            emit('symbol_ticker_response', response, room=request.sid)
