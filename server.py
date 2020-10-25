import socket
import struct
import sys

message = 'very important data'
port = 0
multicastIp = "224.3.29.71"
videoToStream = ""
# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout(0.2)
# Set the time-to-live for messages to 1 so they do not go past the
# local network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
try:
    print("Canales disponibles:")
    print(" (1) video1.mp4")
    print(" (2) video2.mp4")
    print(" (3) video3.mp4")
    print("----------------")
    canal = int(input("Ingrese el número del canal al que quiere conectarse (1, 2 o 3): "))
    multicast_group = (multicastIp, 10000 + canal)
    videoToStream = "./videos/video"+canal+".mp4"

    # Send data to the multicast group
    print('Enviando "%s"' % "video "+canal+".mp4")
    sent = sock.sendto(message.encode("ascii"), multicast_group)
    # Look for responses from all recipients
    while True:
        print('waiting to receive')
        try:
            data, server = sock.recvfrom(16)
        except socket.timeout:
            print('timed out, no more responses')
            break
        else:
            print('received "%s" from %s' % (data, server))

finally:
    print('closing socket')
    sock.close()
