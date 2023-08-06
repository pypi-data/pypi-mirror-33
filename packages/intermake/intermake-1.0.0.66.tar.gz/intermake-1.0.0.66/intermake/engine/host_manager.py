from mhelper import Logger


_AbstractHost = "AbstractHost"

_LOG = Logger( "host_manager" )

_CURRENT_HOST: _AbstractHost = None


def get_current_host():
    return _CURRENT_HOST


def run_host( host: _AbstractHost ) -> None:
    """
    Runs a host.
    """
    RunHost( host )


class UserExitError( BaseException ):
    """
    Used as a special error to indicate the user wishes to exit.
    This is always raised past the usual `ConsoleHost` error, thus allowing termination of the front-end via its handler.
    """
    pass


class RunHost:
    """
    Arguments passed to a host when it runs.
    
    :ivar __previous_host:  Previous host
    :ivar can_return:       Whether the new host has a previous host to return to
    :ivar exit:             If new host sets this to `True` the application will exit the host is released.
                            Use only when `can_return` is set, otherwise the application will exit anyway.
    :ivar persist:          If the new host sets this to `True` it is not released when the `run_host` function
                            exits and must call `release` manually. 
    """
    
    
    def __init__( self, host: _AbstractHost ):
        """
        CONSTRUCTOR
        """
        from intermake.hosts.base import ERunStatus
        global _CURRENT_HOST
        
        self.__previous_host = _CURRENT_HOST
        self.__host = host
        self.can_return = self.__previous_host.can_return if self.__previous_host is not None else False
        self.exit = False
        self.persist = False
        
        if _CURRENT_HOST is not None:
            _CURRENT_HOST.on_status_changed( ERunStatus.PAUSE )
        
        _CURRENT_HOST = host
        _CURRENT_HOST.on_status_changed( ERunStatus.RUN )
        
        try:
            _LOG( "RUN HOST : {}", self.__host )
            _CURRENT_HOST.run_host( self )
        except Exception as ex:
            raise ValueError( "Error running host «{}».".format( _CURRENT_HOST ) ) from ex
        
        if not self.persist:
            self.release()
    
    
    def release( self ):
        global _CURRENT_HOST
        
        _LOG( "RELEASE HOST : {}", self.__host )
        from intermake.hosts.base import ERunStatus
        
        if _CURRENT_HOST is not self.__host:
            raise ValueError( "Attempt to exit a host but this host «{}» has already exited in lieu of «{}».".format( self.__host, _CURRENT_HOST ) )
        
        _CURRENT_HOST.on_status_changed( ERunStatus.STOP )
        
        _CURRENT_HOST = self.__previous_host
        
        if _CURRENT_HOST is not None:
            _CURRENT_HOST.on_status_changed( ERunStatus.RESUME )
        
        if self.exit:
            raise UserExitError( "Host requested all other hosts exit." )
