'''this module has one function fib which takes one integer argument'''
def fib(n):
    '''this function computes the nth fibonacci number'''
    if n==0 or n==1:
        return n
    return fib(n-1) + fib(n-2)
