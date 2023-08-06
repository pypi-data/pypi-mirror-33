import warnings
from collections import OrderedDict
from typing import Dict, Iterable, Iterator, List, Optional, Union

from intermake.commands import visibilities
from intermake.commands.visibilities import VisibilityClass
from intermake.visualisables.visualisable import IVisualisable, UiInfo
from mhelper import abstract, array_helper, exception_helper, override, string_helper, virtual
from mhelper.reflection_helper import ArgInspector


__author__ = "Martin Rusilowicz"



class PartialSuccess( Exception ):
    """
    A plugin may circumnavigate the normal return procedure and return a successful result via an exception.
    """
    
    
    def __init__( self, message = None, result = None ):
        self.result = result
        
        if not message:
            message = "The thread terminated because it has saved or has already created its workload. The primary thread will pick it up. This is not an error."
        
        super().__init__( message )


_unnamed_count = 0


class ArgumentCollection( IVisualisable ):
    def __init__( self, args: Iterable[ArgInspector] ) -> None:
        if args is None:
            args = ()
        
        self.__contents: Dict[str, ArgInspector] = OrderedDict( (x.name, x) for x in args )
        self.__contents_list = list( self.__contents.values() )
    
    
    def __getitem__( self, item: Union[int, str] ) -> ArgInspector:
        if isinstance( item, int ):
            return self.__contents_list[item]
        elif isinstance( item, str ):
            return self.__contents[item]
    
    
    def __iter__( self ) -> Iterator[ArgInspector]:
        return iter( self.__contents.values() )
    
    
    def __len__( self ) -> int:
        return len( self.__contents )
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        super().on_get_vis_info( u )
        u.text = "{} arguments".format( len( self ) )
        u.hint = u.Hints.LIST


@abstract
class AbstractCommand( IVisualisable ):
    """
    Commands, plug-ins, applets, or things that can be run by the user.
    
    The derived class should implement `on_run`.
    
    To run the command as if the user had executed it, use `MCMD.host.acquire().run( command )`.
    This will run the command in the manner set by current host, for instance
    `GuiHost` creates a "please wait" window and runs the command asynchronously.
    
    notes::
    Commands should no longer be run synchronously, this is not exposed by `AbstractCommand`.
    Execute the function instead, e.g. `BasicCommand.function()`.
    """
    
    FOLDER_DELIMITER = "/"
    
    
    def __init__( self,
                  *,
                  names: Optional[Union[str, List[str]]] = None,
                  documentation: Optional[str] = None,
                  visibility: Optional[VisibilityClass] = None,
                  highlight: bool = False,
                  folder: Optional[str] = None,
                  args: Iterable[ArgInspector] = None ):
        """
        CONSTRUCTOR
        
        :param names:           Name or names of the command.
        :param documentation:   Description of the command.
                                The derived class may opt for dynamic documentation via `on_get_documentation`.
        :param visibility:      A `VisibilityClass` denoting the command's visibility.
                                The default, `None`, implies the command is always visible.
        :param highlight:       Whether to highlight the command in lists.
        :param folder:          Optional folder where the command resides.
                                Esoteric use.
                                The default, `None`, implies the name of the residing module.
        :param args:            Description of arguments passed to `on_run`.
                                The derived class may opt for dynamic arguments via `on_get_args`.
        """
        
        # NAME
        # - Can be provided as a `str` or `Sequence`
        names = array_helper.as_sequence( names or None, cast = list )
        
        if not names:
            raise ValueError( "An `AbstractCommand` must have at least one name." )
        
        self.names: List[str] = names
        
        # VISIBILITY
        # - Defaults to `COMMON`
        if visibility is None:
            visibility = visibilities.COMMON
        elif not isinstance( visibility, VisibilityClass ):
            raise exception_helper.type_error( "visibility", visibility, VisibilityClass )
        
        self.visibility_class: VisibilityClass = visibility
        
        # DOCUMENTATION
        # - Defaults to class __doc__, unless it falls back to the base
        if documentation is None:
            documentation = self.__doc__
            if documentation is AbstractCommand.__doc__:
                documentation = ""
        
        if not documentation:
            # Not having a description is probably a mistake
            documentation = "Not documented :("
            warnings.warn( "An `AbstractCommand` «{}» has been instantiated with no description.".format( names ) )
        
        exception_helper.assert_instance( "documentation", documentation, str )
        
        self.__documentation = string_helper.fix_indents( documentation )
        
        # Default other args
        self.__args = ArgumentCollection( args )
        self.__highlight : bool = highlight
        self.folder : Optional[str] = folder
    
    
    @property
    def name( self ) -> str:
        return self.names[0]
    
    
    @property
    def __name__( self ):
        """
        __name__ property for compatibility with functions.
        """
        return self.name
    
    
    @property
    def display_name( self ):
        from intermake.engine.environment import MCMD
        return MCMD.host.translate_name( self.name )
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        super().on_get_vis_info( u )
        u.doc = self.documentation
        u.hint = u.Hints.EXECUTABLE
        u.properties += { "arguments": self.__args }
    
    
    @property
    def is_visible( self ) -> bool:
        return self.visibility_class.is_visible
    
    
    @property
    def is_highlighted( self ) -> bool:
        return self.__highlight
    
    
    @property
    def args( self ) -> ArgumentCollection:
        """
        Returns the set of arguments for this command. See `ArgInspector`.
        """
        return self.on_get_args()
    
    
    @virtual
    def on_get_args( self ) -> ArgumentCollection:
        """
        The derived class should return the description of arguments sent to `on_run`.
        The base class returns the set of arguments passed into the constructor, but this can be overridden.
        """
        return self.__args
    
    
    def find_arg( self, name: str ) -> ArgInspector:
        """
        Returns the specified argument. See `ArgInspector`.
        """
        from intermake.engine.environment import MCMD
        
        host = MCMD.host
        friendly_name = host.translate_name( name )
        
        for arg in self.args:
            if host.translate_name( arg.name ) == friendly_name:
                return arg
        
        raise KeyError( "There is no argument named «{}» in «{}».".format( name, self ) )
    
    
    @override
    def __str__( self ) -> str:
        """
        String representation
        """
        return self.name
    
    
    @override
    def __repr__( self ):
        return "{}({})".format( type( self ).__name__, repr( self.name ) )
    
    
    @property
    def documentation( self ) -> str:
        """
        Documentation of the command.
        """
        return self.on_get_documentation()
    
    
    def get_documentation( self ) -> str:
        warnings.warn( "Deprecated - use the `documentation` property instead.", DeprecationWarning )
        return self.documentation
    
    
    def on_get_documentation( self ) -> str:
        """
        The base class returns the documentation passed into the constructor.
        Derived classes may override this to provide a dynamic documentation.
        """
        return self.__documentation
    
    
    
    
    def args_to_kwargs( self, *args ):
        """
        Given a set of arguments appearing in the same order as the arguments for this executable, produces
        a kwargs dictionary compatible with AbstractCommand.run(), AbstractCommand.modify(), AbstractCommand.copy() etc.
        """
        result = { }
        
        if not args:
            return result
        
        arg_list = list( self.args )
        
        if len( args ) > len( arg_list ):
            raise KeyError( "Cannot convert a positional argument list of length {0} to a key-value argument list of length {1}.".format( len( args ), len( arg_list ) ) )
        
        for i, v in enumerate( args ):
            if v is not None:
                result[arg_list[i].name] = v
        
        return result
    
    
    @abstract
    def on_run( self, *args, **kwargs ) -> Optional[object]:
        """
        The derived class should perform the actual command.
        
        :return: A command specific value.
                 
                 This is not presented in the UI, values may be:
                 * function-bound-commands to return values meaningful if executed from Python.
                 * the result to be something that the host (GUI or CLI) can understand
        """
        raise NotImplementedError( "Abstract" )
    
    
    


class SecondaryError( Exception ):
    pass
