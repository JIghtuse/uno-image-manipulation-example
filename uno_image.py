"""
Example usage of UNO, graphic objects and networking in LO extension
"""

import uno
import unohelper
from com.sun.star.task import XJobExecutor

class ImageExample(unohelper.Base, XJobExecutor):
    '''Class that implements the service registered in LibreOffice'''

    def __init__(self, context):
        self.context = context
        self.desktop = self.createUnoService("com.sun.star.frame.Desktop")
        self.graphics = self.createUnoService("com.sun.star.graphic.GraphicProvider")

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

    def trigger(self, args):
        """This method provides options for ImageExample service"""
        
        if args == 'show_warning':
            self.show_warning("Warning", "Warning description here")

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    ImageExample,
    'org.libreoffice.imageexample.ImageExample',
    ('com.sun.star.task.JobExecutor',))
