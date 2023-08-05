from threading import Thread

import ax26.classes as classes
import ax26.constants as const


class Server(classes.Ax26):
	def __init__(self, kiss_object, callsign):
		super(self.__class__, self).__init__(kiss_object, callsign)
		self._client_callsigns = []

	def _socket_handler(self, client_id, handler):  # Handles each connection
		handler = handler(client_id)
		connected = True
		while connected:
			success, src, dest, type_byte, body = self._get_last_frame([client_id], [self._mycall], [const.DATA_START, const.DISCONNECT])
			if success:  # Packet received, and it matches the source and dest
				if type_byte == const.DATA_START:  # Data inbound
					received_data = self._raw_receive_data([client_id], [self._mycall], body)
					if received_data is not None:
						handler.on_recv(received_data)
				elif type_byte == const.DISCONNECT:  # Disconnection request
					self._write(self._mycall, src, const.ACK)
					connected = False
					self._client_callsigns.remove(client_id)
					if hasattr(handler, 'on_disconnect'):
						handler.on_disconnect()

	def serve_forever(self, handler_class):
		while True:
			success, src = self._accept_connection_handler()
			if success:
				handled = False
				if not src in self._client_callsigns:
					# Spawn new thread
					worker = Thread(target=self._socket_handler, kwargs={'client_id': src, 'handler': handler_class})
					worker.daemon = True
					worker.start()
					self._client_callsigns.append(src)

	def send_data(self, to_c, data):
		return self._raw_send_data(data, self._mycall, to_c)