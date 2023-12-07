class SummaryHandler:
    def __init__(self):
        self._funcs = {}
    def __getitem__(self,item):
        return self._funcs[item]
    def __setitem__(self,key,value):
        self._funcs[key]=value