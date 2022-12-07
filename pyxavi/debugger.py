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
