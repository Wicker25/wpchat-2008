#!/usr/bin/python
# -*- coding: UTF-8 -*-
#=================================================================================
#        Name: WPCHAT
#        Author:   wicker25 (http://hackerforum.devil.it/  -  wicker25@gmail.com)
#        Description: Chat P2P
#        Licence: GPL
#        Version: 0.1
#=================================================================================


import webbrowser
import sys
import gtk, gobject
from socket import *
from thread import *
from urllib import URLopener
from time import localtime
from os import path, spawnv, execv, getcwd, P_NOWAIT
from time import sleep


GLOBALPATH = path.dirname(sys.argv[0])
if len(sys.argv)>1:
    if sys.argv[1][:7].upper() == "--PATH=":
        GLOBALPATH = sys.argv[1][7:].replace("'","").replace('"',"")
sys.path.append(GLOBALPATH)
sys.path.append(sys.argv[0])

#Moduli ausiliari
import WPTag
import WPConfig
import WPGui

try:
    from WPCrypt import *
except:
    print "Attenzion!!!"
    print "Per cifrare di dati in uscita è necessario il modulo Crypto."


gtk.gdk.threads_init()


class Application:


    def __init__(self,Main):

        self.TerminateSettings = False

        #Impostazioni generali del programma
        self.title = "Siesta!"
        self.version = "0.3"
        self.description = "A OpenSource P2P Chat"
        self.author = "Wicker25"
        self.site = "http://wicker25.netsons.org/"
        global GLOBALPATH
        self.GLOBALPATH = GLOBALPATH
        gtk.about_dialog_set_url_hook(lambda x,y,z: start_new_thread(webbrowser.open,(self.site,)), None)
        #impostazioni principali
        self.Main = Main
        self.icon = gtk.gdk.pixbuf_new_from_file(path.join(self.GLOBALPATH, "icon.ico"))
        self.Main.set_icon(self.icon)
        self.port = 6600
        self.port_sfile = 6605
        self.loop = 0
        self.connect_to_ip = "0.0.0.0"
        self.LastSend = 0
        self.ConsecutiveSend = 0
        self.Waiting = 0
        self.AntiFloodActiv = True
        self.WNotifier = WPGui.Notifier("Nuovo Messaggio!")
        self.DlgContacts = None
        self.WaitingContacts = 0
        #self.Main.connect("set_focus", lambda x, y: self.WNotifier.Hide())
        #Impostazioni dal file Config
        Data = WPConfig.ReadNewConf(self.GLOBALPATH)
        self.Name = Data[0]
        self.ByteRate = int(Data[1])
        self.ConRate = int(Data[2])
        self.SecRate = int(Data[3])
        self.Key = Data[4]
        self.Algorithm = Data[5]
        self.MaxChar = int(Data[6])
        self.AntiFlood = Data[7].split("x")
        self.WAlert = int(Data[8])
        self.AServer = Data[9]
        self.AServerNick = Data[10]
        self.AServerPwd = Data[11]
        #Creazione Frame Principale
        self.Main.set_title(self.title)
        self.MainTable = gtk.Table(40,40,False)
        self.Main.add(self.MainTable)
        self.Main.set_default_size(400,300)
        #Barra degli strumenti------------------------------------------------

        self.MenuItems = (
#----------------MenuBar------------------------------------
( "/_File",                  None,          None,                 0, "<Branch>" ),
( "/File/Connetti..",       "<control>1",   self.connect_client,  0, "<StockItem>", gtk.STOCK_CONNECT ),
( "/File/Fai da Server",     "<control>2",  self.connect_server,  0, "<StockItem>", gtk.STOCK_NETWORK ),
( "/File/sep1",              None,          None,                 0, "<Separator>" ),
( "/File/Disconnetti",       "<control>T",  self.stop_connection, 0, "<StockItem>", gtk.STOCK_DISCONNECT ),
( "/File/sep2",              None,          None,                 0, "<Separator>" ),
( "/File/Esci",              "<control>Q",  gtk.main_quit,        0, "<StockItem>", gtk.STOCK_QUIT ),
( "/_Azioni",                None,          None,                 0, "<Branch>" ),
( "/Azioni/Invia File..",    "<control>S",  self.init_send_file,  0, "<StockItem>", gtk.STOCK_FLOPPY ),
( "/Azioni/Smiles..",        "<control>E",  self.DialogSmiles,    0, "<StockItem>", gtk.STOCK_ADD ),
( "/Azioni/Pulisci Chat",    "<control>L",  self.clean_chat,      0, "<StockItem>", gtk.STOCK_CLEAR ),
( "/_Strumenti",             None,          None,                 0, "<Branch>" ),
( "/Strumenti/Avvisi",       "<control>A",  self.SetWAlert,        0, "<ToggleItem>" ),
( "/Strumenti/_AntiFlood",   None,          None,                 0, "<Branch>" ),
( "/Strumenti/AntiFlood/Abilita",    "<control>F",  self.SetAntiFlood,    0, "<ToggleItem>" ),
( "/Strumenti/AntiFlood/Configura",    "<control>D",  self.DlgAntiFlood,    0, "<StockItem>", gtk.STOCK_PROPERTIES ),
( "/Strumenti/Contatti",     "<control>C",  self.contacts,      0, "<StockItem>", gtk.STOCK_ADD ),
( "/Strumenti/Sicurezza",    "<control>P",  self.DlgSecure,       0, "<StockItem>", gtk.STOCK_DIALOG_AUTHENTICATION),
( "/Strumenti/AServer",      "<control>k",  self.DlgAServer,       0, "<StockItem>", gtk.STOCK_NETWORK),
( "/Strumenti/Impostazioni", "<control>I",  self.DlgSettings,     0, "<StockItem>", gtk.STOCK_PREFERENCES ),
( "/_Aiuto",                 None,          None,                 0, "<LastBranch>" ),
( "/Aiuto/About..",          None,          self.info,            0, "<StockItem>", gtk.STOCK_ABOUT ),
#------------------------------------------------------------
)
        Accel = gtk.AccelGroup()
        self.ItemsFactory = gtk.ItemFactory(gtk.MenuBar, "<main>", Accel)
        self.ItemsFactory.create_items(self.MenuItems)
        self.Main.add_accel_group(Accel)
        self.MenuBar = self.ItemsFactory.get_widget("<main>")
        self.MainTable.attach(self.MenuBar, 1, 40, 1, 2)
        self.ItemsFactory.get_widget("/Strumenti/AntiFlood/Abilita").set_active(True)
        if self.WAlert: 
            self.ItemsFactory.get_widget("/Strumenti/Avvisi").set_active(True)
        else:
            self.ItemsFactory.get_widget("/Strumenti/Avvisi").set_active(False)
        #Stato------------------------------------------------
        self.label = gtk.Label("Non connesso!")
        self.label.set_justify(gtk.JUSTIFY_CENTER)
        self.MainTable.attach(self.label, 1, 40, 3, 4)
        #Pannello
        self.WinScroller = gtk.ScrolledWindow(None, None)
        self.WinScroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.WinScroller.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.MainTable.attach(self.WinScroller, 1, 40, 4, 39)
        self.TextChatView = gtk.TextView()
        self.TextChatView.set_editable(False)
        self.TextChatView.set_cursor_visible(False)
        self.TextChatView.set_pixels_above_lines(3)
        self.TextChatView.set_wrap_mode(gtk.WRAP_WORD)
        self.BufferTextChat = gtk.TextBuffer()
        self.TextChatView.set_buffer(self.BufferTextChat)
        self.WinScroller.add(self.TextChatView)
        #Barra + Pulsante "Invia"------------------------------------------------
        self.Text = gtk.Entry(self.MaxChar)
        self.MainTable.attach(self.Text, 1, 39, 39, 40, gtk.FILL, gtk.FILL)
        self.SendButton = gtk.Button("Invia")
        self.SendButton.connect("clicked", self.send)
        self.Main.connect("key_press_event", self.rapid_click)
        self.MainTable.attach(self.SendButton, 39, 40, 39, 40, gtk.FILL, gtk.FILL)
        #Creazione Tag Personalizzati------------------------------------------------
        for t in range(0,len(WPTag.TagListColor)):
            self.BufferTextChat.create_tag(WPTag.TagListColor[t][0], foreground=WPTag.TagListColor[t][1])
        #Messaggio di Benvenuto
        local_time=localtime()
        clock = "["+str(local_time[3])+":"+str(local_time[4])+":"+str(local_time[5])+"]"
        self.newmessage(clock+"  **Aperta WPChat**\n", "color_red")

        self.TerminateSettings = True


    def connect_client(self, event, widget):
        #Impostazioni per la connessione da Client
        self.loop = 0
        self.label.set_text("In attesa di un collegamento..")
        CDialog = gtk.Dialog("Connessione", window, 0,
            (gtk.STOCK_OK, gtk.RESPONSE_OK,
            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        CDialog.set_resizable(0)
        CTable = gtk.Table(10,20,False)
        CDialog.vbox.pack_start(CTable, False, False, 0)
        CTable.attach(gtk.Label("Inserisci l'Ip della chat alla quale vuoi connetterti:"), 1, 10, 3, 8, xpadding=15, ypadding=5)
        CEntry = gtk.Entry(15)
        CTable.attach(CEntry, 1, 10, 8, 16, xpadding=15, ypadding=10)
        CDialog.show_all()
        Resp = CDialog.run()
        if Resp == gtk.RESPONSE_OK:
           StrIns = CEntry.get_text()
           if StrIns != "" and len(StrIns.split(".")) == 4:
               start_new_thread(self.client, (StrIns,))
           else:
               EDialog = gtk.MessageDialog(CDialog, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Il formato dell'indirizzo IP non vè valido!")
               EDialog.run()
               EDialog.destroy()
               self.label.set_text("Non connesso!")
           CDialog.destroy()
        else:
           self.label.set_text("Non connesso!")
           CDialog.destroy()


    def client(self, host):
        #Connessione Client
        tent=1
        while tent<=self.ConRate:
            gtk.gdk.threads_enter()
            self.label.set_text("Tentativo numero "+str(tent)+" in corso..")
            gtk.gdk.threads_leave()
            sleep(self.SecRate)
            try:
                self.connection = socket(AF_INET, SOCK_STREAM)
                self.connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                self.connection.connect((host, self.port))
                self.label.set_text("Connesso all'ip '"+host+"'")
                self.connect_to_ip = host
                if self.DlgContacts != None: 
                    self.DlgContacts.destroy()
                    self.DlgContacts = None
                start_new_thread(self.recev, ())
                break
            except:
                if tent == self.ConRate: self.label.set_text("Impossibile connettersi!")
            tent+=1


    def connect_server(self, event, widget):
        #Impostazioni per la connessione da Server
        self.loop = 0
        start_new_thread(self.server, ())
        self.Online = 1
        start_new_thread(self.SaveDataToServer, ())


    def server(self):
        #Connessione Server
        try:
            gtk.gdk.threads_enter()
            self.label.set_text("In attesa di un collegamento..")
            gtk.gdk.threads_leave() 
            demon = socket(AF_INET, SOCK_STREAM)
            demon.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            demon.bind(("0.0.0.0", self.port))
            demon.listen(5)
            (self.connection, self.address) = demon.accept()
            self.label.set_text("Connesso all'ip '"+str(self.address[0])+"'")
            self.connect_to_ip = self.address[0]
            start_new_thread(self.recev, ())
        except:
            self.label.set_text("Impossibile Connettersi!")
        self.Online = 1


    def newmessage(self, Text, Tag):
        try:
            Text = unicode(Text)
            Text = Text.replace(" ","/5$4$6/ /5$4$6/")
            Text = Text.replace("\n","/5$4$6/\n/5$4$6/")
            Text = Text.split("/5$4$6/")
            for SubText in Text:
                iterend = self.BufferTextChat.get_end_iter()
                for Smile in WPTag.SmilesList:
                    if SubText == Smile[0]:
                        #pixbuf = gtk.gdk.pixbuf_new_from_file(path.join(self.GLOBALPATH, "Smiles", Smile[1]))
                        img = gtk.Image()
                        img.set_from_file(path.join(self.GLOBALPATH, "Smiles", Smile[1]))
                        img.show()
                        #self.BufferTextChat.insert_pixbuf(iterend, pixbuf)
                        anchor = self.BufferTextChat.create_child_anchor(iterend)
                        self.TextChatView.add_child_at_anchor(img, anchor)
                        SubText = ""
                if SubText == "": continue
                if Tag != None:
                    self.BufferTextChat.insert_with_tags_by_name(iterend, SubText, Tag)
                else:
                    self.BufferTextChat.insert(iterend, SubText)
        except:
            iterend = self.BufferTextChat.get_end_iter()
            self.BufferTextChat.insert_with_tags_by_name(iterend, "<<Cifratura Errata!>>\n", "color_red")
        #self.TextChatView.scroll_to_mark(self.BufferTextChat.get_insert(), 0.1)
        End = self.BufferTextChat.get_end_iter()
        self.TextChatView.scroll_to_mark(self.BufferTextChat.create_mark("scroll_end", End, True), 0.1)
            

    def send(self, event):
        #Funzione d'invio
        text = self.Text.get_text()
        if text!="": 
            local_time = localtime()
            clock = "["+str(local_time[3])+":"+str(local_time[4])+":"+str(local_time[5])+"]"
            try:
                data = clock+" "+self.Name+": "+text
                if self.Algorithm != "None":
                    data = DataEncrypt(self.Key, data, self.Algorithm)
                self.connection.send(data)
            except:
                self.label.set_text("Impossibile Connettersi!")
            data = clock+" "+self.Name+": "+text
            self.newmessage(data+"\n", None)
            self.Text.set_text("")


    def recev(self):
        #Funzione di ricezione
        self.loop = 1
        while self.loop:
            #Sistema anti-flood
            local_time = localtime()
            self.ValClock = local_time[3]*60*60
            self.ValClock += local_time[4]*60
            self.ValClock += local_time[5]
            #---------------------
            text = ""
            text = self.connection.recv(self.MaxChar+100)
            if text[:13] == "*$send file$*":
                self.draw_accept_file(text[13:])
            elif text!="":
                if self.Algorithm != "None":
                    text = DataDecrypt(self.Key, text, self.Algorithm)                
                #Sistema anti-flood-------------------------------------
                if (self.ValClock < self.LastSend):
                    #print self.LastSend - self.ValClock
                    self.ConsecutiveSend += 1
                    if self.ConsecutiveSend == int(self.AntiFlood[0]): 
                        self.Waiting = self.ValClock + int(self.AntiFlood[2])
                        if not self.Main.has_focus and self.WAlert:
                            self.WNotifier.Show()
                        gtk.gdk.threads_enter()
                        self.newmessage("<<Attivato Anti-flood!!! Durata: "+str(self.AntiFlood[2])+"s >>\n", "color_red")
                        gtk.gdk.threads_leave()
                else:
                    self.ConsecutiveSend = 0
                if self.AntiFloodActiv:
                    self.ConsecutiveSend = 0
                if (self.ValClock > self.Waiting):
                    if not self.Main.has_focus and self.WAlert:
                        self.WNotifier.Show()
                    if text == "Error": 
                        iterend = self.BufferTextChat.get_end_iter()
                        self.BufferTextChat.insert_with_tags_by_name(iterend, "<<Cifratura Errata!>>\n", "color_red")
                        self.TextChatView.scroll_to_mark(self.BufferTextChat.get_insert(), 0.1)
                        continue
                    gtk.gdk.threads_enter()
                    self.newmessage(text+"\n", "color_blue")
                    gtk.gdk.threads_leave()
                    self.LastSend = self.ValClock + int(self.AntiFlood[1])


    def init_send_file(self, event, widget):
        self.path_file = gtk.FileChooserDialog("Seleziona un file", self.Main, gtk.FILE_CHOOSER_ACTION_OPEN,  (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        resp = self.path_file.run()
        if resp == gtk.RESPONSE_OK:
            self.VerifySelectionFile(self.path_file.get_filename())
            self.path_file.destroy()
            return
        self.path_file.destroy()


    def VerifySelectionFile(self, File):
        if path.isfile(File):
            Args = ["WPFSend", path.join(self.GLOBALPATH,"WPFSend.py"), File, str(self.connect_to_ip), str(self.port_sfile), "SEND", self.Algorithm, self.Key]
            spawnv(P_NOWAIT, "/usr/bin/python", Args)
            self.connection.send("*$send file$*"+self.Name)
            local_time=localtime()
            clock = "["+str(local_time[3])+":"+str(local_time[4])+":"+str(local_time[5])+"]"
            self.newmessage(clock+" "+"*Spedita richiesta d'invio file.*\n", "color_green")
            self.Text.set_text("")
        else:
            EDialog = gtk.MessageDialog(self.path_file, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Percorso file non valido!")
            EDialog.run()
            EDialog.destroy()
        self.path_file.destroy()


    def draw_accept_file(self, name):
        local_time=localtime()
        clock = "["+str(local_time[3])+":"+str(local_time[4])+":"+str(local_time[5])+"]"
        self.newmessage(clock+" "+name+": vuole inviarti un file. ", "color_green")
        iterend = self.BufferTextChat.get_end_iter()
        anchor = self.BufferTextChat.create_child_anchor(iterend)
        self.AcceptButton = gtk.Button("Accetta")
        self.AcceptButton.connect("clicked", self.init_recv_file)
        self.AcceptButton.show_all()
        self.TextChatView.add_child_at_anchor(self.AcceptButton, anchor)
        self.newmessage("\n", None)


    def init_recv_file(self, event):
        self.AcceptButton.set_state(gtk.STATE_INSENSITIVE)
        Args = ["WPFSend", path.join(self.GLOBALPATH,"WPFSend.py"), "recv", str(self.connect_to_ip), str(self.port_sfile), "RECV", self.Algorithm, self.Key]
        spawnv(P_NOWAIT, "/usr/bin/python", Args)


    def myip(self):
        #Funzione che che scova l'ip esterno utilizzando un sito ausiliario
        try:
            url = URLopener()
            url_open = url.open('http://www.myip.it/')
            html = url_open.read()
            start = html.find("<b>Your IP address : ")+21
            end = html.find("</b></big><big>")
            ip = html[start:end].strip()
            IDialog = gtk.MessageDialog(self.Main, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, "Il tuo ip è: "+ip)
            IDialog.run()
            IDialog.destroy()

        except:
            pass


    def DlgSettings(self, event, widget):
        #Finestra per la modifica del profilo
        SDialog = gtk.Dialog("Connessione", window, 0,
            (gtk.STOCK_OK, gtk.RESPONSE_OK,
            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        SDialog.set_resizable(0)
        STable = gtk.Table(10,12,False)
        SDialog.vbox.pack_start(STable, False, False, 0)
        #Separatore
        STable.attach(gtk.Label("Generale"), 1, 9, 0, 1, xpadding=15, ypadding=3)
        #Frame Sinistro
        STable.attach(gtk.Label("Nick:"), 1, 3, 1, 2, xpadding=15, ypadding=5)
        STable.attach(gtk.Label("Byte Rate:"), 1, 3, 2, 3, xpadding=15, ypadding=5)
        STable.attach(gtk.Label("Tentativi:"), 1, 3, 3, 4, xpadding=15, ypadding=5)
        STable.attach(gtk.Label("Intervallo:"), 1, 3, 4, 5, xpadding=15, ypadding=5)
        #Frame Destro
        EntryName = gtk.Entry(15) 
        STable.attach(EntryName, 3, 10, 1, 2, xpadding=15, ypadding=3)
        EntryRate = gtk.Entry(30)
        STable.attach(EntryRate, 3, 10, 2, 3, xpadding=15, ypadding=3)
        EntryConRate = gtk.Entry(10)
        STable.attach(EntryConRate, 3, 10, 3, 4, xpadding=15, ypadding=3)
        EntrySecRate = gtk.Entry(10)
        STable.attach(EntrySecRate, 3, 10, 4, 5, xpadding=15, ypadding=3)
        Pulsante1 = gtk.Button("Mostra mio IP")
        Pulsante1.connect("clicked", lambda x: self.myip())
        STable.attach(Pulsante1, 3, 5, 7, 8, gtk.FILL, gtk.FILL, xpadding=0, ypadding=10)
        SDialog.show_all()
        #Carica le impostazioni attuali
        EntryName.set_text(self.Name)
        EntryRate.set_text(str(self.ByteRate))
        EntryConRate.set_text(str(self.ConRate))
        EntrySecRate.set_text(str(self.SecRate))
        Resp = SDialog.run()
        if Resp == gtk.RESPONSE_OK:
            try:
                self.Name = EntryName.get_text()
                self.ByteRate = int(EntryRate.get_text())
                self.ConRate = int(EntryConRate.get_text())
                self.SecRate = int(EntrySecRate.get_text())
                WPConfig.WriteNewConf(self.GLOBALPATH, self.Name, self.ByteRate, self.ConRate, self.SecRate, self.Key, self.Algorithm, self.MaxChar, str(self.AntiFlood[0])+"x"+str(self.AntiFlood[1])+"x"+str(self.AntiFlood[2]), str(self.WAlert), self.AServer, self.AServerNick, self.AServerPwd)

            except:
                EDialog = gtk.MessageDialog(SDialog, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Formato non valido!")
                EDialog.run()
                EDialog.destroy()
        SDialog.destroy()


    def DlgAServer(self, event, widget):
        #Finestra per la modifica del profilo
        SDialog = gtk.Dialog("Connessione", window, 0,
            (gtk.STOCK_OK, gtk.RESPONSE_OK,
            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        SDialog.set_resizable(0)
        STable = gtk.Table(10,12,False)
        SDialog.vbox.pack_start(STable, False, False, 0)
        #Separatore
        STable.attach(gtk.Label("Server Ausiliaro"), 1, 9, 0, 1, xpadding=15, ypadding=3)
        #Frame Sinistro
        STable.attach(gtk.Label("URL:"), 0, 1, 1, 2, xpadding=1, ypadding=3)
        STable.attach(gtk.Label("Nick:"), 0, 1, 2, 3, xpadding=1, ypadding=3)
        STable.attach(gtk.Label("Password:"), 0, 1, 3, 4, xpadding=1, ypadding=3)
        #Frame Destro
        EntryAServer = gtk.Entry(300) 
        STable.attach(EntryAServer, 1, 10, 1, 2, gtk.FILL, gtk.FILL, xpadding=1, ypadding=3)
        EntryAServerNick = gtk.Entry(30)
        STable.attach(EntryAServerNick, 1, 10, 2, 3, xpadding=1, ypadding=3)
        EntryAServerPwd = gtk.Entry(30)
        EntryAServerPwd.set_visibility(0)
        STable.attach(EntryAServerPwd, 1, 10, 3, 4, xpadding=1, ypadding=3)
        #Basso
        Pulsante1 = gtk.Button("Registrati")
        Pulsante1.connect("clicked", lambda x: start_new_thread(webbrowser.open,("http://wicker25.netsons.org/progetti/RegIP/register.php",)))
        STable.attach(Pulsante1, 4, 6, 7, 8, gtk.FILL, gtk.FILL, xpadding=0, ypadding=10)
        SDialog.show_all()
        #Carica le impostazioni attuali
        EntryAServer.set_text(self.AServer)
        EntryAServerNick.set_text(str(self.AServerNick))
        EntryAServerPwd.set_text(str(self.AServerPwd))

        Resp = SDialog.run()
        if Resp == gtk.RESPONSE_OK:
            try:
                self.AServer = EntryAServer.get_text()
                self.AServerNick = EntryAServerNick.get_text()
                self.AServerPwd = EntryAServerPwd.get_text()
                WPConfig.WriteNewConf(self.GLOBALPATH, self.Name, self.ByteRate, self.ConRate, self.SecRate, self.Key, self.Algorithm, self.MaxChar, str(self.AntiFlood[0])+"x"+str(self.AntiFlood[1])+"x"+str(self.AntiFlood[2]), str(self.WAlert), self.AServer, self.AServerNick, self.AServerPwd)

            except:
                pass
        SDialog.destroy()


    def DlgSecure(self, event, widget):
        #Finestra per la modifica del profilo
        SecDialog = gtk.Dialog("Profilo", window, 0,
            (gtk.STOCK_OK, gtk.RESPONSE_OK,
             gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        SecDialog.set_resizable(0)
        SecTable = gtk.Table(10,10,False)
        SecDialog.vbox.pack_start(SecTable, False, False, 0)
        #Separatore
        SecTable.attach(gtk.Label("Sicurezza"), 1, 9, 0, 1, xpadding=15, ypadding=3)
        #Chiave
        SecTable.attach(gtk.Label("Chiave:"), 1, 2, 1, 2, xpadding=10, ypadding=5)
        EntryKey = gtk.Entry(32)
        SecTable.attach(EntryKey, 2, 10, 1, 2, xpadding=15, ypadding=5)
        EntryKey.set_text(self.Key)   
        #None
        CheckBoxNone = gtk.RadioButton(None, "Nessuno")
        CheckBoxNone.connect("toggled", self.SetAlgorithm, "None")
        SecTable.attach(CheckBoxNone, 1, 3, 4, 5, xpadding=2, ypadding=4)
        #ARC4
        CheckBoxARC4 = gtk.RadioButton(CheckBoxNone, "ARC4")
        CheckBoxARC4.connect("toggled", self.SetAlgorithm, "ARC4")
        SecTable.attach(CheckBoxARC4, 3, 5, 4, 5, xpadding=2, ypadding=4)
        #DES3
        CheckBoxDES3 = gtk.RadioButton(CheckBoxNone, "DES3")
        CheckBoxDES3.connect("toggled", self.SetAlgorithm, "DES3")
        SecTable.attach(CheckBoxDES3, 5, 7, 4, 5, xpadding=2, ypadding=4)
        #Setting
        if self.Algorithm == "None": CheckBoxNone.set_active(1)
        if self.Algorithm == "ARC4": CheckBoxARC4.set_active(1)
        if self.Algorithm == "DES3": CheckBoxDES3.set_active(1)
        OldAlgorithm = self.Algorithm
        SecDialog.show_all()
        Resp = SecDialog.run()
        if Resp == gtk.RESPONSE_OK:
            if self.Algorithm == "DES3" and len(EntryKey.get_text())%8 != 0:
                EDialog = gtk.MessageDialog(SecDialog, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Formato non valido: Nella cifratura DES3 è necessario che la chiave sia di 16 o 24 byte di lunghezza.")
                EDialog.run()
                EDialog.destroy()
                self.Algorithm = OldAlgorithm
                SecDialog.destroy()
                return
            self.Key = EntryKey.get_text()
            WPConfig.WriteNewConf(self.GLOBALPATH, self.Name, self.ByteRate, self.ConRate, self.SecRate, self.Key, self.Algorithm, self.MaxChar, str(self.AntiFlood[0])+"x"+str(self.AntiFlood[1])+"x"+str(self.AntiFlood[2]), str(self.WAlert), self.AServer, self.AServerNick, self.AServerPwd)
        else:
            self.Algorithm = OldAlgorithm
        SecDialog.destroy()


    def DlgAntiFlood(self, event, widget):
        #Finestra per il settaggio del sistema antiflood
        SDialog = gtk.Dialog("Connessione", window, 0,
            (gtk.STOCK_OK, gtk.RESPONSE_OK,
            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        SDialog.set_resizable(0)
        STable = gtk.Table(10,10,False)
        SDialog.vbox.pack_start(STable, False, False, 0)
        #Separatore
        STable.attach(gtk.Label("Anti-Flood"), 1, 9, 0, 1, xpadding=15, ypadding=3)
        #Frame Sinistro
        STable.attach(gtk.Label("N° Messagi:"), 1, 3, 1, 2, xpadding=15, ypadding=5)
        STable.attach(gtk.Label("Intervallo:"), 1, 3, 2, 3, xpadding=15, ypadding=5)
        STable.attach(gtk.Label("Attesa:"), 1, 3, 3, 4, xpadding=15, ypadding=5)
        #Frame Destro
        EntryNMess = gtk.Entry(15) 
        STable.attach(EntryNMess, 3, 10, 1, 2, xpadding=15, ypadding=3)
        EntryRateMess = gtk.Entry(30)
        STable.attach(EntryRateMess, 3, 10, 2, 3, xpadding=15, ypadding=3)
        EntryWait = gtk.Entry(10)
        STable.attach(EntryWait, 3, 10, 3, 4, xpadding=15, ypadding=3)
        SDialog.show_all()
        #Carica le impostazioni attuali
        EntryNMess.set_text(str(self.AntiFlood[0]))
        EntryRateMess.set_text(str(self.AntiFlood[1]))
        EntryWait.set_text(str(self.AntiFlood[2]))
        Resp = SDialog.run()
        if Resp == gtk.RESPONSE_OK:
            try:
                self.AntiFlood[0] = int(EntryNMess.get_text())
                self.AntiFlood[1] = int(EntryRateMess.get_text())
                self.AntiFlood[2] = int(EntryWait.get_text())

                for t in range(0, len(self.AntiFlood)):
                    if self.AntiFlood[t] < 0: self.AntiFlood[t] = 0

                WPConfig.WriteNewConf(self.GLOBALPATH, self.Name, self.ByteRate, self.ConRate, self.SecRate, self.Key, self.Algorithm, self.MaxChar, str(self.AntiFlood[0])+"x"+str(self.AntiFlood[1])+"x"+str(self.AntiFlood[2]), str(self.WAlert), self.AServer, self.AServerNick, self.AServerPwd)

            except:
                EDialog = gtk.MessageDialog(SDialog, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Formato non valido!")
                EDialog.run()
                EDialog.destroy()
        SDialog.destroy()


    def SetAlgorithm(self, event, mode):
        self.Algorithm = mode


    def info(self, event, widget):
        DlgInfo = gtk.AboutDialog()
        DlgInfo.set_logo(self.icon)
        DlgInfo.set_name(self.title)
        DlgInfo.set_version(self.version)
        DlgInfo.set_comments(self.description)
        License = open(path.join(self.GLOBALPATH, "COPYING")).read()
        DlgInfo.set_license(License)
        #self.description
        DlgInfo.set_authors([self.author])
        DlgInfo.set_website(self.site)
        DlgInfo.show_all()
        def close(w, res):
             if res == gtk.RESPONSE_CANCEL:
                     w.hide()
        DlgInfo.connect("response", close)


    def DialogSmiles(self, event, widget):
        self.DlSmiles = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.DlSmiles.set_icon(self.icon)
        self.DlSmiles.set_title("Emoticons")
        self.DlSmiles.set_resizable(0)
        LenBoard = len(WPTag.SmilesList)
        DlSmilesTable = gtk.Table(LenBoard,LenBoard,False)
        self.DlSmiles.add(DlSmilesTable)
        self.SmilesDictionary = {}

        x , y = 0, 0

        for element in WPTag.SmilesList:
            SmileButton = gtk.Button()
            SmileButton.connect("clicked", self.InsertSmile)
            img = gtk.Image()
            img.set_from_file(path.join(self.GLOBALPATH, "Smiles", element[1]))
            img.set_pixel_size(50)
            SmileButton.set_image(img)
            DlSmilesTable.attach(SmileButton, x, x+1, y, y+1, gtk.FILL, gtk.FILL)

            #Imposta il dizionario
            self.SmilesDictionary[SmileButton] = element[0]

            x += 1
            if x > 5:
                x = 0
                y += 1
        y += 1
        AddSmiles = gtk.Button("Chiudi")
        AddSmiles.connect("clicked", lambda x: self.DlSmiles.destroy())
        DlSmilesTable.attach(AddSmiles, 0, LenBoard, y, y+1, xpadding=0, ypadding=2)
        self.DlSmiles.show_all()


    def contacts(self, event, widget):
        self.DlgContacts = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.DlgContacts.set_icon(self.icon)
        self.DlgContacts.set_title("Contatti")
        self.DlgContacts.set_default_size(200,300)
        self.DlgContactsTable = gtk.Table(50,50,False)
        self.DlgContacts.add(self.DlgContactsTable)

        #Pannello
        self.WinScroller = gtk.ScrolledWindow(None, None)
        self.WinScroller.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.WinScroller.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.DlgContactsTable.attach(self.WinScroller, 1, 50, 1, 45)
        self.ListBox = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        #self.ListBox = gtk.ListStore(gobject.TYPE_STRING)           
        self.View = gtk.TreeView(self.ListBox)
        self.WinScroller.add(self.View)
        self.renderer = gtk.CellRendererText()
        COL_RNICKS, COL_RIP, COL_RSTATUS = (0, 1, 2)
        self.col = gtk.TreeViewColumn('Nick', self.renderer, text=COL_RNICKS)
        self.View.append_column(self.col)
        self.col = gtk.TreeViewColumn('Indirizzo IP', self.renderer, text=COL_RIP)
        self.View.append_column(self.col)
        self.col = gtk.TreeViewColumn('Stato', self.renderer, text=COL_RSTATUS)
        self.View.append_column(self.col)
        self.View.set_search_column(0)
        self.col.set_sort_column_id(0)
        self.col.set_sort_column_id(2)
        #Connect
        CButton = gtk.Button("Contatta")
        CButton.connect("clicked", self.ConnectUser)
        self.DlgContactsTable.attach(CButton, 20, 25, 47, 48, xpadding=15, ypadding=10)
        AButton = gtk.Button("Aggiorna")
        AButton.connect("clicked", lambda x: start_new_thread(self.LoadDataFromServer, ()))
        self.DlgContactsTable.attach(AButton, 25, 30, 47, 48, xpadding=15, ypadding=10)
        self.DlgContacts.show_all()

        start_new_thread(self.LoadDataFromServer, ())


    def LoadDataFromServer(self):
        if self.WaitingContacts: return
        self.ListBox.clear()
        try:
            self.WaitingContacts = 1
            url = URLopener()
            url_open = url.open(self.AServer+"regip_server.php?user="+str(self.AServerNick)+"&pwd="+str(self.AServerPwd)+"&mode=load")
            self.Name = self.AServerNick
            Data = url_open.read().replace("\n", "<br>")
            Data = Data.split("<br>")
            #gtk.gdk.threads_enter()
            for t in range(1, len(Data)-1):
                element = Data[t].split(":")
                self.ListBox.append(element)
            #self.cell.set_property('cell-background', 'red')
            #self.col.set_attributes(self.cell, text=0)
            #gtk.gdk.threads_leave()
            self.WaitingContacts = 0
        except:
            self.ListBox.append(["Avviso", "impossibile", "connettersi!"])

    def SaveDataToServer(self):
        old_temp = 0
        while self.Online:
            local_time = localtime()
            temp = local_time[3]*60*60
            temp += local_time[4]*60
            temp += local_time[5]
            if temp < old_temp+30: continue
            try:
                url = URLopener()
                url_open = url.open(self.AServer+"regip_server.php?user="+str(self.AServerNick)+"&pwd="+str(self.AServerPwd)+"&mode=save")  
                self.Name = self.AServerNick
            except:
                pass
            old_temp = temp


    def ConnectUser(self, widget):
        try:
            Rip = self.ListBox.get_value(self.View.get_selection().get_selected()[1], 1)
            start_new_thread(self.client, (Rip,))
        except:
            EDialog = gtk.MessageDialog(self.DlgContacts, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Nessuna voce selezionata!")
            EDialog.run()
            EDialog.destroy()


    def InsertSmile(self, SmileButton):
        self.Text.set_text(self.Text.get_text()+self.SmilesDictionary[SmileButton]+" ")


    def clean_chat(self, event, widget):
        self.BufferTextChat.set_text("")


    def SetAntiFlood(self, arg, widget):
        if not self.AntiFloodActiv: 
            self.AntiFloodActiv = True
            return 
        if self.AntiFloodActiv: 
            self.AntiFloodActiv = False
            return

    def SetWAlert(self, arg, widget):
        if not self.TerminateSettings: return
        if not self.WAlert: 
            self.WAlert = 1
            WPConfig.WriteNewConf(self.GLOBALPATH, self.Name, self.ByteRate, self.ConRate, self.SecRate, self.Key, self.Algorithm, self.MaxChar, str(self.AntiFlood[0])+"x"+str(self.AntiFlood[1])+"x"+str(self.AntiFlood[2]), str(self.WAlert), self.AServer, self.AServerNick, self.AServerPwd)
            return 
        if self.WAlert: 
            self.WAlert = 0
            WPConfig.WriteNewConf(self.GLOBALPATH, self.Name, self.ByteRate, self.ConRate, self.SecRate, self.Key, self.Algorithm, self.MaxChar, str(self.AntiFlood[0])+"x"+str(self.AntiFlood[1])+"x"+str(self.AntiFlood[2]), str(self.WAlert))
            return


    def stop_connection(self, event, widget):
        #Funzione per sconnettersi
        self.label.set_text("Non connesso!")
        self.loop = 0
        try:
            self.connection.close()
        except: pass


    def rapid_click(self, widget, event):
        if self.Main.focus_widget == self.SendButton or self.Main.focus_widget == self.Text:
            if event.keyval == 65293: 
                self.SendButton.clicked()


    def exit(self):
        #Esce
        self.stop_connection
        gtk.main_quit


window = gtk.Window()
App = Application(window)
window.show_all()
window.connect("delete_event", gtk.main_quit)
gtk.gdk.threads_enter()
gtk.main()
gtk.gdk.threads_leave()
