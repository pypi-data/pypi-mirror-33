from typing import Optional, cast, Dict, Tuple

from PyQt5.QtWidgets import QDialog, QWidget

from editorium import EditoriumGrid
import intermake as im
from intermake_qt.forms.designer.frm_arguments_designer import Ui_Dialog
from intermake_qt.forms.designer.resource_files import resources_rc
from mhelper import ArgValueCollection, ArgsKwargs
import mhelper_qt as qt


cast( None, resources_rc )

__author__ = "Martin Rusilowicz"

_Coords_ = "Coords"


class FrmArguments( QDialog ):
    def __init__( self, parent: QWidget, command: im.AbstractCommand, defaults: ArgsKwargs, title: str ) -> None:
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        
        command = im.BasicCommand.retrieve( command )
        
        self.ui = Ui_Dialog( self )
        self.title = title or command.display_name
        self.setWindowTitle( "{} - {}".format( parent.windowTitle(), self.title ) )
        self.options_key = "gui_arguments"
        self.command_state_key = "gui_arguments.{}".format( command.name )
        self.options: _FrmArguments_Options = im.MCMD.environment.local_data.store.retrieve( self.options_key, _FrmArguments_Options() )
        self.command_state: _FrmArguments_CmdOptions = im.MCMD.environment.local_data.store.retrieve( self.command_state_key, _FrmArguments_CmdOptions() )
        
        self.__command = command
        
        self.result: ArgValueCollection = None
        
        self.values = ArgValueCollection( command.args, defaults )
        self.editorium_grid = EditoriumGrid( grid = self.ui.GRID_ARGS,
                                             targets = (self.values,),
                                             fn_description = lambda x: im.MCMD.host.substitute_text( x.description ),
                                             fn_name = lambda x: im.MCMD.host.translate_name( x.name ) )
        self.editorium_grid.create_help_button( self.__command.documentation, self.ui.BTN_HELP_MAIN )
        
        self.__init_controls()
        
        self.ui.LBL_APP_NAME.setText( im.MCMD.environment.name )
    
    
    def save_options( self ):
        im.MCMD.environment.local_data.store.commit( self.options_key, self.options )
    
    
    def __init_controls( self ):
        self.ui.LBL_PLUGIN_NAME.setText( self.title )
        self.editorium_grid.mode = EditoriumGrid.Layouts.INLINE_HELP if self.options.inline_help else EditoriumGrid.Layouts.NORMAL
        self.editorium_grid.recreate()
        
        if self.editorium_grid.editor_count == 0:
            label = qt.QLabel()
            label.setText( "There are no user-configurable arguments for this command." )
            label.setSizePolicy( qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed )
            label.setEnabled(False)
            self.editorium_grid.grid.addWidget( label, 0, 0 )
            self.editorium_grid.grid.update()
    
    
    @staticmethod
    def query( owner_window: QWidget, command: im.AbstractCommand, defaults: ArgsKwargs = None, title: str = None ) -> Optional[ArgValueCollection]:
        """
        As `request` but the command is not run when the form closes.
        """
        if defaults is None:
            defaults = ArgsKwargs()
        
        form = FrmArguments( owner_window, command, defaults, title )
        
        if form.exec_():
            return form.result
        else:
            return None
    
    
    @classmethod
    def request( cls,
                 owner_window: QWidget,
                 command: im.AbstractCommand,
                 defaults: ArgsKwargs = None,
                 title: str = None ) -> Optional[im.AsyncResult]:
        """
        Shows the arguments request form and runs the plugin.
        
        :param title:         Window title override
        :param owner_window:  Owning window 
        :param command:        AbstractCommand to show arguments for 
        :param defaults:      Optional defaults.
        """
        a = cls.query( owner_window, command, defaults, title )
        
        if a is None:
            return None
        
        try:
            return im.MCMD.host.acquire( command, window = owner_window ).run( **a.tokwargs() )
        except Exception as ex:
            from mhelper import ansi_format_helper
            print( ansi_format_helper.format_traceback( ex ) )
            raise
    
    
    @qt.exqtSlot()
    def on_pushButton_clicked( self ) -> None:
        """
        Signal handler:
        """
        
        try:
            self.editorium_grid.commit()
            incomplete = self.values.get_incomplete()
            
            if incomplete:
                raise ValueError( "The following arguments have not been provided:\n{}".format( "\n".join( [("    * " + x) for x in incomplete] ) ) )
            
            self.result = self.values
            
            self.accept()
        except Exception as ex:
            qt.show_exception( self, "Error", ex )
            return
    
    
    def save_command_state( self ):
        im.MCMD.environment.local_data.store.commit( self.command_state_key, self.command_state )
    
    
    @qt.exqtSlot()
    def on_BTN_OPTIONS_clicked( self ) -> None:
        """
        Signal handler:
        """
        mnu_root = qt.QMenu()
        
        mnu_help = qt.QMenu()
        mnu_help.setTitle( "Help" )
        mnu_root.addMenu( mnu_help )
        
        act_help_off = qt.QAction()
        act_help_off.setText( "Show buttons" )
        act_help_off.setCheckable( True )
        act_help_off.setChecked( not self.options.inline_help )
        mnu_help.addAction( act_help_off )
        
        act_help = qt.QAction()
        act_help.setText( "Show inline" )
        act_help.setCheckable( True )
        act_help.setChecked( self.options.inline_help )
        mnu_help.addAction( act_help )
        
        o = self.command_state
        acts = { }
        
        act_save_new = qt.QAction()
        act_save_new.setText( "Save as..." )
        act_save_new.setEnabled( self.editorium_grid.editor_count != 0 )
        
        mnu_auto = qt.QMenu()
        mnu_auto.setTitle( "Prompt" )
        mnu_root.addMenu( mnu_auto )
        
        act_auto_off = qt.QAction()
        act_auto_off.setText( "Ask before running this command" )
        act_auto_off.setCheckable( True )
        act_auto_off.setChecked( not o.auto_run )
        mnu_auto.addAction( act_auto_off )
        
        act_auto = qt.QAction()
        act_auto.setText( "Don't ask in future" )
        act_auto.setCheckable( True )
        act_auto.setChecked( o.auto_run )
        act_auto.setEnabled( self.editorium_grid.editor_count == 0 )
        mnu_auto.addAction( act_auto )
        
        act_sel: qt.QAction = qt.show_menu( self, mnu_root )
        
        if act_sel is None:
            return
        elif act_sel is act_help:
            return self.set_help_on( True )
        elif act_sel is act_help_off:
            return self.set_help_on( False )
        elif act_sel is act_save_new:
            name, ok = qt.QInputDialog.getText( self, self.windowTitle(), "Name your state:" )
            
            if ok and name:
                self.save_state( name )
        elif act_sel is act_auto:
            self.command_state.auto_run = True
            self.save_command_state()
        elif act_sel is act_auto_off:
            self.command_state.auto_run = False
            self.save_command_state()
        else:
            op, state = acts[act_sel]
            
            if op == "load":
                return self.load_state( state )
            elif op == "save":
                return self.save_state( state )
            elif op == "remove":
                return self.delete_state( state )
    
    
    def set_help_on( self, on: bool ):
        self.editorium_grid.commit()
        self.options.inline_help = on
        self.save_options()
        self.__init_controls()
    
    
    def mk_act( self, name: str, acts: Dict[qt.QAction, Tuple[str, str]], menu: qt.QMenu, state: str ):
        a = qt.QAction()
        a.setText( state )
        acts[a] = name, state
        menu.addAction( a )
    
    
    @qt.exqtSlot()
    def on_BTN_HELP_MAIN_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass


class _FrmArguments_CmdOptions:
    def __init__( self ):
        self.auto_run: bool = False


class _FrmArguments_Options:
    """
    :ivar alternate_theme:   Use the alternate theme
    :ivar inline_help:       Show help text alongside the arguments, rather than requiring a mouse-over
    """
    
    
    def __init__( self ):
        self.alternate_theme = False
        self.inline_help = True
        self.per_command_settings: Dict[str, _FrmArguments_CmdOptions] = { }
