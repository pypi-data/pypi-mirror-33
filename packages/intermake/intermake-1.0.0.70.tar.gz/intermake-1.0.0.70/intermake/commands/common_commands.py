"""
This module holds the Intermake common command set.

All functions here are decorated with `@command`, which allows them to be passed as command line arguments to the application.
See `@command` for more details.
"""

import os
import sys
from os import path
from typing import List, Optional

from intermake.commands import visibilities
from intermake.commands.basic_command import BasicCommand, command
from intermake.commands.setter_command import AbstractSetterCommand
from intermake.engine import cli_helper, host_manager
from intermake.engine.abstract_command import AbstractCommand
from intermake.engine.async_result import AsyncResult
from intermake.engine.command_collection import CommandFolder
from intermake.engine.environment import Environment, MCMD, MENV
from intermake.engine.help import HelpTopic
from intermake.engine.host_manager import UserExitError
from intermake.engine.theme import Theme
from intermake.hosts.base import ERunMode
from intermake.hosts.console import ConsoleHost
from intermake.hosts.frontends import command_line
from intermake.hosts.frontends.command_line import _CommandLineFrontendSettings
from mhelper import ArgInspector, EFileMode, Filename, LOGGERS, MOptional, ansi_format_helper, array_helper, file_helper, io_helper, reflection_helper, string_helper


__mcmd_folder_name__ = "CLI"


@command( names = ["exit", "x", "quit", "q", "bye"], visibility = visibilities.CLI, highlight = True )
def cmd_exit( force: bool = False ) -> None:
    """
    Exits the program safely.
    Note that pressing `CTRL+C` in the CLI will also exit the program safely.
    If a command is running, then `CTRL+C` will stop that command and return you to the CLI.
    
    :param force: Force-quits the program.
                  Don't do this unless you can't quit any other way, modified data and command history will not be saved. 
    """
    if force:
        sys.exit( 1 )
    else:
        raise UserExitError( "User requested exit" )


@command( names = ["error", "result"], visibility = visibilities.CLI & visibilities.ADVANCED )
def cmd_error() -> None:
    """
    Displays the details of the previous result.
    """
    # Get the last result (that wasn't a call to this function!)
    host = MCMD.host
    result: AsyncResult = None
    
    for x in reversed( host.result_history ):
        if x.command is not BasicCommand.retrieve( cmd_error ):
            result = x
            break
    
    if result is None:
        return
    
    # Format and print the result
    r = []
    
    r.append( "LAST RESULT" )
    r.append( "    source    = {}({})".format( type( result.command ).__name__, repr( result.command.name ) ) )
    r.append( "    args      = {}".format( repr( result.args ) ) )
    r.append( "    result    = {}".format( result.state ) )
    
    if result.is_error:
        r.append( "    exception = {}".format( repr( result.exception ) ) )
        r.append( "    traceback =\n{}".format( result.traceback ) )
    else:
        r.append( "    value     = {}".format( result.result ) )
    
    MCMD.print( "\n".join( r ) )


@command( names = ["use", "set_visibility"], visibility = visibilities.COMMON )
def cmd_use( category: Optional[str] = None, all: bool = False ) -> None:
    """
    Shows or hides command sets.

    :param all:      When listing the available modes, setting this flag shows all classes, even if they appear to be non-functional.
    :param category: Mode to show or hide. Leave blank to list the available modes. If this is an asterisk (`*`) then all modes are set to visible.
    """
    visibilities = MENV.commands.find_visibilities()
    
    for visibility in visibilities:
        if category == "*":
            visibility.user_override = True
            MCMD.print( Theme.STATUS_YES + "{} is now shown ".format( visibility.name ) + Theme.RESET )
        elif visibility.name == category:
            if visibility.user_override is True:
                visibility.user_override = False
                MCMD.print( Theme.STATUS_NO + "{} is now hidden ".format( visibility.name ) + Theme.RESET )
                return
            elif visibility.user_override is False:
                visibility.user_override = None
                MCMD.print( Theme.STATUS_INTERMEDIATE + "{} has been reset to its default ({})".format( visibility.name, "shown" if visibility.is_visible else "hidden" ) + Theme.RESET )
                return
            else:
                visibility.user_override = True
                MCMD.print( Theme.STATUS_YES + "{} is now shown ".format( visibility.name ) + Theme.RESET )
                return
    
    r = []
    
    for visibility in sorted( visibilities, key = lambda x: x.name ):
        if not visibility.is_functional and not all and category != "*":
            continue
        
        shown = visibility()
        r.append( "{}{}{}{} {}".format( (Theme.STATUS_IS_NOT_SET if visibility.user_override is None else Theme.STATUS_IS_SET),
                                        "[X]" if shown else "[ ]",
                                        (Theme.STATUS_YES if shown else Theme.STATUS_NO) + " " + visibility.name.ljust( 20 ),
                                        Theme.RESET,
                                        visibility.comment ) )
    
    MCMD.print( "\n".join( r ) )


