from signal import signal, SIGPIPE, SIG_DFL
#Ignore SIG_PIPE and don't throw exceptions on it... (http://docs.python.org/library/signal.html)  
signal(SIGPIPE,SIG_DFL)   

import datetime, logging, socket, sys, threading, os, hashlib, time, tqdm
#"192.168.47.129"
HOST = '192.168.47.129'
PORT = 5454
FORMAT = 'utf-8'
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

#Bind socket 
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
	
print ('Socket bind complete')

#Start listening on socket
s.listen(10)
print ('Socket now listening')

def getHashDigest(file):
    BLOCK_SIZE = 65536 # The size of each read from the file

    file_hash = hashlib.sha256() # Create the hash object, can use something other than `.sha256()` if you wish
    
    fb = file.read(BLOCK_SIZE) # Read from the file. Take in the amount declared above
    while len(fb) > 0: # While there is still data being read from the file
        file_hash.update(fb) # Update the hash
        fb = file.read(BLOCK_SIZE) # Read the next block from the file

    return (file_hash.hexdigest()) # Get the hexadecimal digest of the hash

#Function for handling connections. This will be used to create threads
def clientthread(conn, fName):
    print("before id")
    # Identificacion del cliente de la conexion
    idClient = int(conn.recv(1024).decode(FORMAT))
    print(idClient)

    # start sending the file
    fileSizeBytes = os.path.getsize(fName)
    conn.send(f"{fName}{SEPARATOR}{fileSizeBytes}".encode())
    progress = tqdm.tqdm(range(fileSizeBytes), f"Sending {fName}", unit="B", unit_scale=True, unit_divisor=1024)
    print ("antesopen")
    with open(fName, "rb") as f:

        # Calcular hash para el archivo
        hashValue = getHashDigest(f)
        #Envio de archivo
        print("Empiza el envio")
        start = time.time()
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            conn.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

        logging.info('SENT {} WITH SIZE {}MB TO CLIENT #{}'.format(fName, fileSizeBytes/ (1024 * 1024), idClient))

        exito = conn.recv(1024)
        if not exito:
            logging.error('FROM CLIENT #{}: File transfer failed')
            conn.close()

        logging.info('FROM CLIENT #{}: {}'.format(idClient, exito))
        
        end = time.time()

        #Calculo de tiempo de transferencia
        logging.info('TRANSFER TIME FOR CLIENT #{}: {}'.format(idClient, end-start))

        #Envio de hash
        conn.send(hashValue.encode(FORMAT))
        logging.info('SENT HASH {} TO CLIENT #{}'.format(hashValue, idClient))

    conn.close()

#Master client
conn, addr = s.accept()
print ('Connected with ' + addr[0] + ':' + str(addr[1]))
fileName = conn.recv(1024).decode(FORMAT)
#nClients = int.from_bytes(conn.recv(1024), "big")
nClients = int(conn.recv(1024).decode(FORMAT))
#conn.close()

logs = os.path.exists("./Logs")
if not logs:
    os.makedirs("./Logs")

format = "%(asctime)s: %(message)s"
now = datetime.datetime.now()

logFileName = "./Logs/"+ "{}-{}-{}-{}-{}-{}.log".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
logging.basicConfig(format=format, datefmt="%H:%M:%S", filename=logFileName, level=logging.INFO)

tList = []
#now keep talking with the client
print("antes del while")
print(str(fileName))
print(str(nClients))
while nClients > 0:
    print(nClients)
    print("dentro del while")
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))
    logging.info('Connected with ' + addr[0] + ':' + str(addr[1]))

    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    t = threading.Thread(target=clientthread, args=(conn, fileName))
    tList.append(t)

    nClients -= 1

for t in tList:
    t.start()

for t in tList:
    t.join()

s.close()
