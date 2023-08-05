from typing import Callable, Iterator, List, Optional, TypeVar

from intermake.engine.async_result import AsyncResult
from intermake.engine.host_manager import RunHost
from intermake.engine.abstract_command import AbstractCommand, PartialSuccess
from intermake.visualisables.visualisable import IVisualisable, UiInfo
from mhelper import ArgValueCollection, ArgsKwargs, MEnum, abstract, ansi_format_helper, exception_helper, virtual


T = TypeVar( "T" )
__author__ = "Martin Rusilowicz"


class _AbstractHostSettings:
    """
    :ivar number_of_results_to_keep: Number of results to keep in history
    :ivar welcome_message: Whether to display the welcome message when the host starts
    """
    
    
    def __init__( self ):
        self.number_of_results_to_keep = 10
        self.welcome_message = False


class ERunMode( MEnum ):
    """
    How the host should run. Also determines the initial configuration.
    
    :remarks: See also `create_simple_host_provider` and `create_simple_host_provider_from_class`.
              `ARG`, `CLI`, `PYI`, `PYS`, `JUP` all run under `ConsoleHost` by default, whilst `GUI` runs under the Qt `GuiHost`.
    
    :cvar ARG: Parses command line arguments
    :cvar CLI: Console-based host with a command-line-interactive frontend.
    :cvar PYI: Console-based host with a Python-interactive frontend. For interactive sessions, this imports the commands into locals.
    :cvar PYS: Console-based host without a frontend. For your own Python scripts, this does not modify the environment.
    :cvar GUI: Graphical host with a graphical frontend.
    :cvar JUP: Console-based host without a frontend. For Jupyter notebook, this imports the commands into locals.
    """
    ARG = 0
    CLI = 1
    PYI = 2
    PYS = 3
    GUI = 4
    JUP = 5


class ERunStatus( MEnum ):
    RUN = 0
    PAUSE = 1
    RESUME = 2
    STOP = 3


class ResultsCollection( IVisualisable ):
    """
    Maintains a collection of results.
    Items are added to the back, thus [-1] is the most recent result.
    The size of the list is constrained by `_AbstractHostSettings.number_of_results_to_keep`.
    """
    
    
    def __init__( self, owner: "AbstractHost" ) -> None:
        self.__data: List[AsyncResult] = []
        self.__owner: AbstractHost = owner
    
    
    def __str__( self ):
        return "{} results".format( len( self ) )
    
    
    def on_get_vis_info( self, u : UiInfo ) -> None:
        super().on_get_vis_info(u)
        u.hint = u.Hints.FOLDER
        u.contents += self.__data
    
    
    def append( self, result: AsyncResult ) -> None:
        self.__data.append( result )
        
        while len( self ) > self.__owner.host_settings.number_of_results_to_keep:
            self.__data.pop( 0 )
    
    
    def __len__( self ) -> int:
        return len( self.__data )
    
    
    def __bool__( self ) -> bool:
        return bool( self.__data )
    
    
    def __getitem__( self, item ) -> AsyncResult:
        return self.__data[item]
    
    
    def __iter__( self ) -> Iterator[AsyncResult]:
        return iter( self.__data )


