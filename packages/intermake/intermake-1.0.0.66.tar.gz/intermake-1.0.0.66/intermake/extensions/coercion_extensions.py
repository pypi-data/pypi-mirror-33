from typing import Optional, Dict, Union

import stringcoercion
from mhelper import exception_helper
from stringcoercion import AbstractCoercer, CoercionInfo, CoercionError

from intermake.visualisables.visualisable import VisualisablePath
from intermake.commands import console_explorer


class _VisualisableCoercionSettings:
    """
    A class which may be used to control the Visualisable coercions.
    """
    
    
    def __init__( self ):
        self.__auto_search: Dict[type, str] = { }
        self.treat_as_visualisable = []
    
    
    def register_as_explorable( self, type_: type ):
        self.treat_as_visualisable.append( type_ )
    
    
    def register_auto_search( self, type_: type, path: Union[str, VisualisablePath] ) -> None:
        """
        For `IVisualisable`s of the specified type, the specified path will be searched when the user
        types its name or number.
        :param type_:   Type to register 
        :param path:    Path to search
        """
        if not isinstance( path, str ):
            if not isinstance( path, VisualisablePath ):
                raise exception_helper.type_error( "path", path, Union[str, VisualisablePath] )
            
            path = path.path
        
        self.__auto_search[type_] = path
    
    
    def _get_auto_search( self, type_: type ):
        path = self.__auto_search.get( type_ )
        
        if path:
            return path
        else:
            return None


VISUALISABLE_COERCER = _VisualisableCoercionSettings()
"""
An object which may be used to control the Visualisable coercions.
See `_VisualisableCoercionSettings`.
"""


def coerce_explorable( text: str, type_: type ) -> VisualisablePath:
    # Do we have an auto-searcher?
    ext = VISUALISABLE_COERCER._get_auto_search( type_ )
    
    if not VisualisablePath.SEP in text and ext:
        text = ext + VisualisablePath.SEP + text
    
    # Get the path
    r: VisualisablePath = console_explorer.follow_path( path = text, restrict = type_ )
    
    if not isinstance( r.value, type_ ):
        raise CoercionError( "Select visualisable failed. This argument requires a «{}», but you have selected «{}», which is a «{}».".format( type_, r, type( r.value ) ), cancel = True )
    
    return r


class _ExplorableCoercer( AbstractCoercer ):
    """
    Elements appearing in the Intermake hierarchy may be referenced by providing their _name_ or _path_.
    
    e.g. `null`
    e.g. `/endpoints/null`
    """
    
    
    def on_coerce( self, info: CoercionInfo ) -> Optional[object]:
        type_ = info.annotation.value
        vis = coerce_explorable( info.source, type_ ).value
        return vis
    
    
    def on_get_priority( self ):
        return self.PRIORITY.LOW
    
    
    def on_get_archetype( self ) -> Optional[type]:
        if not VISUALISABLE_COERCER.treat_as_visualisable:
            return None
        
        return Union[VISUALISABLE_COERCER.treat_as_visualisable]


class _VisualisablePathCoercion( AbstractCoercer ):
    """
    Paths appearing in the Intermake hierarchy may be referenced by providing their _name_ or _path_.
    
    e.g. `null`
    e.g. `/endpoints/null`
    """
    
    def on_coerce( self, info: CoercionInfo ) -> Optional[object]:
        return coerce_explorable( info.source, info.annotation.value.type_restriction() )
    
    
    def on_get_archetype( self ) -> type:
        return VisualisablePath


class _MAnnotationCoercer( AbstractCoercer ):
    """
    Annotations providing UI hints can be ignored.
    For instance a `Filename[str]` can be presented as any other `str` and a `Limited[int, min = 1, max = 5]` can be presented as any other `int`.
    
    e.g. `c:/folder/file.txt`
    e.g. `123`
    """
    
    def on_coerce( self, args: CoercionInfo ):
        return args.collection.coerce( args.annotation.mannotation_arg, args.source )
    
    
    def on_get_archetype( self ) -> type:
        from mhelper import MAnnotation
        return MAnnotation
    
    
    def on_can_handle( self, info: CoercionInfo ) -> bool:
        return info.annotation.is_mannotation


def init():
    # Register them
    stringcoercion.get_default_collection().register( _ExplorableCoercer(),
                                                      _VisualisablePathCoercion(),
                                                      _MAnnotationCoercer() )
