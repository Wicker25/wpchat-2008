#!/usr/bin/python
# -*- coding: UTF-8 -*-
#=================================================================================
#        Name: WPConfig
#        Author:   wicker25 (http://hackerforum.devil.it/  -  wicker25@gmail.com)
#        Description: Settings Manager Library
#        Licence: GPL
#        Version: 0.1
#=================================================================================

from os import path

def WriteNewConf(GLOBALPATH, Name, ByteRate, ConRate, SecRate, Key, Algorithm, MaxChar, AntiFlood, Avvisi, AServer, AServerNick, AServerPwd):

    try:

        ConfigFile = open(path.join(GLOBALPATH, "Config"), "w")
        Data = "[Name]\n"+str(Name)+"\n"
        Data += "[ByteRate]\n"+str(ByteRate)+"\n"
        Data += "[ConRate]\n"+str(ConRate)+"\n"
        Data += "[SecRate]\n"+str(SecRate)+"\n"
        Data += "[Key]\n"+str(Key)+"\n"
        Data += "[Algorithm]\n"+str(Algorithm)+"\n"
        Data += "[MaxChar]\n"+str(MaxChar)+"\n"
        Data += "[AntiFlood]\n"+str(AntiFlood)+"\n"
        Data += "[Avvisi]\n"+str(Avvisi)+"\n"
        Data += "[AServer]\n"+str(AServer)+"\n"
        Data += "[AServerNick]\n"+str(AServerNick)+"\n"
        Data += "[AServerPwd]\n"+str(AServerPwd)+"\n"
        ConfigFile.write(Data)
        ConfigFile.close()

        return "Settings Written."

    except:

        return "Error!"

#---------------------------------------------------------------------------

def ReadNewConf(GLOBALPATH):

    try:

        ConfigFile = open(path.join(GLOBALPATH, "Config"), "r")
        Data = ConfigFile.read().split()
        ConfigFile.close()

        Config = []

        for t in range(0, len(Data)):

            if t % 2: Config.append(Data[t])

    except:
        
        WriteDefaultConf(GLOBALPATH)

        print "Warning: File Settings Repaired."
        
        return ["Nome", 1024, 3, 1, "Key", "None", 400, "5x2x5", "1", "http://wicker25.netsons.org/progetti/RegIP/", "Nick", "Password"]

    if len(Config) != 12: 

        WriteDefaultConf(GLOBALPATH)

        print "Warning: File Settings Repaired."
        
        return ["Nome", 1024, 3, 1, "Key", "None", 400, "5x2x5", "1", "http://wicker25.netsons.org/progetti/RegIP/", "Nick", "Password"]


    return tuple(Config)
    
#---------------------------------------------------------------------------

def WriteDefaultConf(GLOBALPATH):

    WriteNewConf(GLOBALPATH, "Nome", 1024, 3, 1, "Key", "None", 400, "5x2x5", "1", "http://wicker25.netsons.org/progetti/RegIP/", "Nick", "Password")