@command( names = ["cmdlist", "cl", "commands"], visibility = visibilities.CLI, highlight = True )
def cmd_cmdlist( details: bool = False, all: bool = False ) -> None:
    """
     Lists the available commands

     Commands are listed as:

     «command_name» «command_type» «description»

     «command_name»: The name of the command. Use `help` to see the full path.
     «command_type»: The type of command, 
     «description» :  Command documentation. Use `help` to see it all.

     :param details: When `True`, full details are printed 
     :param all: When `True`, all commands are shown, regardless of their visibility.
     """
    
    # Print the results
    result = []
    last_parent = ""
    WIDTH = MCMD.host.console_width
    PREFIX = Theme.BORDER + "::" + " " * (WIDTH - 4) + "::" + Theme.RESET
    
    folders: List[List[CommandFolder]] = [[MCMD.environment.commands.get_root_folder()]]
    
    while folders:
        path: List[CommandFolder] = folders.pop( 0 )
        folder : CommandFolder = path[-1]
        
        for subfolder in sorted( folder.iter_folders(), key = lambda x: x.name ):
            folders.append( path + [subfolder] )
        
        for command in sorted( folder.iter_commands(), key = lambda x: x.name ):
            if not all and not command.visibility_class.is_visible:
                continue
            
            parent = "/".join( MCMD.host.translate_name( x.name ) for x in path[1:] )
            
            if parent != last_parent:
                padding_size = (WIDTH - len( parent )) // 2 - 1
                padding_text = Theme.BORDER + (":" * padding_size)
                
                if (len( parent ) % 2) != 0:
                    padding_extra = ":"
                else:
                    padding_extra = ""
                
                if result:
                    result.append( PREFIX )
                
                result.append( padding_text + " " + Theme.BOX_TITLE + parent + " " + padding_text + padding_extra + Theme.RESET + "\n" + PREFIX )
                last_parent = parent
            
            cli_helper.get_details( result, command, not details )
    
    result.append( PREFIX )
    result.append( Theme.BORDER + ":" * WIDTH + Theme.RESET )
    
    MCMD.print( "\n".join( result ) )


@command( names = ["eggs", "example"], visibility = visibilities.ADVANCED )
def cmd_eggs( name: str = "no name", good: bool = False, repeat: int = 1 ) -> None:
    """
    Egg-sample command :)
    Prints a message.
     
    :param name:    Name of your egg-sample 
    :param good:    Is this a good egg-sample?
    :param repeat:  Number of times to repeat the egg-sample.
    """
    for _ in range( repeat ):
        MCMD.print( "This is an example command. «{}» is a {} egg-sample.".format( name, "GOOD" if good else "BAD" ) )


@command( names = ["python_help"], visibility = visibilities.ADVANCED )
def cmd_python_help( thing: object = None ) -> None:
    """
    Shows Python's own help.

    :param thing: Thing to show help for, leave blank for general help.
    """
    import pydoc
    
    if thing is None:
        pydoc.help()
    else:
        pydoc.help( thing )


