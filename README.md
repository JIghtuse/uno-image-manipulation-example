# UNO image manipulation example
This repo contains example extension for LibreOffice. It shows how to use UNO
and Python to extract and manipulate images in LibreOffice Writer document.

This plugin is self contained in that it contains the full source to build
itself. To do so, unpack the oxt-extension with any program able to read the
zip format. Running the script './build' in the unpacked source tree, will
then recreate the extension (and possible modifications).

## Running
How to run extension and how to change its behavior.

### Current state
Extension adds a new button to LibreOffice toolbar, which looks like this:
![Toolbar Icon](https://raw.githubusercontent.com/JIghtuse/uno-image-manipulation-example/master/images/imageexample_26.bmp)
For now, when user press this button, extension will export all images from
current document to /tmp folder. See file Addons.xcu for "URL" property (it
sets argument to ImageExample service).

### Changing behavior
Extension can send all images from current document to remote server, get
them back, and replace them in document. If remote server does some
processing of pixels (for example, makes them grayscale), it is possible to
apply some effect to all images in document at once.

To enable this behavior user needs to change argument passed to
ImageExample service (Addons.xcu: change "export\_images" in "URL" property
to "grayscale\_images") and set remote server address and port (uno\_image.py:
look for "TODO", set IP address of a server and its port). After that, it is
needed to build extension (run ./build) and install it to LibreOffice again.

## Limitations
* Extension assumes it is run on UNIX system with /tmp path. It is easy to fix
this limitation by changing code in generate\_tmp\_path().
* There is no any config to set server address and port to send images.
* Extension is dumb. It sends to server raw pixel values instead of original
image, assuming that server will not change image size or format.

## Files

Following below is a description of all the files in this extension and how
LibreOffice learns what to do with them.

### Extension entry points

* ./description.xml - This file (and those that it references) describes the
extension, its license in a human readable form.
* ./META-INF/manifest.xml - This file explains the contents of the extension
for LibreOffice to inject.

### Files referenced from description.xml

* ./description/license.txt - License shown to the user on installation.
* ./description/description\_en.txt - Human readable description to show e.g.
in the extension manager.
* ./description/extensionicon.png - Icon to show e.g. in the extension manager
* ./description/icon.xcf - Icon source image from GIMP

### Files referenced from manifest.xml

* ./uno\_image.py - Python script that implements a service called
org.libreoffice.imageexample.ImageExample
* ./Addons.xcu - Describes how this extension wants to modify the toolbar. It
adds an icon "Grayscale images" that triggers the
org.libreoffice.imageexample.ImageExample service with "export\_images" argument.
* ./images/ - Images in this folder used by Addons.xcu to add icon to new button.

### Files not referenced anywhere and ignored at runtime

* ./build - A simple python script that packs the extension from the unpacked source.
* ./extensionname.txt - A file hinting ./build how to name the produced .oxt file.
* ./README.md - This file.
* ./test_server.py - Example server for extension. It fills all received pixels with
\x00 value and sends them back.