import inspect


def proxy_function(subfunc, superfunc, mapping, /, *args, **kwargs):
    """
    The logic is:
    We want every call to superfunction pass through a subfunction with *args, **kwargs being arguments to
    the superfunction call and mapping being an optional key-value storage for non-existent or overridden
    function arguments.
    :param subfunc:
        function, which has a similar or identical signature as superfunc.
        >>> subfunc = lambda y, x: print(f'x={x}', f'y={y}')
    :param superfunc:
        function, which is to be called with *args, **kwargs.
        >>> superfunc = lambda x, y, z, **kwargs: ...
    :param mapping:
        some additional arguments to the subfunc or an override of them:
        >>> mapping = dict(x=1)
        they will *always* replace the original ones passed in *args, **kwargs.
    :param args: positional arguments for the superfunc.
    :param kwargs: keyword arguments for the superfunc.
    :return:
        result of partial application of *args, **kwargs and mapping to the subfunc in form of *args, **kwargs, which,
        when passed to the subfunc will produce a valid call to the function:
        >>> args, kwargs = proxy_function(subfunc, superfunc, mapping, 15, 18, 22, something='something else')
        >>> args == (18, 1)  # kwargs empty
        >>> subfunc(*args, **kwargs)  # prints "x=1 y=18"
        Notice, that arguments in both functions are not in the same order, yet they've been mapped correctly.
        This allows for some level of abstraction over the function calls, when the same argument names are semantically
        similar or identical.
    """
    # function specs
    subfunc_specs = inspect.getfullargspec(subfunc)
    # wannabe arguments
    superfunc_arg_values = inspect.getcallargs(superfunc, *args, **kwargs)
    if mapping:
        # override or add variables from the mapping
        superfunc_arg_values.update(mapping)
    context_args = []
    # parsing positional args
    for arg_name, default_num in zip(subfunc_specs.args, range(len(subfunc_specs.args) - 1, -1, -1)):
        if arg_name in superfunc_arg_values:  # try to find in function arguments
            context_args.append(superfunc_arg_values[arg_name])
        # else try to find a default value
        # default values in this context are applicable only to keyword-positional arguments
        elif subfunc_specs.defaults and default_num < len(subfunc_specs.defaults):
            # we gotta put the default into context_args, because is *args next,
            # like this: func2(p1, p2, p3=None, *args) - is a valid python function!
            context_args.append(subfunc_specs.defaults[default_num])
        else:
            raise ValueError(f"Missing required positional argument: '{arg_name}'.")
    # now *args
    if subfunc_specs.varargs and subfunc_specs.varargs in superfunc_arg_values:
        # if there are values for varargs, just concatenate them to the context args
        context_args = [*context_args, *superfunc_arg_values[subfunc_specs.varargs]]
    # if there aren't any, just ignore it, because they should be optional
    # now for the **kwargs
    if subfunc_specs.varkw and subfunc_specs.varkw in superfunc_arg_values:
        # try to unpack kwargs from superfunc_arg_values
        context_kwargs = dict(**superfunc_arg_values[subfunc_specs.varkw])
    else:
        context_kwargs = dict()
    for kwarg_name in subfunc_specs.kwonlyargs:
        if kwarg_name in superfunc_arg_values:
            context_kwargs[kwarg_name] = superfunc_arg_values[kwarg_name]
        elif kwarg_name in subfunc_specs.kwonlydefaults:
            context_kwargs[kwarg_name] = subfunc_specs.kwonlydefaults[kwarg_name]
        else:
            raise ValueError(f"Missing required keyword argument: '{kwarg_name}'.")
    return tuple(context_args), context_kwargs
