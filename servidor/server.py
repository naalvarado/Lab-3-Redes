import datetime, logging, socket, sys, threading, os, hashlib, time, tqdm

HOST = '192.168.20.48'
PORT = 444
FORMAT = 'utf-8'
BUFFER_SIZE = 4096

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

    # Identificacion del cliente de la conexion
    idClient = conn.recv(1024)

    # start sending the file
    fileSizeBytes = os.path.getsize(fName)
    progress = tqdm.tqdm(range(fileSizeBytes), f"Sending {fName}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(fName, "rb") as f:

        # Calcular hash para el archivo
        hashValue = getHashDigest(f)
        #Envio de archivo
        start = time.time()
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            s.sendall(bytes_read)
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
nClients = int.from_bytes(conn.recv(1024), "big")
#conn.close()

format = "%(asctime)s: %(message)s"
now = datetime.datetime.now()

logFileName = "{}-{}-{}-{}-{}-{}.log".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
logging.basicConfig(format=format, datefmt="%H:%M:%S", filename=logFileName, level=logging.INFO)

tList = []
#now keep talking with the client
while nClients > 0:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
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
