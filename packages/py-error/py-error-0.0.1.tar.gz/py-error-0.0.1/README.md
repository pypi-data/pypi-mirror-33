# es6-error

An easily-extendable error class for use with python classes 

## Why?

I made this because I wanted to be able to extend Error for inheritance and type
checking .

## Usage

```python
class myClass(ExtendableError):
#     // __init__ is optional; you should omit it if you just want a custom error
#   // type for inheritance and type checking
    def __init__(self, message='OOps!'):
        super(message)

```

#### Todo

- tests