#!/usr/bin/env python3

import socket, os, signal

PORT = 50004

s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

s.bind( ('', PORT) )
s.listen( 5 )

signal.signal(signal.SIGCHLD, signal.SIG_IGN)

while True:
	dialogo, dir_cli = s.accept()
	print( "Cliente conectado desde {}:{}.".format( dir_cli[0], dir_cli[1] ) )
	if os.fork():
		dialogo.close()
	else:
		s.close()
		while True:
			buf = dialogo.recv( 1024 )
			if not buf:
				break
			dialogo.sendall( buf )

			print("hola")
		print( "Solicitud de cierre de conexión recibida." )
		dialogo.close()
		exit( 0 )
s.close()
