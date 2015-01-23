"""
Example usage of UNO, graphic objects and networking in LO extension
"""

import errno
import logging
import socket
import struct
import uno
import unohelper
import uuid
from com.sun.star.beans import PropertyValue
from com.sun.star.task import XJobExecutor
from PIL import Image

# Network functions

def create_socket(server_addr, server_port):
    """Creates socket, connects to server. Returns socket"""

    logging.info("Server address: {}:{}".format(server_addr, server_port))
    logging.info("Creating socket...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        logging.error("Socket creation failed with error {}".format(err))
        return None

    logging.info("Connecting...")
    try:
        sock.connect((server_addr, server_port))
    except socket.error as err:
        logging.error("Connecting failed with error {}".format(err))
        return None

    return sock

def send_image(sock, image_size, image_bytes):
    """Sends image to open and set socket"""

    logging.info("Image size in bytes: {}".format(image_size))
    logging.info("Sending data...")

    sz_bytes = struct.pack("i", image_size)

    try:
        sock.send(sz_bytes)
    except socket.error as err:
        logging.error("Error sending data: {}".format(err))
        return None

    try:
        sock.send(image_bytes)
    except socket.error as err:
        logging.error("Error sending data: {}".format(err))
        return None
    return 1

def recv_bytes(sock, data_sz):
    """Receive exactly sz bytes from sock"""

    data = ""
    while len(data) < data_sz:
        try:
            data += sock.recv(data_sz, socket.MSG_WAITALL)
        except socket.error as err:
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                logging.info("No data, trying again")
                continue
            else:
                logging.error("Socket error: {}".format(err))
                break

    if len(data) < data_sz:
        logging.warning("Server send no data")
        return None

    return data

def recv_image(sock):
    """Receive image data from server socket"""

    data_sz_bytes = recv_bytes(sock, 4)
    if data_sz_bytes is None:
        logging.warning("Server send no data")
        return None

    data_sz = struct.unpack("i", data_sz_bytes)[0]
    logging.info("Will accept {} bytes of data".format(data_sz))

    img_data = recv_bytes(sock, data_sz)
    logging.info("img sz: {}".format(len(img_data)))
    if img_data is None:
        logging.warning("Server send lesser data than needed")
        return None

    return img_data

# Misc functions

def generate_tmp_path():
    """Generates unique temporary path to save image"""
    return "/tmp/" + str(uuid.uuid4()) + ".png"

class ImageExample(unohelper.Base, XJobExecutor):
    '''Class that implements the service registered in LibreOffice'''

    def __init__(self, context):
        self.context = context
        self.desktop = self.createUnoService("com.sun.star.frame.Desktop")
        self.graphics = self.createUnoService("com.sun.star.graphic.GraphicProvider")
        logging.basicConfig(filename="opencl_uno_example.log",
                            level=logging.WARNING)

    def createUnoService(self, name):
        return self.context.ServiceManager.createInstanceWithContext(name, self.context)

    def show_warning(self, title, msg):
        """Shows warning message box"""
        frame = self.desktop.ActiveFrame
        window = frame.ContainerWindow
        window.Toolkit.createMessageBox(
            window,
            uno.Enum('com.sun.star.awt.MessageBoxType', 'WARNINGBOX'),
            uno.getConstantByName("com.sun.star.awt.MessageBoxButtons.BUTTONS_OK"),
            title,
            msg).execute()

    def export_graphic(self, graphic, path):
        """Exports graphic to path"""
        logging.debug("exporting graphic {} to {}".format(graphic, path))

        url = unohelper.systemPathToFileUrl(path)
        props = ((PropertyValue("URL", 0, url, 0),
                  PropertyValue("MimeType", 0, "image/" + path[-3:], 0),))

        try:
            self.graphics.storeGraphic(graphic, props)
        except IOError as err:
            self.show_warning("I/O exception", "I/O exception: {}".format(err))

    def import_graphic(self, graphic, path, props):
        """Imports graphic from path by setting url in props"""
        logging.debug("importing graphic {} from {}".format(graphic, path))

        url = unohelper.systemPathToFileUrl(path)
        props.setPropertyValue("GraphicURL", url)

    def make_grayscale(self, graphic, props, sock):
        """
        Makes graphic grayscale

        This methods pass graphic to server socket sock and receive processed
        image. Image then imported to LO and new url sets in props.
        """
        path = generate_tmp_path()
        logging.debug("making grayscale image {}".format(path))

        self.export_graphic(graphic, path)

        try:
            image = Image.open(path)
        except IOError as err:
            logging.warning("Cannot open image {}".format(path))
            self.show_warning("Image error", "Cannot open {}".format(path))
            return

        raw_data = image.tobytes()

        if send_image(sock, len(raw_data), raw_data) is None:
            logging.warning("Cannot send image {}".format(path))
            self.show_warning("Network error", "Cannot send image")
            return

        processed_image_raw = recv_image(sock)
        if processed_image_raw is None:
            logging.warning("Failed to receive image. Exiting")
            self.show_warning("Network error", "Cannot receive image.")
            return

        try:
            processed_image = Image.frombytes(image.mode, image.size,
                                              processed_image_raw)
        except ValueError as err:
            self.show_warning("Value error",
                              "Cannot save image: {}.".format(err))
            return

        path = generate_tmp_path()
        processed_image.save(path)

        self.import_graphic(graphic, path, props)

    def trigger(self, args):
        """This method provides options for ImageExample service"""

        if args == 'show_warning':
            self.show_warning("Warning", "Warning description here")
        elif args == 'export_images':
            component = self.desktop.CurrentComponent
            graphics = component.getGraphicObjects()

            if not graphics.hasElements():
                self.show_warning("No images",
                                  "This document contains no images. Nothing to do.")
                return

            for name in graphics.getElementNames():
                props = graphics.getByName(name)

                url = props.getPropertyValue("GraphicURL")
                props = ((PropertyValue("URL", 0, url, 0)), )

                graphic = self.graphics.queryGraphic(props)
                self.export_graphic(graphic, generate_tmp_path())

        elif args == "grayscale_images":
            component = self.desktop.CurrentComponent

            try:
                graphics = component.getGraphicObjects()
            except AttributeError:
                self.show_warning("Attribute Error",
                                  "This LO component is not supported")
                return

            if not graphics.hasElements():
                self.show_warning("No images",
                                  "This document contains no images. Nothing to do.")
                return

            # TODO: create some config for this
            server_addr = "192.168.1.241"
            server_port = 9000

            for name in graphics.getElementNames():
                props = graphics.getByName(name)

                url = props.getPropertyValue("GraphicURL")
                props_url = ((PropertyValue("URL", 0, url, 0)), )

                graphic = self.graphics.queryGraphic(props_url)

                sock = create_socket(server_addr, server_port)
                if sock is None:
                    logging.error("Cannot create or set up socket. Exiting")
                    self.show_warning("Network error", "Cannot create socket.")
                    return

                self.make_grayscale(graphic, props, sock)
                sock.close()


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    ImageExample,
    'org.libreoffice.imageexample.ImageExample',
    ('com.sun.star.task.JobExecutor',))
