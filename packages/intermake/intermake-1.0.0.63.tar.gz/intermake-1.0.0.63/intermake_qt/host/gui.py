import sys
import threading
import intermake
from typing import Optional, cast, List
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QProxyStyle, QStyle, QWidget
from intermake import AsyncResult, EDisplay, MENV, Mandate, IProgressReceiver, QueryInfo, UpdateInfo, AbstractHost, RunHost, AbstractCommand, EStream, Message
from intermake.engine.environment import MCMD
from mhelper import Logger, ansi_format_helper, override, string_helper, virtual, ArgsKwargs, exception_helper, ignore

from intermake_qt.forms.frm_maintenance import FrmMaintenance
from intermake_qt.utilities.interfaces import IGuiHostMainWindow


__author__ = "Martin Rusilowicz"

_SIGLOG = Logger( "gui host signals" )


class _FnWrapper:
    """
    Wraps a function, we need to do this because QT won't let us send raw functions across threads, but we can send an object that behaves like a function.
    """
    
    
    def __init__( self, fn ) -> None:
        self.__fn = fn
    
    
    def __call__( self, *args, **kwargs ) -> Optional[object]:
        return self.__fn( *args, **kwargs )
    
    
    def __str__( self ) -> str:
        return str( self.__fn )


class BrowserInvoke:
    """
    If an `AbstractCommand` returns this, the host runs it in the browser.
    This should be used if the host replies `True` to `has_form`.
    """
    
    
    def __init__( self, cypher: str ) -> None:
        self.cypher = cypher


class _GuiHostSettings:
    """
    :ivar number_of_threads: Number of threads to use in commands supporting multi-threading.
    :ivar gui_auto_close_progress: Automatically close the progress dialogue.
    :ivar gui_css: CSS stylesheet. Takes a full path or a name of an Intermake style sheet (with or without the `.css` extension). If not specified uses `main.css`.
    :ivar gui_auto_scroll_progress: GUI option
    :ivar gui_progress_display: GUI option 
    """
    
    
    def __init__( self ) -> None:
        super().__init__()
        self.number_of_threads = 1
        self.gui_auto_close_progress = True
        self.gui_auto_scroll_progress = True
        self.gui_progress_display = EDisplay.TIME_REMAINING
        self.gui_css = ""


class CreateWindowArgs:
    def __init__( self, can_return_to_cli: bool ):
        self.can_return_to_cli = can_return_to_cli


class _NullReceiver( IProgressReceiver ):
    def progress_update( self, info: UpdateInfo ) -> None:
        pass
    
    
    def was_cancelled( self ) -> bool:
        return False
    
    
    def question( self, query: QueryInfo ) -> Optional[object]:
        raise ValueError( "Cannot question the user when an `AbstractCommand` is being run in the main thread! The main thread is already being used to host the GUI." )


