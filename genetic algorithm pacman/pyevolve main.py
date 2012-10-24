from pyevolve import G1DList
from pyevolve import GSimpleGA
from capture import test

def eval_func(chromosome):
   # iterate over the chromosome
   #for value in chromosome:
   #   if value==0:
   #      score += 1
   return test(chromosome)

genome = G1DList.G1DList(8)
genome.evaluator.set(eval_func)
ga = GSimpleGA.GSimpleGA(genome)
ga.evolve(freq_stats=10)
print ga.bestIndividual()