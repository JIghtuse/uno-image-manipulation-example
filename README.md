# UNO image manipulation example
This repo contains example extension for LibreOffice. It shows how to use UNO
and Python to extract and manipulate images in LibreOffice Writer document.

This plugin is self contained in that it contains the full source to build
itself. To do so, unpack the oxt-extension with any program able to read the
zip format. Running the script './build' in the unpacked source tree, will
then recreate the extension (and possible modifications).

Following below is a description of all the files in this extension and how
LibreOffice learns what to do with them.

## Extension entry points

* ./description.xml
  This file (and those that it references) describes the extension, its license
  in a human readable form.
* ./META-INF/manifest.xml
  This file explains the contents of the extension for LibreOffice to inject.

## Files referenced from description.xml

* ./description/license.txt
  License shown to the user on installation.
* ./description/description_en.txt
  Human readable description to show e.g. in the extension manager.
* ./description/extensionicon.png
  Icon to show e.g. in the extension manager
* ./description/icon.xcf
  Icon source image from GIMP

## Files referenced from manifest.xml

* ./uno\_image.py
  Python script that implements a service called
  org.libreoffice.imageexample.ImageExample
* ./Addons.xcu
  Describes how this extension wants to modify the toolbar. It adds an icon
  "Grayscale images" that triggers the
  org.libreoffice.imageexample.ImageExample service with "show_warning"
  argument.
* ./images/
  Images in this folder used by Addons.xcu to add icon to new button.

## Files not referenced anywhere and ignored at runtime

* ./build
  A simple python script that packs the extension from the unpacked source.
* ./extensionname.txt
  A file hinting ./build how to name the produced .oxt file.
* ./README.md
  This file.
