from Node import Node
import random
from copy import deepcopy
import numpy as np
import re
class Tree:
    def __init__(self, root=None, parents=None, operators=None, terminals=None, type=None, desired_value=None):
        self.operators = operators
        self.terminals = terminals
        self.min_depth = 2 # really annoying when it is 0
        self.max_depth = 3
        self.parents = parents  # list of parents => 0
        self.desired_value = desired_value  # what the output should converge towards
        # if type == "burger":
        #     self.root = self.string_to_tree()
        # else:
        #     self.root = self.random_tree()
        self.root = self.random_tree()  # root node of individual tree
        self.root.connect_parent_nodes()  # give every child a parent_node
        # print(self.show_tree())
        self.calculate_tree()  # calculate value of tree
        self.evaluate_tree()  # fitness/other values
        # print(self.metrics)

    def random_tree(self, depth=0, node_type=None, child_type=None):
        if depth > self.min_depth and (depth == self.max_depth or random.random() < 0.1):
            # if node type given a matrix, it means that the parent expects a matrix
            if node_type == "matrix":
                choice = self.terminals[0]
            else:
                # Randomly choose to create a terminal (leaf node)
                choice = random.choice(self.terminals)
            leaf_node = Node(value=choice[1])
            leaf_node.string = choice[0]
            leaf_node.node_type = choice[2]
            # Dirty solution, should be nice
            leaf_node.operator = ("leaf", 0)
            return leaf_node
        else:
            # if node_type is a matrix, then one of the children also has to be a matrix
            child_type = node_type
            # Create an internal node with a random function and two children
            operator = random.choice(self.operators)

            if operator[0] == 'first_grad' or operator[0] == 'second_grad':
                child_type = "matrix"

            children = []
            strings = []
            for i in range(operator[2]):
                child = self.random_tree(depth + 1, node_type=child_type)
                children.append(child)
                strings.append(child.string)

            if len(children) == 2 and children[0].node_type == children[1].node_type:
                node_type = children[0].node_type
            else:
                node_type = "matrix"

            if operator[2] == 2:
                return_string = f"({strings[0]} {operator[0]} {strings[1]})"
            else:
                return_string = f"{operator[0]}({strings[0]})"
            return Node(operator=operator, children=children, string=return_string, node_type=node_type)
    # def specified_tree(self, type="burger"):
    #     if type == "burger":
    #         tree = Node.string_to_tree()
    #     return tree
    # def string_to_tree(self, string="((0.1 * second_grad(u)) - (u * first_grad(u)))"):
    #     # Used for creating tree by hand or from saved strings, brackets denote one depth deeper for operator specified
    #     # Spaces need to be correctly denoted (for finding roots)
    #     # Find middle operator (root of tree)
    #     # list of strings from terminals
    #     string_terminals = [t[0] for t in self.terminals]
    #     # strings of operators, used for checking which operator current node is
    #     string_operators = [op[0] for op in self.operators]
    #
    #     # always two or one children per string
    #     def split_string(s):
    #
    #         # if function has one child
    #         if any(string.startswith(prefix) for prefix in string_operators) or any(string.startswith(prefix) for prefix in string_terminals):
    #             return[string]
    #
    #
    #         new_string = s[1:-1]
    #         print("NEWSTRING")
    #         print(new_string)
    #         # count opening brackets and minus closing brackets
    #         counter = 0
    #         last_index = 0
    #         parts = []
    #
    #         for i, char in enumerate(new_string):
    #             if char == '(':
    #                 counter += 1
    #             elif char == ')':
    #                 counter -= 1
    #             elif char == ' ':
    #                 continue
    #             # if closing and opening brackets are equal, that is first part of string
    #             print(char)
    #             if counter == 0 and (char in string_operators):
    #                 parts.append(new_string[0:i-1])
    #                 parts.append(new_string[i:i+1])
    #                 parts.append(new_string[i+2:])
    #                 last_index = i + 2
    #             # # parts append if second grad
    #             # elif new_string[last_index:i]:
    #             #     last_index = i + 1
    #         print("parts")
    #         print(parts)
    #         return parts
    #
    #     splitted_string = split_string(string)
    #     print(splitted_string)
    #     if len(splitted_string)==1:
    #         # check which terminal node should be
    #         if splitted_string[0] in string_terminals:
    #             terminal = self.terminals[string_terminals.index(splitted_string[0])]
    #             leaf_node = Node(value=terminal[1])
    #             leaf_node.string = terminal[0]
    #             leaf_node.node_type = terminal[2]
    #             # Dirty solution, should be nice
    #             leaf_node.operator = ("leaf", 0)
    #             return leaf_node
    #         else:
    #             Exception("Terminal not found in given terminals")
    #
    #     else:
    #         children = []
    #
    #         # Should be not none after loop, every splitted string should have at index 1 an operator, except if its a leaf
    #         operator = None
    #         for part in splitted_string:
    #             # single child operators
    #             if any(part.startswith(prefix) for prefix in string_operators):
    #                 index = None
    #                 for i, operator_string in enumerate(string_operators):
    #                     # Check if the part starts with any of the prefixes in string_operators
    #                     if part.startswith(operator_string):
    #                         index = i
    #                 operator = self.operators[index]
    #             elif part in string_operators:
    #                 operator = self.operators[string_operators.index(part)]
    #             else:
    #                 # Change string into operator
    #                 node = self.string_to_tree(string=part)
    #                 children.append(node)
    #                 if node == None:
    #                     print("NOO")
    #         print(children)
    #         print(operator)
    #         print(children[0].string)
    #
    #         # print(children[1].string)
    #
    #         if len(children) == 2 and children[0].node_type == children[1].node_type:
    #             node_type = children[0].node_type
    #         else:
    #             node_type = "matrix"
    #         return Node(operator=operator, children=children, string=string, node_type=node_type)
    def calculate_tree(self):
        # calculate tree
        self.value = self.root.calculate()

    def evaluate_tree(self):
        # evaluate fitness for now
        self.metrics = [np.sqrt(np.absolute(((self.desired_value - self.value) ** 2).mean(axis=-1).mean()))]

    def show_tree(self):
        return self.root.string
    def calculate_string(self):
        self.root.calculate_string()
    def copy(self):
        return deepcopy(self)
    # def has_scalars(self):
    #
    #     return True
    # def update_scalars(self):
    #     if self.has_scalars():

    def mutate(self):
        # copy self
        copied_tree = self.copy()
        # print("Before")
        # print(f"Original: {self.root.string}")
        # print(f"Copy:     {copied_tree.root.string}")
        # Select node randomly starting from root node
        node, depth = copied_tree.root.randomly_select_node()

        # generate new tree starting from depth
        new_node = copied_tree.random_tree(depth=depth, node_type=node.node_type)

        # replace node
        node.parent.replace(node, new_node)

        # connect new node with parent
        new_node.connect_parent_nodes(parent=node.parent)

        # Recalculate full tree
        copied_tree.calculate_tree()

        # evaluate full tree
        copied_tree.evaluate_tree()

        # calculate string
        copied_tree.calculate_string()
        # print(f"Original: {self.root.string}")
        # print(f"Copy:     {copied_tree.root.string}")
        return copied_tree

    # def replace(self, node, new_node)
    # start by searching for old node

    # if node found, replace in children list of parent node