import inspect
import subprocess
from inspect import FrameInfo
from typing import Iterable, Union, Optional, TypeVar, Type, cast
import sys

from mhelper.special_types import NOT_PROVIDED


TType = Union[type, Iterable[type]]
"""A type, or a collection of types"""

T = TypeVar( "T" )


class NotSupportedError( Exception ):
    """
    Since `NotImplementedError` looks like an abstract-base-class error to the IDE, `NotSupportedError` provides a more explicit alternative.
    """
    pass


class LogicError( Exception ):
    """
    Signifies a logical error in the subroutine which generally isn't the caller's fault.
    """
    pass


ImplementationError = LogicError
"""Alias for LogicError"""


class MultipleError( Exception ):
    """
    More than one result was found.
    """
    pass


class NotFoundError( Exception ):
    """
    Like FileNotFound error, but when applied to something other than files.
    """
    pass


class ParameterError( Exception ):
    def __init__( self, name, value = None ):
        super().__init__( "The parameter «{}» requires a value that is not «{}».".format( name, value ) )


class SwitchError( Exception ):
    """
    An error selecting the case of a switch.
    """
    
    
    def __init__( self, name: str, value: object, *, instance: bool = False, details: Optional[str] = None ):
        """
        CONSTRUCTOR
        
        :param name:        Name of the switch 
        :param value:       Value passed to the switch 
        :param instance:    Set to indicate the switch is on the type of value (`type(value)`)
        :param details:     Additional message to append to the error text. 
        """
        if details is not None:
            details = " Further details: {}".format( details )
        
        if instance:
            super().__init__( "The switch on the type of «{}» does not recognise the value «{}» of type «{}».{}".format( name, value, type( value ), details ) )
        else:
            super().__init__( "The switch on «{}» does not recognise the value «{}» of type «{}».{}".format( name, value, type( value ), details ) )


class SubprocessError( Exception ):
    """
    Raised when the result of calling a subprocess indicates an error.
    """
    pass


def add_details( exception: Exception, **kwargs ) -> None:
    """
    Attaches arbitrary information to an exception.
    
    :param exception:   Exception 
    :param kwargs:      Information to attach
    """
    args = list( exception.args )
    
    message = create_details_message( **kwargs )
    
    if len( args ) > 0 and isinstance( args[0], str ):
        args[0] += message
    else:
        args.append( message )
    
    exception.args = tuple( args )


def create_details_message( **kwargs ):
    from mhelper import string_helper
    
    result = [""]
    
    lk = 1
    lt = 1
    
    for k, v in kwargs.items():
        lk = max( len( str( k ) ), lk )
        lt = max( len( string_helper.type_name( v ) ), lt )
    
    for k, v in kwargs.items():
        result.append( "--> {0} ({1}) = «{2}»".format( str( k ).ljust( lk ), string_helper.type_name( v ).ljust( lt ), v ) )
    
    return "\n".join( result )


def assert_type( name: str, value: T, type_: Type[T], *, info: str = None, err_class: Type[Exception] = TypeError ) -> T:
    """
    Asserts that the value is of the specified type.
    
    :param name:            Name of the value 
    :param value:           The value itself 
    :param type_:           The type the value must be. This can be a list, in which case any of these types is accepted. 
    :param info:            Additional information to append to the error message. 
    :param err_class:       Type of error to raise should an exception occur. 
    :return: 
    """
    from mhelper.reflection_helper import AnnotationInspector
    
    if isinstance( value, type_ ):
        return cast( T, value )
    
    type_name = str( AnnotationInspector( type_ ) )
    
    raise err_class( "«{}» should be of type «{}», but it's not. It is a «{}» with a value of «{}». Extra information = {}" \
                     .format( name,
                              type_name,
                              AnnotationInspector.get_type_name( type( value ) ),
                              value,
                              info ) )


def exception_to_string( ex: BaseException ):
    result = []
    
    while ex:
        result.append( str( ex ) )
        ex = ex.__cause__
    
    return "\n---CAUSED BY---\n".join( result )


def run_subprocess( command: str ) -> None:
    """
    Runs a subprocess, raising `SubprocessError` if the error code is set.
    """
    status = subprocess.call( command, shell = True )
    
    if status:
        raise SubprocessError( "SubprocessError 1. The command «{}» exited with error code «{}». If available, checking the console output may provide more details.".format( command, status ) )


def format_types( type_: TType ) -> str:
    if isinstance( type_, type ):
        return str( type_ )
    else:
        from mhelper import string_helper
        return string_helper.join_ex( type_, delimiter = ", ", last_delimiter = " or ", formatter = "«{}»" )


def assert_instance( name: str, value: object, type_: TType ) -> None:
    if isinstance( type_, type ):
        type_ = (type_,)
    
    if not any( isinstance( value, x ) for x in type_ ):
        raise TypeError( instance_message( name, value, type_ ) )


def assert_type_or_none( name: str, value: Optional[T], type_: Type[T] ) -> T:
    if value is None:
        return cast(T, value)
    
    return assert_type( name, value, type_ )


