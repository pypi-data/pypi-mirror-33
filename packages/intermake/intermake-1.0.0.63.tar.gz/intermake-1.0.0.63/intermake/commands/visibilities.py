import warnings
from typing import Optional, Callable
from mhelper import reflection_helper


DPredicate = Callable[[], bool]
TPredicate = "Optional[Union[bool, DPredicate]]"


class VisibilityClass:
    """
    Designates a class that manages visibility of an `AbstractCommand`.
    It is a callable returning a boolean, so can be passed to the `AbstractCommand`'s `visibility` parameter.
    
    Example:
    ```
    MARTINS_SET = VisibilityClass( name = "martin", default = False )
    
    @command(visibility = MARTINS_SET)
    def martins_command(...):
        ....
        
    @command(visibility = MARTINS_SET[lambda: time().minute == 42])
    def hourly(...):
        ....
        
    def show_martins_command():
        MARTINS_SET.user_override = True        
    ```
     
    """
    
    
    def __init__( self, *, name: str, is_functional: TPredicate = None, is_visible: TPredicate = None, comment = None, parents = None ):
        """
        CONSTRUCTOR
        :param *: 
        :param is_functional: 
        :param name:            Name of the class
        :param is_functional:   Is this set functional? (see `VisibilityClass`).
                                If this is `False` the class won't even show up in the list of optional `VisibilityClass`es.
        :param is_visible:      Default visibility (see `VisibilityClass`).
        """
        if is_functional is None:
            is_functional = True
        
        if is_visible is None:
            is_visible = is_functional
        
        self.name: str = name
        self.user_override: Optional[bool] = None
        self.comment: str = comment or ""
        self.parents = parents
        
        self.__fn_is_visible_by_default: DPredicate = reflection_helper.as_delegate( is_visible, bool )
        self.__fn_is_functional: DPredicate = reflection_helper.as_delegate( is_functional, bool )
    
    
    def __call__( self ) -> bool:
        """
        Obsolete decoration that just returns is_visible. Please don't use this.
        """
        warnings.warn( "Deprecated - use `is_visible`", DeprecationWarning )
        
        return self.is_visible
    
    
    def __getitem__( self, item: TPredicate ):
        """
        Obsolete function that is the same as `and`, please don't use this.
        """
        warnings.warn( "Deprecated - use `__and__`", DeprecationWarning )
        
        if item is None:
            return self
        
        if item is True:
            return self
        
        return self & item
    
    
    @property
    def is_functional( self ):
        return self.__fn_is_functional()
    
    
    @property
    def is_visible_by_default( self ):
        return self.__fn_is_visible_by_default()
    
    
    @property
    def is_visible( self ):
        if self.user_override is True:
            return True
        elif self.user_override is False:
            return False
        
        return self.is_visible_by_default
    
    
    def __and__( self, other ):
        """
        Combines two visibility classes together.
        
        The resulting class will be visible only if both the classes are visible (A AND B).
        The resulting class will be highlighted if it is visible and either of the classes are highlighted (A OR B).
        
        The result is not considered "functional" so won't show up in lists.
        """
        return VisibilityClass( name = self.name + " & " + other.name,
                                is_functional = False,
                                is_visible = lambda: self.is_visible and other.is_visible,
                                parents = (self, other) )
    
    
    def __str__( self ) -> str:
        return "{} is {}".format( self.name, "visible" if self.user_override else "hidden" )




def __is_gui_host() -> bool:
    from intermake.engine.environment import MCMD
    return MCMD.host.is_gui


def __is_cli_host() -> bool:
    from intermake.engine.environment import MCMD
    return MCMD.host.is_cli


HELP = VisibilityClass( name = "help",
                        is_visible = False,
                        comment = "Help commands. Hidden by default because they are already listed using the `help` command." )

COMMON = VisibilityClass( name = "common",
                          comment = "Common commands. Visible by default." )


ADVANCED = VisibilityClass( name = "advanced",
                            is_visible = False,
                            comment = "Advanced commands. Hidden by default." )

CLI = VisibilityClass( name = "cli",
                       is_visible = __is_cli_host,
                       comment = "Commands best suited to the CLI." )

GUI = VisibilityClass( name = "gui",
                       is_visible = __is_gui_host,
                       comment = "Commands best suited to the GUI." )

TEST = VisibilityClass( name = "test",
                        is_functional = False,
                        comment = "Commands for testing and debugging." )

INTERNAL = VisibilityClass( name = "internal",
                            is_functional = False,
                            comment = "Commands for use internally." )
