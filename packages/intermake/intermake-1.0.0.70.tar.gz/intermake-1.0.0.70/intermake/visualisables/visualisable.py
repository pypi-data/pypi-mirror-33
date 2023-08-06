from collections import namedtuple
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, Union

# noinspection PyPackageRequirements
from flags import Flags
from mhelper import FindError, MGeneric, SwitchError, reflection_helper, string_helper, safe_cast, SimpleProxy
from mhelper.qt_resource_objects import ResourceIcon


OUBasic = Union[str, bool, float, int]
OUAcceptable = Optional[Union[str, bool, float, int, List[OUBasic], Dict[str, OUBasic], Tuple[OUBasic], "IVisualisable"]]
OUExtraIter = Any
CColor = namedtuple( "CColor", ("fore", "back") )


class EColour( Enum ):
    MUTED_FOREGROUND = -2
    NORMAL = -1
    BLACK = 0
    BLUE = 1
    GREEN = 2
    CYAN = 3
    RED = 4
    MAGENTA = 5
    YELLOW = 6
    WHITE = 7


class UiHint:
    NONE: "UiHint" = None
    COMPLEX: "UiHint" = None
    TEXT: "UiHint" = None
    LIST: "UiHint" = None
    EXECUTABLE: "UiHint" = None
    FOLDER: "UiHint" = None
    INTEGER: "UiHint" = None
    BOOLEAN: "UiHint" = None
    UNKNOWN: "UiHint" = None
    ERROR: "UiHint" = None
    SUCCESS: "UiHint" = None
    
    
    def __init__( self, icon: Union[str, ResourceIcon], colour: "EColour" ):
        self.icon = icon
        self.colour = colour


UiHint.NONE = UiHint( "type_none", EColour.MUTED_FOREGROUND )
UiHint.COMPLEX = UiHint( "type_complex", EColour.CYAN )
UiHint.TEXT = UiHint( "type_text", EColour.GREEN )
UiHint.LIST = UiHint( "type_list", EColour.YELLOW )
UiHint.EXECUTABLE = UiHint( "type_exe", EColour.RED )
UiHint.FOLDER = UiHint( "type_folder", EColour.YELLOW )
UiHint.INTEGER = UiHint( "type_integer", EColour.GREEN )
UiHint.BOOLEAN = UiHint( "type_boolean", EColour.GREEN )
UiHint.UNKNOWN = UiHint( "type_unknown", EColour.MAGENTA )
UiHint.ERROR = UiHint( "type_error", EColour.RED )
UiHint.SUCCESS = UiHint( "type_success", EColour.GREEN )


class DictProvider:
    """
    Similar to a `dict`/`list`, but uses lazy evaluation to determine its contents.
    - Functions are called and enumerables are iterated only if the contents
      are actually required.
    
    The following items may be added:
        * Any object with an `items` attribute, such as a `dict`, read as `k, v = x.items()`
        * Any object with an `__iter__` attribute, such as a `list`, read as `k, v = enumerate( x )`
        * A function returning any of the above 
        
    Items should be added via `+=` or `update`.
    Items can be retrieved via `retrieve`.
    """
    
    
    def __init__( self ):
        self.__contents = []
    
    
    def __iadd__( self, other: object ) -> "DictProvider":
        return self.update( other )
    
    
    def update( self, dict_: object ) -> "DictProvider":
        assert dict_ is not None
        self.__contents.append( dict_ )
        return self
    
    
    def retrieve( self ) -> Dict[str, object]:
        r = { }
        
        for x in self.__contents:
            x = reflection_helper.defunction( x )
            
            if hasattr( x, "items" ):
                r.update( { str( k ): v for k, v in x.items() } )
            elif hasattr( x, "__iter__" ):
                r.update( { str( i ): v for i, v in enumerate( x ) } )
            else:
                raise SwitchError( "self.__contents[n]", x, instance = True )
        
        return r
    
    
    def set( self, value ) -> None:
        assert value is not None
        self.__contents = [value]


