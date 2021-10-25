#!/usr/bin/env python3


import socket, os, signal, select

class Video(object):  #Clase que representa los vídeos. Se crea el vídeo sin tags y con un id secuencial que empieza por el 10000
	
	def __init__(self, id, video):
		self.id = id
		self.etiqueta = []
		self.video = video

	def darID(self):
		return self.id
	
	def darEtiqueta(self):
		return self.etiqueta

	def darVideo(self):
		return self.video

	def addEtiqueta(self,etiqueta):
		self.etiqueta.append(etiqueta)

class Usuario(object): #Clase que representa al usuario. Cada usuario tiene un id y su contraseña

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
		

#Creamos vídeos por defecto para probar las funciones
v1 = Video('VID01', '10101')
v2 = Video('VID02', '10101')
v3 = Video('VID03', '10101')

#Añadimos etiquetas para probar las funciones
v1.addEtiqueta('playa')
v1.addEtiqueta('fino')
v2.addEtiqueta('monte')
v3.addEtiqueta('familia')

#Se crean variables globales
ultimo_video_id = 10000  	#Guarda el útlimo id para la función de put
usuario_actual: Usuario 	#Guarda qué usuario ha hecho login
login = False 				#Guarda si se ha hecho login aún
maxVideos = 100				#Variable para simular el código ER06 al quedarse sin espacio el servidor
numVideos = 0				#Cantidad de vídeos actuales

#Creamos usuarios para probar. El servidor no se encarga de esto, pero para probar el protocolo usamos estos usuarios
u1 = Usuario('admin', 'admin')
u2 = Usuario('ibai', 'ibai')
u3 = Usuario('olatz', 'olatz')

listaUsuarios = [u1, u2, u3]

#Se añaden vídeos a los usuarios
u1.addVideo(v1)
u1.addVideo(v2)
u3.addVideo(v3)

#---------------------------------------------#
#---------------------------------------------#

#LISTA DE COMANDOS DEL SERVIDOR
def Log(comando):      #Estructura Log: LOGuser1#user1
	global usuario_actual
	global login

	if(len(comando)<2):  	#Si no hay al menos tres bytes, significa que falta un parámetro
		return'-ER03\r\n'
	else: 					#Ya que se esperan dos parámetros, si no encuentra '#' es el formato incorrecto
		if("#" not in comando):
			return '-ER04\r\n'
		datos = comando.partition('#') 		#Devuelve {usuario#contraseña}
		if datos[0]=='' or datos[2]=='': 	#Si usuario o contraseña son vacíos, faltan parámetros
			return'-ER03\r\n'
		usuario=datos[0]
		contra=datos[2]
		found=False
		
		for user in listaUsuarios:		#Recorre la lista de usuarios para encontrar el que coincida con usuario y contraseña
			if(user.darUsuario()==usuario and user.darContraseña()==contra):
				found=True
				usuario_actual=user
				
				break
		if(found==False):				#Si no se encuentra salta -ER05
				return '-ER05\r\n'
		login = True
		return '+OK\r\n'

def Put(comando):				#Estructura Put: PUTtamaño#video
	global ultimo_video_id
	global usuario_actual
	if (numVideos==maxVideos):	#Si no hay espacio en el servidor
		return ('-ER06\r\n')
	
	#No hacemos tantas comprobaciones de si el comando está bien porque se hacen más abajo
	newVideo = Video(str(ultimo_video_id),comando)	#Se construye el vídeo, se añade al usuario y se suma el último id
	ultimo_video_id+=1
	usuario_actual.addVideo(newVideo)
	return ('+OK' + str(ultimo_video_id-1) + '\r\n') #Devuelve +OKidVideo

def Get(comando):				#Estructura Put: PUTidvideo
	global usuario_actual
	found=False

	if len(comando)!=5:			#Si el id no tiene exáctamente 5 carácteres es formato incorrecto
		return '-ER04\r\n'

	#Busca el vídeo en el usuario que ha hecho login
	#Si está devuelve +OKtamaño#vídeo
	#Si no está devuelve -ER07
	for video in usuario_actual.darVideos(): 
		if video.darID()==comando:
			found=True
			return ('+OK'+str(len(video.darVideo()))+'#'+str(video.darVideo())+'\r\n')
			
			
	if(found==False):
		return '-ER07\r\n'
	

