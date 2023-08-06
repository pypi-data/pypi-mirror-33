import inspect
import warnings
from collections import OrderedDict
from typing import List, Optional, Union, Callable, TypeVar, Type, Dict, cast, Tuple, Sized, Iterable, Iterator, GenericMeta, Any, Sequence

from mhelper import string_helper, documentation_helper, exception_helper
from mhelper.special_types import NOT_PROVIDED
from mhelper.exception_helper import SwitchError
from mhelper.generics_helper import MAnnotation, MAnnotationFactory
from mhelper.special_types import MOptional, MUnion


T = TypeVar( "T" )

_TUnion = type( Union[int, str] )

TTristate = Optional[bool]


class AnnotationInspector:
    """
    Class to inspect PEP484 generics.
    """
    
    
    def __init__( self, annotation: object ):
        """
        CONSTRUCTOR
        :param annotation: `type` to inspect 
        """
        if isinstance( annotation, AnnotationInspector ):
            raise TypeError( "Encompassing an `AnnotationInspector` within an `AnnotationInspector` is probably an error." )
        
        self.value = annotation
    
    
    @classmethod
    def get_type_name( cls, type_: type ):
        return str( cls( type_ ) )
    
    
    def __str__( self ) -> str:
        """
        Returns the underlying type string
        """
        if isinstance( self.value, type ):
            result = self.value.__name__
        elif isinstance( self.value, MAnnotation ):
            result = "~" + self.value.factory.name
        elif hasattr( self.value, "__forward_arg__" ):  # from typing._ForwardRef
            result = getattr( self.value, "__forward_arg__" )
        else:
            result = "*" + str( self.value )
        
        if result.startswith( "typing." ):
            result = result[7:]
        
        if self.is_mannotation:
            if isinstance( self.mannotation_arg, list ) or isinstance( self.mannotation_arg, tuple ):
                result += "[" + ", ".join( str( AnnotationInspector( x ) ) for x in self.mannotation_arg ) + "]"
            else:
                result += "[" + str( AnnotationInspector( self.mannotation_arg ) ) + "]"
            
            if self.value.parameters:
                result += "[" + ", ".join( str( AnnotationInspector( x ) ) for x in self.value.parameters ) + "]"
        
        if self.is_generic:
            result += "[" + ", ".join( str( AnnotationInspector( x ) ) for x in self.generic_args ) + "]"
        
        return result
    
    
    @property
    def is_generic( self ):
        """
        Returns if this class is a generic (inherits `GenericMeta`).
        """
        return isinstance( self.value, GenericMeta )
    
    
    @property
    def generic_arg( self ) -> object:
        return self.generic_args[0]
    
    
    @property
    def generic_args( self ) -> Tuple[object, ...]:
        """
        If this class is a generic, returns the arguments.
        """
        if not self.is_generic:
            raise ValueError( "Cannot get `generic_args` because this annotation, «{}» is not a generic.".format( self ) )
        
        return cast( Any, self.value ).__args__
    
    
    @property
    def is_mannotation( self ):
        """
        Is this an instance of `MAnnotation`?
        """
        return isinstance( self.value, MAnnotation )
    
    
    def is_mannotation_of( self, parent: Union[MAnnotation, MAnnotationFactory] ):
        """
        Is this an instance of `MAnnotation`, specifically a `specific_type` derivative?
        """
        if not self.is_mannotation:
            return False
        
        assert isinstance( self.value, MAnnotation )
        
        if isinstance( parent, MAnnotationFactory ):
            return self.value.factory is parent
        elif isinstance( parent, MAnnotation ):
            return self.value.factory is parent.factory
        else:
            raise SwitchError( "parent", parent )
    
    
    @property
    def mannotation( self ) -> MAnnotation:
        """
        Returns the MAnnotation object, if this is an MAnnotation, otherwise raises an error.
        
        :except TypeError: Not an MAnnotation.
        """
        if not self.is_mannotation:
            raise TypeError( "«{}» is not an MAnnotation[T].".format( self ) )
        
        return cast( MAnnotation, self.value )
    
    
    @property
    def mannotation_arg( self ):
        """
        If this is an instance of `MAnnotation`, return the underlying type, otherwise, raise an error.
        """
        if not self.is_mannotation:
            raise TypeError( "«{}» is not an MAnnotation[T].".format( self ) )
        
        assert isinstance( self.value, MAnnotation )
        return self.value.child
    
    
    @property
    def is_generic_list( self ) -> bool:
        """
        Is this a `List[T]`?
        
        (note: this does not include `list` or `List` with no `T`)
        """
        return self.is_generic_u_of_t( List )
    
    
    def is_generic_u_of_t( self, u: type ):
        """
        Is this a generic U[T]?
        """
        return (isinstance( self.value, type )
                and self.is_generic
                and issubclass( cast( type, self.value ), u )
                and self.generic_args)
    
    
    @property
    def is_generic_sequence( self ) -> bool:
        """
        Is this a `Sequence[T]`?
        """
        return self.is_generic_u_of_t( Sequence )
    
    
    @property
    def generic_list_type( self ) -> type:
        """
        Gets the T in List[T]. Otherwise raises `TypeError`.
        """
        if not self.is_generic_list:
            raise TypeError( "«{}» is not a List[T].".format( self ) )
        
        # noinspection PyUnresolvedReferences
        return self.value.__args__[0]
    
    
    @property
    def is_union( self ) -> bool:
        """
        Is this a `Union[T, ...]`?
        Is this a `MUnion[T, ...]`?
        """
        return isinstance( self.value, _TUnion ) or self.is_mannotation_of( MUnion )
    
    
    def is_direct_subclass_of( self, super_class: type ) -> bool:
        """
        Is `self.value` a sub-class of `lower_class`?
        """
        # If BASE and/or DERIVED is not a type then we count only direct equality
        if self.value is super_class:
            return True
        
        if not self.is_type:
            return False
        
        super_inspector = AnnotationInspector( super_class )
        
        if not super_inspector.is_type:
            return False
        
        if super_inspector.is_generic_list:
            super_inspector = AnnotationInspector( list )
        
        if super_inspector.is_union:
            return any( self.is_direct_subclass_of( x ) for x in super_inspector.union_args )
        else:
            try:
                return issubclass( cast( type, self.value ), super_inspector.value )
            except TypeError as ex:
                raise TypeError( "Cannot determine if «{}» is derived from «{}» because `issubclass({}, {})` returned an error.".format( self, super_class, self, super_class ) ) from ex
    
    
    def is_direct_superclass_of( self, sub_class: type ) -> bool:
        """
        Is `lower_class` a sub-class of `self.value`?
        """
        if not self.is_type:
            return False
        
        if self.is_generic_list:
            # Special case for List[T]
            return issubclass( sub_class, list )
        
        try:
            return issubclass( sub_class, cast( type, self.value ) )
        except TypeError as ex:
            raise TypeError( "Cannot determine if «{}» is a base class of «{}» because `issubclass({}, {})` returned an error.".format( self, sub_class, sub_class, self ) ) from ex
    
    
    def is_direct_subclass_of_or_optional( self, super_class: type ):
        """
        Returns if `value_or_optional_value` is a subclass of `upper_class`.
        """
        return AnnotationInspector( self.value_or_optional_value ).is_direct_subclass_of( super_class )
    
    
    def get_direct_subclass( self, super_class: type ) -> Optional[type]:
        """
        This is the same as `is_direct_subclass_of`, but returns the true `type` (`self.value`) if `True`.
        """
        if self.is_direct_subclass_of( super_class ):
            return cast( type, self.value )
    
    
    def get_direct_superclass( self, lower_class: type ) -> Optional[type]:
        """
        This is the same as `is_direct_superclass_of`, but returns the true `type` (`self.value`) if `True`.
        """
        if self.is_direct_superclass_of( lower_class ):
            return cast( type, self.value )
    
    
    def is_indirect_subclass_of( self, super_class: type ) -> bool:
        """
        Is `self.value` a sub-class of `upper_class`, or an annotation enclosing a class that is a sub-class of `upper_class`? 
        """
        return self.get_indirect_subclass( super_class ) is not None
    
    
    def is_indirectly_superclass_of( self, sub_class: type ) -> bool:
        """
        Is `lower_class` a sub-class of `self.value`, or a sub-class of an annotation enclosed within `self.value`?
        """
        return self.get_indirect_superclass( sub_class ) is not None
    
    
    def get_indirect_superclass( self, sub_class: type ) -> Optional[type]:
        """
        This is the same as `is_indirect_subclass_of`, but returns the true `type` that is above `lower_class`.
        """
        return self.__get_indirectly( sub_class, AnnotationInspector.is_direct_superclass_of )
    
    
    def get_indirect_subclass( self, super_class: type ) -> Optional[type]:
        """
        This is the same as `is_indirectly_superclass_of`, but returns the true `type` that iis below `upper_class`.
        """
        return self.__get_indirectly( super_class, AnnotationInspector.is_direct_subclass_of )
    
    
    def __get_indirectly( self, query: type, predicate: "Callable[[AnnotationInspector, type],bool]" ) -> Optional[object]:
        """
        Checks inside all `Unions` and `MAnnotations` until the predicate matches, returning the type (`self.value`) when it does.
        """
        if predicate( self, query ):
            return self.value
        
        if self.is_union:
            for arg in self.union_args:
                arg_type = AnnotationInspector( arg ).__get_indirectly( query, predicate )
                
                if arg_type is not None:
                    return arg_type
        
        if self.is_mannotation:
            annotation_type = AnnotationInspector( self.mannotation_arg ).__get_indirectly( query, predicate )
            
            if annotation_type is not None:
                return annotation_type
        
        return None
    
    
    @property
    def union_args( self ) -> List[type]:
        """
        Returns the list of Union parameters `[...]`.
        """
        if not self.is_union:
            raise TypeError( "«{}» is not a Union[T].".format( self ) )
        
        # noinspection PyUnresolvedReferences
        if self.is_mannotation_of( MUnion ):
            return self.mannotation_arg
        else:
            return cast( _TUnion, self.value ).__args__
    
    
    @property
    def is_optional( self ) -> bool:
        """
        If a `Union[T, U]` where `None` in `T`, `U`.
        """
        if self.is_mannotation_of( MOptional ):
            return True
        
        if not self.is_union:
            return False
        
        if len( self.union_args ) == 2 and type( None ) in self.union_args:
            return True
        
        return False
    
    
    @property
    def is_multi_optional( self ) -> bool:
        """
        If a `Union[...]` with `None` in `...`
        """
        if self.is_mannotation_of( MOptional ):
            return True
        
        if not self.is_union:
            return False
        
        if None in self.union_args:
            return True
        
        return False
    
    
    @property
    def optional_types( self ) -> Optional[List[type]]:
        """
        Returns `...` in a `Union[None, ...]`, otherwise raises `TypeError`.
        """
        if self.is_mannotation_of( MOptional ):
            return [self.mannotation_arg]
        
        if not self.is_union:
            raise TypeError( "«{}» is not a Union[T].".format( self ) )
        
        union_params = self.union_args
        
        if type( None ) not in union_params:
            raise TypeError( "«{}» is not a Union[...] with `None` in `...`.".format( self ) )
        
        union_params = list( self.union_args )
        union_params.remove( type( None ) )
        return union_params
    
    
    @property
    def optional_value( self ) -> Optional[object]:
        """
        Returns `T` in a `Union[T, U]` (i.e. an `Optional[T]`) or `MOptional[T]`.
        Otherwise raises `TypeError`.
        """
        t = self.optional_types
        
        if len( t ) == 1:
            return t[0]
        else:
            raise TypeError( "«{}» is not a Union[T, None] (i.e. an Optional[T]).".format( self ) )
    
    
    @property
    def value_or_optional_value( self ) -> Optional[object]:
        """
        If this is an `Optional[T]` or `MOptional[T]`, returns `T`.
        Otherwise returns `value`.
        """
        if self.is_optional:
            return self.optional_value
        else:
            return self.value
    
    
    @property
    def safe_type( self ) -> Optional[type]:
        """
        If this is a `T`, returns `T`, else returns `None`.
        """
        if self.is_type:
            assert isinstance( self.value, type )
            return self.value
        else:
            return None
    
    
    @property
    def is_type( self ):
        """
        Returns if my `type` is an actual `type`, not an annotation object like `Union`.
        """
        return isinstance( self.value, type )
    
    
    @property
    def name( self ):
        """
        Returns the type name
        """
        if not self.is_type:
            raise TypeError( "«{}» is not a <type>.".format( self ) )
        
        return self.value.__name__
    
    
    def is_viable_instance( self, value ):
        """
        Returns `is_viable_subclass` on the value's type.
        """
        if value is None and self.is_optional:
            return True
        
        return self.is_indirectly_superclass_of( type( value ) )


