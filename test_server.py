"""Test server for image processing"""

import logging
import socket
import errno
import struct
import time
from PIL import Image

def get_image_data(csock):
    """Gets image data from client socket"""

    data_sz_bytes = ""

    while len(data_sz_bytes) < 4:
        try:
            data_sz_bytes += csock.recv(4, socket.MSG_WAITALL)
        except socket.error as err:
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                logging.info("No data")
                time.sleep(1)
                continue
            else:
                logging.error("Socket error: {}".format(err))
                break

    if len(data_sz_bytes) < 4:
        logging.warning("Client said he wouldn't sent a data")
        return None, None

    data_sz = struct.unpack("i", data_sz_bytes)[0]
    logging.info("Will accept {} bytes of data".format(data_sz))

    raw_data = ""

    while len(raw_data) < data_sz:
        try:
            raw_data += csock.recv(data_sz, socket.MSG_WAITALL)
        except socket.error as err:
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                logging.info("No data")
                time.sleep(1)
                continue
            else:
                logging.error("Socket error: {}".format(err))
                break

    if len(raw_data) < data_sz:
        logging.warning("Client send lesser data than needed")
        return None, None

    return data_sz, raw_data

def send_image(sock, image_size, image_bytes):
    """Sends image to open and set socket"""

    logging.info("Image size in bytes: {}".format(image_size))
    logging.info("Sending data...")

    sz_bytes = struct.pack("i", image_size)

    try:
        sock.send(sz_bytes)
    except socket.error as err:
        logging.error("Error sending data: {}".format(err))
        return

    try:
        sock.send(image_bytes)
    except socket.error as err:
        logging.error("Error sending data: {}".format(err))
        return

def run_server(port=9000):
    """Starts server listening for connections on port 9000"""

    try:
        sock = socket.socket()
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))

    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as err:
        logging.error("Socket set failed with error {}".format(err))

    try:
        sock.bind(("", port))
    except socket.error as err:
        logging.error("Socket binding failed with error {}".format(err))

    try:
        sock.listen(5)
    except socket.error as err:
        logging.error("Socket listen failed with error {}".format(err))

    logging.info("Started listening for connections")

    while True:
        csock, addr = sock.accept()
        logging.info("Got connection from {}".format(addr))

        img_sz, img_data = get_image_data(csock)
        if img_data is None:
            logging.warning("Failed to get image data from client")
            csock.close()
            continue

        logging.info("Got image!")

        img_data = "\x00" * img_sz

        send_image(csock, img_sz, img_data)
        csock.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_server()