def Tag(comando):  			#Estructura Tag: TAGidvideo o TAGidvideo#tag
	global usuario_actual
	if len(comando) < 5:	#Si es demasiado corto es que faltan parámetros
		return "-ER03\r\n"
	

	idvideo = comando[0:5]
	if len(comando) == 5:  #Si son solo 5 bytes, quiere comprobar los tags del video
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
		
	
	#Si son más, se añade la etiqueta al vídeo con dicho id
	#En ámbos casos, si no está el vídeo, se devuelve -ER08
	etiquetaVideo = comando[comando.find("#")+1:len(comando)]
	for i in usuario_actual.darVideos():
		if i.darID() == idvideo:
			i.addEtiqueta(etiquetaVideo)
			return "+OK\r\n"
	return "-ER08\r\n"

def Fnd(comando): #Estructura Fnd: FNDtag
	lista = ''
	
	#Recorre los vídeos y si alguno tiene la etiqueta se añade a la lista
	#Finalmente, se devuelve +OK y la lista, separando los vídeos con #
	for i in usuario_actual.darVideos():
		print(i.darEtiqueta())
		print(comando)
		if comando in i.darEtiqueta():
			lista += i.darID()+'#'
	if lista!='': 
		lista=lista[:-1]

	return "+OK:"+ lista+"\r\n"
def leer():  #Función necesaria para más adelante, que espera un segundo a recibir un mensaje del cliente
	comando=''
	while True:
		recibido, _, _ = select.select( [ dialogo ], [], [],1 )
		
		if recibido:
			buf=dialogo.recv(1024)
			comando+=buf.decode()
			return comando
		if not recibido:
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
			s.close()
			buf = dialogo.recv( 3 )    #Se leen los primeros 3 bytes para saber el comando
			case = 'e'
			if len(buf.decode())==3:
				case=buf.decode()
			else:
				buf2='-ER01\r\n'       #Si se han leído menos, es un comando desconocido
				
			if (login==False):   			#En caso de que no se haya hecho login hay dos comandos permitidos: LOG y QIT
				if (case=='LOG'): 			#Si es LOG, recibe el resto del mensaje y llama a Log, que devuelve +OK o -ER
					comando=leer()
					buf2=Log(comando)
				elif(case=='QIT'): 			#Si es QIT, se cierra la conexión TCP
					if leer()=='':
						print( "Cierre de conexión de {}:{}.".format( dir_cli[0], dir_cli[1] ) )
						dialogo.close()
						break
					else:
						buf2='-ER02\r\n'	#Si se ha hecho QIT seguido de más datos, se devuelve el error de comando inesperado
				else:
					buf2='-ER01'		
			elif (case=='PUT'):				#Si ya se ha hecho login y se quiere hacer PUT, 
											#es necesario conocer primero el tamaño del vídeo para luego leer esa cantidad de bytes
				encontrado = False
				tamaño=''						#Para saber el tamaño, leemos byte a byte hasta encontrarnos con '#'
												#Vamos añadiendo los bytes leídos a 'tamaño'
												#Si no encuentra '#' y no queda nada por leer, significa que falta un parámetro. Esto se hace mirando 'encontrado'
				while True:
					buf3=dialogo.recv(1)
					if buf3.decode()=='#':
						encontrado=True
						break
					tamaño+=buf3.decode()
				
				if encontrado==True:
					buf4=dialogo.recv(int(tamaño))
					if (len(buf4.decode())==0):
						buf2="-ER03\r\n"
					else:
						buf2=Put(buf4.decode())
				else: 
					buf2 = buf2="-ER03\r\n"
			
			#En caso de que se pida otro comando, se llama a la función y se devuelve el resultado
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
				if leer()=='':
					print( "Cierre de conexión de {}:{}.".format( dir_cli[0], dir_cli[1] ) )
					dialogo.close()
					break
				else:
					buf2='-ER02\r\n'
			else:  				#En caso de que se lea mensaje vacío, o un comando desconocido, se devuelve -ER01
				leer()
				buf2='-ER01\r\n'
			
			dialogo.sendall( buf2.encode())

		
		
		exit(0)	
s.close()