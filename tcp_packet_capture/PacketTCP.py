import struct
from abc import ABC, abstractmethod

'''
Initialization 报文:
Type            2B  --- 1
N               4B  ---请求server来reverse的块数


agree 报文:
Type            2B  --- 2


ReverseRequest 报文:
Type            2B  --- 3
Length          4B  --- Data的长度
Data            194B

ReverseAnswer 报文:
Type            2B  --- 3
Length          4B  --- reverseData 的长度
reverseData     194B

'''
DATA_MAX_LEN = 194


class PacketTCP(ABC):
    @abstractmethod
    def pack(self):
        pass

    @classmethod
    @abstractmethod
    def unpack(cls, data):
        pass

    @abstractmethod
    def callme(self):
        pass


class Initialization(PacketTCP):
    def __init__(self, Type, N):
        self.Type = Type
        self.N = N

    def callme(self):
        return 'Initialization'

    def pack(self):
        format_string = "!H I"
        data = self.Type, self.N
        return struct.pack(format_string, *data)

    @classmethod
    def unpack(cls, data):
        format_string = "!H I"
        Type, N = struct.unpack(format_string, data)
        return cls(Type=Type, N=N)


class Agree(PacketTCP):
    def __init__(self, Type):
        self.Type = Type

    def callme(self):
        return 'Agree'

    def pack(self):
        format_string = "!H"
        data = self.Type,
        return struct.pack(format_string, *data)

    @classmethod
    def unpack(cls, data):
        format_string = "!H"
        Type, = struct.unpack(format_string, data)
        return cls(Type=Type)


class ReverseRequest(PacketTCP):
    def __init__(self, Type, Length, Data):
        self.Type = Type
        self.Length = Length
        self.Data = Data

    def callme(self):
        return 'ReverseRequest'

    def pack(self):
        format_string = "!H I 200s"
        Data_Actual = self.Data.ljust(DATA_MAX_LEN)[:DATA_MAX_LEN]
        data = self.Type, self.Length, Data_Actual.encode('utf-8')
        return struct.pack(format_string, *data)

    @classmethod
    def unpack(cls, data):
        format_string = "!H I 200s"
        Type, Length, Data = struct.unpack(format_string, data)
        Data = Data.decode('utf-8').strip('\x00')
        return cls(Type=Type, Length=Length, Data=Data)


class ReverseAnswer(PacketTCP):
    def __init__(self, Type, Length, reverseData):
        self.Type = Type
        self.Length = Length
        self.reverseData = reverseData

    def callme(self):
        return 'ReverseAnswer'

    def pack(self):
        format_string = "!H I 200s"
        reverseData_Actual = self.reverseData.ljust(DATA_MAX_LEN)[:DATA_MAX_LEN]
        data = self.Type, self.Length, reverseData_Actual.encode('utf-8')
        return struct.pack(format_string, *data)

    @classmethod
    def unpack(cls, data):
        format_string = "!H I 200s"
        Type, Length, reverseData = struct.unpack(format_string, data)
        reverseData = reverseData.decode('utf-8').strip('\x00')
        return cls(Type=Type, Length=Length, reverseData=reverseData)
