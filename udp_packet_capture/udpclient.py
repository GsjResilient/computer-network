import socket
import threading
import time
import numpy as np
import PacketUDP

ADRESS = ('localhost', 1118)
PACKET_NUM = 12
VER = 2
TYPE = 0
OVERTIME = 200  # ms
flagcontinue = True
lock = threading.Lock()  # flagcontinue的对象锁
lock1 = threading.Lock()  # GetACK的对象锁
GetACK = set()
send_again = [0 for _ in range(0, 13)]
ACK_unique = [0 for _ in range(0, 13)]

tot_receive_RTT = []
tot_receive_servertime = []


def receive_packet():
    global clientsocket
    while True:
        lock.acquire()
        if not flagcontinue:
            lock.release()
            break
        try:
            # 尝试接收数据
            data, (clientip, clientPort) = clientsocket.recvfrom(1024)
            packet_received = PacketUDP.PacketUDP.unpack(data)
            # 收到的ACK包把他的RTT与servertime放入列表中
            RTT = (time.time() - packet_received.timestamp) * 1000
            print(
                f"sequnce no: {packet_received.seq_no}, {clientip}:{clientPort}, RTT: {RTT} , servetime:{packet_received.server_time}")
            tot_receive_RTT.append(RTT)
            tot_receive_servertime.append(packet_received.server_time)
            lock1.acquire()
            GetACK.add(packet_received.seq_no)
            lock1.release()
            # print(packet_received.seq_no)
        except BlockingIOError:
            # 如果没有数据可用，继续循环
            pass
        lock.release()
        time.sleep(0.1)
    # print("OUT")


def check_packet(seq_no):
    global tot_receive
    time.sleep(OVERTIME / 1000)
    lock1.acquire()
    if seq_no in GetACK and ACK_unique[seq_no] == 0:
        lock1.release()
        tot_receive += 1
        ACK_unique[seq_no] = 1
    elif send_again[seq_no] < 2:
        lock1.release()
        send_again[seq_no] += 1
        # print('重传:', seq_no)
        print(f"sequnce no: {seq_no}, request time out")
        send_packet(seq_no)
        checkit = threading.Thread(target=check_packet(seq_no))
        checkit.start()
        # print("finish",seq_no)
    else:
        GetACK.add(seq_no)
        lock1.release()
        print('重传再次失败!', seq_no)


def send_packet(seg_no):
    global tot_send
    tot_send += 1
    data = PacketUDP.PacketUDP(seq_no=seg_no, ver=2, my_type=0)
    clientsocket.sendto(data.pack(), ADRESS)


def check_flag():
    global flagcontinue
    while True:
        lock.acquire()
        if not flagcontinue:
            lock.acquire()
            break
        # print("长度: ", len(GetACK) + len(send_again))
        lock1.acquire()
        if len(GetACK) == PACKET_NUM:
            flagcontinue = False
            lock.release()
            lock1.release()
            break
        lock.release()
        lock1.release()
        time.sleep(0.1)
    # print('outagain')


def Print():
    len_tot = len(tot_receive_RTT)
    print("收到的udp packets数目", len(tot_receive_RTT))
    print("丢包率", f"{1 - tot_receive / tot_send:.5f}")
    print("RTT的最大值: ", np.max(tot_receive_RTT) if len_tot else 0)
    print("RTT的最小值: ", np.min(tot_receive_RTT) if len_tot else 0)
    print("RTT的平均值: ", np.average(tot_receive_RTT) if len_tot else 0)
    print("RTT的标准差: ", np.std(tot_receive_RTT) if len_tot else 0)
    if len_tot:
        maxt = max(tot_receive_servertime)
        mint = min(tot_receive_servertime)
        tot1 = int(maxt[:2]) * 3600 + int(maxt[3:5]) * 60 + int(maxt[6:8])
        tot2 = int(mint[:2]) * 3600 + int(mint[3:5]) * 60 + int(mint[6:8])
        h = (tot1 - tot2) // 3600
        m = (tot1 - tot2 - h * 3600) // 60
        s = tot1 - tot2 - h * 3600 - m * 60
        print(maxt, mint)
        print(f"server的整体响应时间:{h}小时{m}分钟{s}秒")
    else:
        print("数据包全部丢失!")


def build_link():
    global clientsocket
    data = PacketUDP.PacketUDP(seq_no=0, ver=2, my_type=2, content='hello')
    clientsocket.sendto(data.pack(), ADRESS)
    data, _ = clientsocket.recvfrom(1024)
    packet_received = PacketUDP.PacketUDP.unpack(data)
    if packet_received.my_type == 3:
        print('server: ', packet_received.content)
        data = PacketUDP.PacketUDP(seq_no=0, ver=2, my_type=4, content='hello')
        clientsocket.sendto(data.pack(), ADRESS)
    print("已与服务器建立连接！")


def release_link():
    global clientsocket
    data = PacketUDP.PacketUDP(seq_no=0, ver=2, my_type=5, content='goodbye')
    clientsocket.sendto(data.pack(), ADRESS)
    data, _ = clientsocket.recvfrom(1024)
    packet_received = PacketUDP.PacketUDP.unpack(data)
    if packet_received.my_type == 6:
        print('server: ', packet_received.content)
        data, _ = clientsocket.recvfrom(1024)
        packet_received = PacketUDP.PacketUDP.unpack(data)
        if packet_received.my_type == 5:
            print('server: ', packet_received.content)
            data = PacketUDP.PacketUDP(seq_no=0, ver=2, my_type=6, content='goodbye')
            clientsocket.sendto(data.pack(), ADRESS)


if __name__ == "__main__":
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientsocket.connect_ex(ADRESS)
    # 模拟TCP的连接建立过程，这里是阻塞式的，保证成功建立连接。
    build_link()

    clientsocket.setblocking(False)
    receiver = threading.Thread(target=receive_packet)
    check_finish = threading.Thread(target=check_flag)
    receiver.start()
    check_finish.start()
    cnt = 1
    tot_send, tot_receive = 0, 0
    while cnt <= PACKET_NUM:
        send_packet(cnt)
        checkout = threading.Thread(target=check_packet(cnt))
        checkout.start()
        cnt += 1
        time.sleep(0.2)
    # print(flagcontinue)
    # print(len(GetACK))
    receiver.join()
    check_finish.join()
    clientsocket.setblocking(True)
    # 模拟TCP连接释放的过程
    release_link()
    clientsocket.close()
    print('已与服务器断开连接！')
    Print()
