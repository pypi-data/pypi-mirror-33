"""
Helper functions for reading and writing.
"""
import os
import sys
import platform
import tempfile
import warnings
from typing import Dict, Optional, TextIO, Type, TypeVar, Union, cast, BinaryIO, List

from mhelper import file_helper
from mhelper.comment_helper import abstract, override, virtual
from mhelper.special_types import NOT_PROVIDED
from mhelper.exception_helper import SwitchError


T = TypeVar( "T" )


def load_npy( file_name ):
    """
    Loads an NPY file. If it is an NPZ this extracts the `data` value automatically.
    Requires the :library:`numpy`.
    """
    # noinspection PyPackageRequirements
    import numpy
    result = numpy.load( file_name, allow_pickle = False, fix_imports = False )
    
    if file_name.upper().endswith( ".NPZ" ):
        result = result["data"]
    
    return result


def load_npz( file_name ):
    """
    Loads an NPZ file and returns the `data` value.
    Requires the :library:`numpy`.
    """
    
    # noinspection PyPackageRequirements
    import numpy
    result = numpy.load( file_name, allow_pickle = False, fix_imports = False )
    result = result["data"]
    
    return result


def save_bitarray( file_name: str, value ) -> None:
    """
    Saves a bit array.
    Requires the :library:`bitarray`.
    
    :type value: bitarray
    
    :param file_name: File name
    :param value: Value to save
    """
    # noinspection PyPackageRequirements
    from bitarray import bitarray
    from mhelper.exception_helper import SubprocessError
    from mhelper import exception_helper, file_helper
    
    exception_helper.assert_instance( "save_bitarray::value", value, bitarray )
    assert isinstance( value, bitarray )
    
    try:
        with open( file_name, "wb" ) as file_out:
            value.tofile( file_out )
    except TypeError:
        # Stupid "open file expected" error on OSX (due to bug writing large files - fallback to manual implementation)
        _save_bytes_manually( file_name, value.tobytes() )
    except Exception as ex:
        raise SubprocessError( "Failed to write bitarray of length {} to «{}».".format( len( value ), file_name ) ) from ex
    
    size = float( file_helper.file_size( file_name ) )
    expected = len( value )
    
    if size < expected / 8.0:
        raise ValueError( "Saved file is shorter ({} bytes or {} bits) than the originating bitarray ({} bytes or {} bits).".format( size, size * 8, expected / 8, expected ) )


def _save_bytes_manually( file_name: str, value: bytes ):
    """
    Fallback function used by :func:`save_bitarray`.
    """
    warnings.warn( "Save bitarray failed. This is probably due to an error in your `bitarray` library. The file will be saved incrementally but this will take longer.", UserWarning )
    BATCH_SIZE = 100000
    cursor = 0
    length = len( value )
    
    with open( file_name, "wb" ) as file_out:  # note that writing large arrays on OSX is probably the problem, we can't just dump the bytes
        while cursor < length:
            next = min( cursor + BATCH_SIZE, length )
            slice = value[cursor:next]
            file_out.write( slice )
            cursor = next


def _read_bytes_manually( file_name: str ) -> bytes:
    BATCH_SIZE = 100000
    b = bytearray()
    
    with open( file_name, "rb" ) as file_in:
        while True:
            buf = file_in.read( BATCH_SIZE )
            
            if len( buf ) == 0:
                break
            
            b.extend( buf )
    
    return bytes( b )


def load_bitarray( file_name: str ):
    """
    Loads a bitarray
    :param file_name: File to read 
    :return: bitarray. Note this may be padded with missing bits. 
    """
    # noinspection PyPackageRequirements
    from bitarray import bitarray
    
    result = bitarray()
    
    try:
        with open( file_name, 'rb' ) as file_in:
            result.fromfile( file_in )
    except SystemError:  # OSX error
        result = bitarray()
        result.frombytes( _read_bytes_manually( file_name ) )
        assert len( result ) != 0
    
    return result


