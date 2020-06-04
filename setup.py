import os
import time
import subprocess

try:
    os.system('sudo apt install dnsmasq')
    os.system('sudo apt install hostpad')
    os.system('sudo apt install screen')
    os.system('sudo apt install driftnet')
    os.system('sudo apt install python3-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg62-turbo-dev zlib1g-dev')
    os.system('sudo apt install libcap-dev')
    os.system('sudo pip3 install begin')
    os.system('sudo pip3 install mitmproxy')
    os.system('sudo pip3 install dnspython')
    os.system('sudo pip3 install pcapy')
    os.system('sudo pip3 install twisted')
except:
    print('Failed to install all dependencies')



