import random
import pickle
from concurrent.futures import ThreadPoolExecutor
from scipy.stats import mannwhitneyu, ttest_ind, f_oneway, kruskal
import pandas as pd


class GeneticAlgorithm:
    """
    A class encapsulating a genetic algorithm to select subsets of species
    based on the Mann-Whitney U test p-value.

    Parameters
    ----------
    abundance_data : pd.DataFrame
        Full abundance data with species as columns.
    search_abundance : pd.DataFrame
        Abundance data (subset or same as `abundance_data`) used for evaluation.
    metadata : pd.DataFrame
        Metadata including 'study_condition' column.
    search_disease : str
        Disease label to compare against 'control' in metadata.
    soi_list : list of str
        Species of interest (subset of columns in abundance_data).
    pop_size : int
        Size of the initial population in the GA.
    num_generations : int
        Number of generations to run the GA.
    num_parents : int
        Number of parents to be selected in each generation.
    checkpoint_file : str
        Name of the file used to save/reload checkpoints.
    random_seed : int
        Random seed for reproducibility.
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

        self.pop_size = 300
        self.num_generations = 125
        self.num_parents = 50
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
        self.current_population = []
        self.next_population = []
        self.current_best_solution = []
        self.current_best_score = float('inf')
        self.no_improvement_counter = 0
        self.current_generation = -1
        self.tracking_generations = {}
        random.seed(42)

    def reinit_ga_data(self):
        self._cost_cache = {}
        self.current_population = []
        self.next_population = []
        self.current_best_solution = []
        self.current_best_score = float('inf')
        self.no_improvement_counter = 0
        self.current_generation = -1
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

        if self.objective_function == "Kruskal-Wallis H-test":
            _, p_val = kruskal(GroupA_data, GroupB_data, GroupC_data)
            return p_val

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

    def _create_population(self, pop_size, num_items):
        """
        Creates an initial population of random binary lists.
        """
        return [
            [random.choice([0, 1]) for _ in range(num_items)]
            for _ in range(pop_size)
        ]

    def _select_parents(self, population, fitness, num_parents):
        """
        Selects the best (lowest p-value) parents from the population.
        """
        # Sort by p-value ascending (i.e., smaller is better)
        parents = sorted(zip(population, fitness), key=lambda x: x[1])
        elite_counts = int(num_parents * 0.04)
        elite_solution = [x[0] for x in parents[:elite_counts]]
        parents_for_next = [x[0] for x in parents[elite_counts:num_parents]]
        return elite_solution, parents_for_next

    def _crossover(self, parents, offspring_size):
        """
        Performs crossover (single-point) to produce offspring.
        """
        offspring = []
        # Ensure a valid crossover point
        crossover_point = random.randint(1, len(parents[0]) - 1)

        for _ in range(offspring_size):
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child = parent1[:crossover_point] + parent2[crossover_point:]
            offspring.append(child)

        return offspring

    def _mutate(self, offspring):
        """
        Flips a random bit in each offspring.
        """
        for child in offspring:
            mutation_point = random.randint(0, len(child) - 1)
            child[mutation_point] = 1 - child[mutation_point]
        return offspring

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
        self.current_generation += 1

        if self.current_generation == 0:
            self.current_population = [[1 for _ in range(num_items)]]
            # self.tracking_generations[self.current_generation] = {}

        elif self.current_generation == 1:
            self.current_population = self._create_population(self.pop_size, num_items)

        elif self.next_population is not None and self.current_generation > 1:
            self.current_population = self.next_population

        with ThreadPoolExecutor() as executor:
            fitness = list(executor.map(self._evaluate, self.current_population))

        this_pop_best_score = min(fitness)
        this_pop_best_score_idx = fitness.index(this_pop_best_score)
        this_pop_best_solution = self.get_species_name(self.current_population[this_pop_best_score_idx])
        self.tracking_generations[self.current_generation] = {
            #'population': self.current_population,
            'best_score': this_pop_best_score,
            'best_score_idx': this_pop_best_score_idx,
            'best_solution': this_pop_best_solution
        }

        if this_pop_best_score < self.current_best_score:
            self.current_best_score = this_pop_best_score
            self.current_best_solution = this_pop_best_solution
            self.no_improvement_counter = 0
        else:
            self.no_improvement_counter += 1

        if self.current_generation >= 1:
            elites, parents = self._select_parents(self.current_population, fitness, self.num_parents)
            # Crossover
            offspring = self._crossover(parents, self.pop_size - self.num_parents)
            # Mutation
            offspring = self._mutate(offspring)
            self.next_population = elites + parents + offspring
