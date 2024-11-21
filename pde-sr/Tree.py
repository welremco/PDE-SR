from Node import Node
import random

class Tree:
    def __init__(self, root=None, parents=None, operators=None, terminals=None, fitness=None, desired_value=None):
        self.operators = operators
        self.terminals = terminals
        self.min_depth = 2 # really annoying when it is 0
        self.max_depth = 3
        self.parents = parents  # list of parents => 0
        self.desired_value = desired_value  # what the output should converge towards

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
            leaf_node.operator = ("leaf", 0)
            return leaf_node
        else:
            # if node_type is a matrix, then one of the children also has to be a matrix
            child_type = node_type
            # Create an internal node with a random function and two children
            operator = random.choice(list(self.operators.items()))
            if operator[0] == 'first_grad' or operator[0] == 'second_grad':
                child_type = "matrix"

            children = []
            strings = []
            for i in range(operator[1]):
                child = self.random_tree(depth + 1, node_type=child_type)
                children.append(child)
                strings.append(child.string)

            if len(children) == 2 and children[0].node_type == children[1].node_type:
                node_type = children[0].node_type
            else:
                node_type = "matrix"

            if operator[1] == 2:
                return_string = f"({strings[0]} {operator[0]} {strings[1]})"
            else:
                return_string = f"{operator[0]}({strings[0]})"
            return Node(operator=operator, children=children, string=return_string, node_type=node_type)

    def calculate_tree(self):
        # calculate tree
        self.value = self.root.calculate()

    def evaluate_tree(self):
        # evaluate fitness for now
        self.metrics = [((self.desired_value - self.value) ** 2).mean(axis=-1).mean()]

    def show_tree(self):
        return self.root.string
    def calculate_string(self):
        self.root.calculate_string()
    def mutate(self):
        # Select node randomly starting from root node
        node, depth = self.root.randomly_select_node()

        # generate new tree starting from depth
        new_node = self.random_tree(depth=depth, node_type=node.node_type)

        # replace node
        node.parent.replace(node, new_node)

        # connect new node with parent
        new_node.connect_parent_nodes(parent=node.parent)

        # Recalculate full tree
        self.calculate_tree()

        # evaluate full tree
        self.evaluate_tree()

        # calculate string
        self.calculate_string()



    # def replace(self, node, new_node)
    # start by searching for old node

    # if node found, replace in children list of parent node