# pascalvoc-to-image

This repository contains a Python script that can easily cut images from annotated PascalVOC images. It will:

-   Read the directory containing the XMLs
-   Parse the XMLs to a readable format
-   Create images for all created bounding boxes in a separate folder

# Usage

Using the script is pretty simple, since it only has three parameters.


```
usage: pascalvoc-to-image [-h] pascalDirectory imageDirectory saveDirectory

positional arguments:
  pascalDirectory   A path to the directory with Pascal VOC XML files
  imageDirectory    A path to the directory with images
  saveDirectory     A path to the directory to save Pascal boundingbox images to

optional arguments:
  -h, --help  show this help message and exit
```

# Installation

## Pip

```
$ pip install pascalvoc-to-image
```

## Manual

```
$ git clone https://www.gitlab.com/jdreg95/pascalvoc-to-image.git
$ cd pascalvoc-to-image
$ sudo pip install .
```
