# function-proxy
We want every call to superfunction pass through a subfunction with ```*args, **kwargs``` being arguments to the superfunction call and mapping being an optional key-value storage for non-existent or overridden function arguments. 
This function would return valid set of ```*args, **kwargs``` for a subfunction call, if such exist.
Functional subclassing? Don't know what to call it, but have a peek:

An easy example:
```
from proxy_function import proxy_function
```
Suppose, we have a super function, which does something very clever and complicated with given arguments:
```
def superfunc(z, y, x, *args, transpose=True, **kwargs):
  pass  # do something clever, for example
```
And we have a simple function, which has the same arguments semantically (the meaning is the same) and some additional ones (```divide_by```)
```
def subfunc(x, y, divide_by=2):  # btw, notice, that they're in a different order
  x, y = x // divide_by, y // divide_by
  return x, y
```
Now we wanna call ```superfunc``` AND ```subfunc``` with the same arguments.
How do we do it? That's how:
```
superfunc_args = (15, 18, 22, 48, 95)
superfunc_kwargs = dict(something='something else', lotta='strange arguments')
args, kwargs = proxy_function(subfunc, superfunc, None, *superfunc_args, **superfunc_kwargs)
```
Ignore ```None``` for a sec.
What happened? We put both ```subfunc``` and ```superfunc``` and provided arguments we would've used for a ```superfunc``` call.
The ```proxy_function``` returned a set of correct arguments for the ```subfunc``` based on both function's signatures.

Which means:
```
result = subfunc(*args, **kwargs)
print(result)
assert result == (11, 9)  # IS GOOD
```
Even though there is also a ```divide_by``` argument mixed in ```subfunc```, which ```superfunc``` doesn't have!

OK, suppose another case: ```divide_by``` doesn't have a default value.

```
def subfunc(y, divide_by, x):  # swap around the arguments again!!! NO MERCY, NO RESEMBLANCE
  x, y = x // divide_by, y // divide_by
  return (x, y)
```
And call it again:
```
args, kwargs = proxy_function(subfunc, superfunc, {"divide_by": 4}, *superfunc_args, **superfunc_kwargs)
result = subfunc(*args, **kwargs)
print(result)
assert result == (5, 4)  # IS GOOD AGAIN
```

Notice, that arguments in both examples are not in completely different order from each other and from the ```superfunc```, yet they've been mapped correctly.
This allows for some level of abstraction over the function calls, when the same argument names are semantically similar or identical in their meaning without writing.

> Is there a scientific name for such trick?
