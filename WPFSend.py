#!/usr/bin/python
# -*- coding: UTF-8 -*-
#=================================================================================
#        Name: WPFSend
#        Author:   wicker25 (http://hackerforum.devil.it/  -  wicker25@gmail.com)
#        Description: P2P Send File
#        Licence: GPL
#        Version: 0.1
#=================================================================================

import sys
import md5
import gtk, gobject
from socket import *
from thread import *
from stat import ST_SIZE
from os import path, stat
from time import sleep


try:
    from WPCrypt import *
except:
    print "Attenzion!!!"
    print "Per cifrare di dati in uscita è necessario il modulo Crypto."


gtk.gdk.threads_init()


class Fsend:
   
   
    def __init__(self, File, IP, Port, Mode, Algorithm, Key):
        #Impostazioni Generali
        self.File = File
        self.IP = IP
        self.Port = int(Port)
        self.Mode = Mode
        self.Key = Key
        self.Algorithm = Algorithm
        #Costruzione Finestra
        self.SDialog = gtk.Window()
        self.SDialog.set_title("Attendere..")
        self.SDialog.set_resizable(0)
        self.SDialog.connect("delete_event", gtk.main_quit)
        self.STable = gtk.Table(10,10,False)
        self.SDialog.add(self.STable)
        #Progressbar
        self.ProgresBar = gtk.ProgressBar()
        self.ProgresBar.set_size_request(200, 20)
        self.ProgresBar.set_orientation(0)
        self.ProgresBar.set_fraction(0)
        self.ProgresBar.set_text("In Attesa..")
        self.STable.attach(self.ProgresBar, 2, 8, 4, 5, xpadding=6, ypadding=8)
        self.InfoSend = gtk.Label("In attesa..")
        self.InfoSend.set_justify(gtk.JUSTIFY_CENTER)
        self.STable.attach(self.InfoSend, 2, 8, 6, 7, xpadding=6, ypadding=8)
        self.SDialog.show_all()


    def start(self):
        if self.Mode == "SEND": 
            self.server()
            start_new_thread(self.send_file, ())
           
        if self.Mode == "RECV": 
            self.client()
            start_new_thread(self.recev_file, ())


    def client(self):
        #Client
        self.connection_sfile = socket(AF_INET, SOCK_STREAM)
        self.connection_sfile.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.connection_sfile.connect((self.IP, self.Port))
        self.InfoSend.set_text("Connesso...")
        #Dati
        string = self.connection_sfile.recv(1024)
        string = string.split(":::")
        self.path_file = string[0]
        self.total_size = string[1]
        self.hashrecv = string[2]


    def server(self):
        #Server
        demon = socket(AF_INET, SOCK_STREAM)
        demon.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #demon.setdefaulttimeout(30.0)
        demon.bind(("0.0.0.0", self.Port))
        demon.listen(5)
        try:
            (self.connection_sfile, self.address) = demon.accept()
            self.InfoSend.set_text("Connesso...")
            #Dati
            self.name_file = path.split(self.File)[1]
            self.total_size = stat(self.File)[ST_SIZE]
            self.gdhash = self.generateMD5(self.File)
            self.connection_sfile.send(self.name_file+":::"+str(self.total_size)+":::"+self.gdhash)
        except:
            gtk.main_quit()


    def send_file(self):
        self.SDialog.set_title("WPFSend - Invio File")
        try:
            send_size = 0
            file = open(self.File,'rb')
            while 1:
                gtk.gdk.threads_enter()
                self.InfoSend.set_text("Inviati "+str(send_size/1024)+"/"+str(int(self.total_size)/1024)+" kb")
                gtk.gdk.threads_leave()
                data = file.read(1024)
                if self.Algorithm != "None":
                    data = DataEncrypt(self.Key, data, self.Algorithm)
                if not data: break
                self.connection_sfile.sendall(data)
                send_size += len(data)
                #Progressbar
                self.redrawbar(send_size, self.total_size)
            file.close()
            self.connection_sfile.close()
            self.InfoSend.set_text("Completato.")
        except:
            self.InfoSend.set_text("Interrotto!")


    def recev_file(self):
        #Funzione di ricezione File
        self.SDialog.set_title("WPFSend - Ricezione file")
        try:
            recved_size = 0
            file = open(self.path_file,'wb')
            while 1:
                gtk.gdk.threads_enter()
                self.InfoSend.set_text("Ricostruiti: "+str(recved_size/1024)+"/"+str(int(self.total_size)/1024)+" kb")
                gtk.gdk.threads_leave()
                data = self.connection_sfile.recv(1024)
                if self.Algorithm != "None":
                    data = DataEncrypt(self.Key, data, self.Algorithm)
                if not data: break
                file.write(data)
                recved_size += len(data)
                #Progressbar
                self.redrawbar(recved_size, self.total_size)
            file.close()
            self.connection_sfile.close()
            self.newhash = self.generateMD5(self.path_file)
            if self.newhash != self.hashrecv:
                self.InfoSend.set_text("Verifica MD5 fallita!")
            else:
                self.InfoSend.set_text("Completato.")
        except:
            self.InfoSend.set_text("Interrotto!")



    def redrawbar(self, progress, total):
        #Aggiorna la ProgressBar
        perc = float((progress * 100.0) / int(total))
        if perc != self.ProgresBar.get_text():
            gtk.gdk.threads_enter()
            self.ProgresBar.set_text(str(int(perc))+"%")
            self.ProgresBar.set_fraction(perc/100.0)
            gtk.gdk.threads_leave()


    def generateMD5(self, pathfile):
        #Genera un hash univoco per il file
        file = open(pathfile, "rb")
        date = file.read()
        gdMD5 = md5.new(date).hexdigest()
        file.close()
        return gdMD5


if len(sys.argv) < 7: 
    print "Errore: Sintassi non corretta."
    sys.exit()


print "WPFSend: Start Esecution"
ServerFile = Fsend(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
ServerFile.start()
gtk.gdk.threads_enter()
gtk.main()
gtk.gdk.threads_leave()
print "WPFSend: End Esecution"

