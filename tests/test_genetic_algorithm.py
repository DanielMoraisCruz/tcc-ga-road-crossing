# # test_genetic_algorithm.py
# import unittest
#
# from genetic_algorithm import GeneticAlgorithm
#
# from random_generator import RandomGenerator
#
#
# class TestGeneticAlgorithm(unittest.TestCase):
#     def setUp(self):
#         self.population = [{'redDuration': 30, 'greenDuration': 30, 'cycleStartTime': 0}]
#         self.random_generator = RandomGenerator()
#
#     def test_random_generator_none(self):
#         ga = GeneticAlgorithm(self.population, random_generator=None)
#         self.assertIsNotNone(ga.random_generator)
#
#     def test_empty_population(self):
#         ga = GeneticAlgorithm([], random_generator=self.random_generator)
#         with self.assertRaises(ValueError):
#             ga.crossover([])
#
#     def test_empty_results_returned(self):
#         ga = GeneticAlgorithm(self.population, random_generator=self.random_generator)
#         with self.assertRaises(ValueError):
#             ga.crossover([])
#
#     def test_empty_all_results(self):
#         ga = GeneticAlgorithm(self.population, random_generator=self.random_generator)
#         with self.assertRaises(ValueError):
#             ga.select([])
#
#     def test_extreme_mutation_rate(self):
#         ga = GeneticAlgorithm(self.population, mutation_rate=1, random_generator=self.random_generator)
#         mutated_population = ga.mutate(self.population)
#         self.assertNotEqual(mutated_population, self.population)
#
#
# if __name__ == '__main__':
#     unittest.main()
