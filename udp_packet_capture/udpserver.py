import random
import socket
from datetime import datetime
import PacketUDP

ADRESS = ('127.0.0.1', 1118)
serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serversocket.bind(ADRESS)

while 1:
    data, client_address = serversocket.recvfrom(1024)
    if not data:
        break
    packet_received = PacketUDP.PacketUDP.unpack(data)
    if packet_received.my_type == 2:
        data = PacketUDP.PacketUDP(seq_no=0, ver=2, my_type=3, content='hello')
        print(f'client{client_address}: ', packet_received.content)
        serversocket.sendto(data.pack(), client_address)
        continue
    elif packet_received.my_type == 4:
        print(f'client{client_address}: ', packet_received.content)
        continue
    elif packet_received.my_type == 5:
        data = PacketUDP.PacketUDP(seq_no=0, ver=2, my_type=6, content='goodbye')
        print(f'client{client_address}: ', packet_received.content)
        serversocket.sendto(data.pack(), client_address)
        data = PacketUDP.PacketUDP(seq_no=0, ver=2, my_type=5, content='goodbye')
        serversocket.sendto(data.pack(), client_address)
        continue
    elif packet_received.my_type == 6:
        print(f'client{client_address}: ', packet_received.content)
        continue
    x = random.random() * 100
    x = int(x)
    c = 40
    # print(x, packet_received.seq_no)
    if c < x:
        now = datetime.now()
        # 格式化时间输出为 hh-mm-ss
        formatted_time = now.strftime("%H-%M-%S")
        packet_received.server_time = formatted_time
        packet_received.my_type = 1
        serversocket.sendto(packet_received.pack(), client_address)
serversocket.close()