@abstract
class AbstractHost:
    """
    The `AbstractHost` runs commands according to the current user interface (CLI, python, jupyter, GUI, etc.)
    
    All virtual methods are marked `@virtual` and begin with `on_`.
    Abstract methods are marked `@abstract`.
    Other methods should not be overridden.
    """
    _ABSTRACT_HOST_COUNT = 0
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        """
        AbstractHost._ABSTRACT_HOST_COUNT += 1
        self.__settings: _AbstractHostSettings = None
        self._index = AbstractHost._ABSTRACT_HOST_COUNT
        self.result_history = ResultsCollection( self )
        self.__environment = None
    
    
    @property
    def environment( self ):
        from intermake.engine.environment import Environment
        return Environment.ACTIVE
    
    
    @property
    def can_return( self ):
        return self.on_get_can_return()
    
    
    def get_help_message( self ) -> str:
        return self.on_get_help_message()
    
    
    @property
    def is_gui( self ):
        return not self.on_get_is_cli()
    
    
    @property
    def is_cli( self ):
        return self.on_get_is_cli()
    
    
    def register_thread( self, mandate ) -> None:
        """
        Registers a Mandate onto a new thread.
        This means that when MCMD is called this mandate will be retrieved.
        
        Note this function does not perform any thread management for you!
        It simply means that a new thread will be able to correctly receive the mandate from the calling thread.
        Since mandates are not multi-threaded it is assumed that the that the caller has set up any thread-management
        themselves, such as locking any calls to the Mandate or simply suspending the Mandate's original thread. 
        
        :param mandate: Mandate retrieved from the creating thread and being registered with this thread. 
        """
        self.on_register_thread( mandate )
    
    
    @property
    def host_settings( self ) -> _AbstractHostSettings:
        """
        Obtains the settings used to control the base host class.
        :return:    Settings. 
        """
        if self.__settings is None:
            from intermake.engine.environment import MENV
            self.__settings = MENV.local_data.store.retrieve( "host", _AbstractHostSettings() )
        
        # noinspection PyTypeChecker
        return self.__settings
    
    
    class __Runner:
        def __init__( self, host, command: AbstractCommand, host_args: ArgsKwargs ):
            self.host = host
            self.host_args = host_args
            self.command = command
        
        
        def run( self, *args, **kwargs ) -> AsyncResult:
            """
            Runs the command.
            
            :param args:        Passed to command. 
            :param kwargs:      Passed to command.
            :return:            The `AsyncResult` object.
            """
            args_ = ArgsKwargs( *args, **kwargs )
            
            # The following checks the argument types only
            ArgValueCollection( self.command.args, ArgsKwargs( *args, **kwargs ) )
            
            asr = self.host.on_command_execute( self.command, args_, self.host_args )
            exception_helper.assert_type( "host.on_command_execute", asr, AsyncResult )
            return asr
    
    
    def acquire( self, command, **kwargs ) -> __Runner:
        """
        Acquires an object capable of running a command.
        
        usage::
        ```
            host.acquire( my_command ).run( args )
        ```
        
        :param command:     Either an `AbstractCommand` instance to run
                            OR a `function` previously bound to a `BasicCommand`.
        :param kwargs:      Any host specific parameters dictating _how_ to run the command.
        :return:            An object upon which `run` may be called to invoke the command.
                            See `__Runner.run`. 
        """
        if not isinstance( command, AbstractCommand ):
            from intermake.commands.basic_command import BasicCommand
            command: AbstractCommand = BasicCommand.retrieve( command )
        
        return self.__Runner( self, command, ArgsKwargs( **kwargs ) )
    
    
    def run_host( self, args: RunHost ) -> None:
        """
        Runs the host's main loop, if it has one.
        :param args:    Arguments 
        :return:        `True` to return to the previous host, `False` to tell the previous host to exit too. 
        """
        try:
            self.on_run_host( args )
        except Exception as ex:
            print( ansi_format_helper.format_traceback( ex ) )
            raise
    
    
    def substitute_text( self, text ):
        """
        Formats help text for the current host.
        
        The base implementation replaces $(XXX) from the set of constants. 
        
        Concrete hosts may override this further.
        
        :param text:    Input text 
        :return:        Text to display 
        """
        from intermake.engine.environment import MENV
        
        if text is None:
            return ""
        
        text = text.replace( "$(APPNAME)", MENV.abv_name )
        
        for k, v in MENV.constants.items():
            text = text.replace( "$(" + k + ")", str( v ) )  # TODO: Inefficient
        
        return text
    
    
    @property
    def console_width( self ):
        """
        Some commands (`AbstractCommand`s) want to know the width of the screen for text-display purposes.
        This is how they get that.
        
        This calls the `_get_console_width` virtual function.
         
        :return: Width of text, in characters. 
        """
        return min( 180, self.on_get_console_width() )
    
    
    @property
    def console_width_unsafe( self ):
        """
        `console_width`, without clamping. This may be a large value - use only for wrapping, not for padding!
        """
        return self.on_get_console_width()
    
    
    def translate_name( self, name: str ) -> str:
        """
        Given the `name` of an object, translates it into something more friendly to the user.
        """
        return self.on_translate_name( name )
    
    
    def has_form( self ):
        """
        Returns if it is okay to call `form`. 
        """
        return self.on_get_has_form()
    
    
    @property
    def form( self ):
        return self.on_get_form()
    
    
    def handle_command_complete( self, result: AsyncResult ) -> None:
        """
        To be called by the derived class when a command completes.
        This should only be called in response to `on_run_command`.
        
        :param result: The result of running the command.
        """
        self.result_history.append( result )
        self.on_command_completed( result )
    
    
    def handle_command_execute( self, command: AbstractCommand, args: ArgsKwargs ) -> Optional[object]:
        """
        To be called by the derived class to run the plugin's actual functionality.
        This should only be called in response to `on_run_command`.
        
        :return: The result of the command's `on_run()` method. 
        """
        try:
            result = command.on_run( *args.args, **args.kwargs )
        except PartialSuccess as ex:
            from intermake.engine.environment import MCMD
            MCMD.progress( "The operation has ended early with partial success: {}".format( ex ) )
            return ex.result
        
        return result
    
    
    @virtual
    def on_get_console_width( self ):
        """
        When obtaining the width of the screen this function is called.
        The base implementation suggests no wrapping (an arbitrary large value).
        The derived class may suggest more appropriate text-wrapping limit.
        :return: 
        """
        return 120
    
    
    @abstract
    def on_command_execute( self, command: AbstractCommand, args: ArgValueCollection, host_args: ArgsKwargs ) -> AsyncResult:
        """
        The derived should respond by running the `command` in the appropriate manner:
            1. Ensuring `self.get_mandate` returns an appropriate value when called from within `AbstractCommand.on_run`.
            2. Calling `self.handle_command_execute` on the `command` to perform the actual routine.
            3. Calling `self.handle_command_complete` with the `AsyncResult` of the execution.
        
        :param command:         Command to run 
        :param args:            Arguments to pass to command.
                                These should be retained in the `Mandate`.
        :param host_args:       Any host specific arguments the caller has provided.
        
        :return:                A `AsyncResult` object.
        """
        raise NotImplementedError( "Abstract" )
    
    
    @virtual
    def on_get_has_form( self ):
        return False
    
    
    @virtual
    def on_run_host( self, args: RunHost ) -> None:
        """
        The derived class should perform the host's main loop, if it has one.
        If it does not have one (i.e. if it is a perpetual host), then it should ensure the appropriate flag is set in `args`.
        
        :param args:    Arguments  
        """
        raise NotImplementedError( "abstract" )
    
    
    @abstract
    def on_get_mandate( self ):
        """
        The derived class should return the current `Mandate`.
        
        The `Mandate` acts as a thread intermediary (if required) and contains information on the currently
        executing command (if present), the host, where messages should be printed, etc.
        
        :rtype: Mandate 
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def on_get_form( self ) -> object:
        """
        The derived class should return the main form object associated with the GUI.
        This function should not be called for a non-GUI host.
        """
        raise ValueError( "This plugin must be run under a GUI." )
    
    
    @virtual
    def on_translate_name( self, name: str ) -> str:
        """
        The derived class should translate the name of a command, typically in a Python friendly format such as
        `hello_world` to a form more suitable for the current interface.
        """
        return name
    
    
    @virtual
    def on_command_completed( self, result: AsyncResult ):
        """
        The derived class should perform any response to a command having
        completed and should then call `result.complete_command`.
        """
        pass
    
    
    @virtual
    def on_register_thread( self, mandate ) -> None:
        """
        The derived class should make preparations to ensure that when `on_get_mandate` is called from the current thread,
        that the previous `Mandate` is still returned.
        
        This is used when a host-created thread itself spawns a new thread.
         
        :param mandate: Mandate passed from the thread which created this one. 
        """
        pass
    
    
    @virtual
    def on_status_changed( self, status: ERunStatus ) -> None:
        """
        The derived class should implement any necessary response to the the host status being changed.
        """
        pass
    
    
    @virtual
    def on_get_can_return( self ) -> bool:
        """
        The derived class should return if there is a previous host to return to which is capable of resuming
        operations, otherwise the application will exit. Except in specific circumstances this is generally
        `True` and should not be overridden.
        """
        return True
    
    
    @virtual
    def on_get_help_message( self ) -> str:
        """
        The derived class should return the help the user should received when they request basic help.
        """
        return """You are running in a {} host and I can't give you any help because the creator of this host hasn't provided a `on_get_help_message`.
        Please see `readme.md` in the application directory for more information.""".format( type( self ).__name__ )
    
    
    def on_get_is_cli( self ) -> bool:
        """
        The derived class should return if this is a CLI instance, otherwise a GUI instance is assumed.
        """
        return True


DHostProvider = Callable[[], AbstractHost]
"""
Callable that takes no arguments and returns an `AbstractHost`.
"""
