class better_iter():
    """
    an iterator that allows you to access index, and is more user
    accessible.

    note: getting current value returns the final item if iterator
    is unused, since -1 (default index) references the last item.

    Created by James E. 2025 with help from Github Copilot
    """


    # variables are created when an instance of this class is created
    def __init__(self, iterable, loop = False):
        self.index = -1
        self.list = list(iterable)
        self.iter_through = False
        self.loop = loop    
       
    # used when "next()" is applied
    def __next__(self):

        # either adds to the index or for loop index
        if self.iter_through == False:
            self.index += 1
            index = self.index

        else:
            self.iter_index += 1
            index = self.iter_index

        try:
            return self.list[index]
        except IndexError:

            # loops only if it's not a for loop
            if self.loop == True and self.iter_through == False: 
                self.index = 0
                return self.list[self.index]
                
            # when iterating through runs out, stops the loop lock
            elif self.iter_through == True:
                self.iter_through = False

                # ends the for loop
                raise StopIteration

    # used when "previous()" is applied, works opposite of "next()"
    def __previous__(self):
        self.index -= 1
        try:
            return self.list[self.index]
        except IndexError:
            if self.end == True:
                self.index = 0
                return self.list[self.index]

    def __iter__(self):
        self.iter_through = True

        # custom index means that progress isn't lost in for loops
        self.iter_index = -1
        return self

    def __str__(self): return str(self.list[self.index])
     
    def __int__(self): return int(self.list[self.index])

    def __index__(self): return self.list[self.index]

    def __repr__(self):
        output = str(self.list)
        output = "<" + output[1:-1] + ">"
        return output
    
    def __hash__(self): return self.list[self.index]

    def __eq__(self, other): return self.list[self.index] == other

    def __gt__(self, other): return self.list[self.index] > other
    
    def __ge__(self, other): return self.list[self.index] >= other

    def __lt__(self, other): return self.list[self.index] < other

    def __le__(self, other): return self.list[self.index] <= other

    def __add__(self, other): return self.list[self.index] + other

def previous(arg): return arg.__previous__()