def as_delegate( x: Union[T, Callable[[], T]], t: Type[T] ) -> Callable[[], T]:
    """
    If `x` is a `t`, returns a lambda returning `x`, otherwise, assumes `x` is already a lambda and returns `x`.
    This is the opposite of `dedelegate`.
    """
    if isinstance( x, t ):
        return (lambda x: lambda: x)( x )
    else:
        return x


def defunction( target: Union[T, Callable[[], T]], cast: Type[T] = object ) -> T:
    """
    If `x` is a function or a method, calls `x` and returns the result.
    Otherwise, returns `x`.
    """
    if inspect.isfunction( target ) or inspect.ismethod( target ):
        r = target()
        if cast is not object:
            exception_helper.assert_type( "defunction.result", r, cast )
        return r
    else:
        return target


def dedelegate( x: Union[T, Callable[[], T]], t: Type[T] ) -> T:
    """
    If `x` is not a `t`, calls `x` and returns the result.
    Otherwise, returns `x`.
    This is the opposite of `as_delegate`.
    """
    if not isinstance( x, t ):
        try:
            x = x()
        except Exception as ex:
            raise ValueError( "Failed to dedelegate the value. The value «{}» is not of the correct type «{}» and it clearly isn't a delegate either.".format( x, t ) ) from ex
    
    return x


