import socket
s = socket.socket() 
HOST = "localhost"
PORT = 9999
#s.bind((host, port)) 
# wtf is this??
s.listen(5) 
while True:
    c, addr = s.accept() 
    c.send (' Grace for connecting ') 
    c.close ()
