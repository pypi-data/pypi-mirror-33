try:
    from ._colors   import Colors
    from .debug     import debug
    from .message   import Message
    from .pfmisc    import pfmisc
    from .pfmisc2   import pfmisc2
    from .other     import *
    from .error     import *
except:
    from _colors    import Colors
    from debug      import debug
    from message    import Message
    from pfmisc     import pfmisc
    from pfmisc2    import pfmisc2
    from other      import *
    from error      import *
