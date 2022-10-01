import datetime, logging, socket, sys, threading, os, hashlib, time

HOST = '192.168.47.129'
PORT = 444
FORMAT = 'utf-8'

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

    # Lectura de archivo
    file = open(fName, "r")
    fileStats = os.stat(fName)
    fileSizeMB = fileStats.st_size / (1024 * 1024)
    data = file.read()
    
    # Identificacion del cliente de la conexion
    idClient = conn.recv(1024)

    # Calcular hash para el archivo
    hashValue = getHashDigest(file)

    #Envio de archivo
    start = time.time()
    conn.send(data.encode(FORMAT))
    logging.info('SENT {} WITH SIZE {}MB TO CLIENT #{}'.format(fName, fileSizeMB, idClient))

    exito = conn.recv(1024)
    if not exito:
        logging.error('FROM CLIENT #{}: File transfer failed')
        conn.close()

    logging.info('FROM CLIENT #{}: {}'.format(idClient, exito))
    
    end = time.time()
    
    #Calculo de tiempo de transferencia
    logging.info('TRANSFER TIME FOR CLIENT #{}: {}'.format(idClient, start-end))

    #Envio de hash
    conn.send(hashValue.encode(FORMAT))
    logging.info('SENT HASH {} TO CLIENT #{}'.format(hashValue, idClient))

    conn.close()

#Master client
conn, addr = s.accept()
print ('Connected with ' + addr[0] + ':' + str(addr[1]))
fileName = conn.recv(1024).decode(FORMAT)
nClients = conn.recv(1024)
conn.close()

now = datetime.datetime.now()

logFileName = "{}-{}-{}-{}-{}-{}.log".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
logging.basicConfig(filename=logFileName, level=logging.INFO)

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