def instance_message( name: str, value: object, type_: TType ) -> str:
    """
    Creates a suitable message describing a type error.
    :param name:        Name 
    :param value:       Value 
    :param type_:       Expected type 
    :return:            The message
    """
    return "The value of «{}», which is «{}», should be of type «{}», but it's not, it's a «{}».".format( name, value, format_types( type_ ), type( value ) )


def type_error( name: str, value: object, type_: TType, err_class = TypeError ) -> None:
    """
    Raises a `TypeError` with an appropriate message.
    
    :param name:        Name 
    :param value:       Value 
    :param type_:       Expected type
    :param err_class:   Type of error to raise, `TypeError` by default. 
    :except:            TypeError
    """
    raise err_class( instance_message( name, value, type_ ) )


class SimpleTypeError( TypeError ):
    def __init__( self, name: str, value: object, types: TType ):
        super().__init__( instance_message( name, value, types ) )


class LoopDetector:
    """
    Detects infinite loops and manages looping.
    
    Usage
    -----
    
    A normal `while` loop.
    We loop until `spam` is `False`, calling `safe` each iteration.
    
        ```
        safe = LoopDetector( 100 )
        while spam:
            safe()
            ...
        ```
    
    * * * *
    
    Another normal while loop. 
    This time we pass `spam` through `safe` for brevity.
     
        ```
        safe = LoopDetector( 100 )
        while safe( spam ):
            ...
        ```
        
    * * * *
    
    List comprehension.
    We pass our elements through `safe` to ensure our iterator is finite.
    
        ```
        safe = LoopDetector( 100 )
        y = [ safe( x ) for x in z ]
        ```
        
    * * *
    
    Exit-able iterator.
    By using `safe` to encapsulate the loop, we can call `.exit()` to exit the loop.
    This differs from `break` in that we can exit deeper loops.
    
        ```
        safe = LoopDetector( 100 )
        while safe():
            if not spam:
                safe.exit()
        ```
            
    * * *
    
    Persistent iterator.
    This is the converse of the above, only by calling `persist` does the loop continue.
    
        ```
        safe = LoopDetector( 100, invert = True )
        while safe():
            if spam:
                safe.persist()
        ```
    """
    
    
    def __init__( self, limit, info = None, *, invert = False ):
        """
        CONSTRUCTOR
        :param limit:   Limit for loops.
                        This should be set to a value in line with the task. 
        :param info:    Useful information to be displayed should a loop occur.
                        Should have a useful `__str__` representation. 
        """
        self.__limit = limit
        self.__current = 0
        self.__info = info
        self.__invert = invert
        self.check = True
    
    
    def reset( self ):
        """
        Resets the safety counter, allowing this detector to be used again.
        """
        self.__current = 0
    
    
    def persist( self ):
        """
        Sets the continuation parameter to True (keep looping) 
        """
        self.check = True
    
    
    def exit( self ):
        """
        Sets the continuation parameter to False (stop looping) 
        """
        self.check = False
    
    
    def __call__( self, pass_through = NOT_PROVIDED ):
        """
        Increments the counter, causing an error if the counter hits the limit.
        
        This call returns the continuation parameter, :ivar:`check`, which is
        controlled through :func:`keep`, :func:`exit` and :ivar:`__invert`.
        This allows the loop detector to be used as a predicate on loop continuation.
        
        Alternatively, a `pass_through` parameter may be provided, which is returned in lieu
        of the continuation parameter, and allows this function to be called as part
        of a lambda expression or list comprehension.
        """
        self.__current += 1
        
        if self.__current >= self.__limit:
            raise ValueError( "Possible infinite loop detected. Current loop count is {}. If this detection is in error a higher `limit` should be specified, otherwise the infinite loop should be fixed. Further information: {}".format( self.__current, self.__info ) )
        
        if pass_through is NOT_PROVIDED:
            r = self.check
        else:
            r = pass_through
        
        if self.__invert:
            self.check = False
        
        return r


def get_traceback( ex: BaseException = None ):
    r = []
    
    if ex is None:
        ex = sys.exc_info()[1]
    
    exs = []
    while ex is not None:
        exs.append( ex )
        ex = ex.__cause__
    
    for i, ex in enumerate( exs ):
        r.append( __format_traceback( ex.__traceback__, "{}/{}: {}".format( len( exs ) - i - 1, len( exs ), type( ex ).__name__ ), len( exs ) - i ) )
    
    return "\n".join( r )


def __format_traceback( tb, title, prefix ):
    r = []
    
    # The "File "{}", line {}" bit can't change because that's what PyCharm uses to provide clickable hyperlinks.
    
    r.append( "*{} traceback:".format( title ) )
    for index, frame in reversed( list( enumerate( inspect.getouterframes( tb.tb_frame )[1:] ) ) ):  # type:FrameInfo
        r.append( '{}.{}. File "{}", line {}; Function: {}'.format( prefix, -1 - index, frame.filename, frame.lineno, frame.function ) )
        if frame.code_context:
            r.append( "\n".join( frame.code_context ) )
    
    for index, frame in enumerate( inspect.getinnerframes( tb ) ):  # type:FrameInfo
        r.append( '{}.{}. File "{}", line {}; Function: {}'.format( prefix, index, frame.filename, frame.lineno, frame.function ) )
        if frame.code_context:
            r.append( "\n".join( frame.code_context ) )
    
    return "\n".join( r )
