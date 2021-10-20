#!/usr/bin/env python3

#Se asume el usuario1 para las pruebas
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
		self.num_videos = 0
		self.max_videos = 100
	def darUsuario(self):
		return self.usuario

	def darContraseña(self):
		return self.contraseña
	def darVideos(self):
		return self.videos
	def addVideo(self, video):
		if (self.num_videos==self.max_videos):
			return(-1)
		else:
			self.videos.append(video)
			self.num_videos+=1
		

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


listaUsuarios = [u1, u2, u3]

#LISTA DE COMANDOS DEL SERVIDOR
def Log(comando):
    global usuario_actual
    usuario_actual=u1
    print("LOG command executed")
    return "+OK"

def Put(comando):
    global ultimo_video_id
    global usuario_actual
    if len(comando) < 6:
        return "Error 03"

	#ME HACE FALTA SABER QUÉ USUARIO ESTÁ LOGGEADO PARA METER SU VÍDEO
    datos = comando[3:].partition('#')  #devuelve: ('tamaño','#','el vídeo en sí')
    if (datos[0]=='' or datos[2]==''):
        return ('-ER04\r\n')

    print("tamaño del vídeo",datos[0])
    print("contenido del vídeo",datos[2])

    vídeo = Video(ultimo_video_id,datos[0],datos [2])
    ultimo_video_id+=1
    if(usuario_actual.addVideo(vídeo)==-1):
        return ('-ER06\r\n')
    else:
        return ('+OK' + str(ultimo_video_id-1) + '\r\n')

def Get(comando):
	print("GET command executed")
	return "+OK"

def Tag(comando):
	print("TAG command executed")
	return "+OK"

def Fnd(comando):
	print("FND command executed")
	return "+OK"


def Qit(comando):
	return 0


PORT = 50004

s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

s.bind( ('', PORT) )
s.listen( 5 )


signal.signal( signal.SIGCHLD, signal.SIG_IGN )
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
            if (case=='LOG'):
                buf2=Log(comando)
            elif (case=='PUT'):
                buf2=Put(comando)
            elif (case=='GET'):
                buf2=Get(comando)
            elif (case=='TAG'):
                buf2=Tag(comando)
            elif (case=='FND'):
                buf2=Fnd(comando)
            else:
                buf2='-ERCódigo erróneo'

            dialogo.sendall( buf2.encode())

        print( "Solicitud de cierre de conexión recibida." )
        dialogo.close()
        exit( 0 )
s.close()