def save_npy( file_name, value ):
    # noinspection PyPackageRequirements
    import numpy
    
    numpy.save( file_name, value, allow_pickle = False, fix_imports = False )


def save_npz( file_name, value ):
    # noinspection PyPackageRequirements
    import numpy
    
    numpy.savez_compressed( file_name, data = value )


def load_binary( file_name: str, *, type_: Optional[Type[T]] = None, default: T = NOT_PROVIDED ) -> T:
    """
    Loads a binary file
    
    :param file_name:   Filename to load  
    :param type_:        Type to expect (if not specified no check is performed)
    :param default:     Value to return on failure (if not specified causes an error) 
    :return: Loaded file, or `default` (if specified) 
    """
    
    try:
        import pickle
        
        with open( file_name, "rb" ) as file:
            result = pickle.load( file, fix_imports = False )
            
            if type_ is not None and type( result ) is not type_:
                raise ValueError( "Deserialised object from file «{}» was expected to be of type «{}» but it's not, its of type «{}» with a value of «{}».".format( file_name, type_, type( result ), result ) )
            
            return result
    except Exception:
        if default is NOT_PROVIDED:
            raise
        
        return default
    except BaseException as ex:
        warnings.warn( "Loading the binary file «{}» caused a (critical) «{}» exception.".format( file_name, type( ex ).__name__ ), UserWarning )
        raise


def save_binary( file_name: Optional[str], value ) -> Optional[bytes]:
    import pickle
    
    if file_name is None:
        try:
            return pickle.dumps( value, fix_imports = False )
        except Exception as ex:
            raise IOError( "Error saving data to bytes. Data = «{}».".format( value ) ) from ex
    
    with open( file_name, "wb" ) as file:
        try:
            pickle.dump( value, file, fix_imports = False )
        except Exception as ex:
            raise IOError( "Error saving data to binary file. Filename = «{}». Data = «{}».".format( file_name, value ) ) from ex
    
    return None


def load_json( file_name, keys = True ):
    from mhelper.file_helper import read_all_text
    import jsonpickle
    
    text = read_all_text( file_name )
    
    return jsonpickle.decode( text, keys = keys )


def save_json( file_name, value, keys = True ):
    from mhelper.file_helper import write_all_text
    import jsonpickle
    
    write_all_text( file_name, jsonpickle.encode( value, keys = keys ) )


def default_values( target: T, default: Optional[Union[T, type]] = None ) -> T:
    if default is None:
        if target is None:
            raise ValueError( "Cannot set the defaults for the value because both the value and the defaults are `None`, so neither can be inferred." )
        
        default = type( target )
    
    if isinstance( default, type ):
        default = default()
    
    if target is None:
        return default
    
    if isinstance( target, list ):
        return cast( T, target )
    
    if type( target ) is not type( default ):
        raise ValueError( "Attempting to set the defaults for the value «{}», of type «{}», but the value provided, «{}», of type «{}», is not compatible with this.".format( target, type( target ), default, type( default ) ) )
    
    for k, v in default.__dict__.items():
        if k.startswith( "_" ):
            continue
        
        if k not in target.__dict__:
            target.__dict__[k] = v
    
    to_delete = []
    
    for k in target.__dict__.keys():
        if k not in default.__dict__:
            to_delete.append( k )
    
    for k in to_delete:
        del target.__dict__[k]
    
    return target


TBStr = Union[str, bytes]


@abstract
class WriterBase:
    """
    Base class for writers.
    
    The derived class should implement:
        * (optional) A constructor
        * (optional) on_close
        * (optional) write
        * on_describe
        
    :ivar extension: Extension of the file.
    :ivar closed:    `True` once the file has been closed.
    """
    
    
    def __init__( self, *, extension = None, mode = str ):
        """
        CONSTRUCTOR
        The derived class should pass any and all `**kwargs` to the base class.
        Other `**kwargs` may be added later.
        `*args` are not used and may be passed or not.
        :param extension: Extension of the file
        """
        self.extension = extension
        self.type = mode
        self.closed = False
    
    
    def __enter__( self ):
        return self
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        self.close()
    
    
    def close( self ) -> None:
        if self.closed:
            return
        
        self.on_close()
        
        self.closed = True
    
    
    def write( self, text: TBStr ) -> None:
        self.on_write( text )
    
    
    @virtual
    def on_close( self ):
        pass
    
    
    @virtual
    def on_write( self, text: TBStr ) -> None:
        pass


