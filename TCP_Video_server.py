#!/usr/bin/env python3


import socket, os, signal 

class Video(object):
	
	def __init__(self, id, tamaño, video, etiqueta=None):
		self.id = id
		self.etiqueta = [etiqueta]
		self.tamaño = tamaño
		self.video = video

	def darID(self):
		return self.id
	
	def darEtiqueta(self):
		return self.etiqueta
	
	def darTamaño(self):
		return self.tamaño

	def darVideo(self):
		return self.video

	def addEtiqueta(self,netiqueta):
		return self.etiqueta.append(netiqueta)

class Usuario(object):

	def __init__(self, usuario, contraseña):
		self.usuario = usuario
		self.contraseña = contraseña
		self.videos= []
	
	def darUsuario(self):
		return self.usuario

	def darContraseña(self):
		return self.contraseña
	def darVideos(self):
		return self.videos
	def addVideo(self, video):
		self.videos.append(video)
		

#Creamos la lista de Videos y la rellenamos
v1 = Video('VID01', '2', '10101', 'playa')
v2 = Video('VID02','10', '10101', 'monte')
v3 = Video('VID03', '8', '10101', 'familia')

#Se crean variables globales para saber qué usuario ha hecho login y el último id del vídeo
ultimo_video_id = 0
usuario_actual: Usuario


u1 = Usuario('admin', 'admin')
u2 = Usuario('ibai', 'ibai')
u3 = Usuario('olatz', 'olatz')


u1.addVideo(v1)
u2.addVideo(v2)
u3.addVideo(v3)

login = False

listaUsuarios = [u1, u2, u3]

#LISTA DE COMANDOS DEL SERVIDOR
def Log(comando):
	global usuario_actual
	global login
    #Estructura Log: LOGuser1#user1
	if(len(comando)<6):
		return'-ER03\r\n'
	else:
		if("#" not in comando):
			return '-ER04\r\n'
		datos = comando[3:].partition('#')
		usuario=datos[0]
		contra=datos[2]
		found=False
		

		
		for user in listaUsuarios:
			if(user.darUsuario()==usuario and user.darContraseña()==contra):
				found=True
				usuario_actual=user
				
				break
		if(found==False):
				return '-ER05\r\n'
		login = True
		return '+OK\r\n'

def Put(comando):
	global ultimo_video_id
	global usuario_actual
	if len(comando) < 6:
		return "Error 03"

	datos = comando[3:].partition('#')  #devuelve: ('tamaño','#','el vídeo en sí')
	if (datos[0]=='' or datos[2]==''):
		return ('-ER04\r\n')

	vídeo = Video(ultimo_video_id,datos[0],datos [2])
	ultimo_video_id+=1
	if(usuario_actual.addVideo(vídeo)==-1):
		return ('-ER06\r\n')
	else:
		return ('+OK' + str(ultimo_video_id-1) + '\r\n')

def Get(comando):
	global usuario_actual
	found=False
	if len(comando) < 4:
		return '-ER04\r\n'
	id= comando[3:]
	for video in usuario_actual.darVideos():
		if video.darID()==id:
			found=True
			return ('+OK'+video.darTamaño()+'#'+video.darVideo()+'\r\n')
			
			
	if(found==False):
		return '-ER07\r\n'
	

def Tag(comando):
	if len(comando) < 5:
		return "Error 03: Falta un parametro que no es opcional. El formato es: TAG {id} [etiqueta]"
	
	parametros = comando[4:len(comando)]
	longitud = len(parametros)

	idvideo = parametros[0:5]
	if longitud < 6:
		lista = []
		for i in listaVideos:
			if i.darID() == idvideo:
				lista.append(i.darEtiqueta())
				return "OK: La etiqueta de " + idvideo + " es -> " + lista
		
		return "Error 08: El id de dicho video no existe, introduzca uno correcto."
	
	etiquetaVideo = parametros[parametros.find("#"):len(parametros)]
	for i in listaVideos:
		if i.darID() == idvideo:
			i.etiqueta += etiquetaVideo
			return "OK"
	return "Error 08: El id de dicho video no existe, introduzca uno correcto."

def Fnd(comando):
	lista = ''
	idvideo = ''
	etiqueta = comando[4:len(comando)]

	for i in listaVideos:
		if i.darEtiqueta().find(etiqueta) != -1:
			lista += '#' + i.darID()
	return "OK: Los videos con dicha etiqueta son ->" + lista


def Qit(comando):
	if(len(comando)<3):
		return'-ER01\r\n'
	if(len(comando)>3):
		return '-ER02\r\n'
	
	return '+OK\r\n'

"""
def switch(case, comando):
   sw = {
      "LOG": Log(comando),
      "PUT": Put(comando),
      "GET": Get(comando),
      "TAG": Tag(comando),
	  "FND": Fnd(comando),
	  "QIT": Qit(comando)
   }
   return sw.get(case, "Error 01: Comando Erróneo")
"""

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
			#Lo siento no sé arreglar el switch y esto funciona			
			if (login==False):
				if (case=='LOG'):
					buf2=Log(comando)
					
				else:
					buf2='-ER01'
					
			else:
				if (case=='LOG'):
					buf2='-ER'
					
				elif (case=='PUT'):
					buf2=Put(comando)
					
				elif (case=='GET'):
					buf2=Get(comando)
					
				elif (case=='TAG'):
					buf2=Tag(comando)
					
				elif (case=='FND'):
					buf2=Fnd(comando)
					
				elif (case=='QIT'):
					print( "Cierre de conexión de {}:{}.".format( dir_cli[0], dir_cli[1] ) )
					buf2= Qit(comando)
					dialogo.sendall( buf2.encode())
					
					dialogo.close()
					break
					
				else:
					buf2='-ER01'
					

			dialogo.sendall( buf2.encode())

		
		
		exit( 0 )
s.close()
