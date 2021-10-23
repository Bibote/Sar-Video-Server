#!/usr/bin/env python3


import socket, os, signal, select

class Video(object):
	
	def __init__(self, id, tamaño, video):
		self.id = id
		self.etiqueta = []
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

	def addEtiqueta(self,etiqueta):
		self.etiqueta.append(etiqueta)

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
v1 = Video('VID01', '2', '10101')
v2 = Video('VID02','10', '10101')
v3 = Video('VID03', '8', '10101')

v1.addEtiqueta('playa')
v1.addEtiqueta('fino')
v2.addEtiqueta('monte')
v3.addEtiqueta('familia')

#Se crean variables globales para saber qué usuario ha hecho login y el último id del vídeo
ultimo_video_id = 10000
usuario_actual: Usuario
login = False
maxVideos = 100
numVideos = 0

u1 = Usuario('admin', 'admin')
u2 = Usuario('ibai', 'ibai')
u3 = Usuario('olatz', 'olatz')

u1.addVideo(v1)
u1.addVideo(v2)
u3.addVideo(v3)

listaUsuarios = [u1, u2, u3]

#LISTA DE COMANDOS DEL SERVIDOR
def Log(comando):
	global usuario_actual
	global login
    #Estructura Log: LOGuser1#user1
	if(len(comando)<2):
		return'-ER03\r\n'
	else:
		if("#" not in comando):
			return '-ER04\r\n'
		datos = comando.partition('#')
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
#partition en el LOG, id en el put
def Put(comando):
	global ultimo_video_id
	global usuario_actual
	if (numVideos==maxVideos):
		return ('-ER06\r\n')
	vídeo = Video(ultimo_video_id,len(comando),comando)
	ultimo_video_id+=1
	usuario_actual.addVideo(vídeo)
	return ('+OK' + str(ultimo_video_id-1) + '\r\n')

def Get(comando):
	global usuario_actual
	found=False
	if len(comando)!=5:
		return '-ER04\r\n'

	for video in usuario_actual.darVideos():
		if video.darID()==comando:
			found=True
			return ('+OK'+video.darTamaño()+'#'+video.darVideo()+'\r\n')
			
			
	if(found==False):
		return '-ER07\r\n'
	

def Tag(comando):
	global usuario_actual
	if len(comando) < 5:
		return "-ER03\r\n"
	

	idvideo = comando[0:5]
	if len(comando) == 5:
		for i in usuario_actual.darVideos():
			if i.darID() == idvideo:
				lista=''
				for j in i.darEtiqueta():
					lista+=j+"#"
				if lista=='':
					return "+OK"
				else:
					lista=lista[:-1]
					return "+OK"+lista+"\r\n"	
		return "-ER08\r\n"
		
	
	
	etiquetaVideo = comando[comando.find("#")+1:len(comando)]
	for i in usuario_actual.darVideos():
		if i.darID() == idvideo:
			i.addEtiqueta(etiquetaVideo)
			return "+OK\r\n"
	return "-ER08\r\n"

def Fnd(comando):
	lista = ''
	

	for i in usuario_actual.darVideos():
		print(i.darEtiqueta())
		print(comando)
		if comando in i.darEtiqueta():
			lista += i.darID()+'#'
	if lista!='': 
		lista=lista[:-1]

	return "+OK:"+ lista+"\r\n"
def leer():
	comando=''
	while True:
		recibido, _, _ = select.select( [ dialogo ], [], [],1 )
		
		if recibido:
			buf=dialogo.recv(1024)
			comando+=buf.decode()
			return comando
		if not recibido:
			print("no recibido")
			return ''


		
		






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
		login=False
		while True:
			
			buf = dialogo.recv( 3 )
			case = 'e'
			if len(buf.decode())==3:
				case=buf.decode()
			else:
				buf2='-ER01\r\n'
				
			if (login==False):
				if (case=='LOG'):
					comando=leer()
					buf2=Log(comando)
				elif(case=='QIT'):
					exit( 0 )
				else:
					buf2='-ER01'		
			elif (case=='PUT'):
				tamaño=''
				while True:
					buf3=dialogo.recv(1)
					if buf3.decode()=='#':
						break
					tamaño+=buf3.decode()
				buf4=dialogo.recv(int(tamaño))
				if (len(buf4.decode())==0):
					buf2="-ER03\r\n"
				else:
					buf2=Put(buf4.decode())
			elif(case=='GET'):
				comando=leer()
				buf2=Get(comando)
			elif(case=='TAG'):
				comando=leer()
				buf2=Tag(comando)
			elif(case=='FND'):
				comando=leer()
				buf2=Fnd(comando)
			elif(case=='QIT'):
				exit(0)
				break
			else:
				buf2='-ER01\r\n'
			
			dialogo.sendall( buf2.encode())

		
		
		
s.close()
