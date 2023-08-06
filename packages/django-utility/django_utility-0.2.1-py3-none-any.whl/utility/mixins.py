class DictMixin:
    def __getitem__(self, k):
        return self.__dict__[k]
        
    def __setitem__(self, k, i):
        self.__dict__[k] = i
