'''This is newNester.py module which has a function to find factorial of a number'''
def factorial(n):
    '''This function takes one argument n, an integer and returns the factcorial of the number'''
    if n<1:
        return 0
    if n==1:
        return 1
    return factorial(n-1) * n