class UiInfo:
    """
    Contains information on an IVisualisable.
    
    :ivar __doc:            Either:
                            * the documentation
                            * a function returning the documentation.
                            The default is `value.__doc__`.
                            
    :ivar text:             Either:
                            * the textual representation of the `value`
                            * a function returning the textual representation.
                            The default is `value.__str__`.
    
    :ivar __properties:     A DictProvider containing the properties,
                            accessed through the `properties` property. 
                            
    :ivar __contents:       A DictProvider containing the contents.
                            accessed through the `__contents` property.
                            
    :ivar hint:             Either:
                            * A `UiHint` describing the type
                            * A function returning a `UiHint`
                            The default is `UiHint.UNKNOWN`
    
    :ivar type_name:        Either:
                            * The type name
                            * A function returning the type name
                            The default is `type(value).__name__`
    """
    Hints = UiHint
    
    
    def __init__( self, value ):
        """
        CONSTRUCTOR
        Applies the defaults for a specified `value`
        """
        self.source = value
        try:
            self.__doc = value.__doc__ or ""
        except AttributeError:
            self.__doc = ""
        self.text = lambda: str( value )
        self.__properties = DictProvider()
        self.__contents = DictProvider()
        self.hint = UiHint.UNKNOWN
        self.type_name = type( value ).__name__
        self.cleared = False
    
    
    @property
    def doc( self ):
        return self.__doc
    
    
    @doc.setter
    def doc( self, value ):
        assert value is not None
        self.__doc = value
    
    
    @property
    def properties( self ):
        """
        Read only accessor on :field:__properties.
        """
        return self.__properties
    
    
    @property
    def contents( self ):
        """
        Read only accessor on :field:__contents.
        """
        return self.__contents
    
    
    @contents.setter
    def contents( self, value ):
        assert value is self.__contents, "The `contents` property is read-only. Did you mean to use `contents += {...}` instead?"
    
    
    @properties.setter
    def properties( self, value ):
        assert value is self.__properties, "The `properties` property is read-only. Did you mean to use `properties += {...}` instead?"


class IVisualisable:
    """
    Provides an abstraction of UI properties beyond a simple `__str__`.
    """
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        """
        The derived class should complete the UI representation of this object.
        See `UiInfo` for more details.
        
        Note that this function should not be called manually - please use `VisualisablePath.info`.
        
        :param u: Value to complete
        """
        u.cleared = True


class EIterVis( Flags ):
    __no_flags_name__ = "NONE"
    __all_flags_name__ = "ALL"
    BASIC = 1
    PROPERTIES = 2
    CONTENTS = 4


