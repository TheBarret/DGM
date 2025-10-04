import random
import hashlib
from collections import defaultdict
from typing import Iterable, Tuple, Optional

from genome import Genome
from family import Family
from phenotype import Phenotype
from population import Population
from vis import plot_family_dendrogram
def print_population_stats(stats: dict):
    header = f"{'Trait':<15} {'Min':>8} {'Mean':>8} {'Max':>8}"
    print(header)
    print("-"*len(header))
    for trait, values in stats.items():
        min_v = f"{values.get('min', 0):.2f}"
        mean_v = f"{values.get('mean', 0):.2f}"
        max_v = f"{values.get('max', 0):.2f}"
        print(f"{trait:<15} {min_v:>8} {mean_v:>8} {max_v:>8}")


if __name__ == "__main__":
    print("* * * Population")
    pop = Population(population_size=256)
    print("* creating family cluster...")
    pop.run_generations(num_generations=64, fitness_func=pop.fitness_default)
    print("* creating family statistics...")
    print_population_stats(pop.population_statistics())
    pop.plot_mood_evolution_png('adaptive')
    #plot_family_dendrogram(pop.family)
