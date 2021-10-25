#!/usr/bin/env python3


import socket, os, signal, select

#---------------------------------------------#
#        		 CLASES EXTRA	   		      #
#---------------------------------------------#
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
		
#---------------------------------------------#
#     INICIALIZACIONES PARA LAS PRUEBAS	      #
#---------------------------------------------#

#Creamos vídeos por defecto 
v1 = Video('VID01', 'GFDGDFSGFDG')
v2 = Video('VID02', 'VIDEO2SOBRELAMONTANA')
v3 = Video('VID03', 'VIDEO3SOBREFAIMLIA')
v4 = Video('VID04', 'BuenVideoDeSockets')

#Añadimos etiquetas 
v1.addEtiqueta('playa')
v1.addEtiqueta('fino')
v2.addEtiqueta('monte')
v3.addEtiqueta('familia')
v4.addEtiqueta('SAR')

#Creamos usuarios. El servidor no se encarga de esto, pero para probar el protocolo usamos estos usuarios
u1 = Usuario('admin', 'admin')
u2 = Usuario('ibai', 'ibai')
u3 = Usuario('olatz', 'olatz')

listaUsuarios = [u1, u2, u3]

#Se añaden vídeos a los usuarios
u1.addVideo(v1)
u1.addVideo(v2)
u3.addVideo(v3)
u2.addVideo(v4)

#---------------------------------------------#
#              VARIABLES GLOBALES             #
#---------------------------------------------#

ultimo_video_id = 10000  	#Guarda el útlimo id para la función de put
usuario_actual: Usuario 	#Guarda qué usuario ha hecho login
login = False 				#Guarda si se ha hecho login aún
maxVideos = 100				#Variable para simular el código ER06 al quedarse sin espacio el servidor
numVideos = 0				#Cantidad de vídeos actuales




#---------------------------------------------#
#        LISTA DE COMANDOS DEL SERVIDOR       #
#---------------------------------------------#

def Log(comando):      #Estructura Log: LOGuser1#user1
	global usuario_actual
	global login
	if' ' in comando:
		return '-ER04\r\n'

	if(len(comando)<2):  	#Si no hay al menos tres bytes, significa que falta un parámetro
		return'-ER03\r\n'
	else: 					#Ya que se esperan dos parámetros, si no encuentra '#' es el formato incorrecto
		if("#" not in comando):
			return '-ER04\r\n'
		datos = comando.partition('#') 		#Lee en formato {usuario#contraseña}
		if datos[0]=='' or datos[2]=='': 	#Si usuario o contraseña son vacíos, faltan parámetros
			return'-ER03\r\n'
		usuario=datos[0]
		contra=datos[2]
		found=False
		
		for user in listaUsuarios:		#Recorre la lista de usuarios para encontrar el que coincida con usuario y contraseña
			if(user.darUsuario()==usuario and user.darContraseña()==contra):
				found=True
				usuario_actual=user
				print( "Inicio de sesion: {}:{}".format( dir_cli[0], dir_cli[1])+" Usuario: "+str(usuario_actual.darUsuario()) )
				
				break
		if(found==False):				#Si no se encuentra salta -ER05
				return '-ER05\r\n'
		login = True
		return '+OK\r\n'

def Put(comando):				#Estructura Put: PUTtamaño#video
	if' ' in comando:
		return '-ER04\r\n'
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
	if' ' in comando:
		return '-ER04\r\n'
	if'#' in comando:
		return '-ER04\r\n'
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
	if' ' in comando:
		return '-ER04\r\n'
	global usuario_actual
	if len(comando) < 5:	#Si es demasiado corto es que faltan parámetros
		return "-ER03\r\n"
	

	idvideo = comando[0:5]
	if len(comando) == 5:  #Si son solo 5 bytes, quiere comprobar los tags del video
		if '#' not in comando:
			return '-ER04\r\n'
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
			comando=comando[:-2]
			return comando
		if not recibido:
			return ''

