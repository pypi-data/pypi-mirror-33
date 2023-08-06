import inspect
import warnings
from typing import Dict, Optional, cast
from mhelper import FrozenAttributes, SimpleProxy, NOT_PROVIDED

from intermake.datastore.local_data import LocalData
from intermake.engine.help import HelpTopicCollection
from intermake.engine.host_manager import get_current_host
from intermake.engine.mandate import Mandate
from intermake.hosts.base import DHostProvider, ERunMode, AbstractHost
from intermake.visualisables.visualisable import IVisualisable, UiInfo


_Command_ = "intermake.engine.plugin.AbstractCommand"


class _DefaultRoot( IVisualisable ):
    """
    Used for Intermake applications that do not provide their own explicit root.
    """
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        u.hint = u.Hints.EXECUTABLE
        u.contents += { "commands": MCMD.environment.commands.get_root_folder() }
    
    
    def __repr__( self ):
        return "Root of {}".format( MCMD.environment.name )


class EnvironmentSettings:
    """
    User-settings for environment.
    
    :ivar startup: One or more modules to import when intermake is started.
    """
    
    
    def __init__( self ):
        self.startup = set()


class Environment( FrozenAttributes ):
    """
    The Intermake environment for a particular application.
    
    For consistency of documentation, all fields are accessed through properties, please see the
    documentation on these properties for details on what can be accessed.
    """
    LAST: "Environment" = None
    ACTIVE: "Environment" = None
    AVAILABLE = []
    
    
    def __init__( self,
                  *,
                  name: str = None,
                  version: str = None,
                  abv_name: Optional[str] = None,
                  root: Optional[object] = None,
                  constants: Optional[Dict[str, str]] = None,
                  inherit: Optional["Environment"] = NOT_PROVIDED,
                  activate: bool = True ):
        """
        CONSTRUCTOR
        
        Constructing the `Environment` automatically registers it in `Environment.AVAILABLE` and `Environment.LAST`.
        
        :param name:        Default value for property of same name.
        :param version:     Default value for property of same name.
        :param abv_name:    Default value for property of same name.
        :param root:        Default value for property of same name.
        :param constants:   Default value for property of same name.
        :param inherit:     Specify an existing environment to act as a base to extend.
                            If not specified, the default is `intermake.INTERMAKE_APP`.
        :param activate:    When set, `Environment.ACTIVE` is set to the new environment if either:
                            * There is no existing `Environment.ACTIVE`
                            * The new environment `inherit`s `Environment.ACTIVE`  
        """
        from intermake.engine.command_collection import CommandCollection
        
        if not name:
            raise ValueError( "An application name must be provided." )
        
        if version is not None and not isinstance( version, str ):
            version = ".".join( str( x ) for x in version )
        
        if inherit is NOT_PROVIDED:
            from intermake.init import INTERMAKE_APP
            inherit = INTERMAKE_APP
        
        self.__name: str = name
        self.__version: str = version or "0.0.0.0"
        self.__abbreviated_name: Optional[str] = abv_name
        self.__root: object = root or _DefaultRoot()
        self.__root_name: str = SimpleProxy( lambda: self.abv_name )
        self.__constants: Dict[str, str] = constants or { }
        self.__commands: CommandCollection = CommandCollection( comment = name,
                                                                inherit = inherit.commands if inherit is not None else None )
        self.__local_data: LocalData = LocalData( self.abv_name )
        self.__host_provider: Dict[object, DHostProvider] = None
        self.__is_locked: bool = False
        self.__help = HelpTopicCollection()
        self._environment_settings: EnvironmentSettings = None
        
        self.__constants["APP_NAME"] = SimpleProxy( lambda: self.name )
        self.__constants["APP_ABV"] = SimpleProxy( lambda: self.abv_name )
        self.__constants["APP_VERSION"] = SimpleProxy( lambda: self.version )
        self.__constants["DATA_FOLDER"] = SimpleProxy( lambda: self.local_data.workspace + "/" )
        
        # Preload?
        self._environment_settings = self.local_data.store.bind( "environment", EnvironmentSettings() )
        
        for module_name in self._environment_settings.startup:
            try:
                __import__( module_name )
            except ImportError as ex:
                warnings.warn( "Failed to import a module «{}» mandated by the user-specified environment settings: {}".format( module_name, ex ), UserWarning )
        
        super().__init__()
        
        Environment.LAST = self
        Environment.AVAILABLE.append( self )
        
        if activate:
            if Environment.ACTIVE is None or Environment.ACTIVE is inherit:
                Environment.ACTIVE = self
    
    
    @property
    def root_name( self ) -> str:
        """
        Gets or sets the root name, which is used to specify the name of the `root` object in the UI.
        This may be set to anything (such as a `SimpleProxy` for a dynamic string), but when retrieved is always cast to `str`.
        """
        return str( self.__root_name )
    
    
    @root_name.setter
    def root_name( self, value: object ) -> None:
        self.__root_name = value
    
    
    def __repr__( self ):
        return "Environment('{}')".format( self.name )
    
    
    @property
    def help( self ) -> HelpTopicCollection:
        return self.__help
    
    
    @property
    def stringcoercer( self ):
        import stringcoercion
        return stringcoercion.get_default_collection()
    
    
    @property
    def is_locked( self ) -> bool:
        """
        State that holds the result of the last call to `init`.
        """
        return self.__is_locked
    
    
    @property
    def name( self ) -> str:
        """
        Gets the name of the application.
        """
        return self.__name
    
    
    @property
    def commands( self ):
        """
        Gets the `CommandCollection`, that allows you to view available commands and register new ones.
        See class: CommandCollection
        """
        return self.__commands
    
    
    @property
    def local_data( self ) -> LocalData:
        """
        Obtains the `LocalData` store, used to apply and retrieve application settings.
        """
        return self.__local_data
    
    
    @property
    def constants( self ) -> Dict[str, str]:
        """
        Obtains the constant dictionary, used to replace text `"$(XXX)"` in documentation strings, where `XXX` is the name of a key from this dictionary.
        
        Dictionary keys:        Variable to find
        Dictionary values:      Text to replace. This can be any object coercible via `str`, thus the dictionary supports dynamic values.
        """
        return self.__constants
    
    
    @property
    def root( self ) -> object:
        """
        Gets or sets the application root.
        
        This is an arbitrary item that acts as the "root" folder of the UI hierarchy. 
        """
        if self.__root is None:
            self.__root = _DefaultRoot()
        
        return self.__root
    
    
    @root.setter
    def root( self, value: object ):
        self.__root = value
    
    
    @property
    def host_provider( self ) -> Dict[object, DHostProvider]:
        """
        Gets the host provider (a read/write dictionary).
        
        The host provided is a dictionary of objects to functions that provide the host for that object.
        Objects can be anything, but the user can only specify strings and members of `ERunMode`.
        The `ERunMode` enumeration is used for the default hosts, which are accessed through commands such as `gui`,
        these values can be replaced by the application.
        """
        if self.__host_provider is None:
            self.__host_provider = { }
            from intermake.hosts.console import ConsoleHost
            
            def __gui() -> AbstractHost:
                from intermake_qt.host.gui import GuiHost
                return GuiHost()
            
            
            self.__host_provider[ERunMode.ARG] = lambda: ConsoleHost.get_default( ERunMode.ARG )
            self.__host_provider[ERunMode.CLI] = lambda: ConsoleHost.get_default( ERunMode.CLI )
            self.__host_provider[ERunMode.PYI] = lambda: ConsoleHost.get_default( ERunMode.PYI )
            self.__host_provider[ERunMode.PYS] = lambda: ConsoleHost.get_default( ERunMode.PYS )
            self.__host_provider[ERunMode.JUP] = lambda: ConsoleHost.get_default( ERunMode.JUP )
            self.__host_provider[ERunMode.GUI] = __gui
        
        return self.__host_provider
    
    
    @property
    def version( self ) -> str:
        """
        Gets the application version. 
        """
        return self.__version
    
    
    @property
    def abv_name( self ) -> str:
        """
        Gets the abbreviated name of the application.
        """
        return self.__abbreviated_name or self.name
    
    
    @property
    def host( self ):
        warnings.warn( "Deprecated - use MCMD.host.", DeprecationWarning )
        return MCMD.host


