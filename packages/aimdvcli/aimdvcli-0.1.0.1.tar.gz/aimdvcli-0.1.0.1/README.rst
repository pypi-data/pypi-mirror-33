====================
AIMDV Client
====================

This is for **SNS AIMDV (AI based Mood Detection thru Voice)** clients, who want to install and test mood detection engine in PC or embedded environment, esp., in Android.

.. contents:: Table of Contents


Installation
=========================

Requirements
--------------------------

- OS: Windows, Linux, Mac
- Python 3.4+

Installataion
--------------------------

.. code:: bash
  
  pip install aimdvcli  
  # or
  pip3 install aimdvcli
  
  # for updating  
  pip install -U aimdvcli


Basic Usage
================

Type like this at your console,

.. code:: bash

  aimdvcli <command> [options]


Audio Format Converter
=========================

This is a audio format converter to standardize the wave format to fit into AIMIDV embedded version. It can convert all files of the directory you specify, and save into target directory.

Target format:

- sampling rate: 22,050
- quantization bit: 16 bit
- channels: 1 (mono)

.. code:: bash

  aimdvcli convert [options]
  
*options:*

.. code:: bash

      --help: display help
  -s, --source-dir <source directory>
  -o, --output-dir <output directory>: optional, default is <source directory>/AIMDV
  -r:  convert all audio files and their sub directories recursively
       

*example:*

.. code:: bash
  
  # convert all audios in testset directory recursively
  aimdvcli convert -rs ./testset -o ./output


Change Logs
=============

- 0.1

  - project initialized
  
		