#---------------------------------------------#
#        CONEXIÓN Y PROCESOS HIJOS  	      #
#---------------------------------------------#

PORT = 50004

s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

s.bind( ('', PORT) )
s.listen( 5 )

signal.signal(signal.SIGCHLD, signal.SIG_IGN)
print("Servidor Encendido")
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

			#Se leen 3 bytes para saber el comando y se rechaza si son menos (-ER01)
			buf = dialogo.recv( 3 )    
			case = 'comando erroneo'				   #Case por defecto por si no se ha leído nada
			if len(buf.decode())==3:
				case=buf.decode()
			else:
				buf2='-ER01\r\n'     


			#-----------------------------------------------------------#
			#    Diferenciar si se ha hecho login y/o si se hace put    #
			#-----------------------------------------------------------#

			#SIN LOGIN
			if (login==False):   			#Dos comandos permitidos: LOG y QIT
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

			#LOGIN Y PUT
			elif (case=='PUT'):				
				numero=0						#Es necesario conocer primero el tamaño del vídeo para luego leer esa cantidad de bytes
				encontrado = False
				tamaño=''						#Para saber el tamaño, leemos byte a byte hasta encontrarnos con '#'
												#Vamos añadiendo los bytes leídos a 'tamaño'
												#Si no encuentra '#' y no queda nada por leer, significa que falta un parámetro. Esto se hace mirando 'encontrado'
				while True:
					size, _, _ = select.select( [ dialogo ], [], [],1 )
					if size:
						buf3=dialogo.recv(1)
						
						tamaño+=buf3.decode()
						if buf3.decode()=='#':	#Ha encontrado '#', por lo que tiene el tamaño
							encontrado=True
							break
					else:						#No recibe el tamaño, por lo que falta parámetro
						buf2='-ER03\r\n'
						break

				if encontrado==True:
					tamaño=tamaño[:-1]
					if str.isdigit(tamaño):		#Comprueba que el tamaño es un dígito
						numero=int(tamaño)
					else:						#Si no es dígito no lee nada
						numero=0
						buf2='-ER04\r\n'
				else:							#Si no hay '#' tampoco lee nada
					numero=0
					
				if(numero!=0):
					video, _, _ = select.select( [ dialogo ], [], [],1 )	#Lee el número de bytes que forman el vídeo
					if video:
						buf4=dialogo.recv(numero)
						if buf4.decode()=='':
							buf2='-ER03\r\n'	#Falta el vídeo
						else:
							buf2=Put(buf4.decode())
							print("Cliente:"+ str(usuario_actual.darUsuario())+" comando en uso:"+case+" video a introducir: "+buf4.decode())
					else:
						buf2='-ER03\r\n'


					
			
			#En caso de que se pida otro comando, se llama a la función y se devuelve el resultado
			elif(case=='GET'):
				comando=leer()
				print("Cliente:"+ str(usuario_actual.darUsuario())+" comando en uso:"+case+" parametros: "+comando)
				buf2=Get(comando)
			elif(case=='TAG'):
				comando=leer()
				print("Cliente:"+ str(usuario_actual.darUsuario())+" comando en uso:"+case+" parametros: "+comando)
				buf2=Tag(comando)
			elif(case=='FND'):
				comando=leer()
				print("Cliente:"+ str(usuario_actual.darUsuario())+" comando en uso:"+case+" parametros: "+comando)
				buf2=Fnd(comando)
			elif(case=='QIT'):
				if leer()=='':
					print("Cliente:"+ str(usuario_actual.darUsuario())+" comando en uso:"+case+" parametros: "+comando)
					dialogo.close()
					break
				else:
					buf2='-ER02\r\n'
			else:  				#En caso de que se lea mensaje vacío, o un comando desconocido, se devuelve -ER01
				buf2='-ER01\r\n'
			leer()
			dialogo.sendall( buf2.encode())

		
		
		exit(0)	
s.close()