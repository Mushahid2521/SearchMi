import math
import random
import pickle
from concurrent.futures import ThreadPoolExecutor
from scipy.stats import mannwhitneyu, ttest_ind, f_oneway
import pandas as pd


class SimulatedAnnealing:
    """
    A class encapsulating a genetic algorithm to select subsets of species
    based on the Mann-Whitney U test p-value.

    Parameters
    ----------
    """

    def __init__(
            self
    ):
        self.search_abundance = None
        self.metadata = None
        # self.search_disease = search_disease
        self.positive_label = None
        self.soi_list = None
        self.output_column = None

        self.no_iterations = 1000
        self.temp = 10000
        self.cooling_rate = 0.40

        self.objective_function = "Mann-Whitney"
        self.hypothesis_selection = 'two-sided'
        self.signature_type = 'positive'
        self.output_label_categories = None
        # Default checkpoint filename if not provided
        # if checkpoint_file is None:
        #     checkpoint_file = f'genetic_checkpoint_less_either_10_prevalence.pkl'
        self.checkpoint_file = ''
        self.stop_strategy = True
        self.improvement_patience = 10
        self.random_seed = 42

        self._cost_cache = {}
        self.current_solution = []
        self.current_cost = float('inf')
        self.next_solution = []
        self.next_cost = float('inf')
        self.current_best_solution = []
        self.current_best_score = float('inf')
        self.no_improvement_counter = 0
        self.current_iteration = -1
        self.tracking_generations = {}
        # random.seed(42)

    def reinit_ga_data(self):
        self._cost_cache = {}
        self.current_solution = []
        self.current_cost = float('inf')
        self.next_solution = []
        self.next_cost = float('inf')
        self.current_best_solution = []
        self.current_best_score = float('inf')
        self.no_improvement_counter = 0
        self.current_iteration = -1
        self.tracking_generations = {}

    def set_random_seed(self):
        pass
        # random.seed(self.random_seed)

    def _t_test_cost_function(self, GroupA_data, GroupB_data):
        # Welch's T-test
        if self.hypothesis_selection == 'one-sided':
            if self.signature_type == 'positive':
                stat, p_value = ttest_ind(a=GroupA_data, b=GroupB_data, equal_var=False, alternative='greater')
            else:
                stat, p_value = ttest_ind(a=GroupA_data, b=GroupB_data, equal_var=False, alternative='less')
            return p_value

        elif self.hypothesis_selection == 'two-sided':
            stat, p_value = ttest_ind(a=GroupA_data, b=GroupB_data, equal_var=False, alternative='two-sided')
            return p_value

    def _mann_whitney_u_test(self, GroupA_data, GroupB_data):
        if self.hypothesis_selection == 'one-sided':
            if self.signature_type == 'positive':
                stat, p_value = mannwhitneyu(GroupA_data, GroupB_data, alternative='greater')
            else:
                stat, p_value = mannwhitneyu(GroupA_data, GroupB_data, alternative='less')
            return p_value

        elif self.hypothesis_selection == 'two-sided':
            stat, p_value = mannwhitneyu(GroupA_data, GroupB_data, alternative='two-sided')
            return p_value

    def _calculate_cost_two_groups(self, species_list):
        """
        Calculates the p-value for the Mann-Whitney U test for the given set
        of species, comparing disease vs control.
        """
        if not species_list:
            # If no species selected, return a high p-value so that this solution
            # is less likely to be considered the best.
            return 1.0

        current_abundance_df = self.search_abundance[species_list]
        richness_df = current_abundance_df.apply(lambda x: x.sum(), axis=1)
        data = pd.concat([richness_df.rename('richness'), self.metadata], axis=1)

        if self.hypothesis_selection == 'one-sided':
            positive_label = self.positive_label
        else:
            positive_label = self.output_label_categories[0]

        GroupA_data = data[data[self.output_column] == positive_label]['richness']
        GroupB_data = data[data[self.output_column] != positive_label]['richness']

        if self.objective_function == 'Mann-Whitney U-test':
            p_val = self._mann_whitney_u_test(GroupA_data=GroupA_data, GroupB_data=GroupB_data)
            return p_val

        if self.objective_function == "Welch's T-test":
            p_val = self._t_test_cost_function(GroupA_data=GroupA_data, GroupB_data=GroupB_data)
            return p_val

    def _calculate_cost_three_groups(self, species_list):
        """
        Calculates the p-value for the Mann-Whitney U test for the given set
        of species, comparing disease vs control.
        """
        if not species_list:
            # If no species selected, return a high p-value so that this solution
            # is less likely to be considered the best.
            return 1.0

        current_abundance_df = self.search_abundance[species_list]
        richness_df = current_abundance_df.apply(lambda x: x.sum(), axis=1)
        data = pd.concat([richness_df.rename('richness'), self.metadata], axis=1)

        GroupA_data = data[data[self.output_column] == self.output_label_categories[0]]['richness']
        GroupB_data = data[data[self.output_column] == self.output_label_categories[1]]['richness']
        GroupC_data = data[data[self.output_column] == self.output_label_categories[2]]['richness']

        if self.objective_function == "One Way-ANOVA":
            _, p_value = f_oneway(GroupA_data, GroupB_data, GroupC_data)
            return p_value

        # if self.objective_function == "Welch's ANOVA":
        #     p_val = self._t_test_cost_function(GroupA_data=GroupA_data, GroupB_data=GroupB_data)
        #     return p_val

    def get_species_name(self, best_solution):
        """
        Given a binary combination list, returns the names of species selected (1s).
        """
        selected_species = []
        for i, bit in enumerate(best_solution):
            if bit == 1:
                selected_species.append(self.soi_list[i])
        return selected_species

    def _evaluate(self, combination):
        """
        Evaluates the combination by computing (or retrieving) the p-value from the cache.
        """
        combination_key = tuple(combination)
        if combination_key in self._cost_cache:
            return self._cost_cache[combination_key]

        # Extract the selected species
        combination_species = [
            self.soi_list[i]
            for i, bit in enumerate(combination)
            if bit == 1
        ]

        # Compute the p-value for two groups
        if len(self.output_label_categories) == 2:
            p_val = self._calculate_cost_two_groups(combination_species)
            self._cost_cache[combination_key] = p_val
            return p_val
        elif len(self.output_label_categories) == 3:
            p_val = self._calculate_cost_three_groups(combination_species)
            self._cost_cache[combination_key] = p_val
            return p_val

    def _generate_neighbour(self, solution):
        neighbour = solution.copy()
        idx = random.randint(0, len(solution) - 1)
        neighbour[idx] = 0 if neighbour[idx] == 1 else 1
        return neighbour

    def _acceptance_probability(self, old_cost, new_cost, temperature):
        if new_cost < old_cost:
            return 1.0
        else:
            return math.exp((old_cost - new_cost) / temperature)

    def _save_checkpoint(self, state, filename=None):
        """
        Saves current state (population, generation, etc.) to a pickle file.
        """
        if filename is None:
            filename = self.checkpoint_file
        with open(filename, 'wb') as f:
            pickle.dump(state, f)

    def _load_checkpoint(self, filename=None):
        """
        Loads a previously saved state from a pickle file.
        """
        if filename is None:
            filename = self.checkpoint_file
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None

    def run_one_iteration(self):
        num_items = len(self.soi_list)
        self.current_iteration += 1

        if self.current_iteration == 0:
            self.current_solution = [1 for _ in range(num_items)]

        elif self.current_iteration == 1:
            self.current_solution = [random.choice([1, 0]) for _ in range(num_items)]

        self.current_cost = self._evaluate(self.current_solution)

        self.next_solution = self._generate_neighbour(self.current_solution)
        self.next_cost = self._evaluate(self.next_solution)

        if self._acceptance_probability(self.current_cost, self.next_cost, self.temp) > random.random():
            self.current_solution, self.current_cost = self.next_solution, self.next_cost

            self.temp *= self.cooling_rate

        self.tracking_generations[self.current_iteration] = {
            'current_solution': self.get_species_name(self.current_solution),
            'best_score': self.current_cost,
        }

        if self.current_cost < self.current_best_score:
            self.current_best_score = self.current_cost
            self.current_best_solution = self.get_species_name(self.current_solution)
            self.no_improvement_counter = 0
        else:
            self.no_improvement_counter += 1
