"""
Helper functions for CLI-based `AbstractCommand`s.
"""

from enum import Enum
from typing import List, Optional, Union

# noinspection PyPackageRequirements
from flags import Flags

from intermake.engine import constants
from intermake.engine.environment import MCMD
from intermake.engine.abstract_command import AbstractCommand
from intermake.engine.theme import Theme
from mhelper import ansi, ansi_format_helper, ansi_helper, string_helper, markdown_helper


__print_banner_displayed = False


def get_details_text( command: AbstractCommand ) -> str:
    """
    Gets the help text of the specified `AbstractCommand`, formatted for display in the CLI and returned as a single string.
    """
    result = []
    get_details( result, command )
    return "\n".join( result )


def get_details( result: List[str], command: AbstractCommand, show_quick: bool = False ) -> None:
    """
    Gets the help text of the specified `AbstractCommand`, formatted for display in the CLI and returned as a list of lines.
    """
    type_ = ""
    
    type_colour = Theme.BOX_TITLE_RIGHT
    bar_colour = Theme.BORDER
    deco_colour = type_colour
    
    name = MCMD.host.translate_name( command.name )  # type:str
    
    if not command.is_visible:
        name_colour_extra = Theme.SYSTEM_NAME
    elif command.is_highlighted:
        name_colour_extra = Theme.CORE_NAME
    else:
        name_colour_extra = Theme.COMMAND_NAME
    
    env = MCMD.environment
    line_width = env.host.console_width
    
    result_b = []
    
    if show_quick:
        name = name.ljust( 20 )
        prefix = Theme.BORDER + "::" + Theme.RESET
        
        result_b.append( prefix + " " + type_colour + type_ + Theme.RESET + " " + name_colour_extra + name + Theme.RESET + " -" )
        
        line = command.documentation.strip()
        line = env.host.substitute_text( line )
        
        line = line.split( "\n", 1 )[0]
        
        line = string_helper.fix_width( line, line_width - len( name ) - 10 )
        
        line = highlight_keywords( line, command, Theme.COMMAND_NAME, Theme.COMMENT )
        
        result_b.append( " " + Theme.COMMENT + line + Theme.RESET + " " + prefix )
        
        result.append( "".join( result_b ) )
        
        return
    
    DESC_INDENT = 4
    
    ARG_INDENT = 8
    ARG_DESC_INDENT = 30
    
    DESC_INDENT_TEXT = " " * DESC_INDENT
    
    result.append( "  "
                   + bar_colour + "_"
                   + name_colour_extra + name
                   + bar_colour + "_" * (line_width - len( name ) - len( type_ ) - 4)
                   + deco_colour
                   + type_colour + type_
                   + Theme.RESET )
    
    alt_names = [x for x in command.names if x != name]
    
    if alt_names:
        result.append( Theme.COMMENT + "  Aliases: " + ", ".join( alt_names ) + Theme.RESET )
    
    #
    # DESCRIPTION
    #
    desc = command.documentation
    desc = format_doc( desc )
    
    for line in ansi_helper.wrap( desc, line_width - DESC_INDENT ):
        result.append( DESC_INDENT_TEXT + line + Theme.RESET )
    
    #
    # ARGUMENTS
    #
    extra : str = None
    
    for i, arg in enumerate( command.args ):
        desc = arg.description or (str( arg.annotation ) + (" (default = " + str( arg.default ) + ")" if arg.default is not None else ""))
        desc = format_doc( desc, width = -1 )
        
        t = arg.annotation
        
        viable_subclass_type = t.get_indirect_subclass( Enum ) or t.get_indirect_subclass( Flags )
        
        if viable_subclass_type is not None:
            desc += Theme.RESET
            
            for k in viable_subclass_type.__dict__.keys():
                if not k.startswith( "_" ):
                    desc += "\n" + Theme.ENUMERATION + " * " + Theme.COMMAND_NAME + k + Theme.RESET
            
            desc += Theme.RESET
            
            if not extra:
                extra = arg.name
        
        blb = ansi.FORE_BRIGHT_CYAN
        
        arg_name = Theme.ARGUMENT_NAME + blb + MCMD.host.translate_name( arg.name ) + "\n"
        
        default_text = str( arg.default ) if arg.default is not None else ""
        
        arg_name += "  " + Theme.COMMENT + blb + default_text
        
        desc += "\n"
        
        result.append( ansi_format_helper.format_two_columns( left_margin = ARG_INDENT,
                                                              centre_margin = ARG_DESC_INDENT,
                                                              right_margin = line_width,
                                                              left_text = arg_name,
                                                              right_text = desc,
                                                              left_prefix = Theme.ARGUMENT_NAME + blb,
                                                              left_suffix = ansi.RESET ) )
    
    if extra:
        result.append( "" )
        result.append( "    " + Theme.ENUMERATION + "*" + Theme.RESET +
                       " Specify the argument when you call " + Theme.COMMAND_NAME + "help" +
                       Theme.RESET + " to obtain the full details for these values. E.g. “" +
                       Theme.COMMAND_NAME + "help " + command.display_name + " " + extra + Theme.RESET + "." )
        result.append( "" )


