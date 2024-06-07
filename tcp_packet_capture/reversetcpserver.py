import socket
import threading

import PacketTCP
import select


def client_receive_packet(clientsocket1):
    # 接收Initialization报文
    data = clientsocket1.recv(1024)
    if not data:
        return False
    packet_received = PacketTCP.Initialization.unpack(data)
    print('Received from client: ', packet_received.callme(), clientsocket1.getpeername())
    N = packet_received.N
    # 发送Agree报文
    packet_to_send = PacketTCP.Agree(2)
    clientsocket1.send(packet_to_send.pack())
    # 接收ReverseRequest报文
    for _ in range(0, N):
        data = clientsocket1.recv(1024)
        if not data:
            return False
        packet_received = PacketTCP.ReverseRequest.unpack(data)
        print('Received from client: ', packet_received.callme(), clientsocket1.getpeername())

        # 发送ReverseAnswer报文
        reverse_data = packet_received.Data[::-1]
        reverse_data = reverse_data.strip('\n ')
        packet_to_send = PacketTCP.ReverseAnswer(4, len(reverse_data), reverse_data)
        clientsocket1.send(packet_to_send.pack())
    return True


def check_flag():
    global flagcontinue
    while flagcontinue:
        s = input()
        if s == "end":
            flagcontinue = False


# 服务端
if __name__ == "__main__":
    flagcontinue = True
    spe = threading.Thread(target=check_flag)
    spe.start()
    # 设置需要监听的 socket 地址和端口
    ADDRESS = ("localhost", 1118)
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(ADDRESS)
    serversocket.listen(1)
    client_connected = []
    while flagcontinue:
        readable_sockets, _, _ = select.select([serversocket] + client_connected,
                                               [], [], 1)
        for sock in readable_sockets:
            # 如果是 server_socket 表示有新的连接
            if sock is serversocket:
                client_socket, client_address = serversocket.accept()
                client_connected.append(client_socket)
                print(f"New client connected: {client_address}")
            else:
                try:
                    if not client_receive_packet(sock):
                        print(f"Client {sock.getpeername()} disconnected")
                        client_connected.remove(sock)
                        sock.close()
                except Exception as e:
                    print(f"Error {sock.getpeername()}:{e}")
                    client_connected.remove(sock)
                    sock.close()

    serversocket.close()
