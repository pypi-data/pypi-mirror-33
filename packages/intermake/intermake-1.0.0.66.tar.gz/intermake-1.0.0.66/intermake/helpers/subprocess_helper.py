import re
from typing import Sequence, List, Optional, Callable, Pattern

import os

from intermake.engine.constants import EStream
from intermake.engine.environment import MCMD
from mhelper import async_helper, SubprocessError


DStrReceiver = Callable[[str], None]


class __SubprocessRun:
    def __init__( self,
                  title: str,
                  garbage: List[Pattern],
                  collect_stdout: Optional[DStrReceiver],
                  collect_stderr: Optional[DStrReceiver],
                  hide: bool,
                  trace: bool ):
        self.garbage = garbage
        self.collect_stdout = collect_stdout
        self.collect_stderr = collect_stderr
        self.is_blank = [True, True]
        self.hide = hide
        self.trace = [] if trace else None
        
        if hide:
            self.action = MCMD.action( title ).__enter__()
    
    
    def close( self ):
        if self.hide:
            self.action.__exit__()
    
    
    def __print( self, text, stream, stream_index ):
        if self.trace is not None:
            self.trace.append( text )
        
        if self.hide:
            self.action.increment()
            return
        
        if any( y.search( text ) for y in self.garbage ):
            return
        
        if not text:
            if self.is_blank[stream_index]:
                return
            
            self.is_blank[stream_index] = True
        else:
            self.is_blank[stream_index] = False
        
        MCMD.print( text, stream = stream )
    
    
    def print_1( self, x ):
        self.__print( x, EStream.EXTERNAL_STDOUT, 0 )
        if self.collect_stdout is not None:
            self.collect_stdout( x )
    
    
    def print_2( self, x ):
        self.__print( x, EStream.EXTERNAL_STDERR, 1 )
        if self.collect_stderr is not None:
            self.collect_stderr( x )


def run_subprocess( command: Sequence[str],
                    *,
                    garbage: Optional[List[str]] = None,
                    collect: Optional[DStrReceiver] = None, 
                    collect_stdout: Optional[DStrReceiver] = None,
                    collect_stderr: Optional[DStrReceiver] = None,
                    hide: bool = False,
                    trace: bool = None,
                    stdin: str = None,
                    noerr:bool=False ):
    """
    Runs the specified subprocess
    
    :param noerr:               When set, no SubprocessError is raised.
    :param trace:               When set, STDOUT and STDERR are retained internally.
                                On error, these will displayed to the user.
                                The default value `None`, turns this on if `hide` is set.
    :param stdin:               Standard input (as a UTF-8 string)
    :param collect_stderr:      Function to receive std-err.
    :param collect:             Overrides both `collect_stderr` and `collect_stdout`.  
    :param hide:                Hide output (displays progress bar instead) 
    :param collect_stdout:      Function to receive std-out.
                                e.g. `my_list.append`.
    :param command:             Commands and arguments
    :param garbage:             List containing one or more regex that specify lines
                                dropped from display. This affects the inline display only and
                                does not affect the `trace` or `collect_*` parameters. 
    """
    if garbage is None:
        garbage: List[str] = []
        
    if trace is None:
        trace = hide
    
    if collect is not None:
        collect_stdout = collect
        collect_stderr = collect
    
    garbage: List[Pattern] = [re.compile( x ) for x in garbage]
    
    spr = __SubprocessRun( " ".join( command ), garbage, collect_stdout, collect_stderr, hide, trace )
    
    try:
        async_helper.async_run( command, spr.print_1, spr.print_2, check = True, stdin = stdin )
    except SubprocessError as ex:
        if noerr:
            return
        
        MCMD.print( "*** AN ERROR OCCURRED ***" )
        MCMD.print( "Command  : " + str( command ) )
        MCMD.print( "Exception: " + str( ex ) )
        MCMD.print( "Directory: " + os.getcwd() )
        
        if stdin:
            MCMD.print( "*** DUMPING THE INPUT DATA BECAUSE AN ERROR OCCURRED ***" )
            for index, line in enumerate( stdin.split( "\n" ) ):
                MCMD.print( "LINE {}: {} ".format( index, line ) )
            
            MCMD.print( "*** END OF INPUT ***" )
        
        if spr.trace is not None:
            MCMD.print( "*** DUMPING THE BUFFERED OUTPUT DATA BECAUSE AN ERROR OCCURRED ***" )
            for index, line in enumerate( spr.trace ):
                MCMD.print( "LINE {}: {} ".format( index, line ) )
            
            MCMD.print( "*** END OF OUTPUT ***" )
        
        raise
    finally:
        spr.close()
