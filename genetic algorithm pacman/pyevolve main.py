from pyevolve import G1DList
from pyevolve import DBAdapters
from pyevolve import GSimpleGA
from capture import test
import time

run = 0

def eval_func(chromosome):
  global run
  myFile = open("output.txt", "a")
  myFile.write("Start: " + str(run) + " " + time.asctime( time.localtime(time.time())) + "\n")
  run += 1
  out = ""
  for gene in chromosome:
    out += str(gene) + ", "
  myFile.write("Chromosome: " + out + "\n")
  score = test(chromosome) + 100
  myFile.write("Score: " + str(score) + "\n")
  myFile.write("End: " + time.asctime( time.localtime(time.time())) + "\n")
  myFile.write("\n\n")
  myFile.close()
  return score


genome = G1DList.G1DList(12)
genome.evaluator.set(eval_func)
genome.setParams(rangemin=0, rangemax=20)
ga = GSimpleGA.GSimpleGA(genome)
csv_adapter = DBAdapters.DBFileCSV(identify="run1", filename="stats.csv")
ga.setDBAdapter(csv_adapter)
ga.setGenerations(50)
ga.setPopulationSize(10)
ga.evolve(freq_stats=5)
print ga.bestIndividual()