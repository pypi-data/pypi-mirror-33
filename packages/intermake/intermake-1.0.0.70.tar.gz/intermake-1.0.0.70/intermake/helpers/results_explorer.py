from intermake.engine import constants
from intermake.engine.async_result import AsyncResult
from intermake.engine.environment import MCMD
from intermake.visualisables.visualisable import IVisualisable, UiInfo
from mhelper import override


class ResultsExplorer( IVisualisable ):
    """
    The `ResultsExplorer` class is used to explore results from the execution of previous
    Commands (`AbstractCommand`s). 
    """
    
    
    @override
    def on_get_vis_info( self, u: UiInfo ) -> None:
        super().on_get_vis_info( u )
        host = MCMD.host
        
        u.doc = "Explore your query history"
        u.text = self.__visualisable_info_value()
        u.hint = u.Hints.FOLDER
        u.contents += { "results", host.result_history }
    
    
    @override
    def __str__( self ):
        return constants.EXPLORER_KEY_RESULTS
    
    
    @staticmethod
    def __visualisable_info_value():
        """
        Value property of `on_get_vis_info`.
        """
        host = MCMD.host
        
        if not host.result_history:
            return "(empty)"
        
        last_result = host.result_history[-1]
        
        if last_result.is_success:
            if last_result.result is not None:
                return "Data: {}".format( last_result.title )
            else:
                return "Success: {}".format( last_result.title )
        else:
            return "Error: {}".format( last_result.title )


class _AsyncResultAsVisualisable( IVisualisable ):
    """
    Wraps an individual result to an `IVisualisable` so the user can explore it. 
    """
    
    
    def __init__( self, name, data: AsyncResult, comment ):
        """
        :param name:    Name of the result (name of the result, e.g. last, error, 1, 2, 3...)
        :param data:    The actual AsyncResult 
        :param comment: Comment on the result (where it came from, e.g. my_super_plugin)
        """
        self.name = name
        self.data = data
        self.comment = comment
    
    
    @override
    def on_get_vis_info( self, u: UiInfo ) -> None:
        super().on_get_vis_info( u )
        u.doc = self.comment or self.data.title
        u.text = str( self.data )
        u.hint = u.Hints.ERROR if self.data.is_error else u.Hints.SUCCESS
        u.properties += { "result"   : self.data.result,
                          "exception": self.data.exception,
                          "traceback": self.data.traceback,
                          "messages" : self.data.messages }