@abstract
class BufferedWriter( WriterBase ):
    """
    Buffers all the output data to `self.lines` (currently just in memory).
    
    The derived class should commit the data when `on_close` is called.
    """
    
    
    def __init__( self, *args, **kwargs ) -> None:
        super().__init__( *args, **kwargs )
        self.lines: List[TBStr] = []
    
    
    @override
    def on_write( self, text: TBStr ) -> None:
        if self.closed:
            raise ValueError( "Virtual stream has already been closed." )
        
        self.lines.append( text )
    
    
    def __repr__( self ):
        return self.__class__.__name__
    
    
    def set_extension( self, value: TBStr ) -> None:
        pass


class StdOutWriter( BufferedWriter ):
    """
    Dumps all the data to std-out when the stream is closed.
    
    Note only string data is written. Binary data is ignored.
    """
    
    
    def on_close( self ):
        if self.type is str:
            for line in self.lines:
                sys.stdout.write( line )
        else:
            warnings.warn( "The output contains {} bytes of binary data, cannot be shown in StdOut.".format( sum( len( x ) for x in self.lines ), UserWarning ) )


class OpeningWriter( WriterBase ):
    """
    Dumps all the data to a temporary file when the stream is closed.
    Then opens the stream in the default GUI.
    The file is queued for delete when the program closes.
    """
    
    
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        
        if self.type is bytes:
            mode = "wb"
        else:
            mode = "w"
        
        self.file = tempfile.NamedTemporaryFile( mode, delete = False, suffix = self.extension )
        self.name = self.file.name
        queue_delete( self.name )
    
    
    def on_write( self, text: str ):
        self.file.write( text )
    
    
    def on_close( self ):
        self.file.close()
        system_open( self.name )


class MemoryWriter( BufferedWriter ):
    """
    Writes to RAM.
    * For programmatic use only.
    * Data can be retrieved via :method:`mhelper.io_helper.MemoryWriter.retrieve`
    * Does not support multiple threads.
    """
    __LAST = None
    
    
    @classmethod
    def retrieve( cls ):
        if cls.__LAST is None:
            raise ValueError( "Nothing to retrieve." )
        
        r = "\n".join( cls.__LAST )
        cls.__LAST = None
        return r
    
    
    def on_close( self ):
        type( self ).__LAST = self.lines


class ClipboardWriter( BufferedWriter ):
    """
    Dumps all the data to the clipboard when the stream is closed.
    """
    
    
    def on_close( self ):
        import pyperclip
        
        if self.type is str:
            pyperclip.copy( "\n".join( self.lines ) )
        else:
            pyperclip.copy( b"".join( self.lines ) )


class NowhereWriter( WriterBase ):
    """
    Doesn't write anything.
    """
    pass


open_write_opts = { "stdout": StdOutWriter,
                    "clip"  : ClipboardWriter,
                    "null"  : NowhereWriter,
                    "open"  : OpeningWriter,
                    "memory": MemoryWriter }


