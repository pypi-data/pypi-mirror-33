"""
Module for dealing with coercing values to strings.
See `readme.md` in the project root for details.
"""

from enum import Enum
from traceback import format_exc
from typing import List, Optional, Sequence, Tuple, Type, cast, Iterable, Iterator, Union

import itertools

import mhelper as mh
from mhelper import AnnotationInspector


class CoercionInfo:
    """
    :ivar collection:           Calling coercer collection
    :ivar annotation:           An `AnnotationInspector`, providing information on the intended format to coerce into.
    :ivar source:               Value to translate from. Undefined during queries inside the `can_handle` function.
    :ivar _cancelled:           Setting this to `True` prevents further `AbstractCoercer`s trying to covert this value to this annotation (other annotations may still proceed).
    """
    
    
    def __init__( self,
                  annotation: mh.AnnotationInspector,
                  collection: Optional["CoercerCollection"],
                  source: Optional[str] ):
        """
        CONSTRUCTOR
        See class comments for parameters.
        """
        self.collection = collection
        self.annotation = annotation
        self.source = source
        self._cancelled = False
    
    
    def __str__( self ):
        return "Coerce «{}» into {}".format( self.source, self.annotation )


class CoercionError( Exception ):
    """
    Raised when an individual AbstractCoercer fails, and also when all coercers have failed.
    """
    
    
    def __init__( self, message: str, cancel: bool = False ):
        super().__init__( message )
        self.cancel = cancel


@mh.abstract
class AbstractCoercer:
    """
    Coercer base class.
    
    The abstract methods must be overridden.
    Additionally derived classes should provide a doc string detailing the format the coercer handles.
    """
    
    
    class PRIORITY:
        """
        Priorities namespace.
        
        :cvar _NONE:       AbstractCoercer is unused. Equivalent to `None` and `False`.
        :cvar _HIGHEST:    Highest valid priority (lowest value).
        :cvar _LOWEST:     Lowest expected (highest value).
        :cvar HIGH:        A priority above the default
        :cvar DEFAULT:     The default recommended priority for user coercers. Equivalent to `True`.
        :cvar INBUILT:     The priority used by the inbuilt coercers, which is lower than DEFAULT.
        :cvar FALLBACK:    The priority used by the fallback coercer. No priority should be lower.
        """
        _NONE = 0
        _HIGHEST = 1
        SKIP = 0
        HIGH = 25
        DEFAULT = 50
        INBUILT = 75
        LOW = 75
        FALLBACK = 100
        _LOWEST = 100
    
    
    def coerce( self, info: CoercionInfo ) -> Optional[object]:
        """
        Asks the coercer to perform the actual coercion.
        This should only be called if ``get_priority` returns non-zero.
        :param info:                Information about the coercion to perform. 
        :return:                    Result of the coercion.
        :except CoercionError:      This error will be raised if the coercion cannot be performed.
        """
        return self.on_coerce( info )
    
    
    def can_handle( self, info: CoercionInfo ) -> bool:
        """
        Determines if the coercer can handle this coercion.
        """
        return self.on_can_handle( info )
    
    
    def get_priority( self, _: CoercionInfo ) -> int:
        """
        Returns an `int` above 1 denoting the priority of this coercer in relation to the others.
        """
        return self.on_get_priority()
    
    
    def get_archetype( self ) -> Optional[type]:
        """
        Returns a type associated with this coercer.
        May return `None` if this doesn't make sense.
        """
        return self.on_get_archetype()
    
    
    def __str__( self ):
        t = self.get_archetype()
        
        if t is None:
            return type( self ).__name__
        
        return str( AnnotationInspector( t ) )
    
    
    @mh.virtual
    def on_get_priority( self ) -> int:
        """
        The derived class should return the priority of the coercion.
        """
        return self.PRIORITY.DEFAULT
    
    
    @mh.virtual
    def on_can_handle( self, info: CoercionInfo ) -> bool:
        """
        The derived class should return if it is able to handle the conversion.
        The default implementation returns if `info.annotation` is a subclass of `on_get_archetype`.
        """
        t = self.get_archetype()
        
        if t is None:
            return False
        
        return info.annotation.is_direct_subclass_of( t )
    
    
    @mh.abstract
    def on_get_archetype( self ) -> type:
        """
        Returns a type associated with this coercer.
        Use by the `__str__`.
        """
        raise NotImplementedError( "abstract" )
    
    
    @mh.abstract
    def on_coerce( self, info: CoercionInfo ) -> Optional[object]:
        """
        The derived class should implement the coercion behaviour as described in `coerce`.
        :except CoercionError:  This error should be raised if the coercion cannot be performed.
                                The next coercer in the queue will then be attempted unless the error has the `cancel` flag set.
                                Other error types should not be returned as they will be considered a logic, rather than input,
                                error.
        """
        raise NotImplementedError( "abstract" )


