"""contains a custom iterator, its previous() function, and a custom error,
now contains a custom dictionary as well"""

from collections.abc import Iterable

# except statements catch index errors in case loop is enabled,
# but if not, this is raised in lieu
class tripple_affirmative(IndexError):
    '''"Some said she never had a solution, she just died.
        And when the systems broke down an erroneous signal was sent."'''
    def __init__(
            self, 
            msg = '''iterator index out of range.
            
            "Some said she never had a solution, she just died.
            And when the systems broke down an erroneous signal was sent."'''
        ):
        self.msg = msg

    def __str__(self): return self.msg

    
class better_iter():
    """
    an iterator that allows you to access the index,
    and sucks less. Allows you to loop when completed.

    note: str() returns current value,
    use repr() for viewing entire iter

    Created by James E. 2025 with help from GitHub Copilot
    """

    def __init__(self, iterable, loop = False, start_index = 0):
        self.index = start_index
        self.list = list(iterable)
        self.iter_through = False
        self.loop = loop    
       
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

            else:
                raise tripple_affirmative

    # used when "previous()" is applied, works opposite of "next()"
    def __previous__(self):
        self.index -= 1
        try:
            return self.list[self.index]
        except IndexError:
            if self.loop == True:
                self.index = 0
                return self.list[self.index]
            else:
                raise tripple_affirmative

    def __iter__(self):
        # when for loops use this, iter_through prevents looping
        self.iter_through = True

        # separate index means that progress isn't lost in for loops
        self.iter_index = -1
        return self

    def copy(self):
        """returns a copy of the instance"""
        return better_iter(self.list, self.loop, self.index)

    def __str__(self): return str(self.list[self.index])
     
    def __int__(self): return int(self.list[self.index])

    def __index__(self): return self.list[self.index]

    def __hash__(self): return self.list[self.index]

    def __repr__(self):
        output = str(self.list)
        output = "<" + output[1:-1] + ">"
        return output
    
    def __eq__(self, other): return self.list[self.index] == other

    def __gt__(self, other): return self.list[self.index] > other
    
    def __ge__(self, other): return self.list[self.index] >= other

    def __lt__(self, other): return self.list[self.index] < other

    def __le__(self, other): return self.list[self.index] <= other

    def __add__(self, other):
        val = self.list[self.index]

        # determines whether to return a float or int
        if float(val) % 1 == 0: return int(val) + other
        else: return float(val) + other

    def __sub__(self, other):
        val = self.list[self.index]

        # determines whether to return a float or int
        if float(val) % 1 == 0: return int(val) - other
        else: return float(val) - other

    def __getitem__(self, index): return self.list[index]

    def __len__(self): return len(self.list)

def previous(arg: better_iter): return arg.__previous__()


class better_dict(dict):
    """if keys are created with iterables (not including strings),
    you can access the value with any one of the items in the iterable
    
    default value is accessed if key not found, if there is no default
    value, KeyError is raised as normal"""
    
    NONE = object()
    _ = lambda: _ # type: ignore

    def __init__(self, _dict: dict, default = NONE):
        if default != self.NONE:
            _dict.update({self._: default})
  
        super().__init__(_dict)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:

            # sees if key is value in iterable
            for _key in self.keys(): # stops strings from counting
                if isinstance(_key, Iterable) and type(_key) != str:
                    if key in _key:
                        return super().__getitem__(_key)

            if self._ in super().keys(): return super().__getitem__(self._)
            else: raise KeyError(f"key {key} was not found")

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError: # allows access to dictionary keys as attributes
            return self.__getitem__(name)

    @property
    def default(self):
        """default value returned if key not found"""
        if self._ in super().keys(): return super().__getitem__(self._)
        else: return None

    @default.setter
    def default(self, value):
        super().update({self._: value})

    @default.deleter
    def default(self):
        try: super().__delitem__(self._)
        except KeyError: pass