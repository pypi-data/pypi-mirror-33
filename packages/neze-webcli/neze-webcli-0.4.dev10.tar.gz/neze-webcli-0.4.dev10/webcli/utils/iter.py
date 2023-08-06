class FixedLengthIterable:
    def __init__(self,it,length):
        if not hasattr(it,'__iter__'):
            raise TypeError()
        if not isinstance(length,int):
            raise TypeError()
        self.limit = length
        self.iterable = it
    def __iter__(self):
        return FixedLengthIterator(self)
class FixedLengthIterator(FixedLengthIterable):
    def __init__(self,fli):
        self.limit = fli.limit
        self.iterable = fli.iterable
        self.left = self.limit
        self.iterator = iter(self.iterable)
    def __next__(self):
        self.left -= 1
        if self.left < 0:
            raise StopIteration
        return next(self.iterator,None)

def unpack(it,length=0):
    return iter(FixedLengthIterable(it,length))

if __name__=='__main__':
    l = [1,2,3]
    print([1,2],list(unpack(l,2)))
    print([1,2,3,None],list(unpack(l,4)))

    l = [1,2]
    print(reversed(unpack(reversed(l),3)))
