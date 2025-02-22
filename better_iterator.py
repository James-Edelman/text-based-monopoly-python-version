class better_iter():
    """
    better_iter supports previous(), looping, choosing to raise exceptions
    you can also view the current index and the entire iterator.
    
    Created by James E. 2025 with help from Github Copilot
    """

    # variables are created when an instance of this class is created
    def __init__(self, _iterable, _loops = False, _raise_exception = False):
        self.index = -1
        self.list = _iterable
        self.loops = _loops
        self.exception = _raise_exception

    # used when "next()" is applied
    def __next__(self):
        self.index += 1
        try:
            return self.list[self.index]
        except:

            # if the index is out of range but the iterator loops, it is reset to 0
            if self.loops == True: 
                self.index = 0
                return self.list[self.index]

            # looping takes priority over raising an error, 
            # a message isn't needed since "next()" also raises one
            elif self.exception == True:
                raise

    # used when "previous()" is applied, works opposite of "next()"
    def __previous__(self):
        self.index -= 1
        try:
            return self.list[self.index]
        except:
            if self.loops == True:
                self.index = len(self.list) - 1
                return self.list[self.index]

            elif self.exception == True:
                raise

    # modified with GitHub Copilot
    def __str__(self):
        output = str(self.list)
        output = "<" + output[1:-1] + ">"
        return output

def previous(arg):
    arg.__previous__()
    return arg.list[arg.index]
