from typing import List, Iterator

import itertools

import os

from intermake.visualisables.visualisable import IVisualisable, UiInfo
from mhelper import file_helper


class HelpTopic:
    """
    A help topic for access in an Intermake application.
    """
    
    
    def __init__( self, name, content ):
        """
        CONSTRUCTOR
        :param name:        The name of the topic
                            Typically a sentence case title 
        :param content:     Topic content, EITHER the topic text OR for dynamic documentation,
                            a function providing the topic text.
                            Topic text is expected be formatted in Markdown, if necessary.
        """
        self.__name = name
        self.__content = content
    
    
    @property
    def name( self ):
        """
        The name and access key of the topic
        """
        return self.__name
    
    
    @property
    def content( self ):
        """
        Obtains the topic text.
        """
        if isinstance( self.__content, str ):
            return self.__content
        else:
            return self.__content()


class HelpTopicCollection( IVisualisable ):
    """
    Maintains a collection of `HelpTopic`s.
    """
    
    
    def __init__( self ):
        self.__topics: List[HelpTopic] = []
    
    
    def __iter__( self ) -> Iterator[HelpTopic]:
        return iter( self.__topics )
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        u.contents += { x.name: x for x in self.__topics }
    
    
    def __getitem__( self, item ):
        """
        Retrieves the topic with the specified name.
        """
        for topic in self.__topics:
            if topic.name == item:
                return topic
        
        raise KeyError( item )
    
    
    def add( self, *args, **kwargs ) -> None:
        """
        Adds a help topic.
        
        Provide either:
            * A `HelpTopic` instance.
            * The arguments to be passed to a new `HelpTopic` instance.
        """
        if len( args ) == 1 and isinstance( args[0], HelpTopic ):
            self.__topics.append( args[0] )
        else:
            self.__topics.append( HelpTopic( *args, **kwargs ) )
    
    
    def read( self, source: str = None, file: str = "help.mkd" ) -> None:
        """
        Reads a markdown file into the help.
        One topic is created per title (`===` underscored).
        
        :param source:  If specified, `file` is searched for in the same folder as this file.
                        Permits file to be specified relative to the current source `__file__`.
                        Optional and ignored if the file contains a separator.
        :param file:    File name. 
        """
        if os.path.sep in file:
            path = file
        else:
            path = file_helper.join( file_helper.get_directory( source ), file )
        
        title = ""
        arr = []
        
        with open( path, "r" ) as fin:
            for line in itertools.chain( fin, ("END", "===") ):
                if line.startswith( "===" ):
                    next_title = arr.pop().strip()
                    
                    text = "".join( arr ).strip()
                    
                    if text:
                        topic = HelpTopic( title, text )
                        self.add( topic )
                    
                    title = next_title
                
                arr.append( line )
