import socket
import struct
import sys
import time

rcv_time = time.time()
addr = "172.16.1.10"
data = sys.argv[0]

print(f'Data received: \'{data}\'' \
      f'from \'{addr}\'' \
      f'at \'{rcv_time}\'')

bcastIP = "172.16.15.255"
bcastPort = 60000

sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

udp_payload = data.encode('utf-8')
udp_header = struct.pack(">HHHH", 60001, 60000, 8 + len(udp_payload), 0)
ip_payload = udp_header + udp_payload

version = 4
ihl = 5
version_ihl = (version << 4) | ihl
type_of_service = 0
total_length = 20 + len(ip_payload)
ip_header = struct.pack(">BBH", version_ihl, type_of_service, total_length)

ip_header += struct.pack(">HH", 12345, 0)

ttl = 20
protocol = 17
checksum = 0
ip_header += struct.pack(">BBH", ttl, protocol, checksum)
ip_header += struct.pack(">BBBB", 172, 16, 1, 10)
ip_header += struct.pack(">BBBB", 172, 16, 15, 255)

ip_pkt = ip_header + ip_payload

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

sock.sendto(ip_pkt, (bcastIP, bcastPort))