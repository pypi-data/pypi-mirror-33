from typing import List, Optional, Callable

from intermake.engine.progress_reporter import Message
from intermake.visualisables.visualisable import IVisualisable, UiInfo, EColour
from mhelper import ArgsKwargs, MEnum


__author__ = "Martin Rusilowicz"
_AbstractCommand = "intermake.engine.plugin.AbstractCommand"
_AbstractHost = "intermake.hosts.base.AbstractHost"


class _EResultState( MEnum ):
    PENDING = 0
    SUCCESS = 1
    FAILURE = 2


class AsyncResult( IVisualisable ):
    """
    Intermake asynchronous result container.
    
    notes::
        Receiving:
            All callbacks will be made in the primary thread, i.e. the
            same thread that requested the result.
    
        Calling:
            The `AsyncResult` class is not itself thread safe - it is up to
            the host to ensure that `set_result` or `set_error` is
            called in the main thread.
          
    :cvar __INDEX:          Tally on result count.  
    :ivar state:            State of result (pending, success, failure)
    :ivar host:             Executing host
    :ivar result:           Result (on success)
    :ivar exception:        Exception (on failure)
    :ivar traceback:        Exception traceback (on failure)
    :ivar messages:         Messages (on success or failure)
    :ivar command:          AbstractCommand with which the query was was made
    :ivar args:             Arguments with which the query was was made
    :ivar index:            Index of result (arbitrary)
    :ivar __callbacks:      Result listeners (when pending)
    """
    __INDEX = 0
    
    
    def __init__( self,
                  *,
                  host: _AbstractHost,
                  command: _AbstractCommand,
                  args: ArgsKwargs ) -> None:
        """
        Constructs a `AsyncResult` in the `PENDING` state.
        """
        from intermake.engine.abstract_command import AbstractCommand
        AsyncResult.__INDEX += 1
        
        self.state = _EResultState.PENDING
        self.host = host
        self.result: Optional[object] = None
        self.exception: Exception = None
        self.traceback: str = None
        self.messages: Optional[List[Message]] = None
        self.command: AbstractCommand = command
        self.args: ArgsKwargs = args
        self.index = AsyncResult.__INDEX
        self.__callbacks: List[Callable[[AsyncResult], None]] = [host.handle_command_complete]
    
    
    @property
    def title( self ):
        """
        The title of this Result.
        """
        return self.command.name
    
    
    def get_result( self ):
        if self.is_success:
            return self.result
        else:
            raise ValueError( "Cannot get the result because the status {}, not success.".format( self.state ) )
    
    
    def set_result( self,
                    result: Optional[object],
                    messages: Optional[List[Message]] ):
        """
        Sets the result on this object and calls the callbacks.
        """
        assert self.state == _EResultState.PENDING, self.state
        self.state = _EResultState.SUCCESS
        self.result = result
        self.messages = messages
        self.__callback()
    
    
    def set_error( self,
                   exception: Optional[BaseException],
                   stacktrace: Optional[str],
                   messages: Optional[List[Message]] ):
        """
        Sets the result on this object and calls the callbacks.
        """
        assert self.state == _EResultState.PENDING, self.state
        self.state = _EResultState.FAILURE
        self.exception = exception
        self.traceback = stacktrace
        self.messages = messages
        self.__callback()
    
    
    def listen( self, callback: Callable[["AsyncResult"], None] ):
        """
        Calls `callback` if the result has completed, otherwise calls
        `callback` when the result completes.
        """
        if self.is_pending:
            self.__callbacks.append( callback )
        else:
            callback( self )
    
    
    def __callback( self ):
        """
        Calls the callbacks, including the host itself.
        """
        for callback in self.__callbacks:
            callback( self )
        self.__callbacks = None
    
    
    def on_get_vis_info( self, u : UiInfo ) -> None:
        super().on_get_vis_info(u)
        u.value = str( self.exception ) if self.is_error else str( self.result ),
        u.hint = u.Hints.ERROR if self.is_error else u.Hints.SUCCESS
        u.properties+= { "status": self.state,
                                 "result"     : self.result,
                                 "exception"  : self.exception,
                                 "messages"   : self.messages,
                                 "traceback"  : self.traceback,
                                 "plugin"     : self.command,
                                 "index"      : self.index
                                      }
    
    
    def raise_exception( self ) -> None:
        """
        For a result in the `FAILURE` state, re-raises the exception.
        """
        if self.exception:
            raise self.exception
    
    
    @property
    def is_success( self ) -> bool:
        """
        `True` if the `AsyncResult` is in the `SUCCESS` state.
        """
        return self.state == _EResultState.SUCCESS
    
    
    @property
    def is_error( self ) -> bool:
        """
        `True` if the `AsyncResult` is in the `ERROR` state.
        """
        return self.state == _EResultState.FAILURE
    
    
    @property
    def is_pending( self ) -> bool:
        """
        `True` if the `AsyncResult` is in the `PENDING` state.
        """
        return self.state == _EResultState.PENDING
    
    
    def __repr__( self ):
        if self.is_pending:
            return "Result({}, '{}', 'PENDING')".format( self.index, self.title )
        elif self.is_success:
            return "Result({}, '{}', 'SUCCESS', {})".format( self.index, self.title, repr( self.result ) )
        else:
            return "Result({}, '{}', 'FAILURE', {})".format( self.index, self.title, repr( self.exception ) )
    
    
    def __str__( self ) -> str:
        if self.is_pending:
            return "{} = (Pending)".format( self.title )
        elif self.is_success:
            return "{} = (Success) {}".format( self.title, self.result )
        else:
            return "{} = (Failure) {}".format( self.title, self.exception )
