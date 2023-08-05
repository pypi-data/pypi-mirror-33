from functools import wraps


def are_you_sure(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        user_input = input('Are you sure? y/n: ')
        user_input = user_input.lower()
        if user_input == 'y':
            func(*args, **kwargs)
        else:
            print('Aborted without running')
    return wrapped

def main():
    @are_you_sure
    def dangerous_function(*args, **kwargs):
        print(f'Running {dangerous_function.__name__} with {args,kwargs}')

    dangerous_function(1, "arg_example", name='lol')

if __name__ == '__main__':
    main()
