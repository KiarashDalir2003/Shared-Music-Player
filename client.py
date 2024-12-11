import socket
from tkinter import filedialog
import pygame
from tkinter import *
import tkinter as tk
import threading

# Initialize pygame mixer
pygame.mixer.init()

# Define global socket variable
CLK_Sock = None

# Function to connect to the server socket
def connect_socket():
    global CLK_Sock
    if CLK_Sock is None:
        CLK_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CLK_Sock.connect(('127.0.0.1', 12345))

# Function to close the server socket
def close_socket():
    global CLK_Sock
    if CLK_Sock is not None:
        CLK_Sock.close()
        CLK_Sock = None

# Function to handle login
def login(loginUsername, loginPassword, loginMessageLabel):
    connect_socket()
    data = f"login,{loginUsername.get()},{loginPassword.get()}"
    CLK_Sock.send(data.encode('utf-8'))
    response = CLK_Sock.recv(1024).decode('utf-8')
    loginMessageLabel.config(text=response.split(',')[0], fg="green" if "successfully" in response else "red")
    if "successfully" in response:
        showMusicPlayerFrame()
        receive_updates(response)
        threading.Thread(target=listenForUpdates, daemon=True).start()
    loginUsername.delete(0, "end")
    loginPassword.delete(0, "end")

# Function to handle signup
def signup(signupUsername, signupPassword, signupMessageLabel):
    data = f"signup,{signupUsername.get()},{signupPassword.get()}"
    response = sendRequest(data)
    signupMessageLabel.config(text=response, fg="green" if "successfully" in response else "red")
    signupUsername.delete(0, "end")
    signupPassword.delete(0, "end")

# Function to send request to the server
def sendRequest(data):
    connect_socket()
    CLK_Sock.send(data.encode('utf-8'))
    response = CLK_Sock.recv(1024).decode('utf-8')
    return response

# Function to show signup frame
def ShowSignupFrame():
    loginFrame.pack_forget()
    musicPlayerFrame.pack_forget()
    signupFrame.pack()

# Function to show login frame
def ShowLoginFrame():
    pygame.mixer.music.stop()
    musicPlayerFrame.pack_forget()
    signupFrame.pack_forget()
    loginFrame.pack()

# Function to show music player frame
def showMusicPlayerFrame():
    loginFrame.pack_forget()
    musicPlayerFrame.pack()

# Function to add song to the playlist
def addSong():
    file_path = filedialog.askopenfilename(filetypes=[("Music Player", "*.mp3")])
    if file_path:
        data = f"addsong,{file_path}"
        response = sendRequest(data)
        receive_updates(response)

# Function to delete song from the playlist
def deleteSong():
    selected_song = songListBox.get(ACTIVE)
    if selected_song:
        data = f"deletesong,{selected_song}"
        response = sendRequest(data)
        receive_updates(response)

# Function to receive updates from the server and update playlist
def receive_updates(playlist):
    items = playlist.split(",")[1:]  # Skip the action part
    songListBox.delete(0, END)
    for item in items:
        songListBox.insert(END, item)

# Function to listen for updates from the server
def listenForUpdates():
    global CLK_Sock
    while True:
        try:
            response = CLK_Sock.recv(1024).decode('utf-8')
            receive_updates(response)
        except OSError:
            break

# Function to close socket and application on window close
def on_closing():
    close_socket()
    root.destroy()

# Function to play the selected song
def playSong():
    selected_song = songListBox.get(ACTIVE)
    if selected_song:
        pygame.mixer.music.load(selected_song)
        pygame.mixer.music.play()

# Function to pause/resume the currently playing song
def pauseResumeSong():
    if pygame.mixer.music.get_busy():
        if pygame.mixer.music.get_pos() > 0:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

# Function to stop the currently playing song
def stopSong():
    pygame.mixer.music.stop()

