
import expcompiler


#-----------------------------------------------------------------------------
def compile_exp(src_fn, target_fn, local_imports, reader=None, logger=None):
    """
    Compile an experiment from Excel into a javascript file

    :param src_fn:
    :param target_fn:
    :param reader:
    :param logger:
    """
    logger = logger or expcompiler.logger.Logger()
    parser = expcompiler.parser.Parser(src_fn, reader=reader, logger=logger)
    generator = expcompiler.generator.ExpGenerator(logger=logger, imports_local=bool(int(local_imports)))

    exp = parser.parse()
    if exp is None:
        return 2

    script = generator.generate(exp)
    if script is None:
        return 2

    with open(target_fn, 'w', encoding="utf-8") as fp:
        fp.write(script)

    if parser.warnings_found:
        return 53

    return 0
