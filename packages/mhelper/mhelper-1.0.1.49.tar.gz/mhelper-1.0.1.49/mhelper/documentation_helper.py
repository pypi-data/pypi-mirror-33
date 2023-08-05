import warnings
from typing import Union, Dict, List

import re

from mhelper import string_helper, exception_helper


def parse_doc( doc: str ) -> Dict[str, Dict[str, str]]:
    """
    Parses a doc-string.
    
    usage::
    ```
    doc = parse_doc( parse_doc.__doc__ )
    
    # Root domain
    print( doc[""][""] )
    
    # Bare domain
    print( doc["usage"][""] )
    
    # Domain attribute
    print( doc["param"]["doc"] )
    ```
    
    :param doc: The documentation string to parse
    """
    return Documentation( doc ).data


class Documentation:
    """
    Class to manage and create a documentation `dict` - see `parse_doc`.
    """
    RX_DIRECTIVE = re.compile( "^ *:(.+) +(.+): *(.+)$" )
    """
    _______:blah_____blah:_____blah
            1111     2222      3333
    """
    
    RX_DOMAIN = re.compile( "^ *(.+):: *(.*)$" )
    """
    ________blah::____blah
            1111      2222
    """
    
    
    def __init__( self, doc: str ):
        if doc is None:
            doc = ""
        
        exception_helper.assert_type( "doc", doc, str )
        
        name = ""
        cat = ""
        cur = []
        text_start = 0
        self.data = { }
        
        for line in doc.split( "\n" ):
            rx = self.RX_DIRECTIVE.match( line )
            
            if rx:
                self.add( cat, name, cur )
                
                cat = rx.group( 1 )
                name = rx.group( 2 )
                text = rx.group( 3 )
                text_start = rx.span( 3 )[0]
            else:
                rx = self.RX_DOMAIN.match( line )
                
                if rx:
                    self.add( cat, name, cur )
                    cat = rx.group( 1 )
                    name = ""
                    text = rx.group( 2 )
                    text_start = rx.span( 2 )[0]
                else:
                    text = line
                    
                    if not cur:
                        text_start = len( text ) - len( text.lstrip() )
                    
                    if all( x == " " for x in line[:text_start] ):
                        text = text[text_start:]
            
            if cur or text:
                cur.append( text )
        
        self.add( cat, name, cur )
    
    
    def __getitem__( self, item ):
        """
        Gets the documentation.
        
        :param item:    An item.
                        Specify a `str` to retrieve the dict for that domain.
                        Specify a `tuple` of `domain : str, element : str` to retrieve the text for the domain and element. 
        :return:        The dict or element text, depending on `item`.
                        If the domain or element is not found an empty dict or an empty string is returned;
                        this function should not raise.  
        """
        if isinstance( item, str ):
            return self.data.get( item, { } )
        else:
            a, b = item
            d = self.data.get( a, { } )
            return d.get( b, "" )
    
    
    def add( self, cat, nam, content ):
        c = self.data.get( cat )
        
        if c is None:
            c = { }
            self.data[cat] = c
        
        c[nam] = "\n".join( content ).rstrip()
        
        content.clear()
    
    
    def debug( self ):
        for k, v in self.data.items():
            print( "CATEGORY: " + k )
            
            for k2, v2 in v.items():
                print( "NAME: " + k2 )
                print( v2 )


def extract_documentation( doc, param_keyword = "param", as_string = True ) -> Union[Dict[str, str], Dict[str, List[str]]]:
    """
    DEPRECATED - use `parse_documentation`.
    
    Extracts the documentation into a dictionary
    
    :param doc:             Documentation string
    :param param_keyword:   Keyword to use for parameters, e.g. "param" 
    :param as_string:       `True`: Return each entry as a `str` with "\n" for or newline
                            `False`: Return each entry as a `list` with a `str` on each line.
                            
    :return:                Dictionary of argument name vs. documentation. The primary documentation is under the param name `""`.
    """
    warnings.warn( "Deprecated - use `parse_documentation`.", DeprecationWarning )
    arg_descriptions = { }
    
    param_keyword = ":{} ".format( param_keyword )
    current_desc = []
    arg_descriptions[""] = current_desc
    current_indent = -1
    if doc is not None:
        for line in doc.split( "\n" ):
            if line.lstrip().startswith( param_keyword ):
                line = line.replace( param_keyword, " " * len( param_keyword ) )
                name = line.split( ":", 1 )[0]
                line = line.replace( name, " " * len( name ), 1 )
                line = line.replace( ":", " ", 1 )
                current_indent = string_helper.get_indent( line )
                current_name = name.strip()
                current_desc = [string_helper.remove_indent( current_indent, line )]
                arg_descriptions[current_name] = current_desc
            elif not line.lstrip().startswith( ":" ):
                if current_indent == -1:
                    current_indent = string_helper.get_indent( line )
                
                current_desc.append( string_helper.remove_indent( current_indent, line ) )
            else:
                current_desc = []
    
    if as_string:
        for k in list( arg_descriptions.keys() ):
            arg_descriptions[k] = "\n".join( arg_descriptions[k] ).strip()
    
    return arg_descriptions


def get_enum_documentation( field ):
    return Documentation( field.__doc__ )["cvar", field.name]


def get_basic_documentation( entity ):
    return Documentation( entity.__doc__ )["", ""]
