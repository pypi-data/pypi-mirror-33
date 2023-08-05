# Are you sure

Simple decorator to ask before evaluating a function (just one very simple function)

## Usage example

```python
from are_you_sure import are_you_sure

@are_you_sure
def dangerous_function(*args, **kwargs):
    print(f'Running {dangerous_function.__name__} with {args,kwargs}')

if __name__ == '__main__':
    dangerous_function(1, "arg_example", name='lol')

```