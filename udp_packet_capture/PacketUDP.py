import struct
import time

'''
UDP报文段格式：
seq_no          2B
ver             1B
timestamp       8B
my_type         1B    ———— 0表示client发送的普通数据报，1表示server发送的普通数据报，2表示client发
                           送的hello报文，3表示server发送的ACK hello报文，4表示client确认收到
                           server的ACK hello报文，5表示发送goodbye报文，6表示发送
                           的ACK goodbye报文
server_time     8B
content         183B

client报文——header长度：12
server报文——header长度：20
'''

CONTENT_MAX_LEN = 191


class PacketUDP:
    def __init__(self, seq_no, ver, my_type, server_time="", content="", timestamp=0):
        self.seq_no = seq_no
        self.ver = ver
        self.timestamp = time.time()
        self.my_type = my_type
        self.server_time = server_time
        self.content = content

    def pack(self):
        format_string = "!H B d B 10s 200s"
        content_Actual = self.content.ljust(CONTENT_MAX_LEN)[:CONTENT_MAX_LEN]  # 保证其长度一定不超过报文的长度
        data = self.seq_no, self.ver, self.timestamp, self.my_type, self.server_time.encode(
            'utf-8'), content_Actual.encode('utf-8')
        return struct.pack(format_string, *data)

    @classmethod
    def unpack(cls, data):
        format_string = "!H B d B 10s 200s"
        # 解包数据
        seq_no, ver, timestamp, my_type, server_time, content = struct.unpack(format_string, data)
        # 去除 content 中的字节
        content = content.decode('utf-8').strip('\x00')
        server_time = server_time.decode('utf-8').strip('\x00')
        return cls(seq_no=seq_no, ver=ver, timestamp=timestamp, my_type=my_type, server_time=server_time,
                   content=content)
