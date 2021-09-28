import sys
import expcompiler.parser

rc = expcompiler.compile.compile_exp('config_recent_probes_sample1.xlsx', "result.html")

sys.exit(rc)