def __basic_help() -> str:
    """
    Basics help point text.
    """
    return MCMD.host.substitute_text( string_helper.fix_indents( MCMD.host.get_help_message() ) ) + "\n" + __help_topics()


def __help_topics() -> str:
    return "Help topics\n===========" + "".join( "\n* {}".format( MCMD.host.translate_name( x.name ) ) for x in MCMD.environment.help )


__basic_help_topic = HelpTopic( "Basics", content = __basic_help )
MENV.help.add( __basic_help_topic )
MENV.help.add( HelpTopic( "Topics", content = __help_topics ) )


@command( names = ["history"], visibility = visibilities.ADVANCED )
def cmd_history( find: str = "" ):
    """
    Prints CLI history.
    :param find:    If specified, only lists lines containing this text
    """
    from intermake.hosts.frontends.command_line import iter_history
    r = []
    for line in iter_history():
        if find in line:
            r.append( line )
    
    MCMD.print( "\n".join( r ) )


@command( names = ["topics_help"], visibility = visibilities.ADVANCED )
def cmd_topics_help() -> str:
    """
    Shows the list of help topics.
    """
    topics = []
    
    for command in MENV.commands:
        if command.visibility_class is visibilities.HELP:
            topics.append( command )
    
    r = []
    
    r.append( Theme.TITLE + "-------------------- {} HELP TOPICS --------------------".format( len( topics ) ) + Theme.RESET )
    r.append( "Use one of the following commands for more help on specific topics:" )
    
    for command in topics:
        r.append( Theme.COMMAND_NAME + MCMD.host.translate_name( command.name ) + Theme.RESET )
    
    return "\n".join( r )


in_help = False


@command( highlight = True, names = ["help", "mhelp", "h"] )
def cmd_help( command_name: Optional[str] = None, argument_name: Optional[str] = None ) -> None:
    """
    Shows general help or help on a specific command.
     
    :param command_name: Name of command or script to get help for. If not specified then general help is given. 
    :param argument_name: Name of the argument to get help for. If not specified then help for the command is given.
    :return: 
    """
    if not command_name:
        command = __basic_help_topic
    else:
        command = command_line.find_command( command_name, include_topics = True )
        
        if command is None:
            return
    
    r = []
    
    if isinstance( command, HelpTopic ):
        r.append( cli_helper.format_doc( command.name + "\n" + "=" * len( command.name ) + "\n" + command.content ) )
    elif isinstance( command, AbstractCommand ):
        if not argument_name:
            r.append( cli_helper.get_details_text( command ) )
        else:
            argument: ArgInspector = string_helper.find(
                    source = command.args,
                    namer = lambda x: MCMD.host.translate_name( x.name ),
                    search = argument_name,
                    detail = "argument" )
            
            t = argument.annotation.get_indirect_subclass( object )
            
            if t is None:
                raise ValueError( "Cannot obtain type above object from «{}».".format( argument.annotation ) )
            
            console_width = MCMD.host.console_width
            
            r.append( ansi_format_helper.format_two_columns( left_margin = 4, centre_margin = 30, right_margin = console_width, left_text = Theme.FIELD_NAME + "name       " + Theme.RESET, right_text = Theme.ARGUMENT_NAME + argument.name + Theme.RESET ) )
            r.append( ansi_format_helper.format_two_columns( left_margin = 4, centre_margin = 30, right_margin = console_width, left_text = Theme.FIELD_NAME + "type name  " + Theme.RESET, right_text = t.__name__ ) )
            r.append( ansi_format_helper.format_two_columns( left_margin = 4, centre_margin = 30, right_margin = console_width, left_text = Theme.FIELD_NAME + "optional   " + Theme.RESET, right_text = str( argument.annotation.is_optional ) ) )
            r.append( ansi_format_helper.format_two_columns( left_margin = 4, centre_margin = 30, right_margin = console_width, left_text = Theme.FIELD_NAME + "default    " + Theme.RESET, right_text = Theme.COMMAND_NAME + str( argument.default ) + Theme.RESET ) )
            r.append( ansi_format_helper.format_two_columns( left_margin = 4, centre_margin = 30, right_margin = console_width, left_text = Theme.FIELD_NAME + "description" + Theme.RESET, right_text = cli_helper.highlight_keywords( argument.description, command ) ) )
            
            # Type docs
            docs = reflection_helper.extract_documentation( t.__doc__, "cvar" )
            r.append( ansi_format_helper.format_two_columns( left_margin = 4, centre_margin = 30, right_margin = console_width, left_text = Theme.FIELD_NAME + "type       " + Theme.RESET, right_text = docs[""] or "Values:" ) )
            
            for key, value in docs.items():
                if key and value:
                    r.append( ansi_format_helper.format_two_columns( left_margin = 34, centre_margin = 50, right_margin = console_width, left_text = Theme.ENUMERATION + key + Theme.RESET, right_text = value ) )
    
    MCMD.print( "\n".join( r ) )


