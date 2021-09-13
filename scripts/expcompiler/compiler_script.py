from expcompiler import compiler as c

comp = c.Compiler("config_recent_probes_sample1.xlsx", "result")

comp.compile()

print("finish")
