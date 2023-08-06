from typing import Optional, Union, Any

import editorium
from editorium.default_editors import AbstractBrowserEditor
from editorium.bases import EditorInfo
from intermake.visualisables.visualisable import IVisualisable, VisualisablePath
from intermake.commands import console_explorer


TVis = Union[IVisualisable, VisualisablePath]


def _browse( window: Any, type_: type ) -> VisualisablePath:
    from intermake_qt.forms.frm_tree_view import FrmTreeView
    
    return FrmTreeView.request( window,
                                "Select " + type_.__name__,
                                None,
                                lambda x: isinstance( x.get_value(), type_ ) )


class Editor_Visualisable( AbstractBrowserEditor ):
    """
    Edits:  IVisualisable 
    """


    @classmethod
    def get_priority( cls ) -> int:
        return cls.Priority.LOW # We're very generic


    def __init__( self, info: EditorInfo ):
        super().__init__( info )
        self.visualisable_type = self.info.annotation.value_or_optional_value
        self.last_path = None
        self.fixed_value = None
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_direct_subclass_of_or_optional( IVisualisable )
    
    
    def on_browse( self, value: IVisualisable ) -> Optional[IVisualisable]:
        path = _browse( self.editor.window(), self.visualisable_type )
        
        if path is None:
            return None
        
        self.fixed_value = None
        self.last_path = path
        return path.get_value()
    
    
    def on_convert_to_text( self, value: IVisualisable ):
        assert isinstance( value, IVisualisable ), value
        
        if self.last_path is not None and value is self.last_path.get_last():
            self.fixed_value = None
            return str( self.last_path )
        
        self.last_path = None
        self.fixed_value = value
        return value.get_vis_info().name
    
    
    def on_convert_from_text( self, text: str ) -> VisualisablePath:
        if self.fixed_value is not None and text == self.fixed_value.get_vis_info().name:
            return self.fixed_value
        
        path: VisualisablePath = console_explorer.follow_path( path = text, restrict = self.visualisable_type )
        self.last_path = path
        self.fixed_value = None
        return path.get_value()


class Editor_VisualisablePath( AbstractBrowserEditor ):
    """
    Edits: `VisualisablePath` or `VisualisablePath[T]`. 
    """
    
    
    def __init__( self, info: EditorInfo ):
        super().__init__( info )
        
        self.visualisable_type = self.info.inspector.value_or_optional_value.type_restriction()
    
    
    @classmethod
    def on_can_handle( cls, info: EditorInfo ) -> bool:
        return info.annotation.is_direct_subclass_of_or_optional( VisualisablePath )
    
    
    def on_browse( self, value: IVisualisable ) -> Optional[VisualisablePath]:
        return _browse( self.editor.window(), self.visualisable_type )
    
    
    def on_convert_from_text( self, text: str ) -> object:
        return console_explorer.follow_path( path = text, restrict = self.visualisable_type )


def init():
    pass
    # editorium.register( Editor_Visualisable )
    # editorium.register( Editor_VisualisablePath )
