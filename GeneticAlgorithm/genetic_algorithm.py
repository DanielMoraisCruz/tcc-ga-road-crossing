# genetic_algorithm.py
import math
import random
from typing import List

from DataBase.loggings import Log
from GeneticAlgorithm.random_generator import RandomGenerator
from GeneticAlgorithm.random_interface import RandomInterface
from Models.models import ModelGeneration
from Models.schemas import SchemaProcessResults


class GeneticAlgorithm:
    def __init__(self, mutation_method: str, population: int, selecteds: int = 2, mutation_rate: float = 0.1):
        self.population: int = population
        self.mutation_rate: float = mutation_rate
        self.selecteds: int = selecteds
        self.random_generator: RandomInterface = RandomGenerator()
        self.log = Log('best_citzen_avg_time')
        self.mutation_method: str = mutation_method

    def crossover(self, results_returned: list[SchemaProcessResults]):
        if not results_returned:
            raise ValueError('Results returned is empty')

        parents: List = self.select(results_returned)
        if not parents:
            return None

        new_population: List = []

        all_reds: List = []
        all_greens: List = []
        all_cycles: List = []

        for parent in parents:
            all_reds.append([crossing['redDuration'] for crossing in parent])
            all_greens.append([crossing['greenDuration'] for crossing in parent])
            all_cycles.append([crossing['cycleStartTime'] for crossing in parent])

        while len(new_population) < self.population:
            reds_selecteds = []
            greens_selecteds = []
            cycles_selecteds = []

            _light = []
            for j in range(3):
                for i in range(len(parents) - 1):
                    reds_selecteds.append(all_reds[self.random_generator.randint(0, 1)][i])
                    greens_selecteds.append(all_greens[self.random_generator.randint(0, 1)][i])
                    cycles_selecteds.append(all_cycles[self.random_generator.randint(0, 1)][i])

                _light.append({
                    'redDuration': self.random_generator.choice(reds_selecteds),
                    'greenDuration': self.random_generator.choice(greens_selecteds),
                    'cycleStartTime': self.random_generator.choice(cycles_selecteds),
                })

            new_population.append(_light)

        if self.mutation_method == 'rim':
            new_population = self.random_individual_based_mutation(new_population)
        elif self.mutation_method == 'pbm':
            new_population = self.probability_based_mutation(new_population)
        else:
            raise ValueError('Método de mutação não foi parametrizado corretamente')

        new_population = new_population[: -self.selecteds]

        for parent in parents:
            new_population.append(parent)

        return new_population

    def random_individual_based_mutation(self, generation):
        gen_length = len(generation)
        mutated_qty = math.floor(gen_length * self.mutation_rate)

        num_replacements = mutated_qty
        random_positions = random.sample(range(len(generation)), num_replacements)
        for pos in random_positions:
            citizen = generation[pos]
            for semaphore in citizen:
                semaphore['redDuration'] = self.random_generator.randint(15, 75)
                semaphore['greenDuration'] = self.random_generator.randint(15, 75)
                # ciclo max tem que ser max de red ou green
                semaphore['cycleStartTime'] = self.random_generator.randint(0, 75)

        return generation

    def probability_based_mutation(self, generation):
        for individual in generation:
            random_nun = self.random_generator.random()
            for semaphore in individual:
                if random_nun < self.mutation_rate:
                    semaphore['redDuration'] = self.random_generator.randint(15, 75)
                    semaphore['greenDuration'] = self.random_generator.randint(15, 75)
                    semaphore['cycleStartTime'] = self.random_generator.randint(0, 75)
        return generation

    def select(self, all_results: list[SchemaProcessResults], _delta: float = 0.1):
        # TODO: Delta precisa ser configuravel
        if not all_results:
            raise ValueError('All results is empty')

        results_list = [result.model_dump() for result in all_results]
        results_list.sort(key=lambda x: x['avgTime'])
        citizen_to_log = results_list[0]
        self.log.log_info(citizen_to_log)

        all_light_results = [result['lights'] for result in results_list]
        selected_citizens_lights = all_light_results[: self.selecteds]

        return selected_citizens_lights

    def objective_function(self, avg_time_delta: float, recent_generations: list[ModelGeneration]):
        """
        Evaluate if the simulation should stop based on the moving average of recent generations' best results.
        Fetch generations from the DataBase by simulation_id.
        """

        # Ensure we have enough generations to apply the moving average window
        if len(recent_generations) < self.get_min_generations_required():
            return False

        # Gather the best results from each generation
        best_results = self.get_best_results_from_generations(recent_generations)

        # Calculate the absolute delta of the moving average
        absolute_delta = self.get_absolute_delta(best_results)

        # Check if the change in the average is below the threshold
        if absolute_delta < avg_time_delta:
            return True
        return False

    @staticmethod
    def get_absolute_delta(results_list: list):
        window_range = 4
        window_range_half = int(window_range / 2)
        window_with_offset = window_range + window_range_half

        window_range_1 = results_list[-window_range:]
        window_range_2 = results_list[-window_with_offset:-window_range_half]

        avg_window_range_1 = sum(wr1['avgTime'] for wr1 in window_range_1) / len(window_range_1)
        avg_window_range_2 = sum(wr2['avgTime'] for wr2 in window_range_2) / len(window_range_2)

        return abs(avg_window_range_1 - avg_window_range_2)

    @staticmethod
    def get_best_results_from_generations(generations: list[ModelGeneration]):
        best_results = []
        for generation in generations:
            best_citizen = min(generation.citizens, key=lambda c: c.trip_avg)
            best_results.append({
                'avgTime': best_citizen.trip_avg,
                'simulatedTime': best_citizen.duration,
                'occupationRate': best_citizen.occupation_rate,
                'carsTotal': best_citizen.vehicles_total,
                'avgSpeed': best_citizen.average_speed,
            })
        return best_results

    @staticmethod
    def get_min_generations_required():
        """
        Determine the minimum number of generations needed to calculate the moving average.
        """
        window_range = 4
        window_range_half = int(window_range / 2)
        window_with_offset = window_range + window_range_half
        return window_with_offset
