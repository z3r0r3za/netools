#!/user/bin/env python

import argparse
import signal
import sys
from scapy.all import ARP, Ether, srp


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ipcidr", dest="ipcidr", help="sudo python netscan.py -i 192.168.0.1/24")
    args = parser.parse_args()
    return args


opt = get_arguments()
ip_cidr = str(opt.ipcidr)


def get_ips(ip_cidr):
    try:
        # Get the IP Address for the destination.
        # ip_cidr = "192.168.66.1/24"
        # Set up an ARP packet.
        arp = ARP(pdst=ip_cidr)
        # Set up an Ether broadcast packet with MAC address.
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        # Stack ARP packet and Ether broadcast.
        packet = ether/arp

        result = srp(packet, timeout=3, verbose=0)[0]

        # Create a list to hold the ip addresses found on the network.
        devices = []

        # Append the ip and mac address to the list from each response.
        for sent, received in result:
            devices.append({'ip': received.psrc, 'mac': received.hwsrc})

        # Print everything in the list.
        print("\nDevices found connected to the network:")
        print("---------------------------------------")
        print(f"IP{' '*17}MAC")
        for device in devices:
            print(f"{device['ip']:18} {device['mac']}")
    except Exception as e:    
        print("Error Return Type: ", type(e))


def signal_handler(sig, frame):
    print("\n[+] Scan shutdown with Ctrl-c. Exiting now....")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    try:
        get_ips(ip_cidr)
    except PermissionError as e:
        if type(e).__name__ == 'PermissionError':
            print(f"[*] {type(e).__name__}. You need to be root or use sudo.")
        else:
            print("Error Return Type: ", type(e))
    