@command( names = ["version"], visibility = visibilities.ADVANCED[visibilities.CLI] )
def cmd_version( stdout: bool = False ) -> None:
    """
    Shows the application version.
    
    :param stdout: Print to std.out.
    """
    if stdout:
        print( MENV.version )
    else:
        MCMD.print( "VERSION:" )
        name = MENV.name
        version = MENV.version
        MCMD.print( name + " " + version )


@command( names = ["system"], visibility = visibilities.ADVANCED )
def cmd_system( command_: str ) -> None:
    """
    Invokes a system command in the current terminal.
    
    :param command_: Command to execute.
    """
    os.system( command_ )


@command( names = ["eval"], visibility = visibilities.ADVANCED )
def cmd_eval( command_: str ) -> None:
    """
    Evaluates a Python statement and prints the result.
    
    :param command_: Python statement to run
    """
    MCMD.print( str( eval( command_ ) ) )


@command( names = ["cls", "clear"], visibility = visibilities.ADVANCED )
def cmd_cls() -> None:
    """
    Clears the CLI.
    """
    # The proper way is to send the correct ANSI sequence, however in practice this produces odd results.
    # So we just use the specific system commands.
    if sys.platform.lower() == "windows":
        cmd_system( "cls" )
    else:
        cmd_system( "clear ; clear" )  # once doesn't clear the terminal properly


@command( names = ["start_cli"], visibility = visibilities.ADVANCED )
def cmd_start_cli() -> None:
    """
    Starts the UI: Command line interface
    
    See also :function:`prepare_cli`.
    """
    cmd_start_ui( ERunMode.CLI )


@command( names = ["gui", "start_gui"], visibility = visibilities.ADVANCED )
def cmd_start_gui() -> None:
    """
    Starts the UI: Graphical user interface
    """
    cmd_start_ui( ERunMode.GUI )


@command( names = ["pyi", "start_pyi"], visibility = visibilities.ADVANCED )
def cmd_start_pyi() -> None:
    """
    Starts the UI: Python interactive interface
    """
    cmd_start_ui( ERunMode.PYI )


@command( names = ["ui", "start_ui"], visibility = visibilities.ADVANCED )
def cmd_start_ui( mode: Optional[ERunMode] = None ) -> None:
    """
    Switches the user-interface mode.
    
    :param mode: Mode to use.
    """
    if mode is None:
        MCMD.print( "The current host is {}.".format( MCMD.host ) )
        return
    
    host_manager.run_host( MENV.host_provider[mode]() )


class __LocalDataCommand( AbstractSetterCommand ):
    """
    Modifies the local data store.
    
    :remarks:
    Invoking this `AbstractCommand` is not the best way to modify settings _programmatically_.
    Modify such settings via access to the actual `object`, and then call the associated save function to commit the changes to `MENV.local_data.store` (if the property is not bound). 
    """
    
    
    def on_get_targets( self ):
        store = MENV.local_data.store
        
        for key in store.keys():
            yield key, store.retrieve( key )
    
    
    def on_set_target( self, name: str, target: object ):
        store = MENV.local_data.store
        store.commit( name, target )


