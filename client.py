import socket
import pygame
from tkinter import *
import tkinter as tk
import threading

def login(loginUsername, loginPassword, loginMessageLabel):
    data = f"login,{loginUsername.get()},{loginPassword.get()}"
    response = sendRequest(data)
    loginMessageLabel.config(text=response, fg="green" if "successfully" in response else "red")
    if "successfully" in response:
        showMusicPlayerFrame()
        loginMessageLabel.config(text="", fg="green" if "successfully" in response else "red")

    loginUsername.delete(0, "end")
    loginPassword.delete(0, "end")


def signup(signupUsername, signupPassword, signupMessageLabel):
    data = f"signup,{signupUsername.get()},{signupPassword.get()}"
    response = sendRequest(data)
    signupMessageLabel.config(text=response, fg="green" if "successfully" in response else "red")
    signupUsername.delete(0, "end")
    signupPassword.delete(0, "end")


def sendRequest(data):
    CLK_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    CLK_Sock.connect(('127.0.0.1', 12345))
    CLK_Sock.send(data.encode('utf-8'))
    response = CLK_Sock.recv(1024).decode('utf-8')
    CLK_Sock.close()
    return response

def ShowSignupFrame():

    loginFrame.pack_forget()
    musicPlayerFrame.pack_forget()
    signupFrame.pack()

def ShowLoginFrame():
    musicPlayerFrame.pack_forget()
    signupFrame.pack_forget()
    loginFrame.pack()

def showMusicPlayerFrame():
    loginFrame.pack_forget()
    musicPlayerFrame.pack()

def addSong():
    pass

def deleteSong():
    pass

def playSong():
    pass

def pauseSong():
    pass

def stopSong():
    pass

def createMusicPlayerPage():
    global musicPlayerFrame, songListBox
    musicPlayerFrame = tk.Frame(root, bg='black')

    tk.Button(musicPlayerFrame, text='Back to login', bg='orange', fg='black', font=my_font, command=ShowLoginFrame).pack(pady=5)

    songListLabel = tk.Label(musicPlayerFrame, text='Song List:', bg='black', fg='white', font=my_font)
    songListLabel.pack(pady=5)

    songListBox = tk.Listbox(musicPlayerFrame, font=my_font)
    songListBox.pack(pady=5)

    buttonFrame1 = tk.Frame(musicPlayerFrame, bg='black')
    buttonFrame1.pack(pady=5)

    tk.Button(buttonFrame1, text='Add Song', bg='orange', fg='black', font=my_font, command=addSong).pack(side=LEFT, padx=5)
    tk.Button(buttonFrame1, text='Delete Song', bg='orange', fg='black', font=my_font, command=deleteSong).pack(side=LEFT, padx=5)

    buttonFrame2 = tk.Frame(musicPlayerFrame, bg='black')
    buttonFrame2.pack(pady=5)

    tk.Button(buttonFrame2, text='Play', bg='orange', fg='black', font=my_font, command=playSong).pack(side=LEFT, padx=5)
    tk.Button(buttonFrame2, text='Pause/Resume', bg='orange', fg='black', font=my_font, command=pauseSong).pack(side=LEFT, padx=5)
    tk.Button(buttonFrame2, text='Stop', bg='orange', fg='black', font=my_font, command=stopSong).pack(side=LEFT, padx=5)

def createLoginAndSignupPage():
    global root, loginFrame, signupFrame, loginUsernameEntry, loginPasswordEntry, signupUsernameEntry, signupPasswordEntry, my_font
    root = tk.Tk()
    root.title('Music Player')
    root.geometry('500x500')
    my_font = ('SimSun', 12)

    root.resizable(False, False)
    root.config(bg='black')

    loginFrame = tk.Frame(root, bg='black')
    signupFrame = tk.Frame(root, bg='black')

    # Login Frame
    loginUsernameLabel = tk.Label(loginFrame, text='Username:', bg='black', fg='white', font=my_font)
    loginUsernameLabel.pack(pady=5)

    loginUsernameEntry = tk.Entry(loginFrame, font=my_font)
    loginUsernameEntry.pack(pady=5)

    loginPasswordLabel = tk.Label(loginFrame, text='Password:', bg='black', fg='white', font=my_font)
    loginPasswordLabel.pack(pady=5)

    loginPasswordEntry = tk.Entry(loginFrame, font=my_font, show='*')
    loginPasswordEntry.pack(pady=5)

    loginMessage = tk.Label(loginFrame, bg='black', fg='white', font=my_font)
    loginMessage.pack(pady=5)

    tk.Button(loginFrame, text='Login', bg='orange', fg='black', font=my_font, command=lambda: login(loginUsernameEntry, loginPasswordEntry, loginMessage)).pack(pady=5)
    tk.Label(loginFrame, text='If you don\'t have an account, signup', bg='black', fg='white', font=my_font).pack(pady=5)
    tk.Button(loginFrame, text='Signup', bg='orange', fg='black',font=my_font, command=ShowSignupFrame).pack(pady=5)

    # Signup Frame
    SignupUsernameLabel = tk.Label(signupFrame, text='Username:', bg='black', fg='white', font=my_font)
    SignupUsernameLabel.pack(pady=5)

    SignupUsernameEntry = tk.Entry(signupFrame, font=my_font)
    SignupUsernameEntry.pack(pady=5)

    SignupPasswordLabel = tk.Label(signupFrame, text='Password:', bg='black', fg='white', font=my_font)
    SignupPasswordLabel.pack(pady=5)

    SignupPasswordEntry = tk.Entry(signupFrame, font=my_font, show='*')
    SignupPasswordEntry.pack(pady=5)

    SignupMessage = tk.Label(signupFrame, bg='black', fg='white', font=my_font)
    SignupMessage.pack(pady=5)

    tk.Button(signupFrame, text='Signup', bg='orange', fg='black', font=my_font, command=lambda: signup(SignupUsernameEntry, SignupPasswordEntry, SignupMessage)).pack(pady=5)
    tk.Button(signupFrame, text='Back to login', bg='orange', fg='black', font=my_font, command=ShowLoginFrame).pack(pady=5)

    loginFrame.pack()
    createMusicPlayerPage()
    root.mainloop()

if __name__ == '__main__':
    createLoginAndSignupPage()
