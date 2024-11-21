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
        # two children
        elif self.operator[0] == '*':
            product = 1
            for node in self.children:
                product *= node.calculate()
            self.value = product
            return self.value
        elif self.operator[0] == '+':
            sum_total = 0
            for node in self.children:
                sum_total += node.calculate()
            self.value = sum_total
            return self.value
        elif self.operator[0] == '-':
            total = self.children[0].calculate() - self.children[1].calculate()
            self.value = total
            return self.value
        # one child
        elif self.operator[0] == 'first_grad':
            self.value = first_gradient(self.children[0].calculate())
            return self.value
        elif self.operator[0] == 'second_grad':
            self.value = second_gradient(self.children[0].calculate())
            return self.value
        else:
            print("NOOOOOOOOO")
    def calculate_string(self):
        if self.children==None:
            # sanity check
            if self.string == None:
                Exception("self.string shouldnt be none at leaf")
            return
        for child in self.children:
            child.calculate_string()
        if self.operator[1] == 2:
            return_string = f"({self.children[0].string} {self.operator[0]} {self.children[1].string})"
        else:
            return_string = f"{self.operator[0]}({self.children[0].string})"
        self.string = return_string
    def randomly_select_node(self, depth=0):

        if depth > 0 and random.random() < 0.05 or self.children == None:
            return self, depth
        # explore this random node
        return random.choice(self.children).randomly_select_node(depth=depth + 1)

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