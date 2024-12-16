import socket
from tabnanny import check
from tkinter import filedialog
import pygame
from tkinter import *
import tkinter as tk
import threading
from mutagen.mp3 import MP3
import time
import tkinter.ttk as ttk
from tkinter.ttk import *
from PIL import Image,ImageTk
# Initialize pygame mixer
pygame.mixer.init()

# Define global variables
CLK_Sock = None
paused = False
stopped = False
Username = ''
currently_playing_song = None

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
    global Username
    Username = loginUsername.get()

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
    UsernameLabel.config(text=Username)
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

def voteSong():
    selected_song = songListBox.get(ACTIVE)
    if selected_song:
        data = f"votesong,{selected_song},{Username}"
        response = sendRequest(data)

        receive_updates(response)

def checkVoteStatus(event):
    selected_song = songListBox.get(ACTIVE)
    playSong()

    if selected_song:
        data = f"votestatus,{selected_song},{Username}"
        response = sendRequest(data)

        if 'You have voted' in response:
            voteButton.config(state=DISABLED)
        elif 'You have not voted' in response:
            voteButton.config(state=NORMAL)


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
    global stopped, paused
    stopped = False
    paused = False

    selected_song = songListBox.get(ACTIVE)
    if selected_song:
        pygame.mixer.music.load(selected_song)
        pygame.mixer.music.play()
        my_slider.config(value=0)  # Reset the slider to initial position
        play_time()

# Function to pause/resume the currently playing song
def pauseResumeSong():
    global paused
    if paused:
        pygame.mixer.music.unpause()
        pauseButton.config(image=pause_photo)
        paused = False
    else:
        pygame.mixer.music.pause()
        pauseButton.config(image=resume_photo)
        paused = True


def stopSong():
    global stopped, paused
    stopped = True
    pygame.mixer.music.stop()
    paused = False
    my_slider.set(0)  # Reset slider to initial position


# Function to scale (jump to) a specific time in the currently playing song
def scaleMusic(time_position):
    if pygame.mixer.music.get_busy() or paused:  # Also update the position when paused
        pygame.mixer.music.set_pos(time_position)

# Function to update the play time and slider
def play_time():
    if stopped:
        return
    current_time = pygame.mixer.music.get_pos() / 1000
    song = songListBox.get(ACTIVE)
    song_mut = MP3(song)
    song_length = song_mut.info.length
    current_time += 1
    if int(my_slider.get()) == int(song_length):
        pass
    elif paused:
        pass
    elif int(my_slider.get()) == int(current_time):
        slider_position = int(song_length)
        my_slider.config(to=slider_position, value=int(current_time))
    else:
        slider_position = int(song_length)
        my_slider.config(to=slider_position, value=int(my_slider.get()))
        next_time = int(my_slider.get()) + 1
        my_slider.config(value=next_time)
    my_slider.after(1000, play_time)

# Function to create the slider function
def slide(x):
    scaleMusic(int(my_slider.get()))  # Ensure the new position is set even when paused

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


def createMusicPlayerFrame(root, font):
    global songListBox, my_slider, voteButton, UsernameLabel, pauseButton , pause_photo, resume_photo

    frame = tk.Frame(root, bg='black')

    UsernameLabel = tk.Label(frame, text='', bg='black', fg='white', font=font)
    UsernameLabel.config(text=Username)
    UsernameLabel.place(x=0, y=0)

    songListLabel = tk.Label(frame, text='Song List:', bg='black', fg='white', font=font)
    songListLabel.pack(pady=5)

    songListBox = tk.Listbox(frame, font=font, width=50, height=20)
    songListBox.pack(pady=5)
    songListBox.bind('<Double-1>', checkVoteStatus)
    songListBox.bind('<Motion>', lambda event: event.widget.itemconfig(tk.ACTIVE))
    buttonFrame1 = tk.Frame(frame, bg='black')
    buttonFrame1.pack(pady=5)
    addSongButton = tk.Button(buttonFrame1, text='Add Song', bg='orange', fg='black', font=font, command=addSong)
    addSongButton.pack(side=LEFT, padx=5)
    deleteSongButton = tk.Button(buttonFrame1, text='Delete Song', bg='orange', fg='black', font=font, command=deleteSong)
    deleteSongButton.pack(side=LEFT, padx=5)

    buttonFrame2 = tk.Frame(frame, bg='black')
    buttonFrame2.pack(pady=5)

    # Load images
    play_img = Image.open("play.png").resize((50, 50), Image.Resampling.LANCZOS)
    play_photo = ImageTk.PhotoImage(play_img)

    pause_img = Image.open("pause.png").resize((50, 50), Image.Resampling.LANCZOS)
    pause_photo = ImageTk.PhotoImage(pause_img)

    resume_img = Image.open("resume.png").resize((50, 50), Image.Resampling.LANCZOS)
    resume_photo = ImageTk.PhotoImage(resume_img)

    stop_img = Image.open("stop.png").resize((50, 50), Image.Resampling.LANCZOS)
    stop_photo = ImageTk.PhotoImage(stop_img)

    # Create buttons with images
    playButton = tk.Button(buttonFrame2, image=play_photo, command=playSong, bd=0, bg='orange')
    playButton.image = play_photo  # Keep a reference to avoid garbage collection
    playButton.pack(side=LEFT, padx=5)

    pauseButton = tk.Button(buttonFrame2, image=pause_photo, command=pauseResumeSong, bd=0, bg='orange')
    pauseButton.image = pause_photo  # Keep a reference to avoid garbage collection
    pauseButton.pack(side=LEFT, padx=5)

    stopButton = tk.Button(buttonFrame2, image=stop_photo, command=stopSong, bd=0, bg='orange')
    stopButton.image = stop_photo  # Keep a reference to avoid garbage collection
    stopButton.pack(side=LEFT, padx=5)

    # Adding Scale Music slider
    scaleFrame = tk.Frame(frame, bg='black')
    scaleFrame.pack(pady=5)
    my_slider = ttk.Scale(scaleFrame, from_=0, to=100, orient=HORIZONTAL, value=0, command=slide, length=400)
    my_slider.pack(side=LEFT, padx=5)

    voteFrame = tk.Frame(frame, bg='black')
    voteFrame.pack(pady=5)
    voteButton = tk.Button(voteFrame, text='Vote', bg='orange', fg='black', font=font, command=voteSong)

    voteButton.config(state=DISABLED)
    voteButton.pack(side=LEFT, padx=5)

    return frame



# Create main application window
root = tk.Tk()
icon_image = Image.open("title.png")
icon_photo = ImageTk.PhotoImage(icon_image)
root.iconphoto(False, icon_photo)

root.title('Music Player')
root.geometry('700x600')
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
