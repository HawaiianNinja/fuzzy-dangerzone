from pyevolve import G1DList
from pyevolve import DBAdapters
from pyevolve import GSimpleGA
from capture import test
import time

def eval_func(chromosome):
  myFile = open("output.txt", "a")
  myFile.write("Start: " + time.asctime( time.localtime(time.time())) + "\n")
  out = ""
  for gene in chromosome:
    out += str(gene) + ", "
  myFile.write("Chromosome: " + out + "\n")
  score = test(chromosome)
  myFile.write("Score: " + str(score) + "\n")
  myFile.write("End: " + time.asctime( time.localtime(time.time())) + "\n")
  myFile.write("\n\n")
  myFile.close()
  return score

genome = G1DList.G1DList(12)
genome.evaluator.set(eval_func)
genome.setParams(rangemin=-10, rangemax=10)
ga = GSimpleGA.GSimpleGA(genome)
csv_adapter = DBAdapters.DBFileCSV(identify="run1", filename="stats.csv")
ga.setDBAdapter(csv_adapter)
ga.setGenerations(500)
ga.setPopulationSize(10)
ga.evolve(freq_stats=10)
print ga.bestIndividual()