import warnings
from typing import Callable, Optional
from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QAbstractButton, QAction, QFrame, QHBoxLayout, QLabel, QMenu, QSizePolicy, QSpacerItem, QSplitter, QTextEdit, QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QMessageBox, QApplication
from mhelper import ArgValueCollection, ResourceIcon, ansi_helper, exception_helper, ignore, override, string_helper
from mhelper_qt import exceptToGui
from intermake import AbstractCommand, EIterVis, VisualisablePath

from intermake_qt.forms.designer.resource_files import resources
from intermake_qt.forms.frm_arguments import FrmArguments
from intermake_qt.views.tree_view import TreeItemInfo, TreeView


__author__ = "Martin Rusilowicz"

DSelecting = Callable[[VisualisablePath], bool]
DSelected = Callable[[QTreeWidgetItem], None]


class ResultsView( TreeView ):
    """
    Tree-like tree-view that manages presents a hierarchy starting from a `root` object.
    
    The view can be assigned to existing controls via the constructor (`__init__`), or the
    static `construct` method may be used to create the controls themselves.
    
    The `root` object can be a `VisualisablePath` or any Python object.
    """
    
    
    @staticmethod
    def __set_text_to_tvw_comment( text, tvw ):
        data = tvw.selected_data()
        
        if data is None:
            text.setText( "" )
            return
    
    
    def __init__( self,
                  *,
                  container: QWidget = None,
                  layout: QVBoxLayout = None,
                  tree_widget: QTreeWidget = None,
                  text_widget: QTextEdit = None,
                  toolbar_layout: QHBoxLayout = None,
                  root: VisualisablePath = None,
                  on_selected: DSelected = None,
                  on_selecting: DSelecting = None,
                  flat: bool = False,
                  show_root: bool = True,
                  fn_button: Callable[[QToolButton], None] = None,
                  title_widget: QLabel = None,
                  no_icons: bool = False ):
        """
        CONSTRUCTOR
        
        Controls are created if required.
        
        :param container:           If specified, denotes where the newly created layout is placed.
                                    Unused if `layout` is specified or all three of `tree_widget`, `text_widget`
                                    and `toolbar_layout` are specified.
        :param layout:              If specified, denotes where the newly created tree, text and/or toolbar are placed.
                                    If not specified and required, a new layout is created in `container`.
                                    Unused `container` is specified or if all three of `tree_widget`, `text_widget`
                                    and `toolbar_layout` are specified.
        :param tree_widget:         Tree widget to manage.
                                    This will be created if not provided (requires `container` or `layout`). 
        :param text_widget:         Text widget to manage
                                    This will be created if not provided (requires `container` or `layout`). 
        :param toolbar_layout:      Toolbar layout to manage.
                                    This will be created if not provided (requires `container` or `layout`). 
        :param root:                Root object 
        :param on_selected:         How to "select" items (if `None` the select option will not be visible) 
        :param on_selecting:        How to determine if items can be selected (if `None` all items will be selectable)
        :param flat:                Flat (no hierarchy) 
        :param show_root:           Show the root as its own node (always `False` if `flat` is set).
        """
        layout_required = ((layout is None)
                           and ((tree_widget is None)
                                or (text_widget is None)
                                or (toolbar_layout is None)))
        
        # Create `layout` (if required)
        if layout_required:
            if container is None:
                raise ValueError( "Cannot create the `layout` because `container` not specified." )
            
            layout = QVBoxLayout()
            layout.setSpacing( 0 )
            layout.setContentsMargins( 0, 0, 0, 0 )
            container.setLayout( layout )
        
        # Create `toolbar_layout`
        if toolbar_layout is None:
            if layout is None:
                raise ValueError( "Cannot create the `toolbar_layout` because `layout` not specified." )
            
            toolbar_layout = QHBoxLayout()
            layout.addLayout( toolbar_layout )
        
        splitter_required = not tree_widget or not text_widget
        
        # Create `splitter` (if required)
        if splitter_required:
            if tree_widget is None and text_widget is None:
                if layout is None:
                    raise ValueError( "Cannot create the `splitter` because `layout` not specified." )
                
                splitter = QSplitter()
                splitter.setOrientation( Qt.Vertical )
                layout.addWidget( splitter )
                splitter.setStretchFactor( 0, 3 )
            else:
                splitter = layout
        else:
            splitter = None
        
        # Create `tree_widget` 
        if tree_widget is None:
            if splitter is None:
                raise ValueError( "Cannot create the `tree_widget` because `splitter` not specified." )
            
            tree_widget = QTreeWidget()
            tree_widget.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
            tree_widget.setAlternatingRowColors( True )
            splitter.addWidget( tree_widget )
        
        # Create `text_widget`
        if text_widget is None:
            if splitter is None:
                raise ValueError( "Cannot create the `text_widget` because `splitter` not specified." )
            
            text_widget = QTextEdit()
            text_widget.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
            splitter.addWidget( text_widget )
        
        # Base class initialisation
        super().__init__( tree_widget )
        
        # Fields
        self.__orig_root = root
        self.__root_stack = []
        self.__root = root
        self.__title_widget = title_widget
        self.__text_widget = text_widget
        self.__on_selected = on_selected
        self.__on_selecting = on_selecting
        self.__toolbar_layout = toolbar_layout
        self.__flat = flat
        self.__show_root = show_root
        self.__header_map = { }
        self.__buttons = []
        self.__view_comments = True
        self.__fn_button = fn_button
        self.__buttons_visible = not no_icons
        
        # Setup
        super().set_resize_on_expand()
        self.widget.setContextMenuPolicy( Qt.CustomContextMenu )
        self.__text_widget.setReadOnly( True )
        self.__text_widget.setStyleSheet( "background:transparent;border:none" )
        self.__text_widget.setVisible( False )
        
        if flat:
            self.widget.setRootIsDecorated( False )
        
        # Toolbar
        self.__btn_refresh = self.__add_button( "Refresh", resources.refresh, toolbar_layout, self.__action_refresh,
                                                tip = "Refresh this item" )
        self.__btn_back = self.__add_button( "Back", resources.previous, toolbar_layout, self.__action_back,
                                             tip = "Go back to the previous root" )
        self.__btn_new_window = self.__add_button( "Explore", resources.next, toolbar_layout, self.__action_explore_to,
                                                   tip = "Select this item as the root" )
        self.__btn_view = self.__add_button( "View", resources.view_text, toolbar_layout, self.__action_view,
                                             tip = "View the full text of this item in a new window" )
        self.__btn_run = self.__add_button( "Run", resources.execute, toolbar_layout, self.__action_run,
                                            tip = "Run this command" )
        self.__btn_details = self.__add_button( "Details", resources.maximize, toolbar_layout, self.__action_toggle_details,
                                                tip = "Toggle the display of the details panel" )
        self.__btn_details.setCheckable( True )
        self.__btn_details.setChecked( self.__view_comments )
        
        toolbar_layout.addSpacerItem( QSpacerItem( 1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum ) )
        
        # Signals
        self.widget.itemSelectionChanged.connect( self.__on_widget_itemSelectionChanged )
        self.widget.customContextMenuRequested.connect( self.__on_widget_customContextMenuRequested )
        self.widget.itemActivated[QTreeWidgetItem, int].connect( self.__on_widget_itemActivated )
        
        # Populate
        self.rebuild()
    
    
    def __on_widget_itemActivated( self, item: QTreeWidgetItem, column: int ):
        """
        SIGNAL: self.widget::itemActivated
        """
        ignore( column )
        
        data: VisualisablePath = self.item_data( item )
        
        if data is None:
            return
        
        value = data.value
        
        if isinstance( value, AbstractCommand ):
            self.__action_run( data )
        elif self.__has_children( data ):
            self.__action_explore_to( data )
        else:
            self.__action_view( data )
    
    
    @property
    def root( self ) -> Optional[object]:
        return self.__orig_root
    
    
    def set_root( self, value: Optional[object] ) -> None:
        self.__orig_root = value
        self.__root = value
        self.__root_stack.clear()
        self.rebuild()
    
    
    def rebuild( self ):
        """
        Handles any changes to the root by rebuilding the tree.
        """
        
        self.clear()
        
        # The source should wrapped in a `VisualisablePath`, it it's not we wrap it now.
        if not isinstance( self.__root, VisualisablePath ):
            self.__root = VisualisablePath.from_visualisable_temporary( self.__root )
        
        # Title
        if self.__title_widget is not None:
            self.__title_widget.setText( self.__root.path )
        
        # Setup the headers
        headers = QTreeWidgetItem()
        self.__header_map.clear()
        self.widget.setHeaderItem( headers )
        
        # Add the root
        if self.__root is not None:
            if self.__flat or not self.__show_root:
                for item in self.__root.iter_children( iter = EIterVis.PROPERTIES | EIterVis.CONTENTS ):
                    self.__add( None, item )
            else:
                self.__add( None, self.__root )
        
        self.resize_columns()
        self.__update_buttons()
    
    
    def __add( self, parent: Optional[QTreeWidgetItem], child: VisualisablePath ):
        exception_helper.assert_type( "child", child, VisualisablePath )
        self.add_item( parent, child, loader = self.__requires_children( child ) )
    
    
    @property
    def on_selected( self ):
        return self.__on_selected
    
    
    @property
    def on_selecting( self ):
        return self.__on_selecting
    
    
    @staticmethod
    def __add_separator( toolbar_layout ):
        line = QFrame()
        line.setFixedWidth( 8 )
        line.setFrameShape( QFrame.VLine )
        line.setFrameShadow( QFrame.Sunken )
        toolbar_layout.addWidget( line )
    
    
    def __add_button( self, name: str, icon: ResourceIcon, toolbar_layout: QHBoxLayout, command, in_buttons = True, tip = "" ) -> QAbstractButton:
        button = QToolButton()
        button.setFixedSize( QSize( 64, 64 ) )
        button.setIconSize( QSize( 32, 32 ) )
        button.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )
        button.setText( name )
        button.setToolTip( name + " - " + tip )
        button.setIcon( icon.icon() )
        toolbar_layout.addWidget( button )
        button.TAG_command = command
        button.clicked[bool].connect( self.__on_toolbar_button_clicked )
        button.setEnabled( False )
        button.setVisible( self.__buttons_visible )
        
        if self.__fn_button:
            self.__fn_button( button )
        
        if in_buttons:
            self.__buttons.append( button )
        
        return button
    
    
    @exceptToGui()
    def __on_toolbar_button_clicked( self, _: bool ):
        sender = self.widget.window().sender()
        assert isinstance( sender, QAbstractButton )
        command = sender.TAG_command
        command()
    
    
    @exceptToGui()
    def __on_widget_customContextMenuRequested( self, pos: QPoint ):
        """
        Shows the menu on right-click or Windows menu key.
        """
        tree: QTreeWidget = self.widget
        item: QTreeWidgetItem = tree.itemAt( pos )
        
        if item is None:
            return
        
        menu = QMenu( self.widget.window() )
        
        for button in self.__buttons:
            if button.isEnabled():
                assert isinstance( button, QAbstractButton )
                action_item: QAction = menu.addAction( button.text() )
                action_item.setIcon( button.icon() )
                action_item.setFont( button.font() )
                action_item.setToolTip( button.toolTip() )
                action_item.setCheckable( button.isCheckable() )
                action_item.setChecked( button.isChecked() )
                action_item.TAG_command = button.TAG_command
        
        selection: QAction = menu.exec_( self.widget.mapToGlobal( pos ) )
        
        if selection is not None:
            selection.TAG_command()
    
    
    @property
    def selected( self ):
        property: VisualisablePath = self.selected_data()
        
        if property is None:
            return None
        
        return property.value
    
    
    @exceptToGui()
    def __on_widget_itemSelectionChanged( self ):
        self.__update_buttons()
        self.__update_details_box()
    
    
    def __update_details_box( self ):
        property: VisualisablePath = self.selected_data()
        text = property.documentation if property is not None else ""
        self.__text_widget.setText( text )
        self.__text_widget.setVisible( bool( text ) and self.__view_comments )
        self.__btn_details.setChecked( self.__view_comments )
    
    
    def __update_buttons( self ):
        property: VisualisablePath = self.selected_data()
        value = property.value if property is not None else None
        
        for button in self.__buttons:
            button.setEnabled( True )
            button.setVisible( self.__buttons_visible )
        
        self.__btn_back.setEnabled( bool( self.__root_stack ) )
        self.__btn_run.setEnabled( isinstance( value, AbstractCommand ) )
        self.__btn_view.setEnabled( property is not None )
        self.__btn_new_window.setEnabled( property is not None and self.__has_children( property ) )
        
        if self.__btn_run.isEnabled():
            self.__make_bold( self.__btn_run, True )
            self.__make_bold( self.__btn_new_window, False )
            self.__make_bold( self.__btn_view, False )
        elif self.__btn_new_window.isEnabled():
            self.__make_bold( self.__btn_run, False )
            self.__make_bold( self.__btn_new_window, True )
            self.__make_bold( self.__btn_view, False )
        else:
            self.__make_bold( self.__btn_run, False )
            self.__make_bold( self.__btn_new_window, False )
            self.__make_bold( self.__btn_view, True )
    
    
    def __make_bold( self, button: QAbstractButton, bold: bool ):
        f: QFont = button.font()
        if bold:
            button.setFont( QFont( f.family(), f.pointSize(), QFont.Bold ) )
        else:
            button.setFont( QFont( f.family(), f.pointSize(), QFont.Normal ) )
    
    
    def root_object( self ) -> Optional[object]:
        warnings.warn( "Deprecated - use root", DeprecationWarning )
        return self.root
    
    
    def __requires_children( self, data: VisualisablePath ):
        if self.__flat:
            return False
        
        return self.__has_children( data )
    
    
    def __has_children( self, data: VisualisablePath ):
        return any( True for _ in data.iter_children( EIterVis.PROPERTIES | EIterVis.CONTENTS ) )
    
    
    @override
    def on_update_item( self, node_info: TreeItemInfo ):
        """
        OVERRIDE
        """
        
        node: QTreeWidgetItem = node_info.item()
        property: VisualisablePath = node_info.data()
        
        # Add children
        if node_info.add_children() and not self.__flat:
            # Add actual items
            children = [child for child in property.iter_children( EIterVis.CONTENTS | EIterVis.PROPERTIES )]
            children = sorted( children, key = lambda child: child.key )
            
            for index, child in enumerate( children ):
                if index > 100:
                    # Don't display more than 100 items
                    self.__add( node, VisualisablePath.from_visualisable_temporary( "...only displaying the first 100 items.", name = "" ) )
                    break
                
                self.__add( node, child )
            
            # Columns changed
            self.resize_columns()
        
        # Colour the item by its selectability
        if self.__on_selecting is not None:
            if self.__on_selecting( property ):
                colour = property.qcolour
                colour_2 = QColor( Qt.black )
            else:
                colour = QColor( Qt.gray )
                colour_2 = QColor( Qt.gray )
        else:
            colour = property.qcolour
            colour_2 = QColor( Qt.black )
        
        # Background
        if property.is_property:
            bg_col = QColor( 0, 0, 0, 32 )
        else:
            bg_col = QColor( 0, 0, 0, 0 )
        
        # COLUMN: Key
        key_str = property.key
        key_str = string_helper.max_width( key_str, 40 )
        
        col_index = self.__get_or_create_column( "Name" )
        node.setText( col_index, key_str )
        node.setForeground( col_index, colour_2 )
        node.setBackground( col_index, bg_col )
        
        # COLUMN: Type
        type_str = property.type_name.strip( "_" )
        col_index = self.__get_or_create_column( "Type" )
        node.setText( col_index, type_str )
        node.setForeground( col_index, colour_2 )
        node.setBackground( col_index, bg_col )
        
        # COLUMN: Value
        lines = list( ansi_helper.wrap( property.text, 80 ) )
        text = lines[0] if len( lines ) == 1 else (lines[0] + "…") if lines else ""
        
        if text:
            col_index = self.__get_or_create_column( "Value" )
            node.setText( col_index, text )
            node.setForeground( col_index, colour )
            node.setBackground( col_index, bg_col )
        
        # ICON
        node.setIcon( 0, property.icon.icon() )
        
        # COLUMN: Miscellaneous
        if self.__flat:
            for x in property.iter_children( iter = EIterVis.PROPERTIES ):
                text = x.text
                
                if not text or len( text ) > 100:
                    continue
                
                col_index = self.__get_or_create_column( x.key )
                node.setText( col_index, text )
    
    
    def __get_or_create_column( self, key: str ):
        col_index = self.__header_map.get( key )
        
        if col_index is None:
            col_index = len( self.__header_map )
            self.__header_map[key] = col_index
            self.widget.headerItem().setText( col_index, key )
        
        return col_index
    
    
    @exceptToGui()
    def __action_explore_to( self, data: VisualisablePath = None ):
        prop: VisualisablePath = data if data is not None else self.selected_data()
        
        if prop is None:
            return
        
        self.__root_stack.append( self.__root )
        self.__root = prop
        self.rebuild()
    
    
    @exceptToGui()
    def __action_back( self ):
        if len( self.__root_stack ) == 0:
            QMessageBox.critical( self.window, "Error", "Cannot go back, there is nothing to go back to." )
            return
        
        self.__root = self.__root_stack.pop()
        self.rebuild()
    
    
    @exceptToGui()
    def __action_toggle_details( self ):
        self.__view_comments = not self.__view_comments
        self.__update_details_box()
    
    
    @exceptToGui()
    def __action_run( self, data: VisualisablePath = None ):
        prop: VisualisablePath = data if data is not None else self.selected_data()
        
        if prop is None:
            return
        
        command = prop.value
        
        if not isinstance( command, AbstractCommand ):
            return
        
        arguments: Optional[ArgValueCollection] = FrmArguments.request( self.widget.window(), command )
        
        if arguments is not None:
            command.run_with( arguments )
    
    
    def __action_refresh( self ):
        if QApplication.keyboardModifiers() & Qt.ControlModifier:
            # Debugging
            r = []
            r.append( "__root = {}".format( self.__root ) )
            r.append( "__root_type = {}".format( type( self.__root ) ) )
            r.append( "__root.value = {}".format( self.__root.value if isinstance( self.__root, VisualisablePath ) else None ) )
            r.append( "__root.value_type = {}".format( type( self.__root.value ) if isinstance( self.__root, VisualisablePath ) else None ) )
            r.append( "__root_stack = {}".format( self.__root_stack ) )
            r.append( "__orig_root = {}".format( self.__orig_root ) )
            r.append( "__flat = {}".format( self.__flat ) )
            r.append( "__show_root = {}".format( self.__show_root ) )
            r.append( "__view_comments = {}".format( self.__view_comments ) )
            r.append( "__fn_button = {}".format( self.__fn_button ) )
            r.append( "__buttons_visible = {}".format( self.__buttons_visible ) )
            QMessageBox.information( self.window, "Information", "\n".join( r ) )
            return
        
        item = self.selected_item()
        
        if item is None:
            return
        
        self.update_item( item, True )
        item.setExpanded( True )
    
    
    def __action_view( self, data: VisualisablePath = None ):
        prop: VisualisablePath = data if data is not None else self.selected_data()
        
        if prop is None:
            return
        
        text = prop.text
        
        from intermake_qt.forms.frm_big_text import FrmBigText
        FrmBigText.request( self.window, prop.path, text )
