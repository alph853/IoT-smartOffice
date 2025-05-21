def foo(a=1, b=2, *args, d=4, **kwargs):
    print(a, b, args, d, kwargs)

foo(1, 2, 3, 4, d=11, e=12, f=13)
