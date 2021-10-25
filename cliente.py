#!/usr/bin/env python3
import socket
import sys
import os
import util

SERVER = 'localhost'
PORT = 50004

ERR_MSG = (

    "Correcto.",
    "Comando desconocido o inesperado.",
    "Usuario desconocido.",
    "Clave de paso o password incorrecto.",
    "Error al crear la lista de ficheros.",
    "El fichero no existe.",
    "Error al bajar el fichero.",
    "Un usuario anonimo no tiene permisos para esta operacion.",
    "El fichero es demasiado grande.",
    "Error al preparar el fichero para subirlo.",
    "Error al subir el fichero.",
    "Error al borrar el fichero."
)

class Menu:
    List, Download, Upload, Delete, Exit = range(1, 6)
    Options = (
        "Lista de ficheros",
       "Bajar fichero",
       "Subir fichero",
       "Borrar fichero",
       "Salir"
    )

def menu():
    
    print(f"+{'-' * 30}+")
    for i, option in enumerate(Menu.Options, 1):
        print(f"| {i}.- {option:<25}|")

    print(f"+{'-' * 30}+")
    while True:
        try:
            selected = int(input("Selecciona una opción: "))
        except:
            print("Opción no válida.")
            continue
        if 0 < selected <= len(Menu.Options):
            return selected
        else:
            print("Opción no válida.")

def is_error(message):
    if message.startswith("ER"):
        code = int(message[2:])
        print(ERR_MSG[code])
        return True
    return False

def int2bytes(n):
    if n < 1 << 10:
        return str(n) + "B "
    elif n < 1 << 20:
        return str(round(n / (1 << 10))) + " KiB"
    elif n < 1 << 30:
        return str(round(n / (1 << 20))) + " MiB"
    else:
        return str(round(n / (1 << 30))) + " GiB"

if __name__ == "__main__":
    if len(sys.argv) > 3:
        print("Uso: {} [<servidor> [<puerto>]]".format(sys.argv[0]))
        exit(2)
    elif len(sys.argv) >= 2:
        SERVER = sys.argv[1]
        if len(sys.argv) == 3:
            PORT = int(sys.argv[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER, PORT))
    
    while True:
        user = input("Introduce el nombre de usuario: ")
        message = "{}{}\r\n".format(util.Command.User, user)
        s.sendall(message.encode("ascii"))
        message = util.recvline(s).decode("ascii")
        if is_error(message):
            continue
        password = input("Introduce la contraseña: ")
        message = "{}{}\r\n".format(util.Command.Password, password)
        s.sendall(message.encode("ascii"))
        message = util.recvline(s).decode("ascii")
        if not is_error(message):
            break

while True:
    option = Menu.menu()
    if option ==Menu.List:
        message = "{}\r\n".format(util.Command.List)
        s.sendall(message.encode("ascii"))
        message = util.recvline(s).decode("ascii")
        if is_error(message):
            continue
        filecount = 0
        print("Listado de ficheros disponibles")
        print("-------------------------------")
        while True:
            line = util.recvline(s).decode("ascii")
            if line:
                filecount += 1
                fileinfo = line.split('?')
                print("{:<20} {:>8}".format(
                    fileinfo[0], int2bytes(int(fileinfo[1]))))
            else:
                break
        print("-------------------------------")
        if filecount == 0:
            print("No hay ficheros disponibles.")
        else:
            plural = "s" if filecount > 1 else ""
            print("{0} fichero{1} disponible{1}.".format(filecount, plural))
    elif option == Menu.Download:
        filename = input("Indica el fichero que quieres bajar: ")
        message = "{}{}\r\n".format(util.Command.Download, filename)
        s.sendall(message.encode("ascii"))
        message = util.recvline(s).decode("ascii")
        if is_error(message):
            continue
        filesize = int(message[2:])
        message = "{}\r\n".format(util.Command.Download2)
        s.sendall(message.encode("ascii"))
        message = util.recvline(s).decode("ascii")
        if is_error(message):
            continue
        filedata = util.recvall(s, filesize)
        try:
            with open(filename, "wb") as f:
                f.write(filedata)
        except:
            print("No se ha podido guardar el fichero en disco.")
        else:
            print("El fichero {} se ha descargado correctamente.".format(filename))
   
    elif option == Menu.Upload:
        filename = input("Indica el fichero que quieres subir: ")
        try:
            filesize = os.path.getsize(filename)
            with open(filename, "rb") as f:
                filedata = f.read()
        except:
            print("No se ha podido acceder al fichero {}.".format(filename))
            continue
        message = "{}{}?{}\r\n".format(
            util.Command.Upload, filename, filesize)
        s.sendall(message.encode("ascii"))
        message = util.recvline(s).decode("ascii")
        if is_error(message):
            continue
        message = "{}\r\n".format(util.Command.Upload2)
        s.sendall(message.encode("ascii"))
        s.sendall(filedata)
        message = util.recvline(s).decode("ascii")
        if not is_error(message):
            print("El fichero {} se ha enviado correctamente.".format(filename))
    
    elif option == Menu.Delete:
        filename = input("Indica el fichero que quieres borrar: ")
        message = "{}{}\r\n".format(util.Command.Delete, filename)
        s.sendall(message.encode("ascii"))
        message = util.recvline(s).decode("ascii")
        if not is_error(message):
            print("El fichero {} se ha borrado correctamente.".format(filename))

    elif option == Menu.Exit:
        message = "{}\r\n".format(util.Command.Exit)
        s.sendall(message.encode("ascii"))
        message = util.recvline(s).decode("ascii")
        break
s.close()