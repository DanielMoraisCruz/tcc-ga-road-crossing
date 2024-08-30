import random


class GeneticAlgorithm:
    def __init__(
        self, population: list[dict[str, int]], selecteds: int = 2, mutation_rate: float = 0.1
    ):
        self.results: list = []
        self.population: list = population
        self.mutation_rate: float = mutation_rate
        self.selecteds: int = selecteds

    def crossover(self, total_iterations: int, parents: list):
        new_population: list = []

        # Copiando a população original para a nova população
        new_population.extend(self.population)

        all_reds: list = []
        all_greens: list = []
        all_cycles: list = []

        for parent in parents:
            all_reds.append([crossing['redDuration'] for crossing in parent])
            all_greens.append([crossing['greenDuration'] for crossing in parent])
            all_cycles.append([crossing['cycleStartTime'] for crossing in parent])

        while len(new_population) < (total_iterations - len(parents)):
            reds_selecteds = []
            greens_selecteds = []
            cycles_selecteds = []

            for i in range(len(parents) - 1):
                reds_selecteds.append(all_reds[random.range(2)][i])
                greens_selecteds.append(all_greens[random.range(2)][i])
                cycles_selecteds.append(all_cycles[random.range(2)][i])

            new_population.append({
                'redDuration': random.choice(reds_selecteds),
                'greenDuration': random.choice(greens_selecteds),
                'cycleStartTime': random.choice(cycles_selecteds),
            })

        self.population = new_population
        return new_population

    def mutate(self, individual):
        for semaphore in individual:
            if random.random() < self.mutation_rate:
                semaphore['redDuration'] = random.randint(1, 60)
            if random.random() < self.mutation_rate:
                semaphore['greenDuration'] = random.randint(1, 60)
            if random.random() < self.mutation_rate:
                semaphore['cycleStartTime'] = random.randint(1, 120)
        return individual

    def select(self, all_results: list):
        # ordena os resultados pelo tempo médio de viagem e no final pega os N melhores
        all_results.sort(key=lambda x: x['tripAvg'])
        return all_results[: self.selecteds]
