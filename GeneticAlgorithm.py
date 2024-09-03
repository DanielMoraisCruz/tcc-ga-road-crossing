import random


class GeneticAlgorithm:
    def __init__(
        self, population: list[dict[str, int]], selecteds: int = 2, mutation_rate: float = 0.1
    ):
        self.results: list = []
        self.population: list = population
        self.mutation_rate: float = mutation_rate
        self.selecteds: int = selecteds

    def crossover(self, results_returned: list):
        # TODO: Colocar condição de parada
        #   (quantidade minima de gerações, e delta entre a atual e anterior)
        parents: list = self.select(results_returned)
        if not parents:
            return None

        total_iterations: int = len(self.population)
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

        while len(new_population) < total_iterations:
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
        # Atualiza a população com novos indivíduos e os dois melhores da geração anterior

        new_population = self.mutate(new_population)
        self.population = new_population[: -self.selecteds].append(parents[:])

        return self.population

    def mutate(self, individuals):
        for individual in individuals:
            random_nun = random.random()
            for semaphore in individual:
                if random_nun < self.mutation_rate:
                    semaphore['redDuration'] = random.randint(15, 75)
                    # TODO: Documentar este valor no relatório
                    semaphore['greenDuration'] = random.randint(15, 75)
                    # TODO: Documentar este valor no relatório
                    semaphore['cycleStartTime'] = random.randint(0, 120)
                    # TODO: Documentar este valor no relatório
        return individuals

    def select(self, all_results: list, _delta: float = 0.1):
        # ordena os resultados pelo tempo médio de viagem e no final pega os N melhores
        all_results.sort(key=lambda x: x['tripAvg'])

        desvio_padrao = all_results['tripAvg'].std()

        if desvio_padrao <= _delta:
            return None

        all_light_results = [result['lights'] for result in all_results]
        return all_light_results[: self.selecteds]