class VisualisablePath( MGeneric ):
    """
    Forms a "path" out of Python objects.
    Path elements may provide information on themselves such as names, values, colours, icons, contents, etc.
    
    To control what information is returned, the type should be registered with `register`.
    
    Note that classes implementing `IVisualisable` are automatically use `lambda x: x.on_get_vis_info()`.
    Similarly the `object` class is registered to use `__create_fallback`.
    (These are not physically registered with REG_TYPES for efficiency, though they could be).
    """
    SEP = "/"
    REG_TYPES = { }
    
    
    # region Class methods
    
    @classmethod
    def register_vis_handler( cls, type_, handler ):
        cls.REG_TYPES[type_] = handler
    
    
    @classmethod
    def get_root( cls ):
        from intermake.engine.environment import MCMD
        env = MCMD.environment
        return cls.from_visualisable_root( env.root, name = SimpleProxy( lambda: env.root_name ) )
    
    
    @classmethod
    def from_visualisable_root( cls, vis: object, name: str = "root" ) -> "VisualisablePath":
        return VisualisablePath( None, name, vis, True )
    
    
    @classmethod
    def type_restriction( cls ) -> Type[IVisualisable]:
        """
        Obtains the generic parameter (if not specified returns IVisualisable).
        """
        if cls.__parameters__ is None or len( cls.__parameters__ ) == 0:
            return IVisualisable
        elif len( cls.__parameters__ ) == 1:
            return cls.__parameters__[0]
        else:
            raise ValueError( "A `VisualisablePath` was constructed with the confusing generic parameters «{0}».".format( cls.__parameters__ ) )
    
    
    @classmethod
    def from_visualisable_temporary( cls, vis: object, name = "" ) -> "VisualisablePath":
        """
        Creates a `VisualisablePath` from an object. 
        :param name: Name of element in path returned
        :param vis:  Target object. 
        """
        return VisualisablePath( None, name, vis, False )
    
    
    # endregion
    
    
    def __init__( self,
                  previous: Optional["VisualisablePath"],
                  key: str,
                  value: object,
                  is_root: bool = False,
                  is_property: bool = False ):
        """
        :param previous:        Previous element in path, or `None` if this is the root or the previous elements are unknown. 
        :param key:             Key for this element. This can be any type, for instance a `SimpleProxy`; it will be coerced into a `str` when retrieved. 
        :param value:           The element in the path being represented
        :param is_root:         Whether this element is the root. 
        :param is_property:     Whether this element is a child property of the previous element, otherwise it is assumed to be a child element. 
        """
        self.previous = previous
        self.__key = key
        self.__value = value
        self.is_root = is_root
        self.is_property = is_property
    
    
    @property
    def key( self ) -> str:
        return str( self.__key )
    
    
    def __repr__( self ):
        return "{}(previous={}, key={}, value={}, is_root={})".format( type( self ).__name__, repr( self.previous ), repr( self.key ), repr( self.__value ), repr( self.is_root ) )
    
    
    def join( self, dest: str ) -> "VisualisablePath":
        """
        Returns a new `VisualisablePath` incorporating the new path.
        :param dest: String representation of path
        """
        from intermake.engine.environment import MENV, MCMD
        
        # Where are we now?
        current = self
        env = MENV
        
        # Do we go back to the root?
        for x in (env.root_name, self.SEP):
            if dest.startswith( x ):
                dest = dest[len( x ):]
                current = self.get_root()
                break
        
        # Iterate over the elements
        for element in dest.split( self.SEP ):
            if not element:
                continue
            
            # No change: "."
            if element == ".":
                continue
            
            # Up one level: ".."
            if element == "..":
                if current.previous is None:
                    raise KeyError( "Cannot go up to «{}» (you are already at the top level' - «{}»)".format( element, current ) )
                else:
                    current = current.previous
                    continue
            
            element = MCMD.host.translate_name( element ).lower()
            children = list( current.iter_children() )
            
            try:
                the_next = string_helper.find( source = children,
                                               search = element,
                                               namer = lambda x: MCMD.host.translate_name( x.key ).lower(),
                                               fuzzy = False )
            except FindError:
                try:
                    the_next = string_helper.find( source = children,
                                                   search = element,
                                                   namer = lambda x: MCMD.host.translate_name( x.get_value().get_vis_info().name ).lower(),
                                                   fuzzy = False )
                except FindError as ex:
                    raise LookupError( "Cannot find «{}» in «{}».".format( element, current ) ) from ex
            
            current = the_next
        
        return current
    
    
    @property
    def path( self ):
        if self.previous:
            return self.previous.path + self.SEP + self.key
        elif self.is_root:
            return self.SEP + self.key
        else:
            return "..." + self.SEP + self.key
    
    
    def __has_info( self ):
        return isinstance( self.__value, IVisualisable )
    
    
    def __get_info( self ) -> "UiInfo":
        v = self.__value
        cls = type( self )
        
        # Construct the info
        u = UiInfo( v )
        c = False
        
        # Any `REG_TYPES` get a chance to write
        for vt in reversed( reflection_helper.list_hierarchy( type( v ) ) ):
            fn = cls.REG_TYPES.get( vt )
            if fn is not None:
                fn( u )
                c = True
        
        # `IVisualisable` gets a chance to write 
        if isinstance( v, IVisualisable ):
            v.on_get_vis_info( u )
            c = True
        
        if not c:
            u.hint = UiHint.COMPLEX
            u.doc = type( u.source ).__doc__ or ""
            
            if hasattr( u.source, "__dict__" ):
                u.properties += u.source.__dict__
            
            if hasattr( u.source, "__iter__" ):
                u.contents += u.source
        
        return u
    
    
    @property
    def text( self ) -> str:
        """
        Text of the item.
        The default is str(value)
        """
        return safe_cast( str, reflection_helper.defunction( self.__get_info().text ), info = self )
    
    
    @property
    def icon( self ) -> ResourceIcon:
        """
        Icon of the item.
        Usually corresponds to the type.
        """
        r = reflection_helper.defunction( self.__get_info().hint ).icon
        
        if isinstance( r, str ):
            r = ResourceIcon( r )
        
        return r
    
    
    @property
    def documentation( self ) -> str:
        """
        Documentation of the item. 
        """
        return safe_cast( str, reflection_helper.defunction( self.__get_info().doc ), info = self )
    
    
    @property
    def colour( self ) -> EColour:
        """
        Colour of the item.
        Usually corresponds to the type.
        """
        return safe_cast( EColour, reflection_helper.defunction( self.__get_info().hint ).colour, info = self )
    
    
    @property
    def type_name( self ) -> str:
        return safe_cast( str, reflection_helper.defunction( self.__get_info().type_name ), info = self )
    
    
    @property
    def ccolour( self ) -> CColor:
        """
        Console colour
        :return: Tuple (FG, BG) 
        """
        from colorama import Back, Fore
        
        c = self.colour
        if c == EColour.RED:
            return CColor( Fore.RED, Back.RED )
        elif c == EColour.GREEN:
            return CColor( Fore.GREEN, Back.GREEN )
        elif c == EColour.BLUE:
            return CColor( Fore.BLUE, Back.BLUE )
        elif c == EColour.CYAN:
            return CColor( Fore.CYAN, Back.CYAN )
        elif c == EColour.MAGENTA:
            return CColor( Fore.MAGENTA, Back.MAGENTA )
        elif c == EColour.YELLOW:
            return CColor( Fore.YELLOW, Back.YELLOW )
        elif c == EColour.BLACK:
            return CColor( Fore.BLACK, Back.BLACK )
        elif c == EColour.WHITE:
            return CColor( Fore.WHITE, Back.WHITE )
        elif c == EColour.NORMAL:
            return CColor( Fore.RESET, Back.RESET )
        elif c == EColour.MUTED_FOREGROUND:
            return CColor( Fore.LIGHTBLACK_EX, Back.LIGHTBLACK_EX )
        else:
            raise SwitchError( "c", c )
    
    
    @property
    def qcolour( self ):
        """
        QT Colour
        :rtype: QColor
        """
        from PyQt5.QtGui import QColor
        from PyQt5.QtCore import Qt
        
        c = self.colour
        if c == EColour.RED:
            return QColor( Qt.darkRed )
        elif c == EColour.GREEN:
            return QColor( Qt.darkGreen )
        elif c == EColour.BLUE:
            return QColor( Qt.darkBlue )
        elif c == EColour.CYAN:
            return QColor( Qt.darkCyan )
        elif c == EColour.MAGENTA:
            return QColor( Qt.darkMagenta )
        elif c == EColour.YELLOW:
            return QColor( Qt.darkYellow )
        elif c == EColour.BLACK:
            return QColor( Qt.black )
        elif c == EColour.WHITE:
            return QColor( Qt.darkYellow )
        elif c == EColour.NORMAL:
            return QColor( Qt.black )
        elif c == EColour.MUTED_FOREGROUND:
            return QColor( Qt.gray )
        else:
            raise SwitchError( "c", c )
    
    
    def iter_children( self, iter: EIterVis = EIterVis.ALL ) -> Iterator["VisualisablePath"]:
        """
        Iterates the children of this `UiInfo`, yielding `VisualisablePath`s.
        """
        try:
            i = self.__get_info()
            
            if iter.BASIC:
                yield VisualisablePath( self, "name", self.key, is_property = True )
                yield VisualisablePath( self, "documentation", self.documentation, is_property = True )
            
            if iter.PROPERTIES:
                for key, value in sorted( i.properties.retrieve().items(), key = lambda x: x[0] ):
                    value = reflection_helper.defunction( value )
                    yield VisualisablePath( self, key, value, is_property = True )
            
            if iter.CONTENTS:
                for key, value in sorted( i.contents.retrieve().items(), key = lambda x: x[0] ):
                    value = reflection_helper.defunction( value )
                    yield VisualisablePath( self, key, value )
        except Exception as ex:
            raise ValueError( "Error iterating children of {}.".format( self ) ) from ex
    
    
    def __str__( self ):
        if self.is_root:
            return self.key
        else:
            return self.path
    
    
    @property
    def value( self ):
        return self.__value


def __register_fallbacks() -> None:
    r = VisualisablePath.REG_TYPES
    
    
    def _str( u: UiInfo ):
        u.text = u.source
        u.hint = UiHint.TEXT
    
    
    def _int( u: UiInfo ):
        u.hint = UiHint.INTEGER
    
    
    def _bool( u: UiInfo ):
        u.hint = UiHint.BOOLEAN
    
    
    def _list( u: UiInfo ):
        u.hint = UiHint.LIST
        u.text = lambda: "{} items".format( len( u.source ) )
        u.contents += u.source
    
    
    def _dict( u: UiInfo ):
        u.hint = UiHint.FOLDER
        u.text = lambda: "{} items".format( len( u.source ) )
        u.contents += u.source
    
    
    r[int] = _int
    r[float] = _int
    r[bool] = _bool
    r[list] = _list
    r[tuple] = _list
    r[dict] = _dict
    r[str] = _str


__register_fallbacks()
