#!/usr/bin/env python
"""
Print a description of a MIDI file.
"""

import sys, os
import mydy

if len(sys.argv) != 2:
    print("Usage: {0} <midifile>".format(sys.argv[0]))
    sys.exit(2)

midifile = sys.argv[1]
pattern = mydy.FileIO.read_midifile(midifile)
print(repr(pattern))
