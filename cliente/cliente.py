import socket
import sys
import concurrent.futures
import logging
import datetime
import os
import tqdm
import hashlib

s = socket.socket()
HOST = "192.168.20.48"
PORT = 444
FORMAT = 'utf-8'
BUFFER_SIZE = 4096

logs = os.path.exists("./Logs")
if not logs:
    os.makedirs("./Logs")

format = "%(asctime)s: %(message)s"
now = datetime.datetime.now()
logfile = "./Logs/" + str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + str(now.hour) + "-" + str(now.minute) + "-" + str(now.second) + ".log"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S", filename=logfile)

filesize = 0
fileName = ""

def getHashDigest(file):
    BLOCK_SIZE = 65536 # The size of each read from the file

    file_hash = hashlib.sha256() # Create the hash object, can use something other than `.sha256()` if you wish
    
    fb = file.read(BLOCK_SIZE) # Read from the file. Take in the amount declared above
    while len(fb) > 0: # While there is still data being read from the file
        file_hash.update(fb) # Update the hash
        fb = file.read(BLOCK_SIZE) # Read the next block from the file

    return (file_hash.hexdigest()) # Get the hexadecimal digest of the hash

def conn(tid):
    print("Comiensa hilo: " + str(tid))
    client_socket = socket.socket()
    try:
        client_socket.connect((HOST,PORT))
    except socket.error as msg:
        print(msg)
        exit(1)
    logging.info("Coneccion establecida con: " + str(HOST) + " en puerto: " + str(PORT) + " cliente " + str(tid))
    client_socket.sendall(bytes(tid))
    print("ID enviado")
    progress = tqdm.tqdm(range(filesize), f"Receiving {fileName}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(fileName, "wb") as f:
        while True:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))

        client_socket.sendall(bytes("ACK", FORMAT))
        hashDesc = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
        realHash = getHashDigest(f)
        if hashDesc == realHash:
            print("ok")
        else:
            print(":(")

    client_socket.close()

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
    cons = input()
    message = bytes(cons, FORMAT)
    s.sendall(message)
    print("mensage enviado")

    logging.info("Creando " + str(cons) + " clientes para descargar el archivo " + str(fileName))

    s.close()
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(cons)) as executor:
        executor.map(conn, range(int(cons)))


#s.listen(5) 
#while True:
#    c, addr = s.accept() 
#    c.send (' Grace for connecting ') 
#    c.close ()
