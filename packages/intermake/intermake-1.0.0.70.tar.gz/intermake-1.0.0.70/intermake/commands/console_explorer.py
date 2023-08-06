"""
Provides a basic interface for exploring $(APP_NAME)s internal memory from the command line.
NOTE: These commands are intended for use via ConsoleHost. They may not work or be relevant to other hosts!
"""
from typing import Optional, List, Union, TypeVar, Type
from mhelper import string_helper, AnnotationInspector, exception_helper, ansi_helper, ansi_format_helper

from intermake.engine.environment import MCMD, MENV, _DefaultRoot
from intermake.commands import visibilities
from intermake.commands.visibilities import VisibilityClass
from intermake.commands.basic_command import command
from intermake.visualisables.visualisable import IVisualisable, VisualisablePath, EIterVis
from intermake.engine.theme import Theme


__mcmd_folder_name__ = "CLI"

T = TypeVar( "T" )

_RE_VISIBILITY = VisibilityClass( name = "console_explorer",
                                  is_visible = lambda: MENV.root is not None and not isinstance( MENV.root, _DefaultRoot ) and MCMD.host.is_cli, comment = "Functions for viewing the application hierarchy from the command line. Enabled by default if the application supports a hierarchy and a console host is being used." )


def re_command( visibility = None, **kwargs ):
    """
    Decorator that behaves as `command` but truncates the leading `re_` from the command name.
    """
    visibility = _RE_VISIBILITY[visibility]
    
    
    def __re_command( fn ):
        return command( names = [fn.__name__.replace( "re_", "" ),
                                 fn.__name__.replace( "re_", "cx_" )],
                        visibility = visibility,
                        **kwargs )( fn )
    
    
    return __re_command


@re_command( visibility = visibilities.CLI )
def re_ls( item: Optional[VisualisablePath] = None, limit: int = 10 ):
    """
    Lists the contents of the current "working-item".
    
    :param item: Item to list, or `None` to list the working-item (see the `cd` command). 
    :param limit: Limits the display to this many results (use `-1` for no limit)
    """
    message = resultsexplorer_ls( item, limit )
    MCMD.information( message )


@re_command( visibility = visibilities.CLI[visibilities.ADVANCED] )
def re_dir( item: Optional[VisualisablePath] = None, limit: int = 50 ):
    """
    Alias for `re_ls`, but with a higher default display limit.
    
    :param item: Item to list, or `None` to list the working-item (see the `dir` command). 
    :param limit: Limits the display to this many results (use `-1` for no limit)
    """
    re_ls( item, limit )


def __inset( x ):
    return Theme.BORDER + x + Theme.RESET


def print_comment( print, x ):
    host = MCMD.host
    print( __inset( Theme.C.VERTICAL + " " ) + x.ljust( host.console_width - 4 ) + __inset( " " + Theme.C.VERTICAL ) )


def resultsexplorer_ls( item: Optional[VisualisablePath] = None, limit = 10 ):
    if item is None:
        item = current_path()
    
    exception_helper.assert_instance( "item", item, VisualisablePath )
    
    host = MCMD.host
    w = host.console_width - 2
    
    message = []
    
    message.append( __inset( Theme.C.TOP_LEFT + Theme.C.HORIZONTAL * w + Theme.C.TOP_RIGHT ) )
    message.append( __inset( Theme.C.VERTICAL + " " ) + Theme.TITLE + ansi_helper.ljust( item.path, host.console_width - 4 ) + Theme.RESET + __inset( " " + Theme.C.VERTICAL ) )
    
    __print_row( message, [-1, False], item, True )
    
    message.append( __inset( Theme.C.LEFT_BAR + Theme.C.HORIZONTAL * w + Theme.C.RIGHT_BAR ) )
    
    index = [0, False]
    last_info = item
    
    try:
        # for item2 in last_info.iter_children( iter = EIterVis.BASIC ):
        #     if str(item2.get_raw_value()):
        #         __print_row( message, index, item2, limit )
        
        # index[1] = True
        any_ = False
        
        for item2 in last_info.iter_children( iter = EIterVis.PROPERTIES ):
            __print_row( message, index, item2, limit )
            any_ = True
        
        index[1] = any_
        
        for item2 in last_info.iter_children( iter = EIterVis.CONTENTS ):
            __print_row( message, index, item2, limit )
    
    except StopIteration as ex:
        print_comment( message.append, str( ex ) )
    
    message.append( __inset( Theme.C.BOTTOM_LEFT + Theme.C.HORIZONTAL * w + Theme.C.BOTTOM_RIGHT ) )
    
    return "\n".join( message )