# Function to create the login frame
def createLoginFrame(root, font):
    frame = tk.Frame(root, bg='black')
    loginUsernameLabel = tk.Label(frame, text='Username:', bg='black', fg='white', font=font)
    loginUsernameLabel.pack(pady=5)
    loginUsernameEntry = tk.Entry(frame, font=font)
    loginUsernameEntry.pack(pady=5)
    loginPasswordLabel = tk.Label(frame, text='Password:', bg='black', fg='white', font=font)
    loginPasswordLabel.pack(pady=5)
    loginPasswordEntry = tk.Entry(frame, font=font, show='*')
    loginPasswordEntry.pack(pady=5)
    loginMessage = tk.Label(frame, bg='black', fg='white', font=font)
    loginMessage.pack(pady=5)
    loginButton = tk.Button(frame, text='Login', bg='orange', fg='black', font=font,
                            command=lambda: login(loginUsernameEntry, loginPasswordEntry, loginMessage))
    loginButton.pack(pady=5)
    signupPrompt = tk.Label(frame, text='If you don\'t have an account, signup', bg='black', fg='white', font=font)
    signupPrompt.pack(pady=5)
    signupButton = tk.Button(frame, text='Signup', bg='orange', fg='black', font=font, command=ShowSignupFrame)
    signupButton.pack(pady=5)
    return frame

# Function to create the signup frame
def createSignupFrame(root, font):
    frame = tk.Frame(root, bg='black')
    SignupUsernameLabel = tk.Label(frame, text='Username:', bg='black', fg='white', font=font)
    SignupUsernameLabel.pack(pady=5)
    SignupUsernameEntry = tk.Entry(frame, font=font)
    SignupUsernameEntry.pack(pady=5)
    SignupPasswordLabel = tk.Label(frame, text='Password:', bg='black', fg='white', font=font)
    SignupPasswordLabel.pack(pady=5)
    SignupPasswordEntry = tk.Entry(frame, font=font, show='*')
    SignupPasswordEntry.pack(pady=5)
    SignupMessage = tk.Label(frame, bg='black', fg='white', font=font)
    SignupMessage.pack(pady=5)
    signupSubmitButton = tk.Button(frame, text='Signup', bg='orange', fg='black', font=font,
                                   command=lambda: signup(SignupUsernameEntry, SignupPasswordEntry, SignupMessage))
    signupSubmitButton.pack(pady=5)
    backToLoginButton = tk.Button(frame, text='Back to login', bg='orange', fg='black', font=font, command=ShowLoginFrame)
    backToLoginButton.pack(pady=5)
    return frame

# Function to create the music player frame
def createMusicPlayerFrame(root, font):
    global songListBox
    frame = tk.Frame(root, bg='black')
    backToLoginButtonFromMusicPlayer = tk.Button(frame, text='Back to login', bg='orange', fg='black', font=font, command=ShowLoginFrame)
    backToLoginButtonFromMusicPlayer.pack(pady=5)
    songListLabel = tk.Label(frame, text='Song List:', bg='black', fg='white', font=font)
    songListLabel.pack(pady=5)
    songListBox = tk.Listbox(frame, font=font)
    songListBox.pack(pady=5)
    buttonFrame1 = tk.Frame(frame, bg='black')
    buttonFrame1.pack(pady=5)
    addSongButton = tk.Button(buttonFrame1, text='Add Song', bg='orange', fg='black', font=font, command=addSong)
    addSongButton.pack(side=LEFT, padx=5)
    deleteSongButton = tk.Button(buttonFrame1, text='Delete Song', bg='orange', fg='black', font=font, command=deleteSong)
    deleteSongButton.pack(side=LEFT, padx=5)
    buttonFrame2 = tk.Frame(frame, bg='black')
    buttonFrame2.pack(pady=5)
    playButton = tk.Button(buttonFrame2, text='Play', bg='orange', fg='black', font=font, command=playSong)
    playButton.pack(side=LEFT, padx=5)
    pauseButton = tk.Button(buttonFrame2, text='Pause/Resume', bg='orange', fg='black', font=font, command=pauseResumeSong)
    pauseButton.pack(side=LEFT, padx=5)
    stopButton = tk.Button(buttonFrame2, text='Stop', bg='orange', fg='black', font=font, command=stopSong)
    stopButton.pack(side=LEFT, padx=5)
    return frame

# Create main application window
root = tk.Tk()
root.title('Music Player')
root.geometry('500x500')
root.resizable(False, False)
root.config(bg='black')
root.protocol("WM_DELETE_WINDOW", on_closing)

# Define font
my_font = ('SimSun', 12)

# Create and pack frames
loginFrame = createLoginFrame(root, my_font)
signupFrame = createSignupFrame(root, my_font)
musicPlayerFrame = createMusicPlayerFrame(root, my_font)

# Show login frame by default
loginFrame.pack()

# Start the Tkinter main loop
root.mainloop()
