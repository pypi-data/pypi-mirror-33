class ChoicesList(list):
    def __init__(self,what):
        if isinstance(what,str):
            what = what.split(',')
        super().__init__(what)
    def __contains__(self,X):
        if super().__contains__(X):
            return True
        try:
            for x in X:
                if not super().__contains__(x):
                    return False
        except TypeError:
            return False
        return True

if __name__=='__main__':
    list1 = range(42,70)
    list2 = ','.join(map(str,list1))
    list3 = list(list1)
    print(ChoicesList(list1))
    print(ChoicesList(list2))
    print(ChoicesList(list3))
