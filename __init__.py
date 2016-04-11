import gevent.monkey; gevent.monkey.patch_all(thread=False, subprocess=False)
if not hasattr(gevent, "wait"):
  def mywait(timeout=None):
    return gevent.run(timeout)
  gevent.wait=mywait
import sys
import os
import string
import types

#
# create the root logger
#
import logging

_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)
_formatter = logging.Formatter('* [unnamed, %(name)s] %(levelname)s %(asctime)s %(message)s')


#
# log to stdout
#
_hdlr = logging.StreamHandler(sys.stdout)
_hdlr.setFormatter(_formatter)
logging.getLogger().addHandler(_hdlr)


#
# add the GUI Handler
#
#from Utils import Qt4_GUILogHandler
#_GUIhdlr =Qt4_GUILogHandler.GUILogHandler()

#_logger.addHandler(_GUIhdlr)


#
# Add path to root BlissFramework directory
#
blissframeworkpath = os.path.dirname(__file__)
sys.path.insert(0, blissframeworkpath)


_gui_version = 'qt3'

def set_gui_version(verson_str):
    global _gui_version
    _gui_version = verson_str

def get_gui_version():
    return _gui_version  

def getStdBricksPath():
    stdbrickspkg = __import__('BlissFramework.Bricks', globals(), locals(), [''])
    return os.path.dirname(stdbrickspkg.__file__)

_bricksDirs = []

def addCustomBricksDirs(bricksDirs):
    import sys

    global _bricksDirs
    
    if type(bricksDirs) == list:
        newBricksDirs = list(filter(os.path.isdir, list(map(os.path.abspath, bricksDirs))))

        for newBrickDir in reversed(newBricksDirs):
            if not newBrickDir in sys.path:
                #print 'inserted in sys.path = %s' % newBrickDir
                sys.path.insert(0, newBrickDir)

        _bricksDirs += newBricksDirs

sys.path.insert(0, getStdBricksPath())
    
def getCustomBricksDirs():
    return _bricksDirs


def _frameworkTraceFunction(frame, event, arg):
    print('EVENT %s' % event)
    print('  { FRAME INFO }')
    print('    - filename  %s' % frame.f_code.co_filename)
    print('    - line      %d' % frame.f_lineno)
    print('    - name      %s' % frame.f_code.co_name)
    

loggingName = ''

def setLoggingName(name):
    global _formatter, _hdlr, loggingName
    
    _formatter = logging.Formatter('* [' + str(name) + ', %(name)s] %(levelname)s %(asctime)s %(message)s')
    _hdlr.setFormatter(_formatter)

    loggingName = name
    

def setLogFile(filename):
    #
    # log to rotating files
    #
    global _hdlr
    #from logging.handlers import RotatingFileHandler
    from logging.handlers import TimedRotatingFileHandler

    logging.getLogger().info("Logging to file %s" % filename)

    _logger.removeHandler(_hdlr)
        
    #_hdlr = RotatingFileHandler(filename, 'a', 1048576, 10) #1 MB by file, 10 files max.
    _hdlr = TimedRotatingFileHandler(filename, when='midnight', backupCount=1)
    os.chmod(filename, 0o666)
    _hdlr.setFormatter(_formatter)
    _logger.addHandler(_hdlr)

#
# general framework settings
#
_useDumbDbm = False


def setUseDumbDbm(d):
    global _useDumbDbm

    _useDumbDbm = d


def useDumbDbm():
    return _useDumbDbm


def setDebugMode(on):
    if on:
        sys.settrace(_frameworkTraceFunction) 
    else:
        sys.settrace(None)


