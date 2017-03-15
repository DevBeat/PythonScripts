import imaplib
import smtplib
import re
import os
import dropbox
import time
from os import listdir
from os.path import isfile, join
from email.mime.text import MIMEText
server = 'smtp.gmail.com'
user = 'username@gmail.com'
password = 'password'
number = 'number@smsgateway.com'
session = smtplib.SMTP(server,587)
session.ehlo()
session.starttls()
session.ehlo
session.login(user, password)
client = dropbox.client.DropboxClient('your key here')
data = ""
last = ""
location = ""
def aliasUpdater():
    if not os.path.isfile("alias.txt"):
        return "n/a"
    else:
        with open("alias.txt", "r") as f:
            return f.read().split("\n")
        f.close()
def aliasWriter(z):
    with open("alias.txt", "a") as f:
        f.write(z+"\n")
    f.close()
def aliasReturner(z):
    alias = aliasUpdater()
    for a in alias:
        if a.split("=")[0]==z:
            return a.split("=")[1]
def receptionUpdater(): #reads old data (last) from file
    if not os.path.isfile("previous.txt"):
        return "n/a"
    else:
        with open("previous.txt", "r") as f:
            return f.read()
        f.close()
def writer(last): #writes new data to file
    with open("previous.txt", "w") as f:
        f.truncate()
        f.write(last)
    f.close()
def fitnessTracker(last, data): #compares data
    if data == last:
        return False
    else:
        return True
def sendEmail(receiver, message):
    mseg = message
    recipient = [receiver]
    session.sendmail(user, recipient, mseg)
def receiveEmails(last): #reads new data from email server
    mail = imaplib.IMAP4_SSL('imap.gmail.com',993)
    mail.login(user, password)
    mail.list()
    mail.select("inbox")
    result, data = mail.search(None, "ALL")
    ids = data[0]
    id_list = ids.split()
    latest_email_id = id_list[-1]
    result, data = mail.fetch(latest_email_id, "(RFC822)") 
    try:
        raw_email = data[0][1].decode('utf-8')
        indexOf = raw_email.find("Content-Location:")
        message = raw_email[indexOf+32:-51]
        writer(message)
        return message
    except UnicodeEncodeError:
        return last
def commandHandler(command):
    global location
    split = command.split(" ")
    if split[0] == ".help":
        sendEmail(number, 'Welcome to Devbot!\nv.01- 4 commands available')
    elif split[0] ==".send":
        try:
            sendEmail(number, 'Attempting to send \''+split[2]+'\' to '+split[1])
            try:
                sendEmail(split[1], split[2])
            except:
                pass
        except:
            sendEmail(number,'Invalid syntax')
            pass
    elif split[0] == ".search":
        newS = command.split(" ",1)
        try:
            location = newS[1]+"/"
            string = ""
            for i in os.listdir(newS[1]):
                string = string + i + "\n"
            sendEmail(number,string.encode(encoding='utf_8', errors='strict'))
        except Exception as e:
            sendEmail(number,'Invalid syntax')
            pass
    elif split[0] == ".upload":
        newS = command.split(" ",1)
        try:
            if(newS[1][:2]=="C:/"):
                with open(newS[1], "rb") as f:
                    again = newS[1].split("/")
                    name = again[-1]
                    response = client.put_file('DevBot/'+name,f)
                    sendEmail(number,"Uploaded")
            else:
                with open(location+newS[1], "rb") as f:
                    again = newS[1].split("/")
                    name = again[-1]
                    response = client.put_file('DevBot/'+name,f)
                    sendEmail(number,"Uploaded")        
        except Exception as e:
                pass
    elif split[0] == ".alias":
        newS = command.split(" ",2)
        try:
            aliasWriter(newS[1]+'='+newS[2])
            sendEmail(number,'Alias Written')
        except:
            sendEmail(number,'Invalid syntax')
            pass
    elif split[0] == ".use":
        newS = command.split(" ",2)
        try:
            commandHandler(aliasReturner(newS[1])+newS[2])
        except:
            try:
                commandHandler(aliasReturner(newS[1]))
            except:
                pass
            pass
last = receptionUpdater()
data = receiveEmails(last)
while True:
    data = receiveEmails(last)
    if fitnessTracker(last,data):
        commandHandler(data)
    last = receptionUpdater()
    print(location)
    time.sleep(5)
