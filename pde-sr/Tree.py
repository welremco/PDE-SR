from Node import Node
import random
from copy import deepcopy
import numpy as np
import re
from sklearn.linear_model import SGDRegressor
from sklearn.pipeline import make_pipeline
from scipy.optimize import minimize
import torch

class Tree:
    def __init__(self, root=None, parents=None, operators=None, terminals=None, type=None, desired_value=None):
        self.operators = operators
        self.terminals = terminals
        self.min_depth = 1 # really annoying when it is 0
        self.max_depth = 4
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
        if depth > self.min_depth and (depth == self.max_depth or random.random() < 0.5):
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
            # handle case if one type is a constant and other is matrix -> type is matrix
            elif any(child.node_type == "matrix" for child in children):
                node_type = "matrix"
            # handle case if one type is constant and other is scalar -> type is scalar
            elif any(child.node_type == "scalar" for child in children) and any(child.node_type == "constant" for child in children):
                node_type = "scalar"
            else:
                Exception("Case found outside specified node types")

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
        # calculate value of tree
        self.calculate_tree()
        # evaluate fitness for now
        self.metrics = [np.sqrt(np.absolute(((self.desired_value - self.value) ** 2).mean(axis=None).mean()))]

    def evaluate_tree_scalars(self, scalars):
        for i, scalar_node in enumerate(self.scalar_list):
            scalar_node.value = scalars[i]
            scalar_node.string = f"{scalars[i]}"
        self.evaluate_tree()
        return self.metrics[0]

    def show_tree(self):
        return self.root.string
    def calculate_string(self):
        self.root.calculate_string()
    def copy(self):
        return deepcopy(self)

    def return_scalars(self):
        return self.root.return_scalars()

    def update_scalars(self):
        # find list of nodes which are scalars
        # scalar_list = self.return_scalars()
        self.scalar_list = self.return_scalars()
        # check if list has node in it
        if len(self.scalar_list) > 0:
            # Initial guess: use the current values of all objects
            initial_values = np.array([node.value for node in self.scalar_list])

            # Minimize the objective function using scipy's 'L-BFGS-B' method
            result = minimize(self.evaluate_tree_scalars, initial_values, method='Powell')

            # # Update the objects with the optimized values
            for node, value in zip(self.scalar_list, result.x):
                node.value = value
                node.string = f"{value}"

    def update_scalars_torch(self):
        # find list of nodes which are scalars
        # scalar_list = self.return_scalars()
        self.scalar_list = self.return_scalars()
        # check if list has node in it
        if len(self.scalar_list) > 0:
            # Initial guess: use the current values of all objects
            values = np.array([node.value for node in self.scalar_list])
            values_tensor = torch.tensor(values, requires_grad=True)
            optimizer = torch.optim.Adam([values_tensor], lr=0.01)
            # Minimize the objective function using scipy's 'L-BFGS-B' method
            for step in range(1000):
                optimizer.zero_grad()  # Clear previous gradients

                # Compute the loss value (objective function)
                loss = self.evaluate_tree_scalars(values_tensor)

                # Backpropagate to compute gradients
                loss.backward()

                # Apply the gradients to update the values of the objects
                optimizer.step()

                # Print the progress every 100 steps
                if step % 100 == 0:
                    print(f"Step {step}, Loss: {loss.item()}")
            # # Update the objects with the optimized values
            # for node, value in zip(self.scalar_list, result.x):
            #     node.value = value
            #     node.string = f"{value}"

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
        # copied_tree.calculate_tree()

        # evaluate full tree
        copied_tree.evaluate_tree()

        # calculate string
        copied_tree.calculate_string()
        # print(f"Original: {self.root.string}")
        # print(f"Copy:     {copied_tree.root.string}")
        return copied_tree

    def crossover(self, other_tree):
        # copy self
        copied_tree = self.copy()
        copied_other_tree = other_tree.copy()

        # Select node randomly starting from root node
        node_tree, depth_tree = copied_tree.root.randomly_select_node()

        # select matching node from other tree (same depth and type)
        node_other_tree = copied_other_tree.root.randomly_select_matching_node(specified_type=node_tree.node_type, specified_depth=depth_tree)
        # if node is found that matches criteria
        if node_other_tree is not None:
            # replace node
            node_tree.parent.replace(node_tree, node_other_tree)

            # connect new node with parent
            node_other_tree.connect_parent_nodes(parent=node_tree.parent)

            # Recalculate full tree
            # copied_tree.calculate_tree()

            # evaluate full tree
            copied_tree.evaluate_tree()

            # calculate string
            copied_tree.calculate_string()

        else:
            Exception("No other node of same type found in other tree")
        return copied_tree
    # def replace(self, node, new_node)
    # start by searching for old node

    # if node found, replace in children list of parent node