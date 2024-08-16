#! /usr/bin/env python3

import socket, sys, re, os, time
sys.path.append("../lib")     # for params
import params
from buf import BufferedFdReader, BufferedFdWriter

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

paramMap = params.parseParams(switchesVarDefaults)
server, usage = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af,socktype,proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error : %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)

while True:
    files = input("Input Files to send [to stop enter 'stop': ")
    files = files.split()
    if 'stop' in files:
        break
    archive = b''
    for file in files:
        curFile = os.open(file, os.O_RDONLY)
        reader = buf.BufferedFdReader(curFile)
        fileSize = os.path.getsize(file)

        header = bytearray(64)
        for i in range(len(file)):
            header[i] = file[i].encode()[0]
        for i in range(len(str(fileSize))):
            header[i+32] = str(fileSize)[i].encode()[0]
        data = reader.readByte()
        content = []
        while data is not None:
            content.append(data)
            data = reader.readByte()
        reader.close()

        fileCont = header + bytearray(content)
        archive  += fileCont
    s.send(archive)
s.shutdown(socket.SHUT_WR)
s.close()