def public_dict( d: Dict[str, object] ) -> Dict[str, object]:
    """
    Yields the public key-value pairs.
    """
    r = { }
    
    for k, v in d.items():
        if not k.startswith( "_" ):
            r[k] = v
    
    return r


def find_all( root: object ) -> Dict[int, Tuple[str, str, object]]:
    def __reflect_all( root: object, target: Dict[int, object], name, depth ):
        if id( root ) in target:
            return
        
        short_name = name[-40:]
        
        print( "DEPTH = " + str( depth ) )
        
        print( "ENTER {}".format( short_name ) )
        print( "TYPE = " + type( root ).__name__ )
        
        if type( root ) in (list, dict, tuple):
            print( "LENGTH = " + repr( len( cast( Sized, root ) ) ) )
        else:
            print( "VALUE = " + repr( root ) )
        
        target[id( root )] = type( root ).__name__, name, root
        
        if isinstance( root, dict ):
            print( "ITERATING " + str( repr( len( root ) ) ) + " ITEMS" )
            for i, (k, v) in enumerate( root.items() ):
                print( "START DICT_ITEM {}".format( i ) )
                __reflect_all( v, target, name + "[" + repr( k ) + "]", depth + 1 )
                print( "END DICT_ITEM {}".format( i ) )
        elif isinstance( root, list ) or isinstance( root, tuple ):
            print( "ITERATING " + str( repr( len( root ) ) ) + " ITEMS" )
            for i, v in enumerate( root ):
                print( "START ITEM {}".format( i ) )
                __reflect_all( v, target, name + "[" + repr( i ) + "]", depth + 1 )
                print( "END ITEM {}".format( i ) )
        elif hasattr( root, "__getstate__" ):
            print( "GETTING STATE" )
            print( "START STATE" )
            __reflect_all( root.__getstate__(), target, name + ".__getstate__()", depth + 1 )
            print( "END STATE" )
        elif hasattr( root, "__dict__" ):
            print( "ITERATING DICT OF " + str( repr( len( root.__dict__ ) ) ) + " ITEMS" )
            for i, (k, v) in enumerate( root.__dict__.items() ):
                print( "START DICT_ITEM {}".format( i ) )
                __reflect_all( v, target, name + "." + repr( k ), depth + 1 )
                print( "END DICT_ITEM {}".format( i ) )
        
        print( "EXIT {}".format( short_name ) )
    
    
    target_ = { }
    __reflect_all( root, target_, "root", 0 )
    return target_


