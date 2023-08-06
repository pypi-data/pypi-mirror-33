from typing import Optional, Iterator

import sys

from intermake.engine.constants import EStream
from intermake.commands.setter_command import AbstractSetterCommand
from mhelper import string_helper, ansi
import stringcoercion

from intermake.engine.environment import MCMD, Environment
from intermake.hosts.frontends import command_line
from intermake.hosts.console import ConsoleHost
from intermake.commands.basic_command import command
from intermake.commands.visibilities import TEST
from intermake.engine import cli_helper


@command( visibility = TEST )
def console_width():
    """
    Prints the console width.
    """
    w = MCMD.host.console_width
    msg = "Console width hint is {}. This banner is the same size as the console width hint.".format( MCMD.host.console_width )
    msg = string_helper.max_width( msg, w - 4 )
    MCMD.print( "+" * w )
    MCMD.print( "+ " + msg + " " * (w - len( msg ) - 4) + " +" )
    MCMD.print( "+" * w )


@command( visibility = TEST )
def py_modules():
    """
    Lists the Python modules
    """
    for x in sys.modules.keys():
        cli_helper.print_value( x )


@command( visibility = TEST )
def test_progress( fast: bool = False ):
    """
    Does nothing.
    
    :param fast: Does nothing faster
    """
    count = 1000000 if fast else 10000000
    
    for stream in EStream:
        MCMD.print( "This is a message.", stream = stream )
    
    for _ in MCMD.iterate( range( 10 ), title = "Parent" ):
        for _ in MCMD.iterate( range( int( count / 10 ) ), title = "Child" ):
            pass
    
    for _ in MCMD.iterate( range( count ), title = "Single" ):
        pass
    
    for _ in MCMD.iterate( (x for x in range( count )), title = "Iterator" ):
        pass


@command( visibility = TEST )
def test_banner():
    """
    Tests the banner
    """
    print( cli_helper.format_banner( "<subtitle>", "<help_cmd>", "<list_cmd>", full = True ) )


@command( visibility = TEST )
def test_error():
    """
    Tests the error handling capabilities of the host
    """
    raise ValueError( "This is an error." )


@command( names = ["echo", "test_echo"], visibility = TEST )
def test_echo( text: str ):
    """
    Echos the text. Echos the text.
    :param text: Text to echo. Also accepts `on` and `off`, which turn command echoing on or off (temporarily, for the current session - use `local` to save settings for next session).
    """
    if text.lower() == "on":
        host = MCMD.host
        if isinstance( host, ConsoleHost ):
            host.console_configuration.force_echo = True
        MCMD.print( "Echo is on" )
        return
    elif text.lower() == "off":
        host = MCMD.host
        if isinstance( host, ConsoleHost ):
            host.console_configuration.force_echo = False
        MCMD.print( "Echo is off" )
        return
    
    MCMD.print( text )


@command( visibility = TEST )
def test_coercers():
    """
    Prints out the coercers in the stringcoercion library.
    """
    for coercer in stringcoercion.get_default_collection():
        MCMD.print( str( coercer ) )


@command( visibility = TEST )
def test_modules( filter: Optional[str] = None ):
    """
    Prints out the loaded modules.
    :param filter:  Filter by name.
    """
    for module in sys.modules.values():
        if filter is not None and not filter.lower() in module.__name__.lower():
            continue
        
        MCMD.print( ansi.FORE_GREEN + module.__name__ + ansi.RESET )
        MCMD.print( ansi.FORE_WHITE + (module.__file__ if hasattr( module, "__file__" ) else "").rjust( MCMD.host.console_width ) + ansi.RESET )


class AdvSet( AbstractSetterCommand ):
    """
    Sets the console _configuration_.
    The configuration is active for this session only.
    """
    
    def on_get_targets( self ):
        host = MCMD.host
        
        if isinstance( host, ConsoleHost ):
            yield host.console_configuration
        else:
            raise ValueError( "This operation only works for the Console Host." )


adv_set = AdvSet( names = ["adv_set"], visibility = TEST )
Environment.LAST.commands.register( adv_set )


@command( names = ["get_intermake_css", "css"], visibility = TEST )
def get_intermake_css( css: Optional[str] = None ):
    """
    Gets the Intermake CSS.
    If pyperclip is installed, the result is copied to the clipboard, otherwise it is printed to stdout.
    
    :param css: Theme
    """
    from intermake_qt.utilities import intermake_gui
    css = intermake_gui.default_style_sheet( css )
    
    try:
        import pyperclip
        pyperclip.copy( css )
        MCMD.print( "Copied to clipboard." )
    except ImportError:
        print( "css" )
        MCMD.print( "Printed to stdout (pyperclip not installed so not copied to clipboard)." )


@command( names = ["which", "what"], visibility = TEST )
def which( text: str ) -> None:
    """
    Finds which command will be matched if the user types "text".
    :param text: Text to find
    """
    
    fn = command_line.find_command( text )
    
    if fn:
        MCMD.information( cli_helper.format_kv( "Result", MCMD.host.translate_name( fn.name ) ) )
    else:
        MCMD.information( cli_helper.format_kv( "Result", "(no result)" ) )


@command( visibility = TEST )
def chenv( name: str = "" ) -> None:
    """
    Changes or displays information about the current Intermake environment.
    
    :remarks:
    Use the `ui` command to change the Intermake host instead.
    
    :param name: Name of the new environment, from `Environment.AVAILABLE`.
    """
    
    if name:
        for env in Environment.AVAILABLE:
            if env.name == name:
                Environment.ACTIVE = env
    
    MCMD.information( "MCMD = {}".format( MCMD ) )
    MCMD.information( "MCMD.host = {}".format( MCMD.host ) )
    MCMD.information( "MCMD.environment = {}".format( MCMD.environment ) )
    MCMD.information( "Environment.LAST = {}".format( Environment.LAST ) )
    MCMD.information( "Environment.ACTIVE = {}".format( Environment.ACTIVE ) )
    MCMD.information( "Environment.AVAILABLE = {}".format( Environment.AVAILABLE ) )
