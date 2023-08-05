import inspect
import json
import warnings
from inspect import _empty
from typing import TypeVar, Union, Any, Generator, Tuple, Type, Optional, overload, get_type_hints, Sequence

import os

import asyncio as asyncio
import requests

from depytg.errors import NotImplementedWarning, TelegramError

base_url = "https://api.telegram.org/bot{token}/{method}"
file_url = "https://api.telegram.org/file/bot{token}/{path}"

unacceptable_names = (
    "from", "import", "for", "class", "def", "return", "yield", "with", "global", "print", "del", "is", "not", "while",
    "try", "except", "finally", "if", "elif", "else", "or", "and")

T = TypeVar("T")


def shadow(name: str) -> str:
    if name in unacceptable_names:
        return name + "_"
    return name


def unshadow(name: str) -> str:
    if name[:-1] in unacceptable_names:
        return name[:-1]
    return name


class TelegramObjectBase(dict):
    """
    Base class for Telegram API objects. It should not be used directly.
    """

    __fields = []

    def __init__(self):
        super().__init__()

        self.__fields.extend([i for i, _ in self._get_fields(required=None)])

    @classmethod
    def _get_fields(cls, required: Optional[bool]) -> Generator[Tuple[str, Any], None, None]:
        s = inspect.signature(cls.__init__)
        hints = get_type_hints(cls.__init__)
        for name, p in s.parameters.items():
            if name == "self":
                continue
            if (required or required is None) and p.default == _empty:
                yield name, Any if name not in hints else hints[name]
            if not required and p.default != _empty:
                yield name, Any if name not in hints else hints[name]

    @classmethod
    def _get_required(cls) -> Generator[Tuple[str, Any], None, None]:
        """
        A generator yielding required fields based on the constructor's signature.
        :return: A sequence of (field_name, type) tuples
        """
        for n, t in cls._get_fields(required=True):
            yield n, t

    @classmethod
    def _get_optional(cls) -> Generator[Tuple[str, Any], None, None]:
        """
        A generator yielding optional fields based on the constructor's signature.
        :return: A sequence of (field_name, type) tuples
        """
        for n, t in cls._get_fields(required=False):
            yield n, t

    @classmethod
    def _get_field_type(cls, name: str) -> Optional[Type]:
        # s = inspect.signature(cls.__init__)
        hints = get_type_hints(cls.__init__)
        return hints[name] if name in hints else None

    @classmethod
    def _is_required(cls, name: str) -> bool:
        return inspect.signature(cls.__init__).parameters[name].default == _empty

    @classmethod
    def _is_optional(cls, name: str) -> bool:
        return not cls._is_required(name)

    @classmethod
    @overload
    def from_json(cls, j: dict) -> 'TelegramObjectBase':
        pass

    @classmethod
    @overload
    def from_json(cls, j: str) -> 'TelegramObjectBase':
        pass

    @classmethod
    def from_json(cls, j: dict):
        """
        Converts a Telegram object JSON/dict to a native object.
        :param j: JSON/The source dict
        :return: A TelegramObjectBase subclass instance representing the object
        """

        if isinstance(j, str):
            j = json.loads(j)

        # Check if all required fields are specified
        # (KwArgs /\ Required) = Required
        required = set([i for i, _ in cls._get_required()])
        given = set(j.keys())
        if given.intersection(required) != required:
            # missing = Required \ (KwArgs /\ Required)
            missing = required.difference(given.intersection(required))
            raise TypeError("Not a valid '{}' object. Missing {} required fields: {}"
                            .format(cls.__name__, len(missing), missing))

        args = (cls._depyfy(j[i], shadow(i)) for i, _ in cls._get_required())
        kwargs = {shadow(i): cls._depyfy(j[i], shadow(i)) for i in given.difference(required)}

        return cls(*args, **kwargs)

    @classmethod
    def _depyfy(cls, value: T, name: str = None, field_type: Type = None) -> Union[T, 'TelegramObjectBase', None]:
        """
        Converts a generic object compatible with Telegram's API to an object
        that is native to this library. If the object is already of the right
        type, nothing is done.
        :param name: The name of the field
        :param value: The given object
        :param field_type: The default type for that value, or None to retrieve it automatically
        :return: A TelegramObjectBase subclass instance that represents the object
        """

        from depytg.depyfier import depyfy

        if field_type is None and name is None:
            raise ValueError("At least one of 'name' and 'field_type' must be specified")

        if field_type is None:
            field_type = cls._get_field_type(name)

        try:
            # If the field is optional, the value can be None
            if cls._is_optional(name) and value is None:
                return None
            # Convert the field to a native type
            return depyfy(value, field_type)

        # There has been some mess with parametrized generics and conversion is not implemented
        except TypeError:
            import traceback
            traceback.print_exc()
            warnings.warn(
                "Could not convert field '{name}' of '{object}' from '{t1}' to '{t2}' because\
                of poor implementation."
                    .format(name=name, object=cls.__name__, t1=type(value), t2=field_type),
                NotImplementedWarning)
            return value

            # If the given object is of an incompatible type, raise an exception
            # This should not happen as of now, PyCharm reports it as unreachable code.
            # raise TypeError("Incompatible type for field '{}' of type '{}': '{}'"
            #                 .format(name, field_type.__name__, type(value).__name__))

    def __getattr__(self, item):
        try:
            return super(TelegramObjectBase, self).__getattribute__(item)
        except AttributeError:
            if unshadow(item) in self:
                return self[unshadow(item)]
            if self._is_optional(item):
                return None
            else:
                raise

    def __setattr__(self, item, value):
        try:
            if self._is_required(item):
                self[unshadow(item)] = value
                return
        except AttributeError:
            pass
        try:
            if self._is_optional(item):
                # Avoid setting None defaults when not explicitly provided
                if unshadow(item) not in self and value is None:
                    pass
                else:
                    self[unshadow(item)] = self._depyfy(value, item)
                return
        except AttributeError:
            pass
        warnings.warn(
            "'{}' object has no attribute '{}', but you are trying to set it. It will be set as a Python attribute and \
            will not appear in the ."
                .format(self.__class__.__name__, unshadow(item)), RuntimeWarning)
        return super().__setattr__(item, value)

    def __delattr__(self, item):
        required = False
        try:
            required = self._is_required(item)
        except AttributeError:
            pass

        if required:
            raise AttributeError(
                "Field '{}' of object '{}' is required and can't be deleted."
                    .format(unshadow(item), self.__class__.__name__))

        if unshadow(item) in self:
            self.pop(unshadow(item))
        else:
            return super().__delattr__(item)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, dict(self))

    def __dir__(self):
        return dir(type(self)) + self.__fields


