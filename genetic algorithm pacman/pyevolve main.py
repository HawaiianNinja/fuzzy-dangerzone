from pyevolve import G1DList
from pyevolve import GSimpleGA
from capture import test
import time

def eval_func(chromosome):
  myFile = open("output.txt", "a")
  myFile.write("Start: " + time.asctime( time.localtime(time.time())))
  myFile.write(chromosome.toString())
  score = test(chromosome)
  myFile.write("Score: " + score)
  myFile.write("End: " + time.asctime( time.localtime(time.time())))
  myFile.close()
  return score

genome = G1DList.G1DList(11)
genome.evaluator.set(eval_func)
ga = GSimpleGA.GSimpleGA(genome)
ga.evolve(freq_stats=10)
print ga.bestIndividual()