import random

from Tree import Tree


class Population:
    def __init__(self, n_trees, operators, terminals, desired_value):
        self.trees = [Tree(operators=operators, terminals=terminals, desired_value=desired_value) for i in
                      range(n_trees)]  # generate random trees according to specified number
        # self.trees.append(Tree(operators=operators, terminals=terminals, desired_value=desired_value, type='burger'))
        self.operators = operators  # list of types
        self.terminals = terminals  # list of possible leaf nodes
        self.desired_value = desired_value

    def update_population(self):
        # updates population
        # mutate all trees and save if metrics improve

        new_trees = []

        # add best n individuals to population #TODO update for generic multiobjective
        n = 1
        new_trees.extend(sorted(self.trees, key=lambda tree: tree.metrics[0])[:n])
        # add 10% new trees every population
        new_trees.extend([Tree(operators=self.operators, terminals=self.terminals, desired_value=self.desired_value) for i in range(round(0.1*len(self.trees)))])

        while len(new_trees) < len(self.trees):
            new_tree, tree2 = self.tournament_selection(k=10)
            # crossover chance
            if random.random() < 0.5:
                new_tree = new_tree.crossover(tree2)
            # mutation chance
            if random.random() < 0.5:
                new_tree = new_tree.mutate()

            # optimize scalars
            new_tree.update_scalars()

            # new_tree.update_scalars_torch()


            # add tree to new population
            new_trees.append(new_tree)

        self.trees = new_trees
        return
    # perform tournament selection, return 2 individuals, with tournament size k, and select n individuals to give back
    def tournament_selection(self, k=10, n=2):
        # randomly select k trees from population
        k_trees = random.sample(self.trees, k=k)

        # order from best to worst metrics #TODO currently only one metric, should be generalized
        k_trees_ordered = sorted(k_trees, key=lambda tree: tree.metrics[0])

        # return n objects
        return k_trees_ordered[:n]
    def calculate_population(self):
        # calculates values of trees in population
        return