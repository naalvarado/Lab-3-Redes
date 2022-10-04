import socket
import sys
import concurrent.futures
import logging
import datetime
import os
import tqdm

s = socket.socket()
HOST = "192.168.20.48"
PORT = 444
FORMAT = 'utf-8'

logs = os.path.exists("./Logs")
if not logs:
    os.makedirs("./Logs")

format = "%(asctime)s: %(message)s"
now = datetime.datetime.now()
logfile = "./Logs/" + str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + str(now.minute) + "-" + str(now.second) + ".log"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S", filename=logfile)

filesize = 0
fileName = ""

def conn(tid):
    print("Comiensa hilo: " + str(tid))
    s.sendall(bytes(tid))
    print("ID enviado")
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(fileName, "wb") as f:
        while True:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))

    s.sendall("ACK")
    s.close()

if __name__ == "__main__":
    try:
        s.connect((HOST,PORT))
    except socket.error as msg:
        print(msg)
    print("ceneccion establecida")
    logging.info("Coneccion establecida con: " + str(HOST) + " en puerto: " + str(PORT))

    print("Que archivo quiere descargar?")
    print("1) 100Mb")
    print("2) 250Mb")
    fileCode = input()
    if fileCode == "1":
        fileName = "100MB.txt"
        filesize = 100000
    elif fileCode == "2":
        fileName = "250MB.txt"
        filesize = 250000
    else:
        print("input no valido")
        exit(1)
    message = bytes(fileName, FORMAT)
    s.sendall(message)
    print("Numero de conecciones: ")
    cons = int(input())
    message = bytes(cons)
    s.sendall(message)
    print("mensage enviado")

    logging.info("Creando " + str(cons) + " clientes para descargar el archivo " + str(fileName))

    with concurrent.futures.ThreadPoolExecutor(max_workers=cons) as executor:
        executor.map(conn, range(cons))

#s.listen(5) 
#while True:
#    c, addr = s.accept() 
#    c.send (' Grace for connecting ') 
#    c.close ()