def try_get_attr( object_: object, attr_name: str, default = None ):
    if hasattr( object_, attr_name ):
        return getattr( object_, attr_name )
    else:
        return default


def is_list_like( param ):
    return isinstance( param, list ) or isinstance( param, tuple ) or isinstance( param, set ) or isinstance( param, frozenset )


class ICode:
    """
    Interface for code object (for Intellisense only)
    """
    
    
    def __init__( self ):
        self.__class__ = None
        self.__delattr__ = None
        self.__dir__ = None
        self.__doc__ = None
        self.__eq__ = None
        self.__format__ = None
        self.__ge__ = None
        self.__getattribute__ = None
        self.__gt__ = None
        self.__hash__ = None
        self.__init__ = None
        self.__le__ = None
        self.__lt__ = None
        self.__ne__ = None
        self.__new__ = None
        self.__reduce__ = None
        self.__reduce_ex__ = None
        self.__repr__ = None
        self.__setattr__ = None
        self.__sizeof__ = None
        self.__str__ = None
        self.__subclasshook__ = None
        self.co_argcount = None
        self.co_cellvars = None
        self.co_code = None
        self.co_consts = None
        self.co_filename = None
        self.co_firstlineno = None
        self.co_flags = None
        self.co_freevars = None
        self.co_kwonlyargcount = None
        self.co_lnotab = None
        self.co_name = None
        self.co_names = None
        self.co_nlocals = None
        self.co_stacksize = None
        self.co_varnames = None
        raise NotImplementedError( "type hinting only - not intended for construction" )


