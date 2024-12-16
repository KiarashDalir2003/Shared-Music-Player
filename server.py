import threading
import socket
from pymongo import MongoClient
import bcrypt

clients = []
MongoClk = MongoClient('localhost', 27017)
db = MongoClk['musicDB']

votedSongCollection = db['voteList']
playlistCollection = db['playlist']
userCollection = db['users']

def broadcastToAllClients(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            clients.remove(client)

def handleClient(conn, addr):
    while True:
        request = conn.recv(1024).decode('utf-8')
        if not request:
            break
        p = request.split(',')
        action = p[0]
        if action == 'signup':
            username = p[1]
            password = p[2]
            if userCollection.find_one({'username': username}):
                response = 'Username already exists'
            else:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                userCollection.insert_one({'username': username, 'password': hashed_password})
                response = 'User created successfully'
            conn.send(response.encode('utf-8'))
        elif action == 'login':
            username = p[1]
            password = p[2]
            user = userCollection.find_one({'username': username})
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
                response = 'Login successfully'
                playlist_dict = playlistCollection.find({}, {'_id': 0, 'file_path': 1}).sort('votes', -1)
                for music in playlist_dict:
                    file_path = music['file_path']
                    response += f',{file_path}'
            else:
                response = 'Invalid username or password'
            conn.send(response.encode('utf-8'))
        elif action == 'addsong':
            file_path = p[1]

            if playlistCollection.find_one({'file_path': file_path}):
                response = 'File already exists'
            else:
                response = 'Song added successfully'
                playlistCollection.insert_one({'file_path': file_path, 'votes': 0})

            playlist_dict = playlistCollection.find({}, {'_id': 0, 'file_path': 1}).sort('votes', -1)
            for music in playlist_dict:
                file_path = music['file_path']
                response += f',{file_path}'
            broadcastToAllClients(response)
            conn.send(response.encode('utf-8'))
        elif action == 'deletesong':
            file_path = p[1]
            if playlistCollection.find_one({'file_path': file_path}):
                playlistCollection.delete_one({'file_path': file_path})
                votedSongCollection.delete_many({'file_path': file_path})
                response = 'Song deleted successfully'
                playlist_dict = playlistCollection.find({}, {'_id': 0, 'file_path': 1}).sort('votes', -1)
                for music in playlist_dict:
                    file_path = music['file_path']
                    response += f',{file_path}'
                broadcastToAllClients(response)
            else:
                response = 'File not found'
            conn.send(response.encode('utf-8'))
        elif action == 'votesong':
            file_path = p[1]
            username = p[2]

            if not votedSongCollection.find_one({'file_path': file_path,'username': username}):
                playlistCollection.update_one({'file_path': file_path}, {'$inc': {'votes': 1}})
                votedSongCollection.insert_one({'file_path': file_path, 'username': username})
                response ='Song voted successfully'
            else:
                response = 'Song already voted'
                conn.send(response.encode('utf-8'))

            playlist_dict = playlistCollection.find({}, {'_id': 0, 'file_path': 1}).sort('votes', -1)

            for music in playlist_dict:
                file_path = music['file_path']
                response += f',{file_path}'

            broadcastToAllClients(response)
            conn.send(response.encode('utf-8'))
        elif action == 'votestatus':
            file_path = p[1]
            username = p[2]

            if not votedSongCollection.find_one({'file_path': file_path, 'username': username}):
                response = 'You have not voted'
                conn.send(response.encode('utf-8'))
            else:
                response = 'You have voted'
                conn.send(response.encode('utf-8'))

            playlist_dict = playlistCollection.find({}, {'_id': 0, 'file_path': 1}).sort('votes', -1)

            for music in playlist_dict:
                file_path = music['file_path']
                response += f',{file_path}'

            broadcastToAllClients(response)
            conn.send(response.encode('utf-8'))
    conn.close()

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