class _Coercion:
    def __init__( self, priority, info, coercer ):
        self.priority = priority
        self.info = info
        self.coercer = coercer
    
    
    def __str__( self ):
        return mh.ansi.FORE_CYAN + str( self.coercer ) + mh.ansi.FORE_RESET + "(" + mh.ansi.FORE_MAGENTA + str( self.info.annotation if self.info else "" ) + mh.ansi.FORE_RESET + ")"


class CoercerCollection:
    """
    Collection of coercers.
    Use `register` to register the coercers and `coerce` to coerce strings to values.
    See also `get_default_coercer`.
    
    :ivar __coercers:       The collection of coercers.
    :ivar __debug_depth:    The coercer stack, used for debugging.
    :ivar debug:            Set this to `True` to print status messages from each coercion by default.
    :ivar debug_prefix:     Prefix accepted by `coerce`. If `None` or empty then this feature is not available.
    :ivar eval_prefix:      Prefix accepted by `coerce`. If `None` or empty then this feature is not available.
    :ivar ctor_prefix:      Prefix accepted by `coerce`. If `None` or empty then this feature is not available.
    """
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        """
        self.debug_prefix = "coerce::"
        self.eval_prefix = "eval::"
        self.ctor_prefix = "ctor::"
        self.__coercers: List[AbstractCoercer] = []
        self.__debug_depth: List[_Coercion] = []
        self.debug = False
    
    
    def __iter__( self ) -> Iterator[AbstractCoercer]:
        """
        Iterates over the registered coercers.
        """
        return iter( self.__coercers )
    
    
    def __len__( self ) -> int:
        """
        Returns the number of registered coercers.
        """
        return len( self.__coercers )
    
    
    def get_descriptive_text( self ):
        r = []
        
        r.append( "stringcoercion library - accepted formats" )
        r.append( "=========================================" )
        
        for coercer in self:
            r.append( "" )
            r.append( "" )
            assert isinstance( coercer, AbstractCoercer )
            doc = mh.get_basic_documentation( coercer ) or "(not documented)"
            name = str( coercer )
            r.append( name )
            r.append( "-" * len( name ) )
            r.append( "" )
            r.append( doc )
        
        return "\n".join( r )
    
    
    def register( self, *args: AbstractCoercer ):
        """
        Registers a new coercer or coercers.
        
        :param args:    AbstractCoercer(s) to register
        """
        for arg in args:
            self.__coercers.append( arg )
    
    
    def __str__( self ):
        return "CoercerCollection with «{}» registered coercers: {}.".format( len( self.__coercers ), ", ".join( "«{}»".format( x ) for x in self.__coercers ) )
    
    
    def coerce( self, types: object, value: str ) -> object:
        """
        Tries all registered coercers to coerce the string into the specified type(s).
        
        :param types:           An acceptable type, sequence of types, annotation, or sequence of
                                annotations.
                                * Annotations can be any arbitrary objects that at least one
                                  registered `AbstractCoercer` is able to understand, they do
                                  _not_ need to be concrete `type`s. For instance `Union` is a
                                  suitable annotation.
                                * If a sequence (list or tuple) of is provided, coercion to _any_
                                  of the provided types will be attempted.
                                * The exact types and/or annotations accepted depend on which
                                  coercers have been registered.
                                 
        :param value:           Source text to coerce.
                                This has different meanings to different coercers.
                                This text may be prefixed with `debug_prefix`, `eval_prefix` or
                                `ctor_prefix` to enable debugging, force use of the `eval`
                                statement or force use of the constructor respectively.
                                
        :return:                A value of one of the types in `types`.
        
        :except CoercionError:  Coercion failed. 
        """
        orig_debug = None
        types: Sequence[type] = mh.array_helper.as_sequence( types )
        
        if self.debug_prefix and value.startswith( self.debug_prefix ):
            # DEBUG PREFIX - ENABLE DEBUGGING
            value = value[len( self.debug_prefix ):]
            orig_debug = self.debug
            self.debug = True
        elif self.eval_prefix and value.startswith( self.eval_prefix ):
            # EVAL PREFIX - EXECUTE PYTHON SCRIPT
            value = value[len( self.eval_prefix ):]
            value = eval( value )
            if not mh.AnnotationInspector( Union[types] ).is_viable_instance( value ):
                mh.exception_helper.type_error( "value", value, Union[types], err_class = CoercionError )
            return value
        elif self.ctor_prefix and value.startswith( self.ctor_prefix ):
            # CTOR PREFIX - EXECUTE CONSTRUCTOR
            value = value[len( self.ctor_prefix ):]
            try:
                value = types[0]( value )
            except Exception as ex:
                raise CoercionError( "Failed to construct «{}» from «{}».".format( mh.AnnotationInspector.get_type_name( types[0] ), value ) ) from ex
            
            return value
        
        handlers: List[_Coercion] = []
        
        prefix = mh.ansi.FORE_RED + "𝑪𝑶𝑬𝑹𝑪𝑬 " + mh.ansi.FORE_RESET
        
        if self.debug:
            i = 0
            
            for i, j in enumerate( itertools.chain( [_Coercion( None, None, None )], self.__debug_depth ) ):
                print( prefix + mh.ansi.FORE_RED + ("::::" * (i + 1)) + mh.ansi.FORE_RESET + str( j ) )
            
            type_str = " | ".join( "«{}»".format( x ) for x in types )
            
            if len( self.__debug_depth ) == 0:
                print( prefix + mh.ansi.FORE_RED + ("::::" * (i + 1)) + mh.ansi.FORE_RESET + "===== BEGIN COERCE {} INTO {} =====".format( mh.ansi.FORE_BLUE + value + mh.ansi.FORE_RESET, mh.ansi.FORE_MAGENTA + type_str + mh.ansi.RESET ) )
            else:
                print( prefix + mh.ansi.FORE_RED + ("::::" * (i + 1)) + mh.ansi.FORE_RESET + "DESCENDING INTO {}".format( mh.ansi.FORE_MAGENTA + type_str + mh.ansi.RESET ) )
        
        try:
            if self.debug:
                print( prefix + "ESTABLISHING HANDLERS:" )
            
            for destination_type in cast( List[type], types ):
                coercion_info = CoercionInfo( mh.AnnotationInspector( destination_type ), self, value )
                
                for coercer in self.__coercers:
                    if coercer.can_handle( coercion_info ):
                        priority = coercer.get_priority( coercion_info )
                        
                        if priority is None:
                            priority = 0
                        elif priority is True:
                            priority = AbstractCoercer.PRIORITY.DEFAULT
                        elif priority is False:
                            priority = 0
                        
                        coercion = _Coercion( priority, coercion_info, coercer )
                        
                        if self.debug:
                            print( prefix + " * PRIORITY " + mh.ansi.FORE_YELLOW + str( coercion.priority ) + mh.ansi.FORE_RESET + " " + str( coercion ) )
                        
                        if priority:
                            handlers.append( coercion )
                    elif self.debug:
                        print( prefix + " * PRIORITY " + mh.ansi.FORE_YELLOW + "NO_HANDLE" + mh.ansi.FORE_RESET + " " + str( _Coercion( 0, coercion_info, coercer ) ) )
            
            if not handlers:
                raise CoercionError( "There isn't a handler, in «{}» handlers, that can handle «{}». Details: {}".format( len( self.__coercers ), self.__get_type_names( types ), self ) )
            
            exceptions = []
            handlers = [x for x in sorted( handlers, key = lambda y: y.priority )]
            
            if self.debug:
                print( prefix + "READY TO TRY:" )
                
                for index, coercion in enumerate( handlers ):
                    print( prefix + " * {}. {}".format( index, coercion ) )
                
                print( prefix + "TRYING:" )
            
            for index, coercion in enumerate( handlers ):
                try:
                    if not coercion.info._cancelled:
                        if self.debug:
                            print( prefix + " * {}. {}".format( index, coercion ) )
                        
                        self.__debug_depth.append( coercion )
                        result = coercion.coercer.coerce( coercion.info )
                        self.__debug_depth.pop()
                        
                        if self.debug:
                            print( prefix + "     - SUCCESS = {} {}".format( result, type( result ) ) )
                        return result
                except CoercionError as ex:
                    if self.debug:
                        print( prefix + "     - {} FAILURE = {}\n{}".format( "TERMINATING" if ex.cancel else "NORMAL", ex, format_exc() ) )
                    exceptions.append( (coercion, ex) )
                    if ex.cancel:
                        coercion.info._cancelled = True
            
            assert len( exceptions )
            
            self.__failure( types, value, exceptions )
        finally:
            if orig_debug is not None:
                self.debug = orig_debug
    
    
    @staticmethod
    def __get_type_names( destination_types ):
        return "|".join( str( x ) for x in destination_types )
    
    
    def __failure( self, destination_types, source_value, exceptions: List[Tuple[_Coercion, Exception]] ):
        """
        Raises a descriptive `CoercionError` to indicate coercion failure.
        """
        if not self.debug:
            raise CoercionError( "The value «{0}» is not a valid value (expected «{1}»). Use «coerce::{0}» for details.".format( source_value, self.__get_type_names( destination_types ) ) )
        
        message = []
        
        mh.ignore( source_value )
        message.append( 'Cannot coerce into «{}».'.format( self.__get_type_names( destination_types ) ) )
        
        for index, exx in enumerate( exceptions ):
            coercion, ex = exx
            message.append( "  " + str( ex ).replace( "\n", "\n  " ) )
        
        # We do raise `from` because even though we've already included the description because it makes debugging easier
        raise CoercionError( "\n".join( message ) ) from exceptions[0][-1]


class UnionCoercer( AbstractCoercer ):
    """
    **Union** types can be referenced in a format suitable for _either of their member types_.
    
    notes::
    This coercer serves one function and is not externally configurable.
    """
    
    
    def on_get_priority( self ):
        return self.PRIORITY.INBUILT
    
    
    def on_get_archetype( self ) -> type:
        return Union
    
    
    def on_can_handle( self, info: CoercionInfo ):
        return info.annotation.is_union
    
    
    def on_coerce( self, info: CoercionInfo ):
        params = info.annotation.union_args
        return info.collection.coerce( params, info.source )


class NoneTypeCoercer( AbstractCoercer ):
    """
    The special **None** value may be referenced by the _exact text_ "none" (case insensitive).
    
    notes::
    This coercer serves one function and is not externally configurable. 
    """
    
    
    def on_coerce( self, args: CoercionInfo ):
        if args.source.lower() == "none":
            return None
        
        raise CoercionError( "Only accepting «none» to mean «None»." )
    
    
    def on_get_archetype( self ) -> type:
        return type( None )
    
    
    def on_can_handle( self, info: CoercionInfo ):
        return info.annotation.value is type( None )


class AbstractEnumCoercer( AbstractCoercer ):
    """
    Base class for enumerative coercers.
    If the set of options is fixed, only enough character(s) need to be provided to distinguish the enumeration member from the others.
    If the set of options is variable, the user can specify additional options, but the full text must be used to specify an existing option.
    """
    
    
    def on_get_archetype( self ) -> type:
        raise NotImplementedError( "abstract" )
    
    
    def get_option_names( self, value: object ) -> Tuple[str, ...]:
        return tuple( str( x ) for x in self.on_get_option_names( value ) )
    
    
    def get_option_name( self, value: object ) -> str:
        return mh.array_helper.first_or_error( self.get_option_names( value ) )
    
    
    def get_options( self, info: CoercionInfo ) -> Tuple[object, ...]:
        return mh.array_helper.as_sequence( contents = self.on_get_options( info ),
                                            sequence_types = (Iterable, None),
                                            cast = tuple )
    
    
    def get_accepts_user_options( self ) -> bool:
        return self.on_get_accepts_user_options()
    
    
    @mh.virtual
    def on_get_accepts_user_options( self ) -> bool:
        """
        Derived class should return if values outside those specified in `list` can be provided.
        If not overridden returns False.
        """
        return False
    
    
    @mh.virtual
    def on_get_option_names( self, value: object ) -> Iterable[object]:
        """
        The derived class should return the possible name(s) of the option.
        If the option has only one possible names it should override `on_get_option_name` instead.
        """
        return self.on_get_option_name( value ),
    
    
    @mh.virtual
    def on_get_option_name( self, value: object ) -> object:
        """
        The derived class should return the name of the option.
        
        If the option has multiple possible names it should override `on_get_option_names` instead.
        
        The default implementation returns the `value`. 
        """
        return cast( str, value )
    
    
    @mh.abstract
    def on_get_options( self, info: CoercionInfo ) -> Iterable[object]:
        """
        The derived class should return the options list.
        """
        raise NotImplementedError( "abstract" )
    
    
    @mh.virtual
    def on_convert_user_option( self, info: CoercionInfo ) -> object:
        """
        The derived class should convert user-entered text into a valid result.
        Note that the result is not passed through `on_convert_option`.
        """
        raise ValueError( "Cannot convert." )
    
    
    @mh.virtual
    def on_convert_option( self, info: CoercionInfo, option: object ) -> object:
        """
        The derived class should convert from the selected "option" to the value actually returned.
        If not overridden the `option` and the returned value are considered the same.
        
        :param     info:    Info used to retrieve the option 
        :param     option:  Selected option 
        :return:            Value returned 
        """
        mh.ignore( info )
        return option
    
    
    def on_coerce( self, info: CoercionInfo ):
        opts = self.get_options( info )
        
        try:
            result = mh.string_helper.find( source = opts,
                                            search = info.source.lower(),
                                            namer = self.on_get_option_name,
                                            detail = "option",
                                            fuzzy = not self.get_accepts_user_options() )
        except Exception as ex:
            if self.on_get_accepts_user_options():
                return self.on_convert_user_option( info )
            
            # Halting now to prevent fallback to `str`.
            raise CoercionError( "«" + info.source + "» is not a valid option in: " + ", ".join( "«{}»".format( self.on_get_option_name( x ) ) for x in opts ), cancel = True ) from ex
        else:
            return self.on_convert_option( info, result )


class SimpleEnumCoercer( AbstractEnumCoercer ):
    """
    Class intended for external construction.
    Accepts a options lambda and a type in the constructor.
    """
    
    
    def __init__( self, options, type_ ):
        self.type = type_
        self.options = options
    
    
    def on_get_options( self, info: CoercionInfo ):
        return self.options()
    
    
    def on_get_priority( self ):
        return self.PRIORITY.INBUILT
    
    
    def on_get_archetype( self ) -> type:
        return self.type
    
    
    def on_can_handle( self, info: CoercionInfo ):
        return info.annotation.is_direct_subclass_of( self.type )


class EnumCoercer( AbstractEnumCoercer ):
    """
    **Enumeration members** may be referenced by their _names_ (case insensitive).
    Only enough character(s) need to be provided to distinguish the enumeration member from the others.
    
    notes::
    This coercer serves one function and is not externally configurable.
    """
    
    
    def on_get_options( self, args: CoercionInfo ) -> List[object]:
        if not args.annotation.is_direct_subclass_of( Enum ):
            raise mh.LogicError(
                    "Shouldn't be asking for options when `args.annotation` ({}) is not an `Enum`. `can_handle` returns {}."
                        .format( args.annotation,
                                 self.can_handle( args ) ) )
        
        type_ = cast( Type[Enum], args.annotation.value )
        
        return [x for x in type_ if args.annotation.is_viable_instance( x )]
    
    
    def on_get_priority( self ):
        return self.PRIORITY.INBUILT
    
    
    def on_get_archetype( self ) -> type:
        return Enum
    
    
    def on_can_handle( self, info: CoercionInfo ):
        return info.annotation.is_direct_subclass_of( Enum )
    
    
    def on_get_option_name( self, value ):
        if value is None:
            return "None"
        
        return value.name.lower()


class BoolCoercer( AbstractCoercer ):
    """
    **Boolean** values may be specified as _text_: "true"/"false", "yes"/"no", "y"/"n", "t"/"f" or "1"/"0". Case insensitive.
    
    notes::
    This coercer serves one function and is not externally configurable.
    """
    
    
    def on_coerce( self, args: CoercionInfo ):
        try:
            return mh.string_helper.to_bool( args.source )
        except Exception as ex:
            # Halting now to prevent fallback to True.
            raise CoercionError( "«" + args.source + "» is not a valid boolean in: «true», «false», «yes», «no», «t», «f», «y», «n», «1», «0»", cancel = True ) from ex
    
    
    def on_get_priority( self ):
        return self.PRIORITY.INBUILT
    
    
    def on_get_archetype( self ) -> type:
        return bool
    
    
    def on_can_handle( self, info: CoercionInfo ):
        return info.annotation.value is bool


class ListCoercer( AbstractCoercer ):
    """
    **Lists** may be specified as a _comma delimited string_ (do not add extra spaces between list items).
    
    notes::
    This coercer serves one function and is not externally configurable.
    """
    
    
    def on_coerce( self, args: CoercionInfo ):
        # noinspection PyUnresolvedReferences
        list_type_ = args.annotation.generic_list_type
        elements = args.source.split( "," )
        result = list()
        
        for x in elements:
            result.append( args.collection.coerce( list_type_, x ) )
        
        return result
    
    
    def on_get_priority( self ):
        return self.PRIORITY.INBUILT
    
    
    def on_get_archetype( self ) -> type:
        return list
    
    
    def on_can_handle( self, info: CoercionInfo ):
        return info.annotation.is_generic_list


class PasswordCoercer( AbstractCoercer ):
    """
    **Passwords** may be specified by _an asterisk_ "*", which causes the terminal to prompt for the password safely.
    
    notes::
    This coercer serves one function and is not externally configurable.
    """
    
    
    def on_coerce( self, info: CoercionInfo ):
        if info.source in ("*", "prompt"):
            print( "Prompting for password." )
            import getpass
            value = getpass.getpass( "(PLEASE ENTER PASSWORD)" )
            
            if not value:
                raise CoercionError( "No password provided." )
            
            return info.annotation.value( value )
        else:
            return info.annotation.value( info.source )
    
    
    def on_get_priority( self ):
        return self.PRIORITY.INBUILT
    
    
    def on_get_archetype( self ) -> type:
        return mh.Password


class ObjectCoercer( AbstractCoercer ):
    """
    **Objects** may be provided _as string objects_.
    
    notes::
    This coercer serves one function and is not externally configurable.
    """
    
    
    def on_coerce( self, args: CoercionInfo ):
        return args.source
    
    
    def on_get_priority( self ):
        return self.PRIORITY.INBUILT
    
    
    def on_get_archetype( self ) -> type:
        return object
    
    
    def on_can_handle( self, info: CoercionInfo ):
        # override - "is object" rather than "is derived from object" (which would be everything!)
        return info.annotation.value is object


class FallbackCoercer( AbstractCoercer ):
    """
    **Standard types** may be referenced as _any acceptable value_ to their Python constructor, e.g. text for strings ("hello world"), numbers for integers ("123") and floats ("1.23").
    
    notes::
    This coercer serves one function and is not externally configurable.
    """
    
    
    def on_get_priority( self ):
        return self.PRIORITY.FALLBACK
    
    
    def on_get_archetype( self ) -> Optional[type]:
        return None
    
    
    def on_can_handle( self, info: CoercionInfo ):
        return True
    
    
    def on_coerce( self, args: CoercionInfo ):
        try:
            return args.annotation.value( args.source )
        except Exception as ex:
            raise CoercionError( "Cannot coerce the value via the constructor «{}».".format( args.annotation ) ) from ex


__default_coercer = None


def coerce( *args, **kwargs ):
    """
    Coerces using `get_default_coercer().coerce(...)`.
    """
    return get_default_collection().coerce( *args, **kwargs )


def register( *args ):
    """
    Registers using `get_default_collection().register(...)`.
    """
    return get_default_collection().register( *args )


def get_default_collection() -> CoercerCollection:
    """
    Obtains the default `CoercerCollection`.
    
    Use this function if you prefer the coercer to be a singleton, otherwise construct your own `CoercerCollection`.
    """
    global __default_coercer
    
    if __default_coercer is None:
        __default_coercer = CoercerCollection()
        __default_coercer.register( PasswordCoercer() )
        __default_coercer.register( UnionCoercer() )
        __default_coercer.register( NoneTypeCoercer() )
        __default_coercer.register( EnumCoercer() )
        __default_coercer.register( BoolCoercer() )
        __default_coercer.register( ListCoercer() )
        __default_coercer.register( ObjectCoercer() )
        __default_coercer.register( FallbackCoercer() )
    
    return __default_coercer
