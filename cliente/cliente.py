import socket
import sys
import concurrent.futures
import logging

s = socket.socket()
HOST = "192.168.20.48"
PORT = 444
FORMAT = 'utf-8'

def conn(tid):
    print("Comiensa hilo: " + str(tid))
    s.sendall(bytes(tid))
    print("ID enviado")
    file = s.recv(1024)
    print(file.decode(FORMAT))
    print("Mensaje recivido")
    s.sendall("ACK")

if __name__ == "__main__":
    try:
        s.connect((HOST,PORT))
    except socket.error as msg:
        print(msg)
    print("ceneccion establecida")

    message = bytes("file.txt", FORMAT)
    s.sendall(message)
    message = bytes(3)
    s.sendall(message)
    print("mensage enviado")

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(conn, range(3))

#s.listen(5) 
#while True:
#    c, addr = s.accept() 
#    c.send (' Grace for connecting ') 
#    c.close ()
