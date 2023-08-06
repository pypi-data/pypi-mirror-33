try:
    from common.constants import Const as C
except ImportError:
    pass # import doesn't work at this stage with pyjamas
else:
    __version__ = C.APP_VERSION
