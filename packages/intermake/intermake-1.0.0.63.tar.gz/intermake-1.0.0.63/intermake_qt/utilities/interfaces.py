from intermake.engine.async_result import AsyncResult


    


# noinspection PyAbstractClass
class IGuiHostMainWindow:
    def command_completed( self, result: AsyncResult ) -> None:
        """
        The derived class should respond to the command's completion.
        """
        raise NotImplementedError( "abstract" )
    
    def return_to_console( self ) -> bool:
        raise NotImplementedError( "abstract" )
