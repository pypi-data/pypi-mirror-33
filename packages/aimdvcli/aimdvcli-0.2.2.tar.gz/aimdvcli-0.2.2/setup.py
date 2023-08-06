"""
Hans Roh 2015 -- http://osp.skitai.com
License: BSD
"""
import re
import sys
import os
import shutil, glob
import codecs
from warnings import warn
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

with open('aimdvcli/__init__.py', 'r') as fd:
	version = re.search(r'^__version__\s*=\s*"(.*?)"',fd.read(), re.M).group(1)

if sys.argv[-1] == 'publish':
	buildopt = ['sdist', 'upload']	
	if os.name == "nt":
		buildopt.insert (0, 'bdist_wheel')
	os.system('python setup.py %s' % " ".join (buildopt))
	for each in os.listdir ("dist"):
		os.remove (os.path.join ('dist', each))
	sys.exit()

classifiers = [
  'License :: OSI Approved :: MIT License',
  'Development Status :: 3 - Alpha',
  'Topic :: Database',
	'Intended Audience :: Developers',
	'Programming Language :: Python',	
	'Programming Language :: Python :: 3',	
]

packages = [
	'aimdvcli',	
	'aimdvcli.audio',	
]

package_dir = {'aimdvcli': 'aimdvcli'}
package_data = {}

install_requires = [
	"librosa",
	"aquests",
	"soundfile",
	"tqdm"
]

with codecs.open ('README.rst', 'r', encoding='utf-8') as f:
	long_description = f.read()
    
setup(
	name='aimdvcli',
	version=version,
	description='AIMDV Client',
	long_description=long_description,
	url = 'http://www.sns.co.kr/',
	author='Semicon Networks',
	author_email='hansroh@gmail.com',	
	packages=packages,
	package_dir=package_dir,
	package_data = package_data,
	entry_points = {
        'console_scripts': [
			'aimdvcli=aimdvcli.aimdvcli:main',
		],
    },
	license='MIT',
	platforms = ["posix", "nt"],
	download_url = "https://pypi.python.org/pypi/aimdvcli",
	install_requires = install_requires,
	classifiers=classifiers
)
