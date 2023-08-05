class Test(object):
    def __init__(self, verbose=True):
        self.verbose=verbose

    def decorator(foo):
        def magic( self ):
            if self.verbose:
                print('coiso')
            print("start magic")
            foo( self )
            print("end magic")
        return magic

    def display_message(message, message2='', verbose=True):
        def decorator(fn):
            def decorated(*args,**kwargs):
                #if verbose:
                if args[0].verbose:
                    print(message)
                if message2:
                    print(message2)
                print('decorated')
                fn(*args,**kwargs)
                print('Done.')
            return decorated
        return decorator

    @decorator
    def bar( self ) :
        print("normal call")

    @display_message('msg decorator', '2')
    def bar2( self ) :
        print("another call")

if __name__ == '__main__':
    a = Test(False)
    a.bar()
    print('')
    a.bar2()

