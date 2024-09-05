# genetic_algorithm.py
from typing import Dict, List

from random_interface import RandomInterface


class GeneticAlgorithm:
    def __init__(
        self,
        population: List[Dict[str, int]],
        selecteds: int = 2,
        mutation_rate: float = 0.1,
        random_generator: RandomInterface = None,
    ):
        self.results: List = []
        self.population: List = population
        self.mutation_rate: float = mutation_rate
        self.selecteds: int = selecteds
        self.random_generator: RandomInterface = random_generator or RandomGenerator()

    def crossover(self, results_returned: List):
        if not self.population:
            raise ValueError("Population is empty")
        if not results_returned:
            raise ValueError("Results returned is empty")

        parents: List = self.select(results_returned)
        if not parents:
            return None

        total_iterations: int = len(self.population)
        new_population: List = []

        new_population.extend(self.population)

        all_reds: List = []
        all_greens: List = []
        all_cycles: List = []

        for parent in parents:
            all_reds.append([crossing['redDuration'] for crossing in parent])
            all_greens.append([crossing['greenDuration'] for crossing in parent])
            all_cycles.append([crossing['cycleStartTime'] for crossing in parent])

        while len(new_population) < total_iterations:
            reds_selecteds = []
            greens_selecteds = []
            cycles_selecteds = []

            for i in range(len(parents) - 1):
                reds_selecteds.append(all_reds[self.random_generator.randint(0, 1)][i])
                greens_selecteds.append(all_greens[self.random_generator.randint(0, 1)][i])
                cycles_selecteds.append(all_cycles[self.random_generator.randint(0, 1)][i])

            new_population.append({
                'redDuration': self.random_generator.choice(reds_selecteds),
                'greenDuration': self.random_generator.choice(greens_selecteds),
                'cycleStartTime': self.random_generator.choice(cycles_selecteds),
            })

        new_population = self.mutate(new_population)
        self.population = new_population[: -self.selecteds].append(parents[:])

        return self.population

    def mutate(self, individuals):
        for individual in individuals:
            random_nun = self.random_generator.random()
            for semaphore in individual:
                if random_nun < self.mutation_rate:
                    semaphore['redDuration'] = self.random_generator.randint(15, 75)
                    semaphore['greenDuration'] = self.random_generator.randint(15, 75)
                    semaphore['cycleStartTime'] = self.random_generator.randint(0, 120)
        return individuals


    def select(self, all_results: List, _delta: float = 0.1):
        if not all_results:
            raise ValueError("All results is empty")

        all_results.sort(key=lambda x: x['tripAvg'])

        desvio_padrao = all_results['tripAvg'].std()

        if desvio_padrao <= _delta:
            return None

        all_light_results = [result['lights'] for result in all_results]
        return all_light_results[: self.selecteds]