cmd_local_data = __LocalDataCommand( names = ["local"], visibility = visibilities.ADVANCED )
Environment.LAST.commands.register( cmd_local_data )


def local_data():
    store = MENV.local_data.store
    
    for key in store.keys():
        yield key, store.retrieve( key )


@command( names = ["workspace"], visibility = visibilities.ADVANCED )
def cmd_workspace( directory: Optional[str] = None ) -> None:
    """
    Gets or sets the $(APP_NAME) workspace (where settings and caches are kept)
     
    :param directory:   Directory to change workspace to. This will be created if it doesn't exist. The workspace will take effect from the next $(APP_NAME) restart. 
    """
    MCMD.information( "WORKSPACE: " + MENV.local_data.workspace )
    
    if directory:
        MENV.local_data.set_redirect( directory )
        MCMD.information( "Workspace will be changed to «{}» on next restart.".format( directory ) )


@command( names = ["import", "python_import"], visibility = visibilities.ADVANCED )
def cmd_import( name: str, persist: bool = False, remove: bool = False ) -> None:
    """
    Wraps the python `import` command, allowing external sets of commands to be imported.
    
    :param name:    Name of the package to import.
    :param persist: Always import this command when the application starts.
    :param remove:  Undoes a `persist`. 
    """
    if remove:
        MENV._environment_settings.startup.remove( name )
        MENV.local_data.store.commit( MENV._environment_settings )
        MCMD.progress( "`{}` will not be loaded at startup.".format( name ) )
        return
    
    old_count = array_helper.count( MENV.commands )
    orig_namespace = MENV.commands.namespace
    MENV.commands.namespace = name
    __import__( name )
    new_count = array_helper.count( MENV.commands )
    
    MCMD.progress( "Import {} OK.".format( name ) )
    
    if old_count != new_count:
        MCMD.progress( "{} new commands.".format( new_count - old_count ) )
    
    MENV.commands.namespace = orig_namespace
    
    if persist:
        MENV._environment_settings.startup.add( name )
        MENV.local_data.store.commit( MENV._environment_settings )
        MCMD.progress( "`{}` will be loaded at startup.".format( name ) )


@command( names = ["autostore_warnings"], visibility = visibilities.ADVANCED )
def cmd_autostore_warnings() -> None:
    """
    Displays, in more detail, any warnings from the autostore.
    """
    from intermake.datastore.local_data import autostore_warnings
    
    if len( autostore_warnings ) == 0:
        MCMD.information( "No warnings." )
    
    for i, message in enumerate( autostore_warnings ):
        MCMD.information( Theme.TITLE + "WARNING {} OF {}".format( i, len( autostore_warnings ) ) + Theme.RESET )
        MCMD.information( message )


@command( names = ["messages"], visibility = visibilities.ADVANCED )
def cmd_messages( file: MOptional[Filename[EFileMode.WRITE]] = None ) -> None:
    """
    Repeats the last output messages.
    
    :param file:    See `file_write_help`.
    """
    last_result = MCMD.host.result_history[-1]
    
    with io_helper.open_write( file ) as file_out:
        for message in last_result.messages:
            file_out.write( message + "\n" )


@command( names = ["make_boring"], visibility = visibilities.ADVANCED )
def cmd_make_boring( boring: bool = True ) -> None:
    """
    Disables colour, unicode and stream output.
    Added this after people complained about the exciting default colour scheme.
    
    :param boring:  Boring status.
    """
    host = MCMD.host
    
    if not isinstance( host, ConsoleHost ):
        return
    
    host.console_settings.remove_utf = boring
    host.console_settings.remove_ansi = boring
    host.console_settings.hide_streams = boring
    
    MCMD.progress( "CONSOLE SETTINGS" )
    MCMD.progress( "NON-ASCII [{0}], ANSI-COLOURS [{0}], SIDEBAR [{0}]".format( "OFF" if boring else "ON" ) )


