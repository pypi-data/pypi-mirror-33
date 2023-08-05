"""
LED_Analyze - calc_common
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""
from hashlib import sha1
from copy import copy

class CalcProcess(object):
    """
    Base object for all calculation steps. Defines the inheritance
    structure, inputs (str names), and output (references to DataObject
    instances).
    """    
    def __init__(self, parents):
        
        self.inputs = []
        self.__parents = parents
        self.__children = []
        self.outputs = []
        
        for obj in parents:
            obj.adopt(self)
    
    @property
    def parents(self):
        return tuple(self._CalcProcess__parents)
    
    @property
    def children(self):
        return tuple(self._CalcProcess__children)
    
    def get_ancestors(self):
        
        ancestors = []
        ancestors.extend(self.parents)
        
        for obj in self.parents:
            ancestors.extend(obj.get_ancestors())
        
        return tuple(set(ancestors))
    
    def get_descendants(self):
        
        descendants = []
        descendants.extend(self.children)
        
        for obj in self.children:
            descendants.extend(obj.get_descendants())
            
        return tuple(set(descendants))
    
    def test_dependence(self, calc):
        
        return calc in self.get_descendants()
    
    def test_inheritance(self, calc):
        
        return calc in self.get_ancestors()
    
    def adopt(self, child):
        
        self._CalcProcess__children.append(child)
    
    def remove_data(self):
        
        remove_calc_list = [self]
        remove_out_list = self.outputs
        
        # Remove references to current calc in parent calcs
        for obj in self.parents:
            if self in obj._CalcProcess__children: 
                obj._CalcProcess__children.remove(self)
        
        # Remove all children calcs and gather list of outputs to remove
        for obj in self.children:
            garbage = obj.remove_data()
            remove_calc_list.extend(garbage[0])
            remove_out_list.extend(garbage[1])
            obj._CalcProcess__parents.remove(self)
        
        return (tuple(set(remove_calc_list)), tuple(set(remove_out_list)))
    
    def switcheroo(self, new_calc):
        
        # Switch references from old calc to new in parent calcs
        for obj in self.parents:
            if self in obj._CalcProcess__children:
                obj._CalcProcess__children.insert(
                    obj._CalcProcess__children.index(self), new_calc)
                obj._CalcProcess__children.remove(self)
        
        # Switch references from old calc to new in child calcs
        for obj in self.children:
            if self in obj._CalcProcess__parents:
                obj._CalcProcess__parents.insert(
                    obj._CalcProcess__parents.index(self), new_calc)
                obj._CalcProcess__parents.remove(self)
    
    def check(self):
        
        # Default calculation check. Automatically proceed without errors
        
        return None
    
    def gen_hash(self):
        
        # Generate a hash to capture whether or not the calc process has
        # been modified. Neglect the state of the output
        return sha1(str(id(self)).encode("utf-8")).hexdigest()