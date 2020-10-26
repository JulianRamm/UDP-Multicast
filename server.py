import socket
import struct
import time
import cv2
import math
import numpy as np


class FrameSegment(object):
    """
    Object to break down image frame segment
    if the size of image exceed maximum datagram size
    """
    MAX_DGRAM = 2 ** 16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64  # extract 64 bytes in case UDP frame overflown

    def __init__(self, sock, port, addr="224.3.29.71"):
        self.s = sock
        self.port = port
        self.addr = addr

    def udp_frame(self, img):
        """
        Compress image and Break down
        into data segments
        """
        compress_img = cv2.imencode('.jpg', img)[1]
        dat = compress_img.tobytes()
        size = len(dat)
        count = math.ceil(size / (self.MAX_IMAGE_DGRAM))
        array_pos_start = 0
        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            self.s.sendto(struct.pack("B", count) +
                          dat[array_pos_start:array_pos_end],
                          (self.addr, self.port)
                          )
            array_pos_start = array_pos_end
            count -= 1


def main():
    port = 10000
    multicastIp = "224.3.29.71"
    videoToStream = ""
    bufferSize = 1024
    # Create the datagram socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    sock.settimeout(0.2)
    # Set the time-to-live for messages to 1 so they do not go past the
    # local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    fs = FrameSegment(sock, port, multicastIp)
    try:
        print("Canales disponibles:")
        print(" (1) video1.mp4")
        print(" (2) video2.mp4")
        print(" (3) video3.mp4")
        print("----------------")
        canal = int(input("Ingrese el número del canal al que quiere conectarse (1, 2 o 3): "))
        multicast_group = (multicastIp, 10000)
        videoToStream = "./videos/video1.mp4"
        cap = cv2.VideoCapture(videoToStream)
        # Send data to the multicast group
        print('Enviando video%s' % (str(canal) + ".mp4"))
        while cap.isOpened():
            ret, frame = cap.read()
            fs.udp_frame(frame)
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
        cap.release()
        cv2.destroyAllWindows()
    finally:
        print('closing socket')
        sock.close()


if __name__ == "__main__":
    main()