def format_doc( doc: str, width: int = 0 ) -> str:
    """
    Formats markdown.
    
    :param doc:        Restructured text.
    :param width:      Width of text, otherwise the console width will be used.
    :return:           Formatted text.
    """
    if doc is None:
        doc = ""
    
    doc = doc.strip()
    doc = MCMD.host.substitute_text( doc )
    doc = markdown_helper.markdown_to_ansi( doc, width = width or MCMD.host.console_width )
    doc = string_helper.highlight_quotes( doc, "«", "»", Theme.EMPHASIS, Theme.RESET )
    doc = string_helper.highlight_quotes( doc, '"', '"', '«' + Theme.EMPHASIS, Theme.RESET + '»' )
    return doc.strip()


def highlight_keywords( desc: Union[str, bytes], command_or_list, highlight = None, normal = None ):
    """
    Highlights the keywords in an `AbstractCommand`'s description.
    :param desc:                Source string 
    :param command_or_list:     Either an `AbstractCommand` to get the keywords from, or a list of keywords.
    :param highlight:           Highlight colour 
    :param normal:              Normal colour 
    :return:                    Modified string 
    """
    if highlight is None:
        highlight = Theme.ARGUMENT_NAME
    
    if normal is None:
        normal = Theme.RESET
    
    from intermake.engine.abstract_command import AbstractCommand
    if isinstance( command_or_list, AbstractCommand ):
        args = (z.name for z in command_or_list.args)
    else:
        args = command_or_list
    
    for arg in args:
        desc = desc.replace( "`" + arg + "`", highlight + arg + normal )
    
    return desc


def format_kv( key: str, value: object, spacer = "=" ):
    """
    Prints a bullet-pointed key-value pair to STDOUT
    """
    return "* " + Theme.COMMAND_NAME + key + Theme.BORDER + " " + "." * (39 - len( key )) + Theme.RESET + " " + spacer + " " + Theme.VALUE + str( value ) + Theme.RESET


def print_value( value: str ):
    """
    Prints a bullet-pointed value pair to STDOUT
    """
    MCMD.print( "* " + Theme.COMMAND_NAME + value + Theme.RESET )


def format_title( title: str ) -> str:
    return Theme.TITLE + string_helper.cjust( " " + str( title ) + " ", 20, "-" ) + Theme.RESET


def format_banner( subtitle: str, help_cmd: Optional[str], help_lst: Optional[str], full: bool = False ) -> str:
    """
    Formats a standard welcome message.
    
    :param subtitle:     The launch type / subtitle of the application. Leave blank for no subtitle. 
    :param help_cmd:     If the full banner is displayed, the command the user may invoke for help. Leave blank for no help. If `help_lst` is set, this must be set also. 
    :param help_lst:     If the full banner is displayed, the command the user may invoke to get the list of commands. Leave blank for no help. If `help_cmd` is set, this must be set also.
    :param full:         If not none, force the display of the full banner (true) or partial banner (false), otherwise host.host_settings.welcome_message will be honoured.
    :return:             The formatted welcome message is returned.
    """
    
    s = constants.INFOLINE_SYSTEM_CONTINUED + "    "
    
    env = MCMD.environment
    
    r = []
    r.append( env.name + " " + env.version + ((" " + subtitle) if subtitle else "") )
    
    if full:
        if help_cmd and help_lst:
            r.append( s + "Use " + Theme.COMMAND_NAME + help_cmd + Theme.RESET + " for help." )
        
        if help_cmd and help_lst:
            r.append( s + "Use " + Theme.COMMAND_NAME + help_lst + Theme.RESET + " to view commands." )
        
        r.append( s + "The {} workspace is '{}'".format( env.abv_name, env.local_data.workspace ) )
        
        if env.version.startswith( "0." ):
            r.append( s + "This application is in development; not all features may work correctly and the API may change." )
    
    return "\n".join( r )


def highlight_quotes( text ):
    text = string_helper.highlight_quotes( text, "`", "`", Theme.COMMAND_NAME, Theme.RESET )
    return text
