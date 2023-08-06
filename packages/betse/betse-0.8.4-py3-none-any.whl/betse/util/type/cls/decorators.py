#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright 2014-2018 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
Low-level **decorator** (i.e., classes and callables dynamically wrapping other
classes and callables at runtime) facilities.
'''

# ....................{ IMPORTS                            }....................
from abc import ABCMeta  #, abstractmethod
from betse.util.type.types import (
    type_check, CallableTypes, ClassType, MethodType)

# ....................{ DECORATORS                         }....................
#FIXME: Rename this class to "MethodDecoratorABC".
#FIXME: Rename the "_method" attribute to "_method_unbound".
class MethodDecorator(object, metaclass=ABCMeta):
    '''
    Abstract base class of all **method decorators** (i.e., decorators *only*
    decorating methods bound to class instances), implemented as a class
    descriptor satisfying the standard descriptor protocol.

    This superclass efficiently caches bound methods on behalf of subclasses,
    guaranteeing all subclasses to be efficiently callable as proper methods.

    Attributes
    ----------
    _method: CallableTypes
        Unbound method (i.e., function) to be decorated.
    _obj_id_to_method_bound : dict
        Dictionary mapping from the unique identifier associated with each
        class instance containing a method decorated by this subclass to the
        same method bound to that class instance. While technically optional,
        the cache implemented by this dictionary avoids the need to recreate
        bound methods on each call to the :meth:`__get__` method.
    '''

    # ..................{ INITIALIZERS                       }..................
    @type_check
    def __init__(self, method: CallableTypes) -> None:
        '''
        Initialize this method decorator.

        Parameters
        ----------
        method: CallableTypes
            Unbound method (i.e., function) to be decorated.
        '''

        # Classify all passed parameters.
        self._method = method

        # Initialize all remaining instance variables.
        self._obj_id_to_method_bound = {}

    # ..................{ DESCRIPTORS                        }..................
    def __get__(self, obj: object, cls: ClassType) -> MethodType:
        '''
        Create, cache, and return a decorated method bound to the passed object.

        This method satisfies the descriptor protocol in a similar manner to
        Python itself. Python implicitly converts each function in a class body
        into a descriptor implementing the ``__get__()`` special method by
        internally creating and returning a copy of that function bound to the
        passed class instance.
        '''

        # If this descriptor is accessed as a class rather than instance
        # variable, return this low-level descriptor rather than the high-level
        # value to which this expression evaluates.
        if obj is None:
            return self

        # Unique identifier associated with this object.
        obj_id = id(obj)

        # Attempt to return the previously bound decorated method.
        try:
            return self._obj_id_to_method_bound[obj_id]
        # If this method has yet to be bound...
        except KeyError:
            # Create and cache this bound method. While superficially trivial,
            # doing so is surprisingly non-trivial when examined. In the
            # following assignment:
            #
            # * Accessing "self.__call__" implicitly creates a new method from
            #   the __call__() function bound to the current instance of this
            #   class with the signature:
            #       def __call__bound(obj, *args, **kwargs)
            # * Instantiating "MethodType" implicitly creates a new method from
            #   the __call__bound() method bound to the passed instance of the
            #   parent class with the signature:
            #       def __call__bound_bound(*args, **kwargs)
            #
            # Hence, this bound method is actually a bound bound method (i.e., a
            # function bound to two class instances).
            method_bound = self._obj_id_to_method_bound[obj_id] = MethodType(
                self.__call__, obj)
            return method_bound

    # ..................{ CALLERS                            }..................
    def __call__(self, obj, *args, **kwargs) -> object:
        '''
        Call the decorated method previously passed to the :meth:`__init__`
        method bound to the passed object with the passed positional and keyword
        arguments, returning the value returned by this call.

        This special method is typically overriden by subclass implementations
        wrapping the decorated method with additional functionality.
        '''

        return self._method(obj, *args, **kwargs)
