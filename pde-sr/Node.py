import random
import numpy as np
import scipy.io as scio
from numpy.f2py.auxfuncs import throw_error


class Node:

    def __init__(self, parent=None, children=None, operator=None, value=None, string=None, node_type=None):
        self.parent = parent  # single parent_node
        self.children = children  # list of subnodes (0, 1 or 2)
        self.operator = operator  # type of operator (+,-,*,gradient)
        self.value = value  # value of node
        self.string = string  # string of node
        self.node_type = node_type  # type of node (scalar or matrix)

    def calculate(self):
        if self.operator[0] == 'leaf':
            return self.value
        elif self.operator[2] == 2:
            self.value = self.operator[1](self.children[0].calculate(), self.children[1].calculate())
            return self.value
        elif self.operator[2] == 1:
            self.value = self.operator[1](self.children[0].calculate())
            return self.value
        else:
            Exception("Operator doesn't have one or two input values")

    def calculate_string(self):
        if self.children==None:
            # sanity check
            if self.string == None:
                Exception("self.string shouldnt be none at leaf")
            return
        for child in self.children:
            child.calculate_string()
        if self.operator[2] == 2:
            return_string = f"({self.children[0].string} {self.operator[0]} {self.children[1].string})"
        else:
            return_string = f"{self.operator[0]}({self.children[0].string})"
        self.string = return_string
    def randomly_select_node(self, depth=0):

        if depth > 0 and random.random() < 0.5 or self.children == None:
            return self, depth
        # explore this random node
        return random.choice(self.children).randomly_select_node(depth=depth + 1)

    # def string_to_tree(self, string="((0.1 * second_grad(u)) - (u * first_grad(u)))"):
    #     # Used for creating tree by hand or from saved strings, brackets denote one depth deeper for operator specified
    #     # Spaces need to be correctly denoted (for finding roots)
    #     # Find middle operator (root of tree)
    #     def split_string(s):
    #         # This regular expression matches everything between parentheses and treats it as a single entity
    #         # or matches spaces to split the string
    #         pattern = r'(\([^)]*\))|\s+'
    #
    #         # Split using the regex pattern
    #         parts = re.split(pattern, s)
    #         parts = [part for part in parts if part]
    #         # add remaining back parentheses (should be done easier but idk how)
    #         new_parts = []
    #         for part in parts:
    #             if all(c == ')' for c in part):
    #                 new_parts[-1] = new_parts[-1] + part
    #             else:
    #                 new_parts.append(part)
    #         # Remove empty strings and return the result
    #         return new_parts
    #     def string_to_operator(char=None):
    #
    #         return
    #     splitted_string = split_string(string)
    #     print(splitted_string)
    #     for part in splitted_string:
    #         if len(part) == 1:
    #             # Change string into operator
    #             operator = string_to_operator(part)
    #         else:
    #             node = string_to_tree(string=part)
    #     return node
    def connect_parent_nodes(self, parent=None):
        self.parent = parent
        if self.children is None:
            return
        for child in self.children:
            child.connect_parent_nodes(parent=self)

    def replace(self, node, new_node):
        for i, child in enumerate(self.children):
            if child == node:
                self.children[i] = new_node
                return
        raise Exception("No node to replace found")

data = scio.loadmat('./data/burgers.mat')

x=np.squeeze(data.get("x"))

def first_gradient(u, x=x):
    return np.apply_along_axis(np.gradient, 1, u, x)
def second_gradient(u, x=x):
    return np.apply_along_axis(np.gradient, 1, np.apply_along_axis(np.gradient, 1, u, x), x)
def nonlinear_part(u, x=x):
    return u*np.apply_along_axis(np.gradient, 1, u, x)
def add(left, right):
    return left + right
def multiply(left,right):
    return left*right
def subtract(left, right):
    return left-right