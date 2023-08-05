import collections.abc
import warnings

from depytg.errors import NotImplementedWarning
from depytg.types import *

from typing import GenericMeta, Sequence, Mapping, _ForwardRef, Union, Any


def is_union(some_type: type(Union)) -> bool:
    """
    Apparently there's no way to know if some type is a Union other than checking
    the memory location of its type. Thanks Python <3
    :param some_type: The type you're checking
    :return: True if it is a Union
    """

    # Yeah. Thanks Python.
    return isinstance(some_type, type(Union)) or \
           id(type(some_type)) == id(type(Union)) or \
           str(type(some_type)) == "typing.Union"


def is_sequence(some_type: GenericMeta) -> bool:
    if "__extra__" in dir(some_type):
        return some_type.__extra__ == collections.abc.Sequence
    return False


def is_mapping(some_type: GenericMeta) -> bool:
    if "__extra__" in dir(some_type):
        return some_type.__extra__ == collections.abc.Mapping
    return False


def is_tobject(some_type: type) -> bool:
    return ((
                type(some_type) == type and
                issubclass(some_type, TelegramObjectBase)
            ) or isinstance(some_type, TelegramObjectBase))


def is_forwardref(some_type: GenericMeta) -> bool:
    return isinstance(some_type, _ForwardRef)


def depyfy(obj: Any, otype: Union[type, GenericMeta]) -> Any:
    """
    Walks into a generic object 'obj' and converts it to a DepyTG typechecked
    object, if possible.
    Please note that only JSON-serializable objects are
    supported: other objects will be returned without conversion.
    Moreover, forward references are not supported and objects whose type
    specified as such will not be converted. To avoid passing unwanted forward references,
    please use 'typing.get_type_hints' instead of finding them manually.
    :param obj: The object to convert
    :param otype: The expected type for the object
    :return: The converted object
    """

    if is_sequence(otype):
        return depyfy_sequence(obj, otype)
    elif is_mapping(otype):
        return depyfy_mapping(obj, otype)
    elif is_union(otype):
        return depyfy_union(obj, otype)
    elif is_tobject(otype):
        return depyfy_tobject(obj, otype)
    else:
        return obj


def depyfy_sequence(seq: Sequence, seq_type: GenericMeta) -> Sequence:
    subtype = seq_type.__args__[0]
    newseq = []

    if isinstance(subtype, _ForwardRef):
        warnings.warn("Not depyfying sequence whose argument is a forward reference", NotImplementedWarning)
        return seq
    elif is_sequence(subtype):
        for i in seq:
            newseq.append(depyfy_sequence(i, subtype))
    elif is_mapping(subtype):
        for i in seq:
            newseq.append(depyfy_mapping(i, subtype))
    elif is_tobject(subtype):
        for i in seq:
            newseq.append(depyfy_tobject(i, subtype))
    else:
        # Subtype is a regular Python object. This is not a typechecker, skip loop
        return seq

    # Cast back to original type
    return type(seq)(newseq)


def depyfy_mapping(mapp: Mapping, map_type: GenericMeta) -> Mapping:
    keytype, valtype = map_type.__args__
    newmap = {}

    k_is_fref = is_forwardref(keytype)
    v_is_fref = is_forwardref(valtype)

    # Skip loop if everything is a forward reference
    if k_is_fref or v_is_fref:
        warnings.warn("Not depyfying mapping whose {} defined as _ForwardRef"
                      .format(k_is_fref and not v_is_fref and "key is" or \
                              v_is_fref and not k_is_fref and "value is" or \
                              k_is_fref and v_is_fref and "key and value are"),
                      NotImplementedWarning)
        return mapp

    # Skip loop if both keys and values are regular Python objects
    if not (isinstance(keytype, GenericMeta) or is_tobject(keytype) or
                isinstance(valtype, GenericMeta) or is_tobject(valtype)):
        return mapp

    # Either key or value needs to be depyfied
    for k, v in mapp.items():
        newkey, newval = k, v

        if k_is_fref:
            pass
        elif is_sequence(keytype):
            newkey = depyfy_sequence(k, keytype)
        elif is_mapping(keytype):
            newkey = depyfy_mapping(k, keytype)
        elif is_tobject(keytype):
            newkey = depyfy_tobject(k, keytype)

        if v_is_fref:
            pass
        elif is_sequence(valtype):
            newval = depyfy_sequence(v, valtype)
        elif is_mapping(valtype):
            newval = depyfy_mapping(v, valtype)
        elif is_tobject(valtype):
            newval = depyfy_tobject(v, valtype)

        newmap[newkey] = newval

    # Cast back to original type
    return type(mapp)(newmap)


def depyfy_union(obj: Any, union: GenericMeta) -> Any:
    given_t = type(obj)

    # If the object is a regular Python object and its type is specified
    # in the Union, it's good to go
    if given_t in union.__args__:
        return obj

    # Not a regular type, one first shot looking for TelegramObjectBase
    if given_t == dict and dict not in union.__args__:
        # Try to convert it to every TelegramObjectBase subclass specified
        # in the Union. Return the first one that succeeds
        for t in union.__args__:
            if not is_tobject(t):
                continue
            try:
                return depyfy_tobject(obj, t)
            except Exception:
                import traceback
                import traceback
                traceback.print_exc()

    # Maybe it's a GenericMeta. Check for Sequence and Mapping
    for t in union.__args__:
        try:
            if is_sequence(t):
                return depyfy_sequence(obj, t)
        except Exception:
            import traceback
            traceback.print_exc()

        try:
            if is_mapping(t):
                return depyfy_mapping(obj, t)
        except Exception:
            import traceback
            traceback.print_exc()

    # The object is nothing we can convert. Return it with a warning
    warnings.warn("Could not match object '{}' of type {} with anything in {}".format(obj, given_t, union))
    return obj


def depyfy_tobject(tobj: Union[TelegramObjectBase, dict, str], otype: type) -> TelegramObjectBase:
    if type(tobj) == otype:
        return tobj
    elif type(tobj) in (str, dict):
        return otype.from_json(tobj)
    return tobj
