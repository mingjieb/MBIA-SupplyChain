#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

import numpy as np
import math

def ga_model():
    pareto_solutions = []

    return pareto_solutions

def initialize_population(pop_size, n_genes, input_limits):
    """
    Initializes the population of the problem according to the
    population size and number of genes.
    :param pop_size: number of individuals in the population
    :param n_genes: number of genes (variables) in the problem
    :param input_limits: tuple containing the minimum and maximum allowed
    :return: a numpy array with a randomly initialized population
    """

    population = np.random.uniform(
      input_limits[0], input_limits[1], size=(pop_size, n_genes)
    )

    return population

def fitness_function(individual):
    """
    Implements the logic that calculates the fitness
    measure of an individual.
    :param individual: chromosome of genes representing an individual
    :return: the fitness of the individual
    """

    raise NotImplementedError


def select_parents(self, selection_strategy, n_matings, prob_intervals):
    """
    Selects the parents according to a given selection strategy.
    Options are:
    roulette_wheel: Selects individuals from mating pool giving
    higher probabilities to fitter individuals.

    :param selection_strategy: the strategy to use for selecting parents
    :param n_matings: the number of matings to perform
    :param prob_intervals: the selection probability for each individual in
     the mating pool.
    :return: 2 arrays with selected individuals corresponding to each parent
    """

    ma, pa = None, None

    if selection_strategy == "roulette_wheel":
        ma = np.apply_along_axis(
            lambda value: np.argmin(value > prob_intervals) - 1, 1, np.random.rand(n_matings, 1)
        )
        pa = np.apply_along_axis(
            lambda value: np.argmin(value > prob_intervals) - 1, 1, np.random.rand(n_matings, 1)
        )

    return ma, pa


def create_offspring(first_parent, sec_parent, crossover_pt, offspring_number):
    """
    Creates an offspring from 2 parents. It performs the crossover
    according the following rule:
    p_new = first_parent[crossover_pt] + beta * (first_parent[crossover_pt] - sec_parent[crossover_pt])
    offspring = [first_parent[:crossover_pt], p_new, sec_parent[crossover_pt + 1:]
    where beta is a random number between 0 and 1, and can be either positive or negative
    depending on if it's the first or second offspring
    :param first_parent: first parent's chromosome
    :param sec_parent: second parent's chromosome
    :param crossover_pt: point(s) at which to perform the crossover
    :param offspring_number: whether it's the first or second offspring from a pair of parents.

    :return: the resulting offspring.
    """

    beta = (
        np.random.rand(1)[0]
        if offspring_number == "first"
        else -np.random.rand(1)[0]
    )

    p_new = first_parent[crossover_pt] - beta * (
            first_parent[crossover_pt] - sec_parent[crossover_pt]
    )

    return np.hstack(
        (first_parent[:crossover_pt], p_new, sec_parent[crossover_pt + 1:])
    )


def mutate_population(population, n_mutations, input_limits):
    """
    Mutates the population by randomizing specific positions of the
    population individuals.
    :param population: the population at a given iteration
    :param n_mutations: number of mutations to be performed.
    :param input_limits: tuple containing the minimum and maximum allowed
     values of the problem space.

    :return: the mutated population
    """

    mutation_rows = np.random.choice(
        np.arange(1, population.shape[0]), n_mutations, replace=True
    )

    mutation_columns = np.random.choice(
        population.shape[1], n_mutations, replace=True
    )

    new_population = np.random.uniform(
        input_limits[0], input_limits[1], size=population.shape
    )

    population[mutation_rows, mutation_columns] = new_population[mutation_rows, mutation_columns]

    return population


def solve():
    """
    Performs the genetic algorithm optimization according to the
    global scope initialized parameters

    :return: (best individual, best fitness)
    """

    # initialize the population
    population = initialize_population(pop_size, n_genes)

    # Calculate the fitness of the population
    fitness = calculate_fitness(population)

    # Sort population by fitness
    fitness, population = sort_by_fitness(fitness, population)

    gen_n = 0
    while True:

        gen_n += 1

        # Get parents pairs
        ma, pa = select_parents(selection_strategy, n_matings, fitness, prob_intervals)

        # Get indices of individuals to be replaced
        ix = np.arange(0, pop_size - pop_keep - 1, 2)

        # Get crossover point for each individual
        xp = np.random.randint(0, n_genes, size=(pop_size, 1))

        for i in range(xp.shape[0]):
            # create first offspring
            population[-1 - ix[i], :] = create_offspring(
                population[ma[i], :], population[pa[i], :], xp[i], "first"
            )

            # create second offspring
            population[-1 - ix[i] - 1, :] = create_offspring(
                population[pa[i], :], population[ma[i], :], xp[i], "second"
            )

        population = mutate_population(population, n_mutations, input_limits)

        # Get new population's fitness. Since the fittest element does not change,
        # we do not need to re calculate its fitness
        fitness = np.hstack((fitness[0], calculate_fitness(population[1:, :])))

        fitness, population = sort_by_fitness(fitness, population)

        if gen_n >= max_gen:
            break

        return population[0], fitness[0]


def calculate_fitness(population):
    """
    Calculates the fitness of the population
    :param population: population state at a given iteration
    :return: the fitness of the current population
    """

    return np.array(list(map(fitness_function, population)))


def sort_by_fitness(fitness, population):
    """
    Sorts the population by its fitness.
    :param fitness: fitness of the population
    :param population: population state at a given iteration
    :return: the sorted fitness array and sorted population array
    """

    sorted_fitness = np.argsort(fitness)[::-1]

    population = population[sorted_fitness, :]
    fitness = fitness[sorted_fitness]

    return fitness, population


def get_selection_probabilities(selection_strategy, pop_keep):
    if selection_strategy == "roulette_wheel":

        mating_prob = (
                              np.arange(1, pop_keep + 1) / np.arange(1, pop_keep + 1).sum()
                      )[::-1]

        return np.array([0, *np.cumsum(mating_prob[: pop_keep + 1])])

    elif selection_strategy == "random":
        return np.linspace(0, 1, pop_keep + 1)