class IFunctionBase:
    """
    Interface for function object (for Intellisense only)
    """
    
    
    def __init__( self ):
        self.__annotations__ = None
        self.__call__ = None
        self.__class__ = None
        self.__closure__ = None
        self.__code__ = ICode()
        self.__defaults__ = None
        self.__delattr__ = None
        self.__dict__ = None
        self.__dir__ = None
        self.__doc__ = None
        self.__eq__ = None
        self.__format__ = None
        self.__ge__ = None
        self.__get__ = None
        self.__getattribute__ = None
        self.__globals__ = None
        self.__gt__ = None
        self.__hash__ = None
        self.__init__ = None
        self.__kwdefaults__ = None
        self.__le__ = None
        self.__lt__ = None
        self.__module__ = None
        self.__name__ = None
        self.__ne__ = None
        self.__new__ = None
        self.__qualname__ = None
        self.__reduce__ = None
        self.__reduce_ex__ = None
        self.__repr__ = None
        self.__setattr__ = None
        self.__sizeof__ = None
        self.__str__ = None
        self.__subclasshook__ = None
        raise NotImplementedError( "type hinting only - not intended for construction" )
    
    
    def __call__( self, *args, **kwargs ):
        raise NotImplementedError( "type hinting only - not intended for calling" )


IFunction = Union[IFunctionBase, Callable]