def open_write( file_name: str, extension: str = "", mode: type = str ) -> Union[WriterBase, TextIO, BinaryIO]:
    """
    Opens a file for writing, accepts any of the special values in the global :variable:`open_write_opts: as the filename.
    
    :param file_name:   Name of the file. If this is `None` it is converted to `""`. This allows a default value to be added
                        to :variable:`open_write_opts`.
    :param extension:   Extension (file-type) of the file. Used by some special handlers.
    :param mode:        Mode of operation.
                        `str` and `bytes` are handled by the all default options, except `stdout`, which handles `str`,
                        and shows a warning for `bytes`.
    :return:            A file object or a file-like object (:class:`WriterBase`), which should have the following methods:
                            * write
                            * __enter__, __exit__, close
    """
    if file_name is None:
        file_name_lower = ""
    else:
        file_name_lower = file_name.lower()
    
    mapped: Type[BufferedWriter] = open_write_opts.get( file_name_lower )
    
    if mapped is not None:
        return mapped( extension = extension, mode = mode )
    
    file_name = os.path.abspath( file_name )
    directory_name = file_helper.get_directory( file_name )
    assert directory_name, file_name
    file_helper.create_directory( directory_name )
    
    if mode is str:
        return open( file_name, "w" )
    elif mode is bytes:
        return open( file_name, "wb" )
    else:
        raise SwitchError( "type_", mode )


def load_ini( file_name: str, comments: str = (";", "#", "//") ) -> Dict[str, Dict[str, str]]:
    """
    Loads an INI file.
    
    :param file_name:       File to load 
    :param comments:        Comment lines 
    :return:                INI data:
                                str - Section name ("" contains the data from any untitled section and sections with no name `[]`)
                                dict - Section data:
                                    str - Field key
                                    str - field value
    """
    r = { }
    dd = { }
    d = dd
    
    for line in open( file_name, "r" ):
        line = line.strip()
        
        if any( line.startswith( x ) for x in comments ):
            continue
        
        if line.startswith( "[" ) and line.endswith( "]" ):
            d = { }
            r[line[1:-1]] = d
        elif "=" in line:
            k, v = line.split( "=", 1 )
            d[k.strip()] = v.strip()
    
    if dd:
        if "" in r:
            dd.update( r[""] )
        
        r[""] = dd
    
    return r


class queue_delete:
    """
    The file will be deleted when the program closes.
    
    :remarks:           Class masquerading as function.
                        
                        Example usage:
                            ```
                            queue_delete( "c:\my_temporary_file.txt" )
                            ```    
    
    :cvar queued:       Gets the list of files to be deleted.
                        Acts to keep the references alive until the program closes.
    :ivar file_name:    Name of the file
    """
    
    queued = []
    
    
    def __init__( self, file_name: str ) -> None:
        """
        CONSTRUCTOR
        Automatically adds the reference to the queue, keeping it alive
        until the program closes.
        
        :param file_name: Name of the file
        """
        self.file_name = file_name
        self.queued.append( self )
    
    
    def __del__( self ) -> None:
        """
        OVERRIDE
        On deletion, removes the file.
        """
        os.remove( self.file_name )


class ESystem:
    UNKNOWN = 0
    WINDOWS = 1
    MAC = 2
    LINUX = 3


def get_system():
    s = platform.system()
    if s == "Windows":
        return ESystem.WINDOWS
    elif s == "Darwin":
        return ESystem.MAC
    elif s == "Linux":
        return ESystem.LINUX
    else:
        return ESystem.UNKNOWN


def system_open( file_name: str ):
    """
    Opens the file with the default editor.
    (Only works on Windows, Mac and GUI Linuxes)
    """
    s = platform.system()
    if s == "Windows":
        os.system( file_name )
    elif s == "Darwin":
        os.system( "open \"" + file_name + "\"" )
    elif s == "Linux":
        os.system( "xdg-open \"" + file_name + "\"" )
    else:
        warnings.warn( "I don't know how to open files with the default editor on your platform '{}'.".format( s ) )


def system_select( file_name: str ):
    """
    Selects the file with the default file explorer.
    (Only works on Windows, Mac and GUI Linuxes)
    """
    s = platform.system()
    if s == "Windows":
        os.system( "explorer.exe /select,\"{}\"".format( file_name ) )
    elif s == "Darwin":
        os.system( "open -R \"{}\"".format( file_name ) )
    elif s == "Linux":
        # Just open the parent directory on Linux
        file_name = os.path.split( file_name )[0]
        os.system( "xdg-open \"{}\"".format( file_name ) )
    else:
        warnings.warn( "I don't know how to open files with the default editor on your platform '{}'.".format( s ) )
