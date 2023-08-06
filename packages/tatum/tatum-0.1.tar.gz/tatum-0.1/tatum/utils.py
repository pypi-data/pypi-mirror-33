
def accepts(*types):
    """ from https://www.python.org/dev/peps/pep-0318/ """
    def check_accepts(f):
        assert len(types) == f.func_code.co_argcount

        def new_f(*args, **kwds):
            for (a, t) in zip(args, types):
                assert isinstance(a, t), \
                       "arg %r does not match %s" % (a,t)
            return f(*args, **kwds)

        new_f.func_name = f.func_name
        return new_f

    return check_accepts