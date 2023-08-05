def display_message(message):
    def decorator(fn):
        def decorated(*args,**kwargs):
            if args[0].verbose:
                print(message)
            print('decorated')
            fn(*args,**kwargs)
            print('Done.')
        return decorated
    return decorator


#@display_message('coiso e tal')
#def soma(a,b):
#    print('a + b = {}'.format(a+b))


class Test(object):
    msg = 'bananas'
    verbose=False

    @display_message(msg)
    def pp(self, a, b):
        print('soma a + b', a+b)

if __name__ == '__main__':
    #soma(1, 2)
    print()
    Test().pp(2,2)
