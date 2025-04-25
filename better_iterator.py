class better_iter():
    """
    set _end_action to either "loop", or "exception", default is none
    you can also view the current index and the entire iterator.
    
    Created by James E. 2025 with help from Github Copilot
    """

    # variables are created when an instance of this class is created
    def __init__(self, _iterable, _end_action = None):
        self.index = -1
        self.list = list(_iterable)
        self.iter_through = False
        
        if _end_action not in ["loop", "exception", None]:
            raise Exception("invalid end action")
        else:
            self.end = _end_action
       
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
        except:

            # if the index is out of range but the iterator loops, it is reset to 0
            # when used in a for loop this will not infinitely loop
            if self.end == "loop" and self.iter_through == False: 
                self.index = 0
                return self.list[self.index]

            # looping takes priority over raising an error, 
            # a message isn't needed since "next()" also raises one
            elif self.end == "exception":
                raise

            # when iterating through a better_iter runs out, stops the loop lock
            elif self.iter_through == True:
                self.iter_through = False

                # ends the for loop
                raise StopIteration

    # used when "previous()" is applied, works opposite of "next()"
    def __previous__(self):
        self.index -= 1
        try:
            return self.list[self.index]
        except:
            if self.end == "loop":
                self.index = len(self.list) - 1
                return self.list[self.index]

            elif self.end == "exception":
                raise

    def __iter__(self):
        self.iter_through = True

        # custom index means that progress isn't lost in for loops
        self.iter_index = -1
        return self

    def __str__(self): return str(self.list[self.index])
     
    def __int__(self): return self.list[self.index]

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