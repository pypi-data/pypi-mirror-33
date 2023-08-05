#!/usr/bin/python

"""
    Copyright Ryan Kirkbride 2015
    -----------------------------

    FoxDot: Live Coding with Python and SuperCollider

"""
from __future__ import absolute_import, division, print_function

from .lib import *

def main():
    """ Function for starting the GUI when importing the library """
    FoxDot = Workspace.workspace(FoxDotCode).run()
