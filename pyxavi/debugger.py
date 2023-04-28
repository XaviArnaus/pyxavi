def dd(var, prefix=''):
    """Function to print the inner of a variable

    You know you're a php developer when the first thing you ask for
    when learning a new language is 'Where's var_dump?????'

    Kindly stolen from:
    https://stackoverflow.com/questions/383944/what-is-a-python-equivalent-of-phps-var-dump

    :Authors:
        Xavier Arnaus <xavi@arnaus.net>

    """

    my_type = '[' + var.__class__.__name__ + '(' + str(len(var)) + ')]:'
    print(prefix, my_type, sep='')
    prefix += '    '
    for i in var:
        if type(i) in (list, tuple, dict, set):
            dd(i, prefix)
        else:
            if isinstance(var, dict):
                print(prefix, i, ': (', var[i].__class__.__name__, ') ', var[i], sep='')
            else:
                print(prefix, '(', i.__class__.__name__, ') ', i, sep='')

def full_stack():
    """
    `print full_stack()` will print the full stack trace up to the top, 
    including e.g. IPython's interactiveshell.py calls, 
    since there is (to my knowledge) no way of knowing who would catch exceptions. 
    It's probably not worth figuring out anyway...

    If `print full_stack()` is called from within an `except` block,
    `full_stack` will include the stack trace down to the raise. 
    In the standard Python interpreter, this will be identical to the message
    you receive when not catching the exception (Which is why that del stack[-1] is there,
    you don't care about the except block but about the try block).

    Kindly stolen from:
    https://stackoverflow.com/questions/6086976/how-to-get-a-complete-exception-stack-trace-in-python

    """
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr
