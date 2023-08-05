"""
Contains the `BasicCommand` class, as well as the related decorator `command`.
"""

import inspect
import sys
import warnings
from typing import List, Optional, Union

from intermake.commands.visibilities import VisibilityClass
from intermake.engine import constants
from intermake.engine.abstract_command import AbstractCommand
from intermake.engine.environment import Environment
from mhelper import NOT_PROVIDED, NotFoundError, override
from mhelper.reflection_helper import FunctionInspector, IFunction


__author__ = "Martin Rusilowicz"


def command( *,
             names: Optional[Union[str, List[str]]] = None,
             description: Optional[str] = None,
             visibility: Optional[VisibilityClass] = None,
             true_function = None,
             highlight: bool = False,
             register: Union[bool, Environment] = True,
             folder: Optional[str] = None ):
    """
    A decorator for a function which creates and registers a `BasicCommand` using the decorated function.
    
    See `BasicCommand.__init__` for parameter descriptions.
    
    The created command is stored on the function under the `.command` attribute.
    
        ```
        @command()
        def my_function():
            . . .
        
        my_function.command == BasicCommand.retrieve( function ) 
        ```
        
    If used on a class, or callable that is not a `function`, the class is instantiated as an `AbstractCommand` and registered.
    """
    
    
    def ___command( fn ):
        if not inspect.isfunction( fn ):
            warnings.warn( "Deprecated - use `MCMD.environment.commands.register`.", DeprecationWarning )
            command_ = fn()
            fn.instance = command_
        else:
            command_ = BasicCommand( names = names,
                                   description = description,
                                   visibility = visibility,
                                   function = fn,
                                   highlight = highlight,
                                   true_function = true_function,
                                   folder = folder )
        
        if register is not None and register is not False:
            if hasattr( sys, "_getframe" ):
                # inspect.stack is immensely slow so we prefer to use sys._getframe instead
                frame_ = sys._getframe( 1 )
            else:
                frame_ = inspect.stack()[1]
            
            module_ = inspect.getmodule( frame_ )
            
            if register is True:
                register_ = Environment.LAST
            else:
                register_ = register
            
            register_.commands.register( command_, module_ )
        
        setattr( fn, constants.COMMAND_TAG, command_ )
        return fn
    
    
    return ___command


class BasicCommand( AbstractCommand ):
    """
    Wraps a function into an AbstractCommand object.
    """
    
    
    def __init__( self,
                  *,
                  function: IFunction,
                  true_function = None,
                  names: Optional[Union[str, List[str]]] = None,
                  description: Optional[str] = None,
                  visibility: Optional[VisibilityClass] = None,
                  highlight: bool = False,
                  folder: Optional[str] = None ):
        """
        Constructor.
        See `AbstractCommand.__init__` for argument descriptions.
        
        Note that several of the arguments get defaults from the function via reflection, if not provided.
        
        :param function:        Function to call.
                                AbstractCommand arguments are constructed via reflection, hence this must be a fully annotated function.
                                Any argument named `self` is ignored.
        
        :param true_function:   Function to call. `function` is then only used for the reflection stage. If `None`, `function` is used for reflection and calling.
        :param names:           As `AbstractCommand.__init__`, but a default name (the function name) is used if this is `None`.
        :param description:     As `AbstractCommand.__init__`, but a default description (the function documentation) is used if this is `None`.
        :param visibility:      As `AbstractCommand.__init__`.
        :param highlight:       As `AbstractCommand.__init__`.
        :param folder:          As `AbstractCommand.__init__`.
        """
        self.function_info = FunctionInspector( function ) if function is not None else None
        
        if not names:
            if function is None:
                raise ValueError( "If `function` is not provided then `names` must be." )
            
            name = function.__name__
            name = name.strip( "_" )
            name = name.replace( "cmd_", "" )
            names = [name]
        
        args = []
        
        for arg in (self.function_info.args if function is not None else ()):
            if arg.name != "self":
                args.append( arg )
        
        super().__init__( names = names,
                          documentation = description or (self.function_info.description if function is not None else ""),
                          highlight = highlight,
                          visibility = visibility,
                          folder = folder,
                          args = args )
        
        self.function = true_function if true_function is not None else function
        
        assert self.function is not None and hasattr( self.function, "__call__" ), (
            "A `{}` requires a callable object or `None` as its `function`, but this object «{}» : «{}» is not callable."
                .format( BasicCommand.__name__,
                         type( self.function ),
                         self.function ))
    
    
    @classmethod
    def retrieve( cls, function, default = NOT_PROVIDED ) -> AbstractCommand:
        """
        Retrieves the `function.command` object.
        Unlike `function.command` this presents a more useful error message if the attribute does not exist.
        If `function` is itself an `AbstractCommand` it is simply returned.
        """
        if isinstance( function, AbstractCommand ):
            return function
        
        if hasattr( function, constants.COMMAND_TAG ) and isinstance( getattr( function, constants.COMMAND_TAG ), AbstractCommand ):
            return getattr( function, constants.COMMAND_TAG )
        
        if default is not NOT_PROVIDED:
            return default
        
        raise NotFoundError( "The specified object «{}» has no `.{}` tag. Check the object is a function and has been bound to an `{}` using the `@{}` decorator."
                             .format( function,
                                      constants.COMMAND_TAG,
                                      AbstractCommand.__name__,
                                      command.__name__ ) )
    
    
    @override
    def on_run( self, *args, **kwargs ) -> Optional[object]:
        """
        INHERITED
        """
        if self.function is None:
            raise NotImplementedError( "Cannot call `on_run` on a BasicCommand «{}» with `function = None`. `on_run` should be overridden for such commands.".format( self ) )
        
        return self.function( *args, **kwargs )


