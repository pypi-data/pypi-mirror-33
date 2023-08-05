"""
intermake package entry-point.
See `readme.md` for details.
"""
import intermake.init
from intermake.engine.host_manager import RunHost
from intermake.engine.async_result import AsyncResult
from intermake.engine.environment import start, MENV, MCMD, register, run_jupyter, Environment, acquire
from intermake.engine.command_collection import CommandCollection
from intermake.engine.progress_reporter import ActionHandler, IProgressReceiver, QueryInfo, TaskCancelledError, UpdateInfo, Message
from intermake.extensions import coercion_extensions
from intermake.extensions.coercion_extensions import VISUALISABLE_COERCER
from intermake.helpers.results_explorer import ResultsExplorer
from intermake.helpers.table_draw import Table
from intermake.hosts.base import ERunMode, AbstractHost
from intermake.hosts.console import ConsoleHost
from intermake.commands.basic_command import command, BasicCommand
from intermake.engine.constants import EStream, EDisplay
from intermake.commands.setter_command import AbstractSetterCommand
from intermake.engine import cli_helper, theme, constants, environment, constants
from intermake.engine.abstract_command import AbstractCommand
from intermake.engine.mandate import Mandate
from intermake.engine.theme import Theme
from intermake.commands import visibilities, basic_command, common_commands, console_explorer, setter_command, test_plugins
from intermake.commands.visibilities import VisibilityClass
from intermake.visualisables.visualisable import EColour, IVisualisable, UiInfo, VisualisablePath, UiHint, EIterVis
from intermake.helpers import subprocess_helper
from intermake.visualisables import visualisable
from intermake.commands.common_commands import \
    cmd_exit, \
    cmd_error, \
    cmd_use, \
    cmd_cmdlist, \
    cmd_eggs, \
    cmd_python_help, \
    cmd_history, \
    cmd_topics_help, \
    cmd_help, \
    cmd_version, \
    cmd_system, \
    cmd_eval, \
    cmd_cls, \
    cmd_start_cli, \
    cmd_start_gui, \
    cmd_start_pyi, \
    cmd_start_ui, \
    cmd_workspace, \
    cmd_import, \
    cmd_autostore_warnings, \
    cmd_messages, \
    cmd_make_boring, \
    cmd_log, \
    cmd_setwd, \
    cmd_source, \
    cmd_prepare_cli, \
    cmd_alias, \
    cmd_local_data


__author__ = "Martin Rusilowicz"
__version__ = "1.0.0.63"

coercion_extensions.init()
