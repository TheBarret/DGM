import random
import hashlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform

from genome import Genome
from family import Family

def plot_family_dendrogram(family: Family):
    genomes = list(family.members.values())
    if len(genomes) < 2:
        raise ValueError("Need at least two genomes to plot a dendrogram.")

    n = len(genomes)
    labels, colors = [], []
    color_map = {
        0: 'red', 1: 'blue', 2: 'green', 3: 'orange', 4: 'purple',
        5: 'brown', 6: 'cyan', 7: 'magenta'
    }

    distances = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = genomes[i].distance(genomes[j])
            distances[i][j] = distances[j][i] = d

    condensed_distances = squareform(distances, checks=False)

    generations = [
        family.lineage.get(g.instance_id, {}).get("generation", 0)
        for g in genomes
    ]

    for genome, gen in zip(genomes, generations):
        labels.append(f"S{genome.seed}")
        colors.append(color_map.get(gen, 'gray'))

    linkage_matrix = linkage(condensed_distances, method="ward")

    fig, ax = plt.subplots(figsize=(16, 10))
    dendro = dendrogram(
        linkage_matrix,
        labels=labels,
        orientation="top",
        leaf_rotation=0,
        leaf_font_size=0,  # annotate manually
        color_threshold=0,
        ax=ax
    )

    # --- Step 6: Annotate split junctions
    for xs, ys in zip(dendro['icoord'], dendro['dcoord']):
        for x, y in zip(xs[1:3], ys[1:3]):
            leaf_idx = min(
                range(len(dendro['leaves'])),
                key=lambda i: abs(dendro['leaves'][i]*10 - x)
            )
            label = labels[leaf_idx]
            color = colors[leaf_idx]
            ax.text(x, y, label, rotation=90, ha="right", va="bottom",
                    fontsize=8, color=color)

    plt.title(f"Family Dendrogram ({n} genomes, {len(set(generations))} generations)")
    plt.ylabel("Genetic Distance")
    plt.tight_layout()
    plt.savefig("family.png", dpi=120, bbox_inches="tight")
    plt.close()

#if __name__ == "__main__":
#    random.seed(100)
#    genomes, distances, generation_tracking = generate_family_tree_data(num_generations=3, population_size_per_gen=3)
#    print(f"\nGenerated {len(genomes)} total genomes")
#    print(f"Distance matrix shape: {distances.shape}")
#    print(f"Min distance: {np.min(distances[np.nonzero(distances)]):.2f}")
#    print(f"Max distance: {np.max(distances):.2f}")
#    plot_dendrogram_from_data(genomes, distances, generation_tracking)
    
 