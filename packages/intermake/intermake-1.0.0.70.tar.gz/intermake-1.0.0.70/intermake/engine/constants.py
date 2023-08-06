from colorama import Back, Fore, Style
from mhelper import MEnum


__author__ = "Martin Rusilowicz"

DEFAULT_NAME = "intermake"

PLUGIN_TYPE_COMMAND = "command"
EXPLORER_KEY_PLUGINS = "commands"
EXPLORER_KEY_RESULTS = "Results"
VIRTUAL_FOLDER = "SPECIAL"

RES_FOLDER = "folder"
RES_UNKNOWN = "unknown"
RES_COMMAND = "command"

INFOLINE_MESSAGE = Back.GREEN + Fore.WHITE + "MSG" + Style.RESET_ALL + " "
INFOLINE_ERROR = Back.RED + Fore.WHITE + "ERR" + Style.RESET_ALL + " "
INFOLINE_WARNING = Back.YELLOW + Fore.RED + "WRN" + Style.RESET_ALL + " "
INFOLINE_INFORMATION = Back.BLUE + Fore.WHITE + "INF" + Style.RESET_ALL + " "
INFOLINE_PROGRESS = Back.GREEN + Fore.BLUE + "PRG" + Style.RESET_ALL + " "
INFOLINE_ECHO = Fore.BLACK + Back.CYAN + Style.DIM + "ECO" + Style.RESET_ALL + " "
INFOLINE_SYSTEM = Back.YELLOW + Fore.WHITE + "SYS" + Style.RESET_ALL + " "
INFOLINE_EXTERNAL_STDOUT = Back.WHITE + Fore.BLUE + "APP" + Style.RESET_ALL + " "
INFOLINE_EXTERNAL_STDERR = Back.WHITE + Fore.RED + "APE" + Style.RESET_ALL + " "
INFOLINE_VERBOSE = Back.BLUE + Fore.CYAN + "VER" + Style.RESET_ALL + " "

INFOLINE_MESSAGE_CONTINUED = Back.GREEN + Fore.WHITE + "   " + Style.RESET_ALL + " "
INFOLINE_WARNING_CONTINUED = Back.YELLOW + Fore.RED + "   " + Style.RESET_ALL + " "
INFOLINE_INFORMATION_CONTINUED = Back.BLUE + Fore.WHITE + "   " + Style.RESET_ALL + " "
INFOLINE_PROGRESS_CONTINUED = Back.GREEN + Fore.BLUE + "   " + Style.RESET_ALL + " "
INFOLINE_ECHO_CONTINUED = Fore.BLACK + Back.CYAN + Style.DIM + "   " + Style.RESET_ALL + " "
INFOLINE_SYSTEM_CONTINUED = Back.YELLOW + Fore.WHITE + "   " + Style.RESET_ALL + " "
INFOLINE_ERROR_CONTINUED = Back.RED + Fore.WHITE + "   " + Style.RESET_ALL + " "
INFOLINE_EXTERNAL_STDOUT_CONTINUED = Back.WHITE + Fore.BLUE + " . " + Style.RESET_ALL + " "
INFOLINE_EXTERNAL_STDERR_CONTINUED = Back.WHITE + Fore.RED + " . " + Style.RESET_ALL + " "
INFOLINE_VERBOSE_CONTINUED = Back.BLUE + Fore.CYAN + "   " + Style.RESET_ALL + " "

FOLDER_SETTINGS = "settings"
FOLDER_TEMPORARY = "temporary"
FOLDER_PLUGIN_DATA = "data"


class EDisplay( MEnum ):
    """
    Various methods for converting `UpdateInfo` to a string.
    """
    TIME_REMAINING = 0
    OPERATIONS_REMAINING = 1
    TIME_PER_OPERATION = 2
    OPERATIONS_PER_SECOND = 3
    SAMPLE_RANGE = 4
    OPERATIONS_COMPLETED = 5
    TIME_TAKEN = 6
    TIME_REMAINING_SHORT = 7
    TOTAL_RANGE = 8


class EStream( MEnum ):
    """
    Indicates the nature of a progress update, hinting (but not enforcing) the appropriate behaviour of the receiving host (CLI or GUI).
    The `styles` listed below are the default styles for the default hosts.
    
    :cvar PROGRESS:             General progress update.
                                Sent by: Any plugin may send this.
                                         Progress bar updates are also sent using this stream.
                                Style:   De-emphasised. Does not prevent GUI from closing window after plugin completes.
                                
    :cvar INFORMATION:          Key information.
                                Sent by: Any plugin may send this.
                                Style:   Displayed. Keeps GUI window open after plugin completes
                                
    :cvar WARNING:              Key warning or non-critical error.
                                Sent by: Any plugin may send this.
                                         `warnings.warn` is also directed here.
                                Style:   Emphasised. Keeps GUI window open.
                                
    :cvar ECHO:                 Echoed command.
                                Sent by: Only Intermake internals send this, to echo commands back to the user.
                                Style:   Hidden by default in CLI. Ignored by GUI.
                                
    :cvar SYSTEM:               System messages.
                                Sent by: Only Intermake internals send this, to display messages of no particular origin.
                                Style:   Displayed in CLI. Ignored by GUI.
                                
    :cvar ERROR:                Error messages.
                                Sent by: Only Intermake internals send this, to display errors and traceback.
                                         - Use `raise` to identify an error.
                                Style:   Displayed in CLI, ignored by GUI, which uses the `Exception` object verbatim.
                                    
    :cvar EXTERNAL_STDOUT:      External messages.
                                Sent by: Only Intermake internals send this, to relay messages received from external tools.
                                         - Use `subprocess_helper.run_subprocess` to run a process with piping to this stream.
                                Style:   Similar to `VERBOSE`.

    :cvar EXTERNAL_STDERR:      See `EXTERNAL_STDOUT`.
                        
    :cvar VERBOSE:              Verbose messages.
                                Sent by: Any plugin may send this, but its use for logging is discouraged.
                                         - For logging, Intermake uses `mhelper.Logger`, other commands`AbstractCommand`s will use their own preferred tool.
                                Style:   Hidden by default.
                                         Possible to view later if the last result is available to view.
                        
    """
    PROGRESS = 1
    INFORMATION = 2
    WARNING = 3
    ECHO = 4
    SYSTEM = 5
    ERROR = 6
    EXTERNAL_STDOUT = 7
    EXTERNAL_STDERR = 8
    VERBOSE = 9

    
COMMAND_TAG = "command"