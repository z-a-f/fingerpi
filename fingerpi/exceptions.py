
## Exceptions specifically for the FingerPi communication
## All exceptions inherit from RuntimeError

################################################################################
# Port IO related errors
class PortError(IOError):
    """Base class for port errors"""
    def __init__(self, *args, **kwargs):
        IOError.__init__(self, *args, **kwargs)

################################################################################
# Cases when trying to reuse variables that are already in use
class AlreadyError(RuntimeError):
    """Base class"""
    def __init__(self, *args, **kwargs):
        RuntimeError.__init__(self, *args, **kwargs)

class AlreadyInitializedError(AlreadyError):
    """If trying to initialize the device that is already initialized"""
    def __init__(self, *args, **kwargs):
        AlreadyError.__init__(self, *args, **kwargs)

class AlreadyOpenError(AlreadyError):
    """If trying to open the device that is already open"""
    def __init__(self, *args, **kwargs):
        AlreadyError.__init__(self, *args, **kwargs)
################################################################################
# Cases when trying to use variables that are not yet created
class NotYetError(RuntimeError):
    """Base class"""
    def __init__(self, *args, **kwargs):
        RuntimeError.__init__(self, *args, **kwargs)

class NotInitializedError(NotYetError):
    """If trying to use methods without initializing first"""
    def __init__(self, *args, **kwargs):
        NotYetError.__init__(self, *args, **kwargs)

class NotOpenError(NotYetError):
    """If trying to use methods without opening first"""
    def __init__(self, *args, **kwargs):
        NotYetError.__init__(self, *args, **kwargs)

################################################################################
# Nack errors (tricky)
class NackError(RuntimeError):
    """Any NACK errors would be here"""
    def __init__(self, *args, **kwargs):
        RuntimeError.__init__(self, *args, **kwargs)

################################################################################
# Name/Key/Value errors
class OutOfBoundsError(ValueError):
    """If the values are outside the range!"""
    def __init__(self, *args, **kwargs):
        ValueError.__init__(self, *args, **kwargs)



