==========
AIMDV Client
==========

This is for SNS AIMDV(AI based Mood Detection thru Voice) clients, who want to install and test mood detection engine in PC or embedded environment, esp., in Android.

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


Basic Usage
================

.. code:: bash

  aimdvcli <command> [options]


Audio Format Converter
=========================

This is a format converter to standardize the wave format to fit into AIMIDV embedded version.

.. code:: bash

  aimdvcli convert [options]
  
*options:*

.. code:: bash

  -s, --source-dir <source directory>
  -o, --output-dir <output directory>: optional, default is <source directory>/AIMDV
  -r:  recursive converting
      --help 

*example:*

.. code:: bash

  aimdvcli convert -s /home/ubuntu/audios


Change Logs
=============

- 0.1a1

  - project initialized
  
		