#!/usr/bin/python
# -*- coding: utf-8 -*-
from urllib import *
import os , sys, time, json
try:
    import requests
except:
	os.system("clear")
	print '\t\033[31;3;1;1m* \033[37mChecking Modules'
	time.sleep(3)
	print '\t\033[31;3;6m* \033[37mPlease install modules requests'
	print '\t\033[31;3;6m* \033[37mpip2 install requests\033[37;0m'
	print
	sys.exit()
    
    
def banner():
    print '''\t
                \033[31m_          _____           __
               (_)___     / __(_)___  ____/ /__  _____
              / / __ \   / /_/ / __ \/ __  / _ \/ ___/
             \033[0m/ / /_/ /  / __/ / / / / /_/ /  __/ /
            /_/ .___/  /_/ /_/_/ /_/\__,_/\___/_/
	     /_/\033[33;3;2mCo\033[31md\033[34mer: \033[36;3;2mMrY86 & Mr.K3R3H\033[0m'''


def menu():
	os.system("clear")
	banner()
	print
	print "\n\t\033[31;3m* \033[37mThis Tools Not 100% Accurate\033[0m"
	print
	print "\t\033[31;1m[ \033[33m1 \033[31m] \033[0;1mMyIpInfo"
	print "\t\033[31m[ \033[33m2 \033[31m] \033[0;1mTrackIpInfo"
	print
	print "\t\033[31m[ \033[33m00 \033[31m] \033[0mEXIT"
	print
	cek = raw_input("\t\033[33;3;2mIPF\033[31m@\033[36mMenu > \033[0;0m")
	if cek == "1":
		no1()
	elif cek == "2":
		no2()
	elif cek == "00":
		os.system("clear")
		sys.exit()
		
	else:
		print "\n\t\033[31;3m* \033[37mWrong Input"
        time.sleep(2)
        restart = sys.executable
        os.execl(restart, restart, *sys.argv)
	


def no1():
	try:
		myinfoip()
	except (KeyboardInterrupt, EOFError):
		print "\n\t\033[31;3m* \033[37mWrong Input"
		time.sleep(2)
		myinfoip()

def no2():
	try:
		trackipinfo()
	except (KeyboardInterrupt, EOFError, KeyError):
		print "\n\t\033[31;3m* \033[37mWrong Input"
		time.sleep(2)
		trackipinfo()
	
def myinfoip():
    os.system("clear")

    url = "https://api.ipify.org/?format=json"
    data = urlopen(url).read().decode("utf-8")
    data2 = json.loads(data)

    ip = str(data2["ip"])

    url = "http://ip-api.com/json/" +ip
    data = urlopen(url).read().decode("utf-8")
    data2 = json.loads(data)
    
    lat = str(data2["lat"])
    lon = str(data2["lon"])
    
    banner()
    print
    print "\t\033[37;7;2;3m              YOUR IP AND THE INFORMATION                   \033[37;0;1m"
    print
    print "\t\033[1;31m[ \033[33m¤ \033[31m] \033[0mYour Ip \t\t:\033[1;32m",ip
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mAS \t\t:\033[1;32m", str(data2["as"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mCOUNTRY \t\t:\033[1;32m", str(data2["country"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mCITY \t\t:\033[1;32m", str(data2["city"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mCOUNTRY CODE \t:\033[1;32m", str(data2["countryCode"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mISP \t\t:\033[1;32m", str(data2["isp"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mLATITUDE \t\t:\033[1;32m", str(data2["lat"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mLONGTITUDE \t:\033[1;32m", str(data2["lon"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mORG \t\t:\033[1;32m", str(data2["org"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mQUERY \t\t:\033[1;32m", str(data2["query"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mREGION CODE\t:\033[1;32m", str(data2["region"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mREGION NAME \t:\033[1;32m", str(data2["regionName"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mTIME ZONE \t:\033[1;32m", str(data2["timezone"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mZIP \t\t:\033[1;32m ", str(data2["zip"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mSTATUS \t\t:\033[32;1m", str(data2["status"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mGOOGLE MAPS \t:\033[1;32m http://www.google.com/maps/place/%s,%s/@%s,%s,16z" %(lat,lon,lat,lon)
    print
    print "\t\033[31m[ \033[33m99 \033[31m] \033[0;1mBACK"
    print "\t\033[31m[ \033[33m00 \033[31m] \033[0mEXIT"
    print
    cek = raw_input("\t\033[33;3;2mIPF\033[31m@\033[36mMyIpInfo > \033[0m")
    
    if cek == '00':
        os.system("clear")
        sys.exit()
    elif cek == '99':
    	menu()
    else:
        print "\n\t\033[31;3m* \033[37mWrong Input"
        time.sleep(2)
        no1()
        
def trackipinfo():
    os.system("clear")
    banner()
    print ""
    try:
        ip = raw_input("\t\033[33;3;2mIPF\033[31m@\033[36mIpTarget > \033[0m")
    except (KeyError, KeyboardInterrupt):
        print "\n\t\033[31;3m* \033[37mWrong Input"
        time.sleep(2)
        trackipinfo()
        
    os.system("clear")
    
    url = "http://ip-api.com/json/" +ip
    data = urlopen(url).read().decode("utf-8")
    data2 = json.loads(data)
    
    lat = str(data2["lat"])
    lon = str(data2["lon"])
    
    banner()
    print
    print "\t\033[37;7;2;3m                   IP AND THE INFORMATION                   \033[37;0m"
    print
    print "\t\033[1;31m[ \033[33m¤ \033[31m] \033[0mAS \t\t:\033[1;32m", str(data2["as"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mCOUNTRY \t\t:\033[1;32m", str(data2["country"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mCITY \t\t:\033[1;32m", str(data2["city"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mCOUNTRY CODE \t:\033[1;32m", str(data2["countryCode"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mISP \t\t:\033[1;32m", str(data2["isp"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mLATITUDE \t\t:\033[1;32m", str(data2["lat"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mLONGTITUDE \t:\033[1;32m", str(data2["lon"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mORG \t\t:\033[1;32m", str(data2["org"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mQUERY \t\t:\033[1;32m", str(data2["query"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mREGION CODE\t:\033[1;32m", str(data2["region"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mREGION NAME \t:\033[1;32m", str(data2["regionName"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mTIME ZONE \t:\033[1;32m", str(data2["timezone"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mZIP \t\t:\033[1;32m ", str(data2["zip"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mSTATUS \t\t:\033[32;1m", str(data2["status"])
    print "\t\033[31m[ \033[33m¤ \033[31m] \033[0mGOOGLE MAPS \t:\033[1;32m http://www.google.com/maps/place/%s,%s/@%s,%s,16z" %(lat,lon,lat,lon)
    print
    print "\t\033[31m[ \033[33m99 \033[31m] \033[0;1mBACK"
    print "\t\033[31m[ \033[33m00 \033[31m] \033[0mEXIT"
    print
    cek = raw_input("\t\033[33;3;2mIPF\033[31m@\033[36mIpTrackInfo > \033[0m")
    
    if cek == '00':
        os.system("clear")
        sys.exit()
    elif cek == '99':
    	menu()
    else:
        print "\n\t\033[31;3m* \033[37mWrong Input"
        time.sleep(2)
        no2()

if __name__ == '__main__':
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print "\n\t\033[31;3m* \033[37mWrong Input"
        time.sleep(2)
        restart = sys.executable
        os.execl(restart, restart, *sys.argv)