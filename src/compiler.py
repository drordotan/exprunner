#!/opt/rh/rh-python35/root/usr/bin/python

import sys
import os
import expcompiler.parser

if len(sys.argv) != 3:
    print("Usage: {} <source-file-xlsx> <target-file-html>".format(os.path.basename(sys.argv[0])))
    sys.exit(1)

rc = expcompiler.compile.compile_exp(sys.argv[1], sys.argv[2])
sys.exit(rc)