class ArgInspector:
    """
    Function argument details
    
    Please see the constructor for attribute descriptions.
    """
    
    
    def __init__( self,
                  name: str,
                  annotation: object,
                  default: Optional[object] = NOT_PROVIDED,
                  description: str = "",
                  is_kwonly: bool = True,
                  index: int = -1 ):
        """
        CONSTRUCTOR
        :param name:                Name of the argument 
        :param annotation:          Annotation of the argument.
                                    May be wrapped in an `AnnotationInspector`, or if not, this will be done.
                                    `None` if the argument is not annotated. 
        :param description:         Description of the argument
                                    `""` if the argument does not appear in the doc-string.
        :param default:             Default value of the argument.
                                    `NOT_PROVIDED` if the argument has no default.
        :param is_kwonly:           `True` if this is a kw-only argument, `False` otherwise. 
        :param index:               Index of the argument within the function's definition.
        """
        if not isinstance( annotation, AnnotationInspector ):
            annotation = AnnotationInspector( annotation )
        
        self.name = name
        self.annotation = annotation
        self.description: str = description or ""
        self.default = default
        self.is_kw_only = is_kwonly
        self.index = index
    
    
    def __repr__( self ):
        return "ArgInspector('{}' : {} = {})".format( self.name, self.annotation, repr( self.default ) )
    
    
    @property
    def type( self ):
        warnings.warn( "Deprecated - use annotation", DeprecationWarning )
        return self.annotation
    
    
    def extract( self, *args, **kwargs ):
        if self.index != -1 and self.index < len( args ):
            return args[self.index]
        
        return kwargs.get( self.name, NOT_PROVIDED )


class ArgCollection:
    def __init__( self ):
        self.__contents = OrderedDict()
        self.__order = []  # because OrderedDict doesn't support indexing.
    
    
    def append( self, item: ArgInspector ):
        self.__contents[item.name] = item
        self.__order.append( item )
    
    
    def __iter__( self ) -> Iterator[ArgInspector]:
        return iter( self.__contents.values() )
    
    
    def __len__( self ):
        return len( self.__contents )
    
    
    def by_name( self, name ) -> ArgInspector:
        return self.__contents[name]
    
    
    def by_index( self, index ) -> ArgInspector:
        return self.__order[index]
    
    
    def __getitem__( self, item ):
        if isinstance( item, int ):
            return self.by_index( item )
        elif isinstance( item, str ):
            return self.by_name( item )
        else:
            raise SwitchError( "item", item, instance = True )


class FunctionInspector:
    """
    Class for inspecting a function.
    
    :ivar function:     Absolute function object, an `IFunction`
    :ivar name:         Name of the function
    :ivar args:         Arguments, as an `ArgCollection` object, which can retrieve arguments by name or index. 
    :ivar description:  Function doc-string.
    """
    
    
    def __init__( self, fn: IFunction ):
        self.function: IFunction = fn
        self.name: str = fn.__name__
        self.args = ArgCollection()
        
        # arg_names = inspect.getargs(fn).args
        
        arg_names = fn.__code__.co_varnames[:fn.__code__.co_argcount + fn.__code__.co_kwonlyargcount]
        
        arg_types = { }
        
        self.return_type = None
        
        for k, v in fn.__annotations__.items():
            if k != "return":
                arg_types[k] = v
            else:
                self.return_type = v
        
        doc = fn.__doc__  # type:str
        
        arg_descriptions = extract_documentation( doc, "param", False )
        
        arg_defaults = { }
        has_args = (fn.__code__.co_flags & 0x4) == 0x4
        has_kwargs = (fn.__code__.co_flags & 0x8) == 0x8
        
        if fn.__defaults__:
            num_defaults = len( fn.__defaults__ )
            default_offset = len( arg_names ) - num_defaults
            
            if has_args:
                default_offset -= 1
            
            if has_kwargs:
                default_offset -= 1
            
            for i, v in enumerate( fn.__defaults__ ):
                name = arg_names[default_offset + i]
                arg_defaults[name] = v
        
        for index, arg_name in enumerate( arg_names ):
            arg_desc_list = arg_descriptions.get( arg_name, None )
            arg_desc = "\n".join( arg_desc_list ) if arg_desc_list else ""
            arg_desc = string_helper.fix_indents( arg_desc )
            arg_type = arg_types.get( arg_name, None )
            arg_default = arg_defaults.get( arg_name, NOT_PROVIDED )
            
            if arg_type is None and arg_default is not NOT_PROVIDED and arg_default is not None:
                arg_type = type( arg_default )
            
            self.args.append( ArgInspector( arg_name,
                                            AnnotationInspector( arg_type ),
                                            arg_default,
                                            arg_desc,
                                            index >= fn.__code__.co_argcount,
                                            index ) )
        
        fn_desc = "\n".join( arg_descriptions[""] )
        fn_desc = string_helper.fix_indents( fn_desc )
        
        self.description: str = fn_desc
    
    
    def __str__( self ):
        return str( self.function )
    
    
    def call( self, *args, **kwargs ):
        """
        Calls the function.
        """
        # noinspection PyCallingNonCallable
        return self.function( *args, **kwargs )