@command( names = ["log"], visibility = visibilities.ADVANCED )
def cmd_log( name: Optional[str] = None ) -> None:
    """
    Enables, disables, or displays loggers.
    
    :param name:    Logger to enable or disable, or `None` to list all.
    """
    for logger in LOGGERS:
        if name == logger.name:
            if logger.enabled is False:
                logger.enabled = True
            elif logger.enabled is True:
                logger.enabled = False
            else:
                MCMD.print( "Cannot change status because this logger has been bound to another destination." )
        
        MCMD.print( cli_helper.format_kv( logger.name, logger.enabled ) )


@command( names = ["setwd", "chdir"], visibility = visibilities.ADVANCED )
def cmd_setwd( path: Optional[str] = None ) -> None:
    """
    Displays or sets the working directory.
    This is not the same as the `cd` command, which navigates $(APPNAME)'s virtual object hierarchy.
    
    :param path:    Path to set.
    """
    if path:
        os.chdir( path )
    
    MCMD.print( os.getcwd() )


__EXT_IMK = ".imk"


@command( names = ["source"], visibility = visibilities.ADVANCED )
def cmd_source( file_name: Filename[EFileMode.READ, __EXT_IMK] ) -> None:
    """
    Executes a file using the command line interpreter.
    This can be better than pipe-ing to std-in, since, with `source`, the CLI will halt if it encounters an error rather than continuing with future commands. 
    
    :param file_name:   File to execute. If this cannot be found the `.imk` extension will be attempted. 
    """
    if not path.isfile( file_name ):
        file_name += ".imk"
    
    if not path.isfile( file_name ):
        raise ValueError( "The path «{}» cannot be found or is not a file.".format( file_name ) )
    
    for line in file_helper.read_all_lines( file_name ):
        command_line.execute_text( line )


def __format_help() -> None:
    """
    Displays help on formatting items
    """
    import stringcoercion
    r = []
    
    for coercer in stringcoercion.get_default_collection():
        if coercer.__doc__:
            r.append( "* " + str( coercer.__doc__ ).strip() )
    
    MCMD.print( cli_helper.format_doc( "\n".join( r ) ) )


MENV.help.add( "Format", __format_help )


@command( names = ["cli", "prepare_cli"] )
def cmd_prepare_cli( store: bool = False ) -> None:
    """
    When called, ensures that the CLI is invoked:
        * When an error occurs in ARG mode
        * When ARG mode completes
    
    :remarks:
    This is an alternative to putting `CLI` at the end of the command string, because it ensures that, even in error, the CLI is started.
    
    :param store:   Settings are saved to disk (they can be reverted through the :method:`local`). 
    """
    s: _CommandLineFrontendSettings = command_line.get_clf_settings()[0 if store else 1]
    s.error_invokes_cli = True
    s.args_invokes_cli = True


@command( names = ["alias"], visibility = visibilities.ADVANCED )
def cmd_alias( target: Optional[str] = None, source: Optional[str] = None, store: bool = False ) -> None:
    # noinspection SpellCheckingInspection
    """
        Creates or displays a command line alias.
        Aliases are replaced verbatim, so if you create an alias `"e" --> "XYZ"` then `hello` will be interpreted as `hXYZllo`.
        
        :param store:   When true, displays or modifies the permanent list
                        When false, displays or modifies the list for this session 
        :param target:  Term to find. If None prints all aliases.
        :param source:  New text. If None displays the alias. If empty deletes the alias. 
        """
    
    s = command_line.get_clf_settings()[0 if store else 1]
    
    if target is None:
        MCMD.print( "{} aliases.".format( len( s.aliases ) ) )
        for k, v in s.aliases.items():
            MCMD.print( cli_helper.format_kv( k, v ) )
        return
    
    if source is not None:
        if not source:
            del s.aliases[target]
        else:
            s.aliases[target] = source
        
        s.aliases = s.aliases  # commits to local data store 
    
    MCMD.print( cli_helper.format_kv( target, s.aliases.get( target ) ) )
