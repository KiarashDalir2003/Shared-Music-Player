import threading
import socket
from threading import *
from pymongo import *
import bcrypt
clients = []
MongoClk = MongoClient('localhost', 27017)
db = MongoClk['musicDB']
playlistCollection = db['playlist']
userCollection = db['users']

# def broadcast(playlist_data):
#     for c in clients:
#         try:
#             c.send(playlist_data.encode('utf-8'))
#         except:
#             clients.remove(c)

def handleClient(conn, addr):
    while True:
        request = conn.recv(1024).decode('utf-8')
        if not request:
            break
        action, username, password = request.split(',')
        if action == 'signup':
            if userCollection.find_one({'username': username}):
                response = 'Username already exists'
            else:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                userCollection.insert_one({'username': username, 'password': hashed_password})
                response = 'User created successfully'
            conn.send(response.encode('utf-8'))
        elif action == 'login':
            user = userCollection.find_one({'username': username})
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
                response = 'Login successfully'
            else:
                response = 'Invalid username or password'
            conn.send(response.encode('utf-8'))
            conn.close()

def getPlaylist():
    pass

def server():
    SRV_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SRV_Sock.bind(('localhost', 12345))
    SRV_Sock.listen()
    print("Server is listening...")
    while True:
        conn, addr = SRV_Sock.accept()
        clients.append(conn)
        threading.Thread(target=handleClient, args=(conn, addr)).start()

if __name__ == '__main__':
    server()
