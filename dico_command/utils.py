import re
import typing
import inspect


SPLIT_PATTERN = re.compile(r'((".+")|[.\S]+)')
FMT_REGEX = re.compile(r'^<[at]?(:[^:]*)?(@[!&]?|#|:)(\d+)(:)?.*>$')
T = typing.TypeVar("T")


def is_coro(coro):
    return inspect.iscoroutinefunction(coro) or inspect.isawaitable(coro) or inspect.iscoroutine(coro)


def read_function(func):
    params = [*inspect.signature(func).parameters.values()]
    if params[0].name in ["self", "cls"]:
        del params[0]  # Skip self or cls
    del params[0]  # skip Context
    ret = {}
    for x in params:
        ret[x.name] = {
            "required": x.default == inspect._empty,  # noqa
            "default": x.default,
            "annotation": x.annotation if x.annotation != inspect._empty else None,  # noqa
            "kind": x.kind
        }
    return ret


def smart_split(ipt: str, args_data: dict, subcommand: bool = False) -> typing.Tuple[list, dict]:
    if len(args_data) == 0:
        if subcommand and ipt:
            return [*[x[0] for x in re.findall(SPLIT_PATTERN, ipt)]], {}
        return [], {}
    raw_split = [x[0] for x in re.findall(SPLIT_PATTERN, ipt)]
    initial_split = raw_split
    args_name = [*args_data.keys()]
    last_arg = args_data[args_name[-1]]
    var_positional_in = True in [*map(lambda n: n["kind"] == n["kind"].VAR_POSITIONAL, args_data.values())]
    keyword_only_count = len([x for x in args_data.values() if x["kind"] == x["kind"].KEYWORD_ONLY])
    if len(args_data) == 1:
        if last_arg["kind"] == last_arg["kind"].VAR_POSITIONAL:
            if ipt:
                return [ipt], {}
            else:
                return [], {}
        elif last_arg["kind"] == last_arg["kind"].KEYWORD_ONLY:
            if ipt:
                return [], {args_name[-1]: ipt}
            else:
                return [], {}
        else:
            return [initial_split[0]] if initial_split else [], {}
    if (len(initial_split) == len(args_data) and not keyword_only_count) or last_arg["kind"] == last_arg["kind"].VAR_POSITIONAL:  # assuming this matches
        return initial_split, {}
    if len(initial_split) != len(args_data) and not var_positional_in and not keyword_only_count:
        raise ValueError("argument count does not match.")
    if keyword_only_count > 1:
        raise AttributeError("maximum keyword-only param number is 1.")
    args = []
    kwargs = {}
    if not ipt.replace(" ", ""):
        raise ValueError("empty input.")
    for i, x in enumerate(args_data.items()):
        k, v = x
        if v["kind"] == v["kind"].KEYWORD_ONLY:
            if var_positional_in:
                raise AttributeError("unable to mix positional-only and keyword-only params.")
            kwargs[k] = ipt or None
            # TODO: fix kwargs is added even if it is not present
            break
        args.append(initial_split[i])
        ipt = ipt.split(initial_split[i], 1)[-1].lstrip()
    return args, kwargs


def maybe_fmt(value: str) -> typing.Optional[str]:
    match = FMT_REGEX.match(value)
    if match:
        return match.group(3)


def search(items: typing.Sequence[T], **attributes) -> typing.Optional[T]:
    for x in items:
        for k, v in attributes.items():
            resp = getattr(x, k)
            if inspect.ismethod(resp):
                resp = resp()
            if resp == v:
                return x
