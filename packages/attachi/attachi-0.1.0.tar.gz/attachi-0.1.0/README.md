# Attachi
[![Language](https://img.shields.io/github/languages/top/qbicsoftware/attachi-cli.svg)](https://img.shields.io/github/languages/top/qbicsoftware/attachi-cli.svg)
[![Build Status](https://travis-ci.org/qbicsoftware/attachi-cli.svg?branch=master)](https://travis-ci.org/qbicsoftware/attachi-cli)


A small helper script, that creates the folder structure needed to register files as attachment to openBIS.

## Installation

### Stable release from PyPi:

``pip install attachi``

### Current master branch:

``pip install git+https://github.com/qbicsoftware/attachi-cli``

or from a specific branch:

``pip install git+https://github.com/qbicsoftware/attachi-cli@<branch>``

## Run

```pyhton
> attachi --help
Usage: attachi [OPTIONS] PROJECTID FILE COMMENT

  Attachi - A helper tool that prepares attachments for openBIS registration

Options:
  -u, --user ID      Username shown in openbis as uploader
  -o, --outdir PATH  Output folder path
  --version          Show the version and exit.
  --help             Show this message and exit.

```
# Example

Creating the folder structure for an upload:

```python

attachi -u myusername QABCD README.md "this is a test for uploading the readme file"

#--> folder QABCD000AQ_20180627102707758164 is created
```

Use tar and dync to upload the file to openBIS:

```bash
tar -c QABCD000AQ_20180627102707758164 | dync -n QABCD000AQ_20180627102707758164.tar -k untar:True data.qbic.uni-tuebingen.de
```