class GuiHost( AbstractHost ):
    """
    Manages a set of asynchronous workers and their progress dialogue
    
    :ivar __settings:       These settings used by the GUI which can be configured by the user through the `set` command.
    :ivar __owner_window:   The main window
    :ivar __beehives:       Each `AbstractCommand` gets its own "bee hive", which manages the threads ("busy bees") for that command.
    :ivar thread_local:     Thread-local data store. Each thread gets its own version of this, including the main thread.
    :ivar thread_local.tag_receiver:     The progress receiver for a particular thread.
    :ivar thread_local.tag_mandate:      The stack of commands called on a particular thread.
    :ivar __base_mandate:   This is the mandate used at the bottom of the main thread, when no commands are running this is what `MCMD` returns. 
    """
    HOST_ARG_AUTO_CLOSE = -1, "auto_close"
    HOST_ARG_PARENT_WINDOW = 0, "window"
    HOST_ARG_LISTEN = -1, "callback"
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        super().__init__()
        self.__settings: _GuiHostSettings = None
        self.__owner_window = cast( IGuiHostMainWindow, None )
        self.__beehives = []
        self.thread_local = threading.local()
        self.thread_local.tag_receiver = _NullReceiver()
        self.__base_mandate = Mandate( self, self.thread_local.tag_receiver, "Base" )
        self.thread_local.tag_mandate = [self.__base_mandate]
        self.__exec_index = 0
        
        threading.currentThread().name = "main_intermake_gui_thread"
    
    
    def on_get_is_cli( self ):
        return False
    
    
    def on_register_thread( self, mandate: Mandate ):
        if hasattr( self.thread_local, "tag_mandate" ):
            raise ValueError( "Attempt to register a thread with the GuiHost but that thread has already been registered. This is probably an error." )
        
        self.thread_local.tag_receiver = mandate._get_receiver()
        self.thread_local.tag_mandate = [mandate]
    
    
    def __str__( self ) -> str:
        return "GuiHost(QT)"
    
    
    def on_translate_name( self, name: str ) -> str:
        return string_helper.capitalise_first_and_fix( name, "_-." )
    
    
    @override
    def on_get_mandate( self ) -> Mandate:
        """
        Obtains the mandate, stored in the thread-local pool for the `AbstractCommand`.
        This doesn't work for unmanaged commands, they need to pass the mandate along as a parameter themselves.
        :return: 
        """
        try:
            return self.thread_local.tag_mandate[-1]
        except AttributeError as ex:
            raise ValueError( "Attempt to get the mandate from a thread «{}» that is neither the main thread nor a thread running an `AbstractCommand`.".format( threading.currentThread().name ) ) from ex
    
    
    def on_get_help_message( self ) -> str:
        return """
            You are in GUI mode.
            Double-click commands to run them.
            Try running the sample `eggs` command, which can be found in the `Default/Commands` folder."""
    
    
    def __is_executing_command( self ):
        return self.thread_local.tag_mandate[0] is not self.__base_mandate
    
    
    @virtual
    def on_create_window( self, args: CreateWindowArgs ):
        from intermake_qt.forms.frm_intermake_main import FrmIntermakeMain
        frm_main = FrmIntermakeMain( args.can_return_to_cli )
        return frm_main
    
    
    @override
    def on_run_host( self, args: RunHost ) -> None:
        """
        Helper function to start the GUI
        """
        # Unfortunate notice: If the GUI fails to initialise with a segmentation fault this is probably a bad QT
        # installation. The user will need to reinstall QT/PyQt5. TODO: Detect this scenario and inform the user.
        from intermake.engine import cli_helper
        print( cli_helper.format_banner( "GUI-Frontend. The GUI is now active. Input will not be accepted in this terminal until the GUI completes.", None, None ) )
        
        import sys
        from PyQt5.QtWidgets import QApplication
        
        # Read the CSS
        from intermake_qt.utilities import intermake_gui
        style = intermake_gui.parse_style_sheet().get( 'QApplication.style', "" )
        small_icon_size = int( intermake_gui.parse_style_sheet().get( 'QApplication.smallIconSize', "16" ) )
        
        # Start the GUI
        if style:
            QApplication.setStyle( ProxyStyle( style, small_icon_size ) )
        
        app = QApplication( sys.argv )
        app.setStyleSheet( intermake_gui.default_style_sheet() )
        main_window = self.on_create_window( CreateWindowArgs( can_return_to_cli = args.can_return ) )
        self.set_window( main_window )
        main_window.show()
        
        app.exec_()
        print( intermake.constants.INFOLINE_SYSTEM + "The GUI has closed." )
        
        if not main_window.return_to_console():
            args.exit = True
    
    
    def set_window( self, window: IGuiHostMainWindow ):
        self.__owner_window = window
    
    
    @property
    def gui_settings( self ) -> _GuiHostSettings:
        if self.__settings is None:
            self.__settings = MENV.local_data.store.bind( "gui", _GuiHostSettings() )
        
        # noinspection PyTypeChecker
        return self.__settings
    
    
    @override
    def on_command_execute( self, command: AbstractCommand, args: ArgsKwargs, host_args: ArgsKwargs ) -> AsyncResult:
        """
        IMPLEMENTATION
        
        This host's run command uses `FrmMaintenance` to perform the legwork.
        Acceptable host args include:
            `window` (`QWidget`)
            `auto_close` (`bool`) 
        """
        window: QWidget = host_args.get( *self.HOST_ARG_PARENT_WINDOW, self.__owner_window )
        
        async_result = AsyncResult( host = self,
                                    command = command,
                                    args = args )
        
        self.__invoke_threaded( async_result, host_args, window )
        
        listen = host_args.get( *self.HOST_ARG_LISTEN, None )
        
        if listen is not None:
            async_result.listen( listen )
        
        return async_result
    
    
    def __get_next_exec_index( self ):
        self.__exec_index += 1
        return self.__exec_index
    
    
    def __invoke_unmanaged( self, async_result: AsyncResult ):
        mandate = Mandate( self, self.thread_local.tag_receiver, async_result.command.name )
        self.thread_local.tag_mandate.append( mandate )
        
        try:
            result = self.handle_command_execute( async_result.command, async_result.args )
            async_result.set_result( result = result,
                                     messages = None )
        except Exception as ex:
            async_result.set_error( exception = ex,
                                    stacktrace = exception_helper.get_traceback(),
                                    messages = None )
        finally:
            self.thread_local.tag_mandate.pop()
    
    
    def __invoke_threaded( self, async_result: AsyncResult, host_args: ArgsKwargs, window: QWidget ) -> None:
        self.__beehives.append( self.__BeeHive( self, window, async_result, 1, host_args ) )
    
    
    @override
    def on_command_completed( self, result ):
        self.__owner_window.command_completed( result )
    
    
    class __BeeHive:
        def __init__( self, host: "GuiHost", window, async_result: AsyncResult, num_threads: int, host_args: ArgsKwargs ):
            if window is None:
                raise ValueError( "__BeeHive expects a Window." )
            
            auto_close = host_args.get( *host.HOST_ARG_AUTO_CLOSE, False )
            
            self._dialogue = FrmMaintenance( window, MCMD.host.translate_name( async_result.command.name ), auto_close )
            self._dialogue.setModal( True )
            self._dialogue.show()
            
            self._host = host
            self.__async_result = async_result
            
            self.__bees = set()
            
            for i in range( num_threads ):
                try:
                    bee = self.__BusyBee( self, async_result, self._dialogue, i, num_threads )
                    bee.start()
                    self.__bees.add( bee )
                except Exception as ex:
                    # Bee failed to start
                    self.bee_finished( None, None, ex, exception_helper.get_traceback(), [Message( "Worker thread failed to start.", EStream.PROGRESS )] )
        
        
        def bee_finished( self, bee: "__BusyBee", result: object, exception: Exception, traceback: str, messages: List[Message] ) -> None:
            """
            Called when a thread finishes (back in the main thread)
            """
            if bee is not None:
                self.__bees.remove( bee )
            
            if self.__bees:
                return
            
            # We do !NOT! set the result on the `async_result` UNTIL the dialogue has CLOSED.
            
            # Close the dialogue. It is the dialogue that sets the result!
            self._dialogue.worker_finished( self.__async_result, result, exception, traceback, messages )
        
        
        class __BusyBee( QThread, IProgressReceiver ):
            """
            Actual thread
            """
            __callback = pyqtSignal( _FnWrapper )
            
            
            @override  # IProgressReceiver
            def was_cancelled( self ) -> bool:
                return self.__dialogue.was_cancelled()
            
            
            @override  # IProgressReceiver
            def question( self, query: QueryInfo ) -> Optional[object]:
                raise NotImplementedError( "This feature (question user) has not been implemented in the GUI, please run in the CLI." )  # TODO!!!
            
            
            @override  # IProgressReceiver
            def progress_update( self, info ) -> None:
                self.invoke_in_main_thread( lambda: self.__dialogue.worker_update( info ) )
            
            
            def __init__( self, hive: "GuiHost.__BeeHive", async_result: AsyncResult, dialogue, my_index, num_threads ):  # MAIN
                """
                Creates the thread object
                """
                QThread.__init__( self )
                
                self.__callback.connect( self.__invoke_returned )
                
                self.__async_result = async_result
                
                self.__dialogue = dialogue
                
                self.__result = None  # type:Optional[object]
                self.__exception = None  # type:Optional[Exception]
                self.__exception_trace = None  # type: Optional[str]
                
                self.__was_cancelled = False
                self.__hive = hive
                
                self.__mandate = Mandate( self.__hive._host, self, async_result.command.name, my_index, num_threads, 0.2 )
            
            
            @override  # QThread
            def run( self ) -> None:  # WORKER
                """
                QThread Implementation
                """
                
                threading.currentThread().name = "intermake_busybee_{}_hive_{}_running_{}".format( id( self ),
                                                                                                   id( self.__hive ),
                                                                                                   self.__async_result.command.name.replace( " ", "_" ) )
                
                try:
                    self.__hive._host.thread_local.tag_mandate = [self.__mandate]
                    self.__hive._host.thread_local.tag_receiver = self
                    true_result = self.__hive._host.handle_command_execute( self.__async_result.command, self.__async_result.args )
                    result = true_result, None, None, self.__mandate.get_message_records()
                except Exception as ex:
                    result = None, ex, exception_helper.get_traceback(), self.__mandate.get_message_records()
                    
                    # Print a message for the debugger
                    print( "EXCEPTION IN __BusyBee.run:", file = sys.stderr )
                    print( ansi_format_helper.format_traceback( ex ), file = sys.stderr )
                
                self.invoke_in_main_thread( lambda: self.__hive.bee_finished( self, *result ) )
            
            
            def invoke_in_main_thread( self, where ) -> None:  # WORKER
                """
                Calls "where" back in the main thread
                """
                where = _FnWrapper( where )
                _SIGLOG( "S __invoke_emit --> {}".format( where ) )
                self.__callback.emit( where )  # --> MAIN (via signal)
                _SIGLOG( "E __invoke_emit --> {}".format( where ) )
            
            
            @staticmethod
            def __invoke_returned( where ) -> None:  # <- MAIN (via signal)
                """
                The callback from invoke_in_main_thread - just calls "where".
                """
                _SIGLOG( "S __invoke_returned --> {}".format( where ) )
                where()
                _SIGLOG( "E __invoke_returned --> {}".format( where ) )
    
    
    @override
    def on_get_has_form( self ):
        return True
    
    
    @override
    def on_get_form( self ):
        return self.__owner_window


