#!/usr/bin/python
# -*- coding: UTF-8 -*-
#=================================================================================
#        Name: WPGui - Grafic Library
#        Author:   wicker25 (http://hackerforum.devil.it/  -  wicker25@gmail.com)
#        Description: Grafic Library
#        Licence: GPL
#        Version: 0.1
#=================================================================================

import gtk
from urllib import URLopener

class Notifier:

    def __init__(self, Text):

        self.WNotifier = gtk.Window(gtk.WINDOW_POPUP)
        self.WNotifier.set_title("Emoticons")
        self.WNotifier.move(0, 50)
        self.WNotifierTable = gtk.Table(10, 2, False)
        self.WNotifier.add(self.WNotifierTable)
        ExitButton = gtk.Button("X")
        ExitButton.connect("clicked", lambda x: self.Hide())
        self.WNotifierTable.attach(ExitButton, 9, 10, 1, 2, gtk.FILL, gtk.FILL, xpadding=2, ypadding=2)
        self.WNotifierTable.attach(gtk.Label(Text), 1, 9, 1, 2, gtk.FILL, gtk.FILL, xpadding=2, ypadding=2)

    def Show(self):

        self.WNotifier.show_all()

    def Hide(self):

        self.WNotifier.hide_all()

#----------------------------------------------------
  
