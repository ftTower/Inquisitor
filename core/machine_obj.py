from ainsi import *

from getmac import get_mac_address as gma
import ipaddress
import re

class Machine:
    def __init__(self, mac_address, ip_address, type):
        self.ip_address = ip_address
        self.mac_address = mac_address
        
        self.type = type
        self.poisoned = False
    
        #? FOR ATTACKER MACHINE
        if mac_address == None:
           self.find_mac_adress() 
    
        #? FOR ALL MACHINES VERIFY DATA FORMAT
        self.verify_ip_adress()
        self.verify_mac_adress()
    
    #! VERIFY INFORMATION GIVED
    def verify_ip_adress(self):
        if not self.ip_address:
            return 
        ipaddress.ip_address(self.ip_address) 
    
    def verify_mac_adress(self):
        if not self.ip_address:
            return
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        if not mac_pattern.match(self.mac_address):
            raise Exception("Invalid MAC address format")
    
    #! FIND MAC ADRESS FOR ATTACKER
    def find_mac_adress(self):
        self.mac_address = gma()
    
    #! UTILS
    
    def __str__(self):
        type_str = str(colored(self.type, BRIGHT_YELLOW)) if self.type is not None else "None"
        ip_str = str(self.ip_address) if self.ip_address is not None else "None"
        mac_str = str(self.mac_address) if self.mac_address is not None else "None"
        poisoned_str = colored(str(self.poisoned), BRIGHT_GREEN if self.poisoned else BRIGHT_RED)
        return f"{type_str:<17} | IP: {ip_str:<15} | MAC: {mac_str:<17} | Poisoned: {poisoned_str:<5}"
    