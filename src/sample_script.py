import sys
import expcompiler.parser

rc = expcompiler.compile.compile_exp('/Users/dror/data/projects/simple-experiment-runner/docs/config_recent_probes_sample1.xlsx',
                                '/Users/dror/temp/test.html')

sys.exit(rc)
