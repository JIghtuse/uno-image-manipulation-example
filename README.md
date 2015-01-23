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

* ./META-INF/manifest.xml
  This file explains the contents of the extension for LibreOffice to inject.

## Files referenced from manifest.xml

* ./uno\_image.py
  Python script that implements a service called
  org.libreoffice.imageexample.ImageExample

## Files not referenced anywhere and ignored at runtime

* ./build
  A simple python script that packs the extension from the unpacked source.
* ./extensionname.txt
  A file hinting ./build how to name the produced .oxt file.
* ./README.md
  This file.
