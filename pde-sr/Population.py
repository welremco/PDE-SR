from Tree import Tree


class Population:
    def __init__(self, n_trees, operators, terminals, desired_value):
        self.trees = [Tree(operators=operators, terminals=terminals, desired_value=desired_value) for i in
                      range(n_trees)]  # generate random trees according to specified number
        self.operators = operators  # list of types
        self.terminals = terminals  # list of possible leaf nodes

    def update_population(self):
        # updates population
        return

    def calculate_population(self):
        # calculates values of trees in population
        return