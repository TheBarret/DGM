import random
import hashlib
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

from genome import Genome
from family import Family

def generate_family_tree_data(num_generations, population_size_per_gen, parent_seed=None):
    """
    Generates a population of genomes over several generations with proper lineage tracking.
    """
    if parent_seed is None:
        parent_seed = random.randint(0, (8 + 1)**4 - 1)
    # Initialize with two fictional founders
    founderA = Genome(seed=random.randint(0,parent_seed))
    founderB = Genome(seed=random.randint(0,parent_seed))
    population = [founderA, founderB]
    all_genomes = [founderA, founderB]
    
    # Track by generation
    generation_tracking = {0: [founderA, founderB]}
    print(f"Founder A: seed={founderA.seed}, fields={founderA.fields}")
    print(f"Founder B: seed={founderB.seed}, fields={founderB.fields}")
    
    # Generate subsequent generations
    for gen in range(1, num_generations + 1):
        next_gen_population = []
        generation_tracking[gen] = []
        
        for parent_idx, parent in enumerate(population):
            for child_idx in range(population_size_per_gen):
                branche = 0
                parent_a, parent_b = random.sample(population, 2)
                child = parent_a.crossover(parent_b, branch_code=branche)
                next_gen_population.append(child)
                generation_tracking[gen].append(child)
        
        population = next_gen_population
        all_genomes.extend(population)
    # Compute distance matrix
    num_genomes = len(all_genomes)
    distances = np.zeros((num_genomes, num_genomes))
    
    print(f"  computing distance matrix for {num_genomes} genomes...")
    for i in range(num_genomes):
        for j in range(i + 1, num_genomes):
            dist = all_genomes[i].distance(all_genomes[j])
            distances[i, j] = dist
            distances[j, i] = dist
        distances[i, i] = 0  # Distance to self is 0

    return all_genomes, distances, generation_tracking

def plot_dendrogram_from_data(genomes, distances, generation_tracking):
    """
    Plots a dendrogram using the generated distance matrix with generation coloring.
    """
    from scipy.spatial.distance import squareform
    
    # Create informative labels
    labels = []
    colors = []
    color_map = {0: 'red', 1: 'blue', 2: 'green', 3: 'orange', 4: 'purple'}
    
    for i, genome in enumerate(genomes):
        # Find which generation this genome belongs to
        gen_found = 0
        for gen, gen_genomes in generation_tracking.items():
            if genome in gen_genomes:
                gen_found = gen
                break
            if gen == 0 and genome.seed == gen_genomes[0].seed:  # Founder
                gen_found = 0
                break
        
        labels.append(f"G{gen_found}-S{genome.seed}")
        colors.append(color_map.get(gen_found, 'gray'))
        print(f"  family {gen_found} seed: {genome.seed} branche mask: {bin(genome.bitmask_state)}")

    # Convert to condensed form and perform hierarchical clustering
    print("Performing hierarchical clustering...")
    condensed_distances = squareform(distances, checks=False)
    linkage_matrix = linkage(condensed_distances, method='ward')

    # Plot the dendrogram
    plt.figure(figsize=(14, 8))
    dendro = dendrogram(
        linkage_matrix,
        labels=labels,
        orientation='top',
        leaf_rotation=90,
        leaf_font_size=8
    )
    
    # Color leaves by generation
    for leaf, leaf_color in zip(dendro['leaves'], colors):
        plt.gca().get_xticklabels()[leaf].set_color(leaf_color)
    
    plt.title(f"Genomic Family Tree ({len(genomes)} genomes across {len(generation_tracking)} generations)")
    plt.xlabel("Genome (Generation-Seed)")
    plt.ylabel("Genetic Distance")
    plt.tight_layout()
    plt.savefig('family.png', dpi=100, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    random.seed(100)
    genomes, distances, generation_tracking = generate_family_tree_data(num_generations=4, population_size_per_gen=2)
    print(f"\nGenerated {len(genomes)} total genomes")
    print(f"Distance matrix shape: {distances.shape}")
    print(f"Min distance: {np.min(distances[np.nonzero(distances)]):.2f}")
    print(f"Max distance: {np.max(distances):.2f}")
    plot_dendrogram_from_data(genomes, distances, generation_tracking)
    
 