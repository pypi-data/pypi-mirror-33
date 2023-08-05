.. -*- coding: utf-8 -*-

===================
 Simulagora client
===================

Summary
-------

A python library to use Simulagora programatically either directly from the
command line or via a Python program.


Prerequisites
-------------

You will need a proper installation of cwclientlib_, which itself requires
Python 2.7 and `Python requests`_.

An account on Simulagora_ is of course also needed.


Using Simulagora client
-----------------------

#. Log in on Simulagora_ and consult the token that was generated for you at the
   `dedicated URL <https://www.simulagora.com/AuthToken>`_;

#. Create a ``cwclientlibrc`` file in your user's ``.config`` directory (only
   readable by yourself), like::

     [simulagora]
     url = https://www.simulagora.com
     token-id = the token id
     secret = the token itself


Examples
--------

Examples directly from the command line. Get a list of the studies you can
access:

.. code-block:: sh

    $ simulagora studies
    [{'eid': 4173, 'name': u'Study 1'},
     {'eid': 4277, 'name': u'Study 2'},
     {'eid': 4310, 'name': u'Study 3'}]
    $ simulagora executables
    [{'eid': 2454, 'name': u'Attente (secondes)'},
     {'eid': 2470, 'name': u'paraview'},
     {'eid': 4672, 'name': u'bash_command #0'},
     {'eid': 4883, 'name': u'lmgc90_donut'}]


A more complete example using Python. Create a "Code Aster piston test" study
and an eponym folder, upload the data in it, and run a Code Aster computation
with this data as an input on a "m1.large" server, equiped with the last
Simulagora machine image (which currently has Code Aster 11.5):

.. code-block:: python

   from simulagora import Simulagora
   from time import sleep

   client = Simulagora.for_instance('simulagora')

   # create the folder, upload the files and get their identifiers
   folder = client.create_folder('Code Aster piston test')
   file_eids = client.upload_files(folder, 'piston.comm', 'piston.mmed', 'piston.export')

   # get the "bash command" executable which will run the "as_run" command
   executable = client.find_one('Executable', name='bash command')
   params = {'command': 'as_run piston.export'}

   # get the server type, create the study and the run, then start it
   server_type = client.find_one('CloudServerType', name='m3.xlarge')
   study = client.create_study('Code Aster piston test')
   run = client.create_run(study, executable, server_type, file_eids, params)
   client.start_run(run)

   # check its state every 5 seconds until its crashed or completed
   state = None
   while state not in ('wfs_run_crashed', 'wfs_run_completed'):
       state = client.state(run)
       sleep(5)
   print "Run " + state.rsplit('_', 1)[-1]

.. _Simulagora: https://www.simulagora.com
.. _cwclientlib: http://www.cubicweb.org/project/cwclientlib
.. _`Python requests`: http://docs.python-requests.org/en/latest