# noinspection PyDeprecation
def extract_documentation( *args, **kwargs ) -> Union[Dict[str, str], Dict[str, List[str]]]:
    warnings.warn( "Deprecated - use documentation_helper", DeprecationWarning )
    return documentation_helper.extract_documentation( *args, **kwargs )


class ArgsKwargs:
    EMPTY: "ArgsKwargs" = None
    
    
    def __init__( self, *args, **kwargs ) -> None:
        self.args = args
        self.kwargs = kwargs
    
    
    def __bool__( self ):
        return bool( self.args ) or bool( self.kwargs )
    
    
    def __getitem__( self, item ):
        r = self.get( item[0], item[1] )
        
        if isinstance( r, NOT_PROVIDED ):
            raise KeyError( item )
        
        return r
    
    
    def get( self, index, name, default = NOT_PROVIDED ):
        if 0 <= index < len( self.args ):
            return self.args[index]
        
        if name:
            return self.kwargs.get( name, default )
        
        return default
    
    
    def __repr__( self ):
        r = []
        
        for x in self.args:
            r.append( "{}".format( x ) )
        
        for k, x in self.kwargs.items():
            r.append( "{} = {}".format( k, x ) )
        
        return ", ".join( r )


ArgsKwargs.EMPTY = ArgsKwargs()


class _ArgValue:
    def __init__( self, arg: ArgInspector, value: object ):
        self.arg = arg
        self.__value = value
    
    
    @property
    def value( self ) -> object:
        return self.__value
    
    
    @value.setter
    def value( self, value: object ):
        if not self.arg.annotation.is_viable_instance( value ):
            msg = "Trying to set the value «{}» on the argument «{}» but the value is of type «{}» and the argument takes «{}»."
            raise TypeError( msg.format( value, self.arg.name, type( value ), self.arg.annotation ) )
        
        self.__value = value
    
    
    def __repr__( self ):
        return "{}({} = {})".format( type( self ).__name__, self.arg, repr( self.__value ) )


