#!/usr/bin/env python

'''
This small module handles some error reporting for several
python classes.

The module assumes that the callingClass provides these methods:

    o callingClass.name()       -- returns the string name of the class
    o callingClass.log()        -- returns a Message() object member that
                                   is used a 'log' destination

Also, the callingClass must have a class dictionary, _dictErr, in which each
key has a dictionary of 'action', 'error', 'exitCode':

    callingClass._dictErr = {
        'someKey':      {
            'action':   'some action being performed,',
            'error':    'the error that occured',
            'exitCode': <int>
        }
    }

'''

import  inspect
import  sys

try: 
    from    ._colors    import Colors
    from    .message    import Message
except:
    from    _colors     import Colors
    from    message     import Message


class slog(object):
    """
    A simple class that simply appends to an internal
    'payload' each time it is called.
    """

    def syslog(self, *args):
        if len(args):
            self.b_syslog = args[0]
        else:
            return self.b_syslog

    def __init__(self, *args, **kwargs):
        self.str_payload    = ""
        self.b_syslog       = False

    def clear(self):
        self.str_payload    = ""

    def __call__(self, astr):
        self.str_payload += str(astr)

    def border_draw(self):
        l_padding = 2
        r_padding = 4

        msg_list = self.str_payload.split('\n')
        msg_list = [ x.replace('\t', '       ') for x in msg_list]
        l_c0    = [x.count('\x1b[0;')*7 for x in msg_list]
        l_c1    = [x.count('\x1b[1;')*7 for x in msg_list]
        l_nc    = [x.count('\x1b[0m')*4 for x in msg_list]
        l_offset = [x + y + z for x, y, z in zip(l_c0, l_c1, l_nc)]
        msg_listNoEsc   = [(len(x) - w) for x, w in zip(msg_list, l_offset)]
        width   = max(msg_listNoEsc)
        h_len   = width + l_padding + r_padding
        top_bottom = ''.join(['+'] + ['-' * h_len] + ['+']) + '\n'
        result = top_bottom

        for m, l in zip(msg_list, msg_listNoEsc):
            spaces   = h_len - l
            l_spaces = ' ' * l_padding
            r_spaces = ' ' * (spaces - l_padding)
            result += '|' + l_spaces + m + r_spaces + '|\n'

        result += top_bottom
        return result

    def __repr__(self):
        return self.str_payload

def report(     callingClass,
                astr_key,
                ab_exitToOs     = 1,
                astr_header     = "",
                **kwargs
                ):
    '''
    Error handling.

    Based on the <astr_key>, error information is extracted from
    _dictErr and sent to log object.

    If <ab_exitToOs> is False, error is considered non-fatal and
    processing can continue, otherwise processing terminates.

    '''

    astr_header         = ""
    ab_exitToOS         = False
    ab_drawBox          = False
    for k, v in kwargs.items():
        if k == 'header':   astr_header     = v
        if k == 'exitToOS': ab_exitToOS     = v
        if k == 'drawBox':  ab_drawBox      = v

    if ab_drawBox:
        log     = slog()
    else:
        log     = Message()

    b_syslog    = log.syslog()
    log.syslog(False)
    if ab_exitToOs: log( Colors.RED +    ":: FATAL ERROR :: " + Colors.NO_COLOUR )
    else:           log( Colors.YELLOW + "::   WARNING   :: " + Colors.NO_COLOUR )
    if len(astr_header): log( Colors.BROWN + astr_header + Colors.NO_COLOUR )
    log( "\n" )
    log( "\tSorry, some error seems to have occurred in:\n\n\t\t<" )
    try:
        caller = inspect.stack()[3][4][0].strip()
    except:
        caller = '__main__'
    log( Colors.LIGHT_GREEN + ("%s" % callingClass.__class__.__name__) + Colors.NO_COLOUR + "::")
    log( Colors.LIGHT_CYAN + ("%s" % caller) + Colors.NO_COLOUR)
    log( ">\n\n")

    log( "\tWhile %s\n" % callingClass._dictErr[astr_key]['action'] )
    log( "\t%s\n" % callingClass._dictErr[astr_key]['error'] )
    log( "\n" )
    log( "Returning with error code %s%d%s" % (
                    Colors.YELLOW,
                    callingClass._dictErr[astr_key]['exitCode'],
                    Colors.NO_COLOUR
                    )
    )

    if ab_drawBox:
        print(log.border_draw())
    if ab_exitToOS:
        sys.exit( callingClass._dictErr[astr_key]['exitCode'] )
    log.syslog(b_syslog)
    return callingClass._dictErr[astr_key]['exitCode']

def fatal( callingClass, astr_key, **kwargs ):
    '''
    Convenience dispatcher to the error_exit() method.

    Will raise "fatal" error, i.e. terminate script.
    '''
    kwargs['exitToOS']  = True
    report( callingClass, astr_key, **kwargs )


def warn( callingClass, astr_key, **kwargs ):
    '''
    Convenience dispatcher to the error_exit() method.

    Will raise "warning" error, i.e. script processing continues.
    '''
    kwargs['exitToOS']  = False
    report( callingClass, astr_key, **kwargs )

    
    