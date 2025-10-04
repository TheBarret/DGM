import random
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Callable, Optional
from genome import Genome
from family import Family
from phenotype import Phenotype

class Population:
    """
    Simulation engine for populations of genomes with phenotypes and lineage tracking.
    Supports selection, breeding, and trait statistics.
    """
    def __init__(self, population_size: int, initial_seed: Optional[int] = None):
        self.family = Family()
        self.history = []
        self.population_size = population_size
        self.generations = 0
        self.population: List[Genome] = []
        self.initial_seed = initial_seed or random.randint(0, 512)
        self._init_population()
        self.mood_map = {
            0: "explorative",   # seeks out new territory/resources, bold
            1: "cautious",      # avoids risk, conservative in decisions
            2: "aggressive",    # competes for resources, dominates others
            3: "social",        # seeks companions, cooperative behaviors
            4: "territorial",   # defends space, prioritizes location over exploration
            5: "curious",       # investigates surroundings, experiments with objects
            6: "solitary",      # avoids groups, acts independently
            7: "adaptive"       # flexible, changes strategy based on context
        }

    def _init_population(self):
        """Create founder genomes and register in family."""
        for _ in range(self.population_size):
            g = Genome(seed=random.randint(0, self.initial_seed))
            self.family.add_member(g, generation=0)
            self.population.append(g)

    def evaluate_traits(self) -> List[Phenotype]:
        """Return Phenotype objects for the current population."""
        return [Phenotype(g) for g in self.population]

    def select_parents_random(self, fitness_func: Optional[Callable[[Phenotype], float]] = None) -> List[Genome]:
        """
        Select genomes for breeding.
        fitness_func: callable taking Phenotype -> fitness score (higher better)
        Returns a list of selected parents (length = population_size)
        """
        phenotypes = self.evaluate_traits()
        if fitness_func is None:
            return random.choices(self.population, k=self.population_size)
        else:
            weights = [fitness_func(p) for p in phenotypes]
            return random.choices(self.population, weights=weights, k=self.population_size)

    def breed_next_generation(self, fitness_func: Optional[Callable[[Phenotype], float]] = None, branch_code: int = 0):
        """Generate a new population via crossover, replacing the old population."""
        parents = self.select_parents_random(fitness_func)
        print(f'  selection: {parents[0].seed} | {parents[1].seed} = fitness {((parents[0].fitness() + parents[1].fitness()) / 2)}')
        next_population = []
        for _ in range(self.population_size):
            p1, p2 = random.sample(parents, 2)
            child = self.family.pair(p1, p2, branch_code)
            next_population.append(child)
        self.population = next_population
        self.generations += 1
        self.record_generation_stats()

    def population_statistics(self) -> dict:
        """Compute basic statistics for numeric traits."""
        phenos = self.evaluate_traits()
        stats = {}
        if not phenos:
            return stats
        traits_keys = phenos[0].traits.keys()
        for key in traits_keys:
            values = [p.traits[key] for p in phenos if isinstance(p.traits[key], (int, float))]
            if values:
                stats[key] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values)/len(values)
                }
        return stats

    def record_generation_stats(self):
        """Compute and record mean trait per mood for current generation."""
        phenos = self.evaluate_traits()
        mood_summary = {}

        for p in phenos:
            mood_name = self.mood_map.get(p.traits.get("mood", 0), "unknown")
            mood_summary.setdefault(mood_name, {"count": 0, "score": 0.0})
            t = p.traits
            strength = np.mean([t.get(k, 0) for k in ("speed", "endurance", "strength")])
            mood_summary[mood_name]["score"] += strength
            mood_summary[mood_name]["count"] += 1

        # normalize
        for mood in mood_summary:
            count = mood_summary[mood]["count"]
            if count > 0:
                mood_summary[mood]["score"] /= count

        self.history.append({m: mood_summary[m]["score"] for m in mood_summary})
        
    def plot_mood_evolution_png(self, title: str):
        """
        Plot how average mood strength evolves over generations.
        X-axis: generation index
        Y-axis: average strength (0–1)
        """
        if not self.history:
            print("No historical data to plot — run some generations first.")
            return

        plt.figure(figsize=(12, 6))
        generations = range(len(self.history))

        # Gather all mood labels encountered
        all_moods = sorted({m for gen in self.history for m in gen.keys()})

        for mood in all_moods:
            y_vals = [gen.get(mood, np.nan) for gen in self.history]
            plt.plot(generations, y_vals, marker='o', label=mood)

        plt.xlabel("Generation")
        plt.ylabel("Trait Strength")
        plt.title(f"Mood Evolution: {title}")
        plt.legend()
        plt.tight_layout()
        plt.savefig("mood_evolution.png", dpi=150)
        plt.close()

    def run_generations(self, num_generations: int, fitness_func: Optional[Callable[[Phenotype], float]] = None):
        """Run multiple generations of the simulation."""
        for _ in range(num_generations):
            self.breed_next_generation(fitness_func)
    
    # PRIMARY FACTORS
    def fitness_lifespan(self, p: Phenotype) -> float:
        """
        Rewards lifespan
        """
        return p.traits["lifespan"] / 100.0
        
    def fitness_balanced(self, p: Phenotype) -> float:
        """
        Rewards balanced specs
        """
        return 0.4*p.traits["speed"] + 0.3*p.traits["endurance"] + 0.3*p.traits["strength"]
        
    def fitness_appearance(self, p: Phenotype) -> float:
        """
        Rewards appearance
        """
        return (p.traits["color_index"] % 10) / 10.0 + p.traits["hair"]
        
    # SECONDARY FACTORS
    def fitness_explorer(self, p: Phenotype) -> float:
        """
        Rewards speed and exploratory mood.
        """
        base = 0.5*p.traits["speed"] + 0.3*p.traits["endurance"] + 0.2*p.traits["strength"]
        mood_bonus = 0.2 if self.mood_map.get(p.traits["mood"]) == "explorative" else 0.0
        return min(base + mood_bonus, 1.0)

    def fitness_social(self, p: Phenotype) -> float:
        """
        Rewards cooperative behaviors and social mood.
        """
        base = 0.4*p.traits["endurance"] + 0.3*p.traits["strength"] + 0.3*p.traits["speed"]
        mood_bonus = 0.2 if self.mood_map.get(p.traits["mood"]) == "social" else 0.0
        return min(base + mood_bonus, 1.0)

    def fitness_aggressive(self, p: Phenotype) -> float:
        """
        Rewards dominance-oriented mood and high strength.
        """
        base = 0.5*p.traits["strength"] + 0.3*p.traits["speed"] + 0.2*p.traits["endurance"]
        mood_bonus = 0.3 if self.mood_map.get(p.traits["mood"]) == "aggressive" else 0.0
        return min(base + mood_bonus, 1.0)

    def fitness_cautious(self, p: Phenotype) -> float:
        """
        Rewards careful traits like high endurance and lifespan, coupled with cautious mood.
        """
        base = 0.5*p.traits["endurance"] + 0.3*p.traits["lifespan"]/100 + 0.2*p.traits["strength"]
        mood_bonus = 0.2 if self.mood_map.get(p.traits["mood"]) == "cautious" else 0.0
        return min(base + mood_bonus, 1.0)

    def fitness_adaptive(self, p: Phenotype) -> float:
        """
        Rewards flexibility and overall balanced traits, plus adaptive mood.
        """
        base = (p.traits["speed"] + p.traits["endurance"] + p.traits["strength"] + p.traits["lifespan"]/100)/4
        mood_bonus = 0.25 if self.mood_map.get(p.traits["mood"]) == "adaptive" else 0.0
        return min(base + mood_bonus, 1.0)

    def fitness_default(self, p: Phenotype) -> float:
        f_social = self.fitness_social(p)
        f_cautious = self.fitness_cautious(p)
        f_aggressive = self.fitness_aggressive(p)
        val = 0.45 * f_social + 0.45 * f_cautious - 0.25 * f_aggressive
        balance_penalty = abs(f_social - f_cautious) * 0.2
        val -= balance_penalty
        return max(0.0, min(1.0, val))