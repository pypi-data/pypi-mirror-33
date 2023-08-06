from typing import IO, Iterable, List, Optional, Sequence, Tuple, TypeVar, Union

from intermake.engine.constants import EStream
from intermake.engine.progress_reporter import ActionHandler, IProgressReceiver, Message, ProgressReporter, QueryInfo, TText
from intermake.hosts.base import AbstractHost
from mhelper import NOT_PROVIDED, exception_helper


T = TypeVar( "T" )

TIterable = Union[Sequence[T], Iterable[T], IO]
FPlugin = "AbstractCommand"


class Mandate:
    """
    The `Mandate` provides the mechanism for the programmer to report progress and information back to the calling host,
    regardless of whether the host is a GUI, terminal session, Jupyter notebook, or another Python program.
    
    The Mandate can be considered by the programmer to be a singleton, accessed via the globally available `MCMD`
    proxy variable.
    
    Internally, Mandates exist on a per-thread, per-plugin basis. `MCMD` is in fact a proxy variable bound to the active Mandate.
    Mandates are instantiated by Intermake whenever a new plugin or thread runs, and there is a base Mandate which serves when
    no plugin is running.
    
    The Mandate class has no public fields, all functionality is accessed through its methods and properties.
    """
    
    
    def __init__( self,
                  host: AbstractHost,
                  receiver: IProgressReceiver,
                  title: str = None,
                  thread_index: int = 0,
                  num_threads: int = 1,
                  update_interval: float = 0.2 ) -> None:
        """
        CONSTRUCTOR
        
        :param host:                Executing host   
        :param receiver:            Where to send progress updates to 
        :param title:               The title of the mandate (arbitrary) 
        :param thread_index:        Index of the thread. 0-based. Always 0 for single threaded execution and system-wide mandates.
        :param num_threads:         Number of executing threads. Always 1 for single threaded execution and system-wide mandates.
        :param update_interval:     How often should similar progress updates be sent 
        """
        exception_helper.assert_type( "receiver", receiver, IProgressReceiver )
        
        self.__host: AbstractHost = host
        self.__progress: ProgressReporter = ProgressReporter( receiver, title, thread_index, num_threads, update_interval )
    
    
    def get_self( self ):
        return self
    
    
    def acquire( self, *args, **kwargs ):
        return self.host.acquire( *args, **kwargs )
    
    
    @property
    def environment( self ):
        return self.__host.environment
    
    
    def log( self, condition: bool, message: str, stream: EStream = EStream.INFORMATION ):
        """
        As `print`, but conditional.
        """
        if condition:
            self.print( message, stream )
    
    
    def print( self, message: str, stream: EStream = EStream.INFORMATION ) -> None:
        """
        Issues a message to the handling UI.
        
        The nature of the message is specified using the `stream` parameter.
        Several accessory functions are provided which provide a different default `stream`:
        `warning`, `information`, `progress`, etc.
        
        See the `EStream` enumeration for more details.
        
        :param message: Message.  
        :param stream:  Stream to send to. 
        """
        self.__progress.print( message, stream )
    
    
    def __repr__( self ) -> str:
        return "Mandate({}/{})".format( repr( self.host ), repr( self.host.environment ) )
    
    
    @property
    def host( self ) -> AbstractHost:
        """
        Gets the current host.
        """
        return self.__host
    
    
    def _get_receiver( self ) -> IProgressReceiver:
        """
        Obtains the `IProgressReceiver` associated with this mandate.
        """
        return self.__progress.receiver
    
    
    def enumerate( self, iterable: TIterable, title: str, count: Optional[int] = None, text: TText = None ) -> Iterable[Tuple[int, T]]:
        """
        Enumerates the selection with progress feedback to the user.

        Usage is the same as the `Mandate.iterate` function.

        See the Python function `enumerate` for the return value.
        """
        return enumerate( self.iterate( iterable, title, count, text ) )
    
    
    def iterate( self, iterable: TIterable, title: str, count: Optional[int] = None, text: TText = None ) -> Iterable[T]:
        """
        Iterates over an iterable and relays the progress to the GUI.
        
        :param iterable:        What to iterate over. This can be any iterable, though special cases for `list` `tuple` and file objects allow an automated `count`. 
        :param title:           Title of the progress bar 
        :param count:           OPTIONAL. A count of how many items in the iterable. The default is len(iterable), or the length of the file in bytes (for a file object). 
        :param text:     If set the progress counter displays the string representation of the current iteration using this function.
                                    `None` : Don't print the items, just print the count 
                                    `True` : Print the string representation (same as `str` or "{0}")
                                    `Callable[[Any], str]`: Use this function to get string representations
                                    `str`: Format this string to get string representation
                                
        :return:                Yields each item from `iterable`. 
        """
        if count is None:
            try:
                count = len( iterable )
                count_is_file = False
            except TypeError:
                try:
                    original_position = iterable.tell()
                    count = iterable.seek( 0, 2 )
                    iterable.seek( original_position )
                    count_is_file = True
                except AttributeError:
                    count = 0
                    count_is_file = False
        else:
            count_is_file = False
        
        with self.action( title, count, text ) as action:
            for x in iterable:
                if count_is_file:
                    action.set_value( iterable.tell() )
                elif text:
                    action.increment()
                else:
                    action.increment()
                
                yield x
    
    
    def action( self, title: str, count: int = 0, interesting: object = None ) -> ActionHandler:
        """
        Creates an object (an `ActionHandler`) to report the current stage of work.

        This automatically sends progress messages to represent the work.
        
        For usage example and further details see the `ActionHandler` class documentation.

        :param title:       Title of the workload
        :param count:       Size of the workload, or 0 if unknown.
        :param interesting: See `iterate`
        :return:            An `ActionHandler` object that can be used to relay progress information about the workload.
        """
        return self.__progress.action( title, count, interesting )
    
    
    def warning( self, message: str = "" ) -> None:
        """
        See :method:`print`.
        """
        self.print( message, EStream.WARNING )
    
    
    def information( self, message: str = "" ) -> None:
        """
        See :method:`print`.
        """
        self.print( message, EStream.INFORMATION )
    
    
    def progress( self, message: str = "" ) -> None:
        """
        See :method:`print`.
        """
        self.print( message, EStream.PROGRESS )
    
    
    def autoquestion( self, message: str ):
        if not self.question( message, default = True ):
            raise ValueError( "User cancelled." )
    
    
    def question( self, message: Union[str, QueryInfo], options: Optional[Sequence[object]] = None, default: Optional[object] = NOT_PROVIDED ):
        """
        Requests intervention from the user.
        
        :param default: The default value. `NOT_PROVIDED` prevents a default being selected (`None` implies the default is `None`).
        :param message: Message, or a `QueryInfo` object.
        :param options: Options.
                        The default is `None`.
                        If `None` assumes `(True,False)`.
                        The following translations are assumed:
                            `True`  = "yes"
                            `False` = "no"
                            `None`  = "cancel" 
        :return:        The selected option.
        """
        if isinstance( message, QueryInfo ):
            query_info = message
        else:
            query_info = QueryInfo( message, options, default )
        
        return self.__progress.question( query_info )
    
    
    @property
    def num_threads( self ) -> int:
        """
        The number of "threads" the plugin is running in.
        Note: The "threads" themselves may be processes running on separate machines.
        """
        return self.__progress.num_threads()
    
    
    @property
    def is_multithreaded( self ) -> bool:
        """
        If the current operation is multi-threaded (`True`), or not (`False`).
        """
        return self.__progress.num_threads() != 1
    
    
    @property
    def is_singlethreaded( self ) -> bool:
        """
        If the current operation is multi-threaded (`False`), or not (`True`).
        """
        return self.__progress.num_threads() == 1
    
    
    @property
    def is_first_thread( self ) -> bool:
        """
        Convenience function that identifies if this is the first thread.
        """
        return self.__progress.thread_index() == 0
    
    
    @property
    def is_secondary_thread( self ) -> bool:
        """
        Convenience function that identifies if this is not the first thread.
        """
        return self.__progress.thread_index() != 0
    
    
    @property
    def thread_index( self ) -> int:
        """
        If the current operation is multi-threaded, the index of the current thread.
        Zero-based indexing is used. This is always `0` for a single threaded plugin.
        """
        return self.__progress.thread_index()
    
    
    def divide_workload( self, quantity: int ) -> Tuple[int, int]:
        """
        See `MHelper.BatchList.divide_workload`.
        """
        from mhelper import array_helper
        return array_helper.get_workload( self.thread_index, quantity, self.num_threads )
    
    
    def get_message_records( self ) -> List[Message]:
        """
        Obtains all messages ever sent via this mandate.
        """
        return self.__progress._message_records
