from typing import Any, Dict, Sequence, Union

__all__ = (
    "JSONPointerError",
    "build",
    "build_pointer",
    "parse_pointer",
    "escape_token",
    "unescape_token",
)


RefTokens = Sequence[Union[int, str]]

JSONPointer = str
JSONPointers = Dict[JSONPointer, Any]


class JSONPointerError(Exception):
    pass


def build(obj: dict, *, initial_ref_tokens: RefTokens = None) -> JSONPointers:
    ref_tokens = initial_ref_tokens or []
    result = {}

    def walk(obj):
        for key, value in obj.items():
            ref_tokens.append(key)

            if isinstance(value, dict):
                walk(value)
            else:
                result[build_pointer(ref_tokens)] = value

            ref_tokens.pop()

    walk(obj)

    return result


def build_pointer(ref_tokens: RefTokens) -> JSONPointer:
    if not ref_tokens:
        return ""

    pointer = "/".join(escape_token(str(ref_token)) for ref_token in ref_tokens)
    pointer = f"/{pointer}"

    return pointer


def parse_pointer(pointer: JSONPointer) -> RefTokens:
    if pointer == "":
        return []

    if not pointer.startswith("/"):
        raise JSONPointerError()

    return [unescape_token(ref_token) for ref_token in pointer[1:].split("/")]


def escape_token(token: str) -> str:
    to_escape = (("~", "~0"), ("/", "~1"))

    for old, new in to_escape:
        token = token.replace(old, new)

    return token


def unescape_token(token: str) -> str:
    to_unescape = (("~0", "~"), ("~1", "/"))

    for old, new in to_unescape:
        token = token.replace(old, new)

    return token
