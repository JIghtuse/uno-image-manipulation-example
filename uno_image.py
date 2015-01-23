"""
Example usage of UNO, graphic objects and networking in LO extension
"""

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

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    ImageExample,
    'org.libreoffice.imageexample.ImageExample',
    ('com.sun.star.task.JobExecutor',))
