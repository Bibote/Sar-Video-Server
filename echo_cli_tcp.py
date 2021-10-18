#!/usr/bin/env python3

import socket, sys

PORT = 50004

if len( sys.argv ) != 2:
	print( "Uso: {} <servidor>".format( sys.argv[0] ) )
	exit( 1 )

dir_serv = (sys.argv[1], PORT)

s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
s.connect( dir_serv )

print( "Introduce el comando:" )
while True:
	mensaje = input()
	if not mensaje:
		break
	s.sendall( mensaje.encode() )

	buf = s.recv( 1024 )
	print( buf.decode() )
s.close()