def __print_row( output: List[str], index: List[Union[int, bool]], value: VisualisablePath, limit ):
    """
    Internally used to print a result using the InstanceHandler
    """    
    if 0 < limit == index[0]:
        raise StopIteration( "Not printing any more contents due to `limit` = {0} parameter.".format( limit ) )
    
    host = MCMD.host
    
    alt = (index[0] % 2) == 0
    
    name = host.translate_name( value.key )
    
    col_colour_1 = value.ccolour.fore
    col_colour_2 = col_colour_1 + Theme.CX_VALUE
    
    width_name_ = 20
    width_class = 25
    width_value = host.console_width - (width_name_ + width_class + 4)
    
    text_name_ = string_helper.max_width( name, width_name_ - 1 )
    text_value = string_helper.max_width( value.text, width_value - 1 )
    text_class = string_helper.max_width( value.type_name, width_class - 1 )
    
    colour_class = Theme.CX_CLASS
    
    spacer_colour = Theme.CX_SPACER_1 if alt else Theme.CX_SPACER_2
    spacer_char = Theme.C.SHADE
    
    if index[1]:
        output.append( __inset( Theme.C.LEFT_BAR + Theme.C.HORIZONTAL * (host.console_width - 2) + Theme.C.RIGHT_BAR ) )
        index[1] = False
    
    output.append( __inset( Theme.C.VERTICAL + " " )
                   + col_colour_1 + text_name_ + spacer_colour + spacer_char * (width_name_ - len( text_name_ )) + Theme.RESET  # KEY
                   + col_colour_2 + text_value + spacer_colour + spacer_char * (width_value - len( text_value )) + Theme.RESET  # VALUE
                   + spacer_colour + spacer_char * (width_class - len( text_class )) + colour_class + text_class + Theme.RESET  # TYPE
                   + __inset( " " + Theme.C.VERTICAL ) )
    
    index[0] += 1


@re_command()
def re_view( item: Optional[VisualisablePath] = None, verbose: bool = False ) -> None:
    """
    Displays the full text of the current "working-item".
    :param verbose:    When `True` prints out additional debugging data.
    :param item:    Item to view, or `None` to use the working-item (see the `dir` command). 
    """
    if item is None:
        item = current_path()
    
    message = []
    
    if verbose:
        message.append( "[META]" )
        message.append( "    D.TYPE: {0}".format( type( item.value ).__name__ ) )
        message.append( "    TYPE  : {0}".format( item.type_name ) )
        message.append( "    NAME  : {0}".format( item.key ) )
        message.append( "" )
        
        message.append( "[VALUE]" )
    else:
        message.append( "{} {}".format( item.type_name, item.key ) )
    
    text = str( item.value )
    
    message.append( ansi_format_helper.format_source( text, [], [] ) )
    
    MCMD.print( "\n".join( message ) )


def current_path() -> VisualisablePath:
    host = MCMD.host
    
    from intermake.hosts.console import ConsoleHost
    
    if isinstance( host, ConsoleHost ):
        return host.browser_path
    
    return VisualisablePath.get_root()


@re_command( visibility = visibilities.CLI, highlight = True )
def re_cd( dest: Optional[VisualisablePath] ):
    """
    Changes the "working-item".
    This is the item affected by the results explorer component of the CLI.
    Using `cd` without any parameters displays the current working-item.
    
    Whilst these functions can be used in the GUI, they only affect the CLI-backed working-item - not the item displayed in the GUI views.
    Using the dedicated GUI explorers is therefore recommended.
    
    :param dest:    Specify the name of the element to change to, you can specify the key (first column), or the value (second column) or the zero-based index (right column). Use:
                        `/` to return to the root
                        `..` to move back up to the previous item.
                    If `None` (the default if not specified), the current contents are displayed without changing them. 
    """
    
    host = MCMD.host
    
    from intermake.hosts.console import ConsoleHost
    
    if not isinstance( host, ConsoleHost ):
        raise ValueError( "Cannot obtain the current path because the user is not using a console host." )
    
    host.browser_path = dest
    
    re_ls()


def follow_path( path: str, restrict: type = None ) -> VisualisablePath[T]:
    """
    For use internally, this gets the result from a "path".
    This cannot be called manually because `dest_type` cannot be specified from the CLI or GUI.
     
    :param path: Path to select  
    :param restrict: Type of path to obtain 
    :return: 
    """
    selected_path = current_path().join( path )
    
    if restrict is not None and not AnnotationInspector( restrict ).is_viable_instance( selected_path.value ):
        raise ValueError( "This argument requires a «{}», but you have selected «{}», which is a «{}».".format( restrict, selected_path.value, type( selected_path.value ) ) )
    
    return selected_path