class TelegramMethodBase(TelegramObjectBase):
    ReturnType = Any

    def _prepare_for_call(self, token: str) -> Tuple[str, dict, dict, dict, bool]:
        # Local import to issues due to recursive imports
        # Python is smart enough to work everything out
        from depytg.types import InputFile

        form = {}
        files = {}
        inputfiles = {}
        use_multipart = False

        # Look for InputFile objects and turn them into something that makes
        # sense to requests
        filecounter = 0
        for k, v in self.items():
            if isinstance(v, InputFile):
                use_multipart = True

                fname = "file{}".format(filecounter)

                if v.name and not v.name in files:
                    fname += "_" + v.name
                elif getattr(v.file, "name", None) and os.path.basename(v.file.name) not in files:
                    fname += "_" + os.path.basename(v.file.name)

                form[k] = "attach://" + fname

                files[fname] = v.file
                inputfiles[fname] = v
                filecounter += 1

            else:
                form[k] = json.dumps(v) if isinstance(v, (list, dict)) else v

        url = base_url.format(token=token, method=self.__class__.__name__)

        return url, form, files, inputfiles, use_multipart

    def __call__(self, token: str) -> ReturnType:
        url, form, files, _, use_multipart = self._prepare_for_call(token)

        if use_multipart:
            r = requests.post(url, data=form, files=list(files.items()))
        else:
            r = requests.post(url, json=form)

        j = r.json()
        return self.read_result(j)

    @asyncio.coroutine
    def async_call(self, session, token: str) -> ReturnType:
        url, form, files, inputfiles, use_multipart = self._prepare_for_call(token)

        if use_multipart:
            data = form.copy()
            data.update(files)

            print("Method:", self.__class__.__name__)
            print("Data:", data)

            from aiohttp import FormData
            data = FormData()
            data.add_fields(*((str(k), str(v)) for k, v in form.items()))
            for name, f in inputfiles.items():
                print(name, f.file, f.mime, name)
                data.add_field(name, f.file, content_type=f.mime, filename=name)

            req = session.post(url, data=data)
        else:
            req = session.post(url, json=form)

        r = yield from req
        j = yield from r.json()
        return self.read_result(j)

    @classmethod
    @overload
    def read_result(cls, j: dict) -> ReturnType:
        pass

    @classmethod
    @overload
    def read_result(cls, j: str) -> ReturnType:
        pass

    @classmethod
    def read_result(cls, j) -> ReturnType:
        """
        Reads a result for this method (which was called externally) and converts it into a
        DepyTG object.
        :param j: The response JSON/dict
        :return: A TelegramObjectBase subclass instance representing the response
        """
        from depytg.depyfier import depyfy

        if isinstance(j, str):
            j = json.loads(j)

        if "ok" in j and j["ok"] and "result" in j:
            return depyfy(j["result"], cls.ReturnType)
        else:
            raise TelegramError(j.get("description", "Unknown error"),
                                j.get("error_code", None))
