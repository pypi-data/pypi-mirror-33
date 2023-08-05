import inspect
import warnings
from typing import Dict, Iterable, Iterator, List, Tuple

from intermake.engine import cli_helper
from intermake.engine.abstract_command import AbstractCommand, ArgumentCollection
from intermake.engine.environment import MCMD
from intermake.engine.theme import Theme
from mhelper import MOptional, array_helper, reflection_helper
from mhelper.comment_helper import abstract, override, sealed, virtual
from mhelper.reflection_helper import ArgInspector


class FieldToArg:
    def __init__( self, argument: ArgInspector, field_name: str, target_object: object, target_name: str ):
        self.argument = argument
        self.field_name = field_name
        self.target_object = target_object
        self.target_name = target_name
    
    
    def get_value( self ):
        return getattr( self.target_object, self.field_name )
    
    
    def set_value( self, value ):
        setattr( self.target_object, self.field_name, value )


class FieldToArgCollection:
    def __init__( self ):
        self.__arguments: List[ArgInspector] = []
        self.__contents: Dict[str, FieldToArg] = { }
    
    
    def get_field( self, arg_name: str ):
        return self.__contents[arg_name]
    
    
    def get_arguments( self ):
        return ArgumentCollection( self.__arguments )
    
    
    def add_arg( self, arg: ArgInspector ):
        self.__arguments.append( arg )
    
    
    def iter_fields( self ) -> Iterable[FieldToArg]:
        return self.__contents.values()
    
    
    def read( self, target: object, target_name: str = "unnamed" ):
        """
        Extracts the arguments from a sample's fields. 
        :param target: 
        :param target_name: 
        :return: Iterator of:
                    N: Tuple of:
                        0: Argument, as an `ArgInspector`
                        1: Python name of the field
        """
        
        if target is None:
            return
        
        documentation_dict = { }
        
        for x in inspect.getmro( type( target ) ):
            documentation_dict.update( reflection_helper.extract_documentation( x.__doc__, "ivar" ) )
        
        for field_name, field_value in target.__dict__.items():
            if field_name.startswith( "_" ):
                continue
            
            if target_name:
                argument_name = "{}/{}".format( target_name, field_name )
            else:
                argument_name = field_name
            
            if not argument_name:
                continue
            
            documentation = documentation_dict.get( field_name )
            
            if documentation is None:
                msg = "A AbstractSetterCommand references the field " + Theme.ERROR_BOLD + "`{}::{}`" + Theme.RESET + " (under the name `{}`) on the sample object «{}», but does not provide any documentation for that field."
                warnings.warn( msg.format( type( target ).__name__, field_name, argument_name, target ), UserWarning )
                documentation = "Not documented :("
            
            if type( field_value ) in (str, int, float, bool):
                default = field_value
                annotation = type( field_value )
            else:
                default = None
                annotation = MOptional[type( field_value )]
            
            self.__contents[argument_name] = FieldToArg( ArgInspector( argument_name, annotation, default, documentation ), field_name, target, target_name )


class AbstractSetterCommand( AbstractCommand ):
    """
    Sets values on an object.
    """
    
    
    def get_targets( self ) -> Iterator[Tuple[str, object]]:
        for item in self.on_get_targets():
            if isinstance( item, tuple ):
                yield item
            else:
                yield "", item
    
    
    def get_fields( self ) -> FieldToArgCollection:
        """
        Given the `key` property, returns the name of the associated parameter, or `None` if the parameter should be hidden.
        The default implementation returns the key verbatim.
        """
        
        result = FieldToArgCollection()
        
        for key, target in self.get_targets():
            if type( target ) in (dict, list):
                continue
            
            result.read( target, key )
        
        return result
    
    
    def on_get_args( self ) -> ArgumentCollection:
        return self.get_fields().get_arguments()
    
    
    @abstract
    def on_get_targets( self ) -> Iterator[Tuple[str, object]]:
        """
        Derived class must provide the target(s) to be modified.
        Yield the name of the target, and the target.
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def on_set_target( self, name: str, target: object ):
        """
        After modification, the derived class may save the target.
        """
        pass
    
    
    @override
    @sealed
    def on_run( self, **kwargs ):
        """
        Sets the specified value(s).
        """
        map: FieldToArgCollection = self.get_fields()
        
        modified_keys = { }
        
        r = []
        
        for arg_name, arg_value in kwargs.items():
            if arg_value is None:
                continue
            
            accessor = map.get_field( arg_name )
            existing = accessor.get_value()
            
            if existing == arg_value:
                continue
            
            accessor.set_value( arg_value )
            
            modified_keys[accessor.target_name] = accessor.target_object
            
            r.append( cli_helper.format_kv( arg_name, arg_value, "->" ) )
        
        if modified_keys:
            for data_key, data_target in modified_keys.items():
                self.on_set_target( data_key, data_target )
        else:
            last = None
            
            for arg in map.iter_fields():
                if arg.target_name is not last:
                    r.append( "" )
                    r.append( arg.target_name )
                    last = arg.target_name
                
                try:
                    text = arg.get_value()
                except AttributeError as ex:
                    text = repr( ex )
                
                if array_helper.is_simple_iterable( text ):
                    text = "List of {} items".format( len( text ) )
                else:
                    text = str( text )
                
                if len( text ) > 40:
                    text = text[:40] + "..."
                
                r.append( cli_helper.format_kv( arg.argument.name, text, ":" ) )
        
        MCMD.information( "\n".join( r ) )
