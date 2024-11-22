from Tree import Tree


class Population:
    def __init__(self, n_trees, operators, terminals, desired_value):
        self.trees = [Tree(operators=operators, terminals=terminals, desired_value=desired_value) for i in
                      range(n_trees)]  # generate random trees according to specified number
        self.operators = operators  # list of types
        self.terminals = terminals  # list of possible leaf nodes

    def update_population(self):
        # updates population
        # mutate all trees and save if metrics improve

        new_trees = []
        for tree in self.trees:
            new_tree = tree.mutate()
            # TODO update for multi objective
            if new_tree.metrics[0] < tree.metrics[0]:
                new_trees.append(new_tree)
            else:
                new_trees.append(tree)
        self.trees = new_trees
        return

    def calculate_population(self):
        # calculates values of trees in population
        return