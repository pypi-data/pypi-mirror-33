"""
Contains the `LocalData` class.
"""
import os
import warnings
from os import path
from typing import Optional, TypeVar, cast
import mhelper as mh

from intermake.engine import constants


__author__ = "Martin Rusilowicz"
_AUTOSTORE_EXTENSION = ".pickle"
autostore_warnings = []
T = TypeVar( "T" )
_LOG = mh.Logger( "autostore", False )


class _AutoStore:
    """
    Manages a local data store, loading and saving the keys to and from files in the specified folder.
    """
    KEY_TAG = "_AutoStore_key"
    
    
    def __init__( self, directory ):
        """
        CONSTRUCTOR
        :param directory:   Directory to use 
        """
        self.__directory = directory
        mh.file_helper.create_directory( directory )
    
    
    def bind( self, key: str, value: T ) -> T:
        """
        Binds to the specified setting object.
        If any changes have been made on disk, these will be propagated into the `value`.
        
        :param key:         Key to use to get and set the value
        :param value:       Object to wrap in the proxy
                            The `__dict__` is accessed to marshal the attributes, hence this must be a _simple_ object
        :return:            `value`, wrapped in a proxy which detects changes, and commits those changes to disk.
                            Note only attribute changes are registered, not changes to attributes of attributes, etc.
        """
        existing = self.retrieve( key, value )
        
        if existing is None:
            self[key] = value
        else:
            updates = { }
            
            for pk, pv in value.__dict__.items():
                if pk.startswith( "_" ):
                    continue
                
                if pk in existing.__dict__:
                    epv = existing.__dict__[pk]
                    
                    updates[pk] = epv
            
            value.__dict__.update( updates )
        
        proxy = mh.SimpleProxy( target = value, on_set_attr = self.__proxy_changed )
        object.__setattr__( proxy, self.KEY_TAG, key )  # sets the field on the proxy, not the underlying object
        
        return cast( T, proxy )
    
    
    def __proxy_changed( self, e: mh.PropertySetInfo ):
        """
        Responds to a change in a value accessed via `bind`.
        """
        self.commit( e.proxy )
    
    
    def retrieve( self, key: str, default: Optional[T] = None ) -> T:
        """
        Retrieves a setting.
        Unlike `bind`, no caching is performed.
        
        :param key:     Setting key 
        :param default: Default 
        :return:        Setting 
        """
        # Load from disk
        t = type( default ) if default is not None else None
        result = self.__read_item( key, expected_type = t )
        
        # Apply defaults from `default`
        if default is not None:
            result = mh.io_helper.default_values( result, default )
        
        return result
    
    
    def get_key( self, key: object ):
        if isinstance( key, str ):
            return key
        elif isinstance( key, mh.SimpleProxy ):
            return object.__getattribute__( key, self.KEY_TAG )
    
    
    def commit( self, key: object, value: object = None ):
        """
        Saves the setting
        
        
        :param key:   Either:
                      * the key passed to `retrieve` or `bind`
                      * the proxy object returned from `bind`
                      Note: the objects encapsulated by the proxies, or objects returned from `retrieve`, are __not retained__ by the store and are not acceptable!
        :param value: Value to commit (only if the `key` is a `str`).
        """
        if isinstance( key, str ):
            if value is None:
                raise ValueError( "Must specify `value` when the `key` is not the `value`. Specified `key` = «{}», `value` = «{}».".format( key, value ) )
            
            key_ = key
            value_ = value
            
            if isinstance( value_, mh.SimpleProxy ):
                value_ = mh.SimpleProxy.get_source( value_ )
        
        elif isinstance( key, mh.SimpleProxy ):
            if value is not None:
                raise ValueError( "Cannot specify `value` when the `key` is the `value`. Specified `key` = «{}», `value` = «{}».".format( key, value ) )
            
            key_ = object.__getattribute__( key, self.KEY_TAG )
            value_ = mh.SimpleProxy.get_source( key )
        else:
            raise mh.type_error( "key", key, [str, mh.SimpleProxy] )
        
        self.__write_item( key_, value_ )
    
    
    def drop( self, key: str ):
        """
        Removes a setting from disk.
        If a instance bound with `bind` is present then it is deleted.
        """
        if isinstance( key, str ):
            key_ = key
        elif isinstance( key, mh.SimpleProxy ):
            key_ = object.__getattribute__( key, self.KEY_TAG )
        else:
            raise mh.type_error( "key", key, [str, mh.SimpleProxy] )
        
        self.__write_item( key_, None )
    
    
    def __read_item( self, key: str, expected_type ):
        """
        Reads the specified setting from disk.
        """
        file_name = self.__key_to_filename( key )
        
        if not path.isfile( file_name ):
            _LOG( "read {} = absent", key )
            return None
        
        try:
            result = mh.io_helper.load_binary( file_name, type_ = expected_type )
            _LOG( "read {} = success", key )
        except Exception as ex:
            # Data cannot be restored - ignore it
            # autostore_warnings.append( exception_helper.get_traceback() )
            # _LOG( "read {} = failure", key )
            # file_helper.recycle_file( file_name )
            # warnings.warn( "Failed to restore settings from «{}» due to the error «{}: {}». This is probably due to a version incompatibility, if so please recreate your settings using the new version and disregard this warning. Otherwise, use the `autostore_warnings` function to obtain the full error traceback. The problematic file has been automatically sent to the recycle bin to avoid this problem in future. If it is important, please retrieve it now.".format( file_name, type( ex ).__name__, ex ), UserWarning )
            # return None
            raise ValueError( "Failed to restore settings from «{}» due to the error «{}: {}». This is probably due to a version incompatibility. Please delete the offending file and recreate your settings using the new version.".format( file_name, type( ex ).__name__, ex ) )
        
        return result
    
    
    def __key_to_filename( self, key ):
        file_name = path.join( self.__directory, key + _AUTOSTORE_EXTENSION )
        return file_name
    
    
    def __write_item( self, key: str, value: Optional[object] ) -> None:
        """
        Saves the settings to disk
        """
        file_name = self.__key_to_filename( key )
        
        if value is not None:
            _LOG( "write {}", key )
            mh.io_helper.save_binary( file_name, value )
        else:
            _LOG( "delete {}", key )
            os.remove( file_name )
    
    
    def __contains__( self, key: str ):
        """
        Returns if the specified setting exists on disk.
        """
        return path.isfile( self.__key_to_filename( key ) )
    
    
    def keys( self ):
        """
        Returns saved settings
        """
        keys = []
        
        for file in mh.file_helper.list_dir( self.__directory, _AUTOSTORE_EXTENSION ):
            keys.append( mh.file_helper.get_filename_without_extension( file ) )
        
        return keys


class LocalData:
    """
    Manages $(APPNAME)'s primary working directory, usually "~/$(ABVNAME)-data" (UNIX) or "%user%/$(ABVNAME)-data" (Windows).
    """
    
    
    def __init__( self, env_name ) -> None:
        """
        CONSTRUCTOR
        """
        self.__env_name = env_name
        value = self.get_redirect() or self.default_workspace()
        
        if not value or path.sep not in value:
            raise ValueError( "A complete workspace path is required, «{}» is not valid.".format( self.__workspace ) )
        
        if "~" in value:
            value = path.expanduser( value )
        
        self.__workspace = value
        self.__store: _AutoStore = None
    
    
    @property
    def workspace( self ) -> str:
        """
        Obtains the workspace folder.
        Once this is called, `set_workspace` no longer functions.
        """
        return self.__workspace
    
    
    def get_workspace( self ) -> str:
        warnings.warn( "Deprecated - use `workspace`", DeprecationWarning )
        return self.__workspace
    
    
    def set_redirect( self, content: Optional[str] ) -> None:
        """
        Sets or clears the workspace redirection.
        """
        r = self.__get_redirect_file_name()
        
        if content:
            mh.file_helper.write_all_text( r, content )
        else:
            mh.file_helper.delete_file( r )
    
    
    def get_redirect( self ) -> Optional[str]:
        """
        Gets the current redirection.
        """
        redirect = self.__get_redirect_file_name()
        
        if path.isfile( redirect ):
            return mh.file_helper.read_all_text( redirect ).strip()
        else:
            return None
    
    
    def default_workspace( self ) -> str:
        if not path.sep in self.__env_name:
            return path.join( "~", ".intermake-data", self.__env_name )
        else:
            return self.__env_name
    
    
    @property
    def store( self ) -> _AutoStore:
        """
        Obtains the settings store.
        """
        if self.__store is None:
            self.__store = _AutoStore( self.local_folder( constants.FOLDER_SETTINGS ) )
        
        # noinspection PyTypeChecker
        return self.__store
    
    
    def __get_redirect_file_name( self ) -> str:
        """
        Obtains the name of the file used to redirect the default workspace.
        """
        return path.join( self.default_workspace(), "redirect.txt" )
    
    
    def local_folder( self, name: str ) -> str:
        """
        Obtains a folder in the workspace. See `intermake.engine.constants.FOLDER_*` for suggested defaults.
        """
        folder_name = path.join( self.workspace, name )
        mh.file_helper.create_directory( folder_name )
        return folder_name
