#!/usr/bin/env python3
class Tree():
    def __init__(self, size, rank):
        self.size = size
        self.rank = rank
        self.child = []
        self.childdict = {}
        clist = [[i for i in range(0, size)]]
        while len(clist) > 0:
            l = clist.pop()
            #print("procesisng "+str(l))
            pilot = l[0]
            while len(l) > 1:
                temp = []
                for i in range(len(l)//2):
                    e = l.pop()
                    temp.insert(0, e)
                #print("temp: "+str(temp))
                if pilot not in self.childdict:
                    self.childdict[pilot] = []
                if len(temp) > 0:
                    self.childdict[pilot].insert(0, temp[0])
                if len(temp) > 1:
                    clist.append(temp)
            #print(self.childdict)


    def getParent(self):
        for k,v in self.childdict.items():
            if self.rank in v:
                return k

    def getChild(self):
        if self.rank in self.childdict.keys():
            return self.childdict[self.rank]
        else:
            return []

if __name__ == '__main__':
 #   for i in range(0,8):
    tree = Tree(8,0)
    print(str(tree.getChild()))
    print(str(tree.getParent()))

    tree = Tree(3,0)
    print(str(tree.getChild()))

