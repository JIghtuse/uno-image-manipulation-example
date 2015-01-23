"""
Example usage of UNO, graphic objects and networking in LO extension
"""

import logging
import uno
import unohelper
import uuid
from com.sun.star.beans import PropertyValue
from com.sun.star.task import XJobExecutor

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


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    ImageExample,
    'org.libreoffice.imageexample.ImageExample',
    ('com.sun.star.task.JobExecutor',))
