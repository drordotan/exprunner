import sys
import expcompiler.parser

d='/Users/dror/data/assessment-tests/numbers/MIM-v5/prepapre/איפה האפס/'
rc = expcompiler.compile.compile_exp(d+'where-is-0-demo-config.xlsx', d+"where_is_the_zero-generated.html")

sys.exit(rc)