class ArgValueCollection:
    """
    Manages a set of arguments and their values.
    """
    
    
    def __init__( self, args: Iterable[ArgInspector] = (), provided: ArgsKwargs = None ):
        """
        CONSTRUCTOR
        :param provided:    Values to apply to the arguments
        """
        self.__values: Dict[str, _ArgValue] = OrderedDict()
        
        for arg in args:
            exception_helper.assert_type( "arg", arg, ArgInspector )
            self.__values[arg.name] = _ArgValue( arg, arg.default )
        
        if provided:
            self.from_argskwargs( provided )
    
    
    def __getstate__( self ):
        raise ValueError( "Pickling `ArgValueCollection` is probably an error. Did you mean to pickle the arguments instead?" )
    
    
    def __repr__( self ):
        return str( self.__values )
    
    
    def append( self, arg: ArgInspector, value: object = NOT_PROVIDED ):
        v = _ArgValue( arg, arg.default )
        self.__values[arg.name] = v
        
        if value is not NOT_PROVIDED:
            v.value = v
    
    
    def tokwargs( self ) -> Dict[str, object]:
        """
        Converts the arguments to kwargs that can be passed to a method.
        Only the arguments of type `HFunctionParameterType[T]` are passed through, where T indicates the type passed to the function.
        
        Note: Since all `AbstractCommand` arguments must be named and `AbstractCommand`s do not currently support variadic arguments, there is no equivalent `toargs`.
        """
        result = { }
        
        for arg in self.__values.values():
            if arg.value is not NOT_PROVIDED:
                result[arg.arg.name] = arg.value
        
        return result
    
    
    def to_argskwargs( self ) -> ArgsKwargs:
        return ArgsKwargs( **self.tokwargs() )
    
    
    def from_argskwargs( self, provided: ArgsKwargs ):
        assert isinstance( provided, ArgsKwargs )
        
        if len( provided.args ) > len( self.__values ):
            raise ValueError( "Attempt to specify {} values but this function takes {}.".format( len( provided.args ), len( self.__values ) ) )
        
        for arg, value in zip( self.__values.values(), provided.args ):
            arg.value = value
        
        for key, value in provided.kwargs.items():
            try:
                self.__values[key].value = value
            except KeyError as ex:
                raise KeyError( "There is no argument named «{}».".format( key ) ) from ex
    
    
    def __len__( self ):
        return len( self.__values )
    
    
    def __iter__( self ) -> Iterator[ArgInspector]:
        return iter( x.arg for x in self.__values.values() )
    
    
    def items( self ) -> Iterable[Tuple[ArgInspector, object]]:
        for name, value in self.__values.items():
            yield self.get_arg( name ), value.value
    
    
    def __get_argvalue( self, key: Union[ArgInspector, str] ) -> _ArgValue:
        if isinstance( key, ArgInspector ):
            key = key.name
        
        return self.__values[key]
    
    
    def get_value( self, key: Union[ArgInspector, str] ) -> Optional[object]:
        """
        Equivalent to `get_arg`, but returns the value on the `PluginArgValue`.
        """
        return self.__get_argvalue( key ).value
    
    
    def set_value( self, key: Union[ArgInspector, str], value: Optional[object] ) -> None:
        """
        Sets the value of the argument with the specified key.
        See `PluginArgValue.set_value` for details on accepted values.

        :param key:     A `PluginArg`. Unlike `get` a name is not accepted.
        :param value:   The value to apply.
        """
        self.__get_argvalue( key ).value = value
    
    
    def get_arg( self, key: Union[ArgInspector, str] ) -> "ArgInspector":
        """
        Retrieves the `ArgInspector` from the specified argument name.
        
        :param key: Argument name, or an `ArgInspector` to get the name from.
        :except KeyError:  If the argument does not exist
        :except TypeError: If the argument is not a `ArgInspector` or `str`.
        """
        return self.__get_argvalue( key ).arg
    
    
    def get_incomplete( self ) -> List[str]:
        """
        Returns the set of arguments that require a value to be set before run() is called
        """
        return [x.arg.name for x in self.__values.values() if x.value is NOT_PROVIDED]


HNotFunctionParameterType = MAnnotationFactory( "HNotFunctionParameterType" )

DPredicate = Callable[[object], bool]


def iter_all( obj: object, predicate: DPredicate = None, private: bool = False ) -> Iterator[Tuple[str, object]]:
    for name in dir( obj ):
        if name.startswith( "_" ) and not name.endswith( "__" ) and not private:
            continue
        
        value = getattr( obj, name )
        
        if predicate is not None and not predicate( value ):
            continue
        
        yield name, value


def iter_hierarchy( type_: type ):
    """
    Iterates DOWN the hierarchy, starting with the MOST DERIVED class.
    """
    queue: List[Type] = []
    queue.append( type_ )
    
    while queue:
        type_ = queue.pop( 0 )
        yield type_
        queue.extend( type_.__bases__ )


def list_hierarchy( x ):
    return list( iter_hierarchy( x ) )
