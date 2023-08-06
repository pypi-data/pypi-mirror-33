from typing import Optional, Callable

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QTreeWidgetItem, QWidget


from intermake_qt.forms.designer.frm_tree_view_designer import Ui_Dialog
from intermake_qt.views.results_view import ResultsView
from intermake.visualisables.visualisable import VisualisablePath


class FrmTreeView( QDialog ):
    def __init__( self,
                  parent: QWidget,
                  message: str,
                  root: VisualisablePath,
                  on_selecting: Optional[Callable[[VisualisablePath], bool]],
                  flat: bool = False ):
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        self.setWindowTitle( message )
        self.ui.splitter.setStretchFactor( 0, 3 )
        
        self.__results = ResultsView( tree_widget = self.ui.TVW_MAIN,
                                      text_widget = self.ui.TXT_MAIN,
                                      toolbar_layout = self.ui.HOZ_TOOLBAR,
                                      root = root,
                                      on_selected = self.__on_selected,
                                      on_selecting = on_selecting,
                                      flat = flat,
                                      title_widget = self.ui.LBL_MAIN )
        self.__acceptability = on_selecting
        self.__result: VisualisablePath = None
        self.on_TVW_MAIN_itemSelectionChanged()
        
        if on_selecting is None:
            self.ui.BTNBOX_MAIN.setVisible( False )
    
    
    def __on_selected( self, item: QTreeWidgetItem ) -> None:
        self.__accept( item )
    
    
    @staticmethod
    def request( parent: QWidget,
                 message: Optional[str] = None,
                 root: Optional[VisualisablePath] = None,
                 on_selecting: Optional[Callable[[VisualisablePath], bool]] = None,
                 flat: bool = False 
                 ) -> Optional[VisualisablePath]:
        if root is None:
            root = VisualisablePath.get_root()
        
        if message is None:
            if on_selecting is None:
                message = "Explorer"
            else:
                message = "Select object"
        
        frm = FrmTreeView( parent, message, root, on_selecting, flat )
        
        if frm.exec_():
            return frm.__result
        
        return None
    
    
    @pyqtSlot()
    def on_TVW_MAIN_itemSelectionChanged( self ) -> None:  # TODO: BAD_HANDLER - The widget 'TVW_MAIN' does not appear in the designer file.
        data = self.__results.selected_data()
        
        box = self.ui.BTNBOX_MAIN  # type: QDialogButtonBox
        
        if data is not None:
            box.button( QDialogButtonBox.Ok ).setEnabled( self.__acceptability is None or self.__acceptability( data ) )
        else:
            box.button( QDialogButtonBox.Ok ).setEnabled( False )
    
    
    @pyqtSlot()
    def on_BTNBOX_MAIN_accepted( self ) -> None:
        """
        Signal handler:
        """
        self.__accept( self.__results.selected_item() )
    
    
    def __accept( self, item: QTreeWidgetItem ):
        path = self.__results.item_data( item )
        
        if path is not None and self.__acceptability( path ):
            self.__result = path
            self.accept()
    
    
    @pyqtSlot()
    def on_BTNBOX_MAIN_rejected( self ) -> None:
        """
        Signal handler:
        """
        self.reject()
