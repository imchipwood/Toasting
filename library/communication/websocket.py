import socketserver


class TCPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		# self.request is the TCP socket connected to the client
		data = self.request.recv().strip()
		print("{} wrote: {}".format(self.client_address[0], m oyd pemdata))


if __name__ == "__main__":
	HOST, PORT = "localhost", 9999

	# create the server, binding to HOST and PORT
	server = socketserver.TCPServer((HOST, PORT), TCPHandler)

	# Activate the server - this will run forever until interrupted
	try:

		server.serve_forever()
	except KeyboardInterrupt:
		print("shutting down server")
		server.server_close()