def __current_environment() -> Environment:
    """
    See field: `MCMD`.
    """
    if Environment.LAST is None:
        raise ValueError( "Request for environment when Environment.LAST is None." )
    
    return Environment.LAST


def __current_mandate() -> Mandate:
    """
    See field: `MCMD`.
    """
    host = get_current_host()
    
    return host.on_get_mandate()


# noinspection SpellCheckingInspection
MCMD: Mandate = SimpleProxy( __current_mandate )
"""
Obtains a copy to the current mandate, which abstracts functionality such as "print" (MCMD.print) so that the output is sent to the
correct place (e.g. GUI or CLI).

Please see the `Mandate` class documentation in `intermake/engine/mandate.py` for the actual member list and descriptions!
"""

MENV: Environment = SimpleProxy( __current_environment )
"""
A proxy variable which points to `intermake.Environment.LAST`.

Deprecated, please use:
    Environment.LAST - the last defined environment (used for registering commands, etc)
    MCMD.environment - the currently executing environment (used for reading run-time settings etc)
"""


def acquire( *args, **kwargs ):
    return MCMD.host.acquire( *args, **kwargs )


def start( caller: Optional[str] = None ):
    """
    Quickly starts up the appropriate intermake frontend.
    
    :param caller:        Name of caller (i.e. __name__), used to start the CLI (ERunMode.ARG) if this is "__main__".
                          * If you have added your own check, or wish to force the CLI to start, then you do not need to supply this argument.
                          * If you do not wish the CLI to start, do not call this function!
    """
    from intermake.init import INTERMAKE_APP
    if __current_environment() is INTERMAKE_APP:
        raise ValueError( "Preventing `intermake.start` call without defining a new `intermake.Environment`: This probably means that your `__init__` has not been called." )
    
    if caller is None or caller == "__main__":
        from intermake.commands import common_commands
        common_commands.cmd_start_ui( ERunMode.ARG )


def register( command: _Command_ ) -> _Command_:
    """
    This is a convenience function which wraps to MENV.commands.register.
    :param command:  AbstractCommand to register
    """
    # We can't just call MENV.commands.register directly because it will look like this module
    # is the origin of the `AbstractCommand`, so we need to specify the module explicitly.
    frame = inspect.stack()[1]
    module_ = inspect.getmodule( frame[0] )
    
    # Register the plugin
    MENV.commands.register( command, module_ )
    return command


def run_jupyter( import_: str ) -> None:
    """
    Convenience command equivalent to `ui pyi`
    """
    __import__( import_ )
    from intermake.engine import host_manager
    host_manager.run_host( MENV.host_provider[ERunMode.JUP]() )
