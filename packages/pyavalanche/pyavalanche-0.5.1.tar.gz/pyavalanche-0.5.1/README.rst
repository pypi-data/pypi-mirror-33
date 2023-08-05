
Todo:
samples
docs

This package implements Python OO API for Avalanche.

Functionality
"""""""""""""
The current version supports the following test flow:
	Load configuration -> Get/Set attributes -> Start/Stop traffic -> Get statistics.
Supported operations:
	- Basic operations - get/set attributes, get/create children.
	- Connect - to chassis
	- Load configuration - load configuration (spf), select test, reserve ports and assign ports to interfaces
	- Test - start, stop, wait, get status
	- Statistics - subscribe, read views, unsubscribe
	- Save configuration
	- Disconnect

Prerequisite
""""""""""""
Avalanche application installed.
Tcllib package installed.

Installation
""""""""""""
pip instsll pyavalanche

Getting started
"""""""""""""""
Under avalanche.test.avl_samples you will find some basic samples.
See inside for more info.

Documentation
"""""""""""""
http://pyavalanche.readthedocs.io/en/latest/

Related work
""""""""""""
pytestcenter, pyixload

Contact
"""""""
Feel free to contact me with any question or feature request at yoram@ignissoft.com