class ProxyStyle( QProxyStyle ):
    def __init__( self, style: Optional[str], small_icon_size: int ):
        if style != "default":
            super().__init__( style )
        else:
            super().__init__()
        
        self.__small_icon_size = small_icon_size
    
    
    def pixelMetric( self, QStyle_PixelMetric, option = None, widget = None ):
        if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
            return self.__small_icon_size
        else:
            return QProxyStyle.pixelMetric( self, QStyle_PixelMetric, option, widget )


class BrowserHost( GuiHost ):
    class Settings:
        """
        :ivar enable_browser:  Web browser status.
        
                               notes::
                               This parameter is interpreted as a boolean but can be anything.
                               `True` - enables the browser.
                               `False` - disables the browser.
                                        
                               Values with a `__bool__` may be used for application specific control.
                               e.g. `0` = disabled, `1` = enabled, `2` = enabled, but ask before show
        """
        
        
        def __init__( self ):
            self.enable_browser: bool = True
    
    
    @classmethod
    def get_settings( cls ) -> Settings:
        from intermake.engine.environment import MCMD
        return MCMD.environment.local_data.store.bind( "BrowserHostSettings", cls.Settings() )
    
    
    def on_run_host( self, args: RunHost ):
        settings = self.get_settings()
        
        if settings.enable_browser:
            from PyQt5.QtWebEngineWidgets import QWebEngineView
            ignore( QWebEngineView )
        
        super().on_run_host( args )
