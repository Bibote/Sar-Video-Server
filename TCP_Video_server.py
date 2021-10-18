#!/usr/bin/env python3

import socket, os, signal

class Video(object):
	
	def __init__(self, id, etiqueta, tamaño):
		self.id = id
		self.etiqueta = etiqueta
		self.tamaño = tamaño

	def darID(self):
		return self.id
	
	def darEtiqueta(self):
		return self.etiqueta
	
	def darTamaño(self):
		return self.tamaño

class Usuario(object):

	def __init__(self, usuario, contraseña):
		self.usuario = usuario
		self.contraseña = contraseña
	
	def darUsuario(self):
		return self.usuario

	def darContraseña(self):
		return self.contraseña

#Creamos la lista de Videos y la rellenamos
v1 = Video('VID01', 'playa', '2')
v2 = Video('VID02', 'monte', '10')
v3 = Video('VID03', 'familia', '8')

listaVideos = [v1, v2, v3]

u1 = Usuario('admin', 'admin')
u2 = Usuario('ibai', 'ibai')
u3 = Usuario('olatz', 'olatz')


listaUsuarios = [u1, u2, u3]

#LISTA DE COMANDOS DEL SERVIDOR
def Log(comando):
	return 0

def Put(comando):
	return 0

def Get(comando):
	return 0

def Tag(comando):
	return 0

def Fnd(comando):
	return 0

def Qit(comando):
	return 0

def switch(case, comando):
   sw = {
      "LOG": Log(comando),
      "PUT": Put(comando),
      "GET": Get(comando),
      "TAG": Tag(comando),
	  "FND": Fnd(comando),
	  "QIT": Qit(comando)
   }
   return sw.get(case, "Comando Erróneo")

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
			comando = buf.decode()
			
			#Comprobamos los tres caracteres
			case = comando[0:3]

			#Ejecutamos con la funcion switch el comando y si no existe nos lanza error(declaración arriba)
			buf2 = switch(case, comando)

			dialogo.sendall( buf2.encode())

		print( "Solicitud de cierre de conexión recibida." )
		dialogo.close()
		exit( 0 )
s.close()
