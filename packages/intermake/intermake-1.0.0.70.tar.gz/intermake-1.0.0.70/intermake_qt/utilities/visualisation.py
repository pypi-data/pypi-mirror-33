from intermake import IVisualisable, MENV
from mhelper_qt import qt_gui_helper


def visualisable_to_html( value: IVisualisable ):
    visualisable_info = value.get_vis_info()
    lookup = qt_gui_helper.ansi_scheme_light()
    
    host = MENV.host
    
    comment_string = qt_gui_helper.ansi_to_html( host.substitute_text( visualisable_info.doc or "" ), lookup = lookup, background = False )
    
    if len( visualisable_info.source ) > host.console_width or "\n" in visualisable_info.source:
        lookup2 = lookup.copy()
        lookup2.values[-1] = lookup2.values[-1].copy()
        lookup2.values[-1].family = "Consolas,monospace"
        value_string = qt_gui_helper.ansi_to_html( visualisable_info.source, lookup = lookup2, background = False )
    else:
        value_string = qt_gui_helper.ansi_to_html( visualisable_info.source, lookup = lookup, background = False )
        value_string = "<h3>{}</h3>".format( value_string )
    
    prefix = '<html><body style="' + lookup.get_default().to_style(background = False) + '">'
    suffix = "</body></html>"
    
    name_string = '<h2>{}</h2>'.format( visualisable_info.name )
    
    comment_string = "{}".format( comment_string )

    return "{}{}{}{}{}".format( prefix, name_string, value_string, comment_string, suffix )