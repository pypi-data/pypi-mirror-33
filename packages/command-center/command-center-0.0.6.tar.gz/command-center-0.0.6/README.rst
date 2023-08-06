=====================
Python Command Center
=====================

Save and run terminal commands for frequent use.
Also supports a button grid GUI window for using a mouse.

Installation
============
Install from pypi using pip::

   pip install command-center

Usage
=====
Create a ``pcc.json`` file to hold your commands.::

   {
     "test": "pytest",
     "lint": "flake8"
   }

Then simply run pcc in the terminal with your command key.::

   $ pcc test

Note: You can run as many commands in sequential order as you want.
For example ``pcc test lint`` would run test and then lint.

If you forget key of your command you can run ``pcc --commands`` to get a list
of commands printed to the console.

GUI
===

If you want to display a button window for easy mouse use, use pcc-gui.::

   $ pcc-gui

Adding ``--help`` to pcc or pcc-gui will display helpful information.

