"""
Example usage of UNO, graphic objects and networking in LO extension
"""

import unohelper
from com.sun.star.task import XJobExecutor

class ImageExample(unohelper.Base, XJobExecutor):
    '''Class that implements the service registered in LibreOffice'''

    def __init__(self, context):
        self.context = context

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    ImageExample,
    'org.libreoffice.imageexample.ImageExample',
    ('com.sun.star.task.JobExecutor',))
