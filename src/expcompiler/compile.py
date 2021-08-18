
import expcompiler


#todo: "trial types" worksheet is optional. If omitted, all items appear without time limit. If responses are defined, they will be all used. If not, SPACE will advance to the next trial.

#-----------------------------------------------------------------------------
def compile_exp(src_fn, target_fn, reader=None, logger=None):
    """
    Compile an experiment from Excel into a javascript file

    :param src_fn:
    :param target_fn:
    :param reader:
    :param logger:
    """
    logger = logger or expcompiler.logger.Logger()
    parser = expcompiler.parser.Parser(src_fn, reader=reader, logger=logger)
    generator = expcompiler.generator.ExpGenerator(logger=logger)

    exp = parser.parse()
    if exp is None:
        return 2

    script = generator.generate(exp)
    if script is None:
        return 2

    with open(target_fn, 'w') as fp:
        fp.write(script)

    if parser.warnings_found:
        return 53

    return 0
