"""
Houses the PluginManager and PluginFolder classes.
"""

import inspect
import warnings
from importlib import import_module
# noinspection PyUnresolvedReferences
from types import ModuleType
from typing import Iterator, List, Optional, Set, Tuple, Union
from warnings import warn

from intermake.commands.visibilities import VisibilityClass
from intermake.engine import constants
from intermake.engine.abstract_command import AbstractCommand
from intermake.visualisables.visualisable import IVisualisable, UiInfo
from mhelper import SwitchError, file_helper, module_helper, string_helper


__author__ = "Martin Rusilowicz"
_Plugin_ = "intermake.engine.plugin.AbstractCommand"
_PluginFolder_ = "intermake.engine.plugin_manager.CommandFolder"
TModule = Union[ModuleType, str]
TPluginOrModuleOrList = Union[ModuleType, _PluginFolder_, _Plugin_, List[Union[ModuleType, _PluginFolder_, _Plugin_]], Tuple[Union[ModuleType, _PluginFolder_, _Plugin_]]]


class CommandCollection:
    """
    Manages the set of user-defined functions formally identified as "commands" formerly identified as "plugins".
    
    :ivar __root_folder:               CommandFolder that holds all the registered commands
    :ivar __namespace:                 Some arbitrary text we prefix on the front of all registered plugin folder names.
                                            This is only used to track user-imports via the `import_` command, so it is usually `None`.
    :ivar __namespace_visibilities:    `VisibilityClass`es associated with the `__namespace`, usually empty.
    """
    
    
    def __init__( self, *, comment: str, inherit: "CommandCollection" = None ) -> None:
        """
        CONSTRUCTOR
        
        :param inherit: Include commands from another manager.
                        The instance will be persisted, so this manager will reflect changes in the other.
        """
        self.__root_folder = CommandFolder( constants.EXPLORER_KEY_PLUGINS, "All loaded commands" )
        self.__namespace = None
        self.__namespace_visibilities = { }
        self.__comment = comment
        
        if inherit:
            self.__root_folder.inherit( inherit.__root_folder )
    
    
    def all_plugins( self ):
        warnings.warn( "Deprecated - use `__iter__`.", DeprecationWarning )
        return list( self )
    
    
    def __str__( self ):
        return "CommandCollection({})".format( repr( self.__comment ) )
    
    
    @property
    def namespace( self ) -> str:
        """
        Gets or sets the namespace.
        This string is prefixed onto the front of all newly registered plugin folder names.
        It is usually empty.
        When set, all newly registered commands are automatically put into a `VisibilityClass` of the same name.
        """
        return self.__namespace
    
    
    @namespace.setter
    def namespace( self, value: str ) -> None:
        self.__namespace = value
        
        if value and value not in self.__namespace_visibilities:
            self.__namespace_visibilities[value] = VisibilityClass( name = value, is_functional = True, is_visible = False )
    
    
    def find_visibilities( self ) -> Set[VisibilityClass]:
        result = set()
        
        for plugin in self:
            command_visibilities = { plugin.visibility_class }
            
            while command_visibilities:
                result.update( command_visibilities )
                
                new_visibilities = set()
                
                for visibility in command_visibilities:
                    if visibility.parents:
                        for parent in visibility.parents:
                            new_visibilities.add( parent )
                
                command_visibilities = new_visibilities
        
        return result
    
    
    def register( self, plugin: _Plugin_, module_: Optional[TModule] = None ):
        """
        Registers a plugin.
        
        :remarks:
        The plugin will not be registered if the :global:`MENV` is locked.
        
        :param module_:  Module to register under. If `None` uses the calling module. 
        :param plugin:   AbstractCommand to register.
        """
        from intermake.engine.abstract_command import AbstractCommand
        assert isinstance( plugin, AbstractCommand )
        
        from intermake.engine.environment import MENV
        if MENV.is_locked:
            # Prevent registering new commands if the environment is locked
            return
        
        if module_ is None:
            frame = inspect.stack()[1]
            module_ = inspect.getmodule( frame[0] )
        
        if inspect.ismodule( module_ ):
            module_name, module_docs = self.__module_name_and_docs( module_ )
        else:
            module_name = module_
            module_docs = None
        
        if plugin.folder:
            module_name = plugin.folder
        
        if self.__namespace:
            module_name = self.__namespace + "/" + module_name
            plugin.visibility_class = self.__namespace_visibilities[self.__namespace] & plugin.visibility_class
        
        from intermake.engine.abstract_command import AbstractCommand
        
        assert isinstance( plugin, AbstractCommand )
        
        # Check that it isn't already registered
        if plugin in self:
            raise KeyError( "The command «{0}» is exported more than once. Check that you haven't accidentally re-exported a command.".format( plugin.name ) )
        
        # Add the plugin itself
        folder = self.__register_folder( module_docs, module_name )
        folder.add_plugin( plugin )
        
        # Fix the names
        for ex_plugin in self:
            if ex_plugin is not plugin:
                conflicts = []
                
                for name_1 in plugin.names:
                    if name_1 in ex_plugin.names:
                        conflicts.append( name_1 )
                
                for conflict in list( conflicts ):
                    ex_plugin.names.remove( conflict )
                    
                    if len( ex_plugin.names ) == 0:
                        ex_plugin.names.append( "cmd_{}".format( id( ex_plugin ) ) )
                    else:
                        conflicts.remove( conflict )
                
                if conflicts:
                    if plugin in folder and ex_plugin in folder:
                        msg = "There are two commands with the name «{}». This is probably a mistake and so an error has been raised."
                        raise ValueError( msg.format( plugin.name ) )
                    else:
                        msg = "There are two commands with the name «{}». The original plugin has been renamed to \"{}\". This looks like the commands just have the same name, but check that you haven't accidentally re-exported a plugin imported from another module."
                        warn( msg.format( plugin.name ), UserWarning )
    
    
    @staticmethod
    def legacy_load_namespace( namespace: TModule ):
        """
        Utility function that loads all modules in a namespace.
        This replaces old _register-all-in-namespace_ type functions that are now replaced by plugin self-registration.
        """
        module_helper.load_namespace( namespace )
    
    
    def __register_folder( self, docs: str, name: str ):
        for folder in self.__root_folder.iter_folders():  # type: CommandFolder
            if folder.name == name:
                if docs:
                    if docs not in folder.description:
                        folder.description += "\n\n" + docs
                
                return folder
        
        folder = CommandFolder( name, docs )
        self.__root_folder.add_folder( folder )
        return folder
    
    
    @staticmethod
    def __module_name_and_docs( module_: TModule ):
        if isinstance( module_, str ):
            module_ = import_module( module_ )
        
        doc = module_.__doc__
        path = module_helper.get_module_path( module_ )
        
        if doc:
            doc = doc.strip() + "\n\n"
        else:
            doc = ""
        
        doc += "This module contains the set of commands from `" + path + "`:"
        
        name = file_helper.get_filename_without_extension( path )
        name = string_helper.undo_camel_case( name, "_" )
        
        for attr in ["mcmd_folder_name", "_mcmd_folder_name_", "__mcmd_folder_name__"]:
            name = getattr( module_, attr, name )
        
        return name, doc
    
    
    def __iter__( self ) -> "Iterator[.engine.plugin.AbstractCommand]":
        """
        OVERRIDE 
        """
        return self.__iterate( self.__root_folder )
    
    
    def get_root_folder( self ) -> "CommandFolder":
        return self.__root_folder
    
    
    @classmethod
    def __iterate( cls, x ):
        from intermake.engine.abstract_command import AbstractCommand
        
        if isinstance( x, AbstractCommand ):
            yield x
        elif isinstance( x, CommandFolder ):
            for c in x.iter_folders():
                yield from cls.__iterate( c )
            
            for c in x.iter_commands():
                yield from cls.__iterate( c )
        else:
            raise SwitchError( "x", x )


