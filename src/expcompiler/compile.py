
import expcompiler


#-----------------------------------------------------------------------------
def compile_exp(src_fn, target_fn, reader=None, logger=None):
    """
    Compile an experiment from Excel into a javascript file

    :param src_fn:
    :param target_fn:
    :param reader:
    :param logger:
    """
    parser = expcompiler.parser.Parser(src_fn, reader=reader, logger=logger)
    exp = parser.parse()

    if exp is None or parser.errors_found:
        return 2
    elif parser.warnings_found:
        return 1
    else:
        return 0

    #todo write the js file
