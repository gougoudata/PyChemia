__author__ = 'Guillermo Avendano-Franco'

from _searcher import Searcher


class AntColony(Searcher):

    def __init__(self, population, params, fraction_evaluated=0.8, generation_size=32, stabilization_limit=10):
        self.population = population
        Searcher.__init__(self, self.population, fraction_evaluated, generation_size, stabilization_limit)
        self.params = None
        self.set_params(params)

    def set_params(self, params):
        self.params = params

    def run_one_cycle(self):
        pass