class CommandFolder( IVisualisable ):
    """
    A collection of commands organised into a folder.
    """
    
    
    def __init__( self, name: str, doc: str ) -> None:
        """
        Constructor
        :param name:    Folder name 
        :param doc:     Documentation 
        :param parent:  Parent folder (if any) 
        """
        self.name = name
        self.__inherit = []
        self.__folders = []
        self.__plugins = []
        self.description = doc
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        """
        OVERRIDE 
        """
        super().on_get_vis_info( u )
        num_plugins = len( self.__plugins )
        num_modules = len( self.__folders )
        
        if num_modules:
            if num_plugins != num_modules:
                text = "{0} commands".format( num_plugins )
            else:
                text = "{0} modules".format( num_modules )
        else:
            if num_plugins:
                text = "{0} commands".format( num_plugins )
            else:
                text = "No commands".format( num_plugins )
        
        u.doc = self.description
        u.text = text
        u.hint = u.Hints.FOLDER
        u.contents += { x.name: x for x in self.iter_all() }
    
    
    def iter_all( self ):
        yield from self.iter_folders()
        yield from self.iter_commands()
    
    
    def iter_commands( self ):
        yield from self.__plugins
        for x in self.__inherit:
            yield from x.iter_commands()
    
    
    def iter_folders( self ):
        yield from self.__folders
        for x in self.__inherit:
            yield from x.iter_folders()
    
    
    def __str__( self ):
        """
        OVERRIDE 
        """
        return self.name
    
    
    def add_plugin( self, plugin ):
        """
        :type plugin: AbstractCommand
        """
        self.__assert_name_free( plugin.name )
        self.__plugins.append( plugin )
    
    
    def add_folder( self, folder: "CommandFolder" ):
        self.__assert_name_free( folder.name )
        self.__folders.append( folder )
    
    
    def __assert_name_free( self, name ):
        if any( x.name == name for x in self.iter_all() ):
            raise ValueError( "An object with this name '{}' already exists.".format( name ) )
    
    
    def inherit( self, folder: "CommandFolder" ):
        self.__inherit.append( folder )
