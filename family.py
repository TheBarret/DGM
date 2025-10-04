import random
from collections import defaultdict
from typing import Iterable, Optional, Union

from genome import Genome


class Family:
    """
    Family class manages genomes, their lineage, and canonical grouping.

    Responsibilities:
    - Store all genomes with unique instance IDs
    - Track parentage and generation
    - Provide controlled reproduction (pair)
    - Allow ancestry inspection
    """

    def __init__(self):
        self._next_instance_id: int = 1
        self.members: dict[int, Genome] = {}                 # instance_id -> Genome
        self.lineage: dict[int, dict] = {}                   # instance_id -> metadata
        self.by_canonical: defaultdict[int, list[int]] = defaultdict(list)  # canonical_id -> [instance_ids]

    def add_member(self, genome: Genome, parents: Iterable[Union[int, Genome]] = (),
                   branch_code: int = 0,generation: int = 0) -> int:
        """
        Add a genome to the family, with optional parents and metadata.
        Returns the assigned instance ID.
        """

        # If genome already tracked, reuse its ID
        if getattr(genome, "instance_id", None) in self.members:
            return genome.instance_id

        # Ensure canonical ID exists
        if not hasattr(genome, "canonical_id"):
            genome.canonical_id = genome._compute_canonical_id()

        instance_id = self._allocate_instance_id()
        genome.instance_id = instance_id

        # Store
        self.members[instance_id] = genome
        self.by_canonical[genome.canonical_id].append(instance_id)

        # Resolve parents
        resolved_parents = self._resolve_parents(parents, generation)

        # Record lineage metadata
        self.lineage[instance_id] = {
            "parents": tuple(resolved_parents),
            "canonical": genome.canonical_id,
            "bitmask": getattr(genome, "bitmask_state", 0),
            "branch_code": branch_code,
            "generation": generation,
        }

        return instance_id

    def pair(self, parent_a: Genome, parent_b: Genome, branch_code: int = 0) -> Genome:
        """
        Cross two parents into a child genome, register it into the family.
        """
        child = parent_a.crossover(parent_b, branch_code=branch_code)

        # Generation = max parent gen + 1
        gen_a = self._get_generation(parent_a)
        gen_b = self._get_generation(parent_b)
        generation = max(gen_a, gen_b) + 1

        self.add_member(child, parents=(parent_a, parent_b), branch_code=branch_code, generation=generation)
        return child

    def create_family(self, founders: int = 4, offspring: int = 10) -> list[Genome]:
        """
        Create an initial family tree with N founders and M offspring.
        """
        members: list[Genome] = []

        # Founders
        for _ in range(founders):
            g = Genome(seed=random.randint(0, 512))
            self.add_member(g, generation=0)
            members.append(g)

        # Offspring
        for _ in range(offspring):
            p1, p2 = random.sample(members, 2)
            child = self.pair(p1, p2)
            members.append(child)

        return members

    def ancestry(self, genome_or_id: Union[int, Genome], _depth_limit: int = 50) -> str:
        """
        Return a human-readable ancestry string for a genome.
        """
        gid = self._to_instance_id(genome_or_id)
        if gid not in self.lineage:
            return "External"

        def _recurse(gid_inner: int, depth: int) -> str:
            if depth > _depth_limit:
                return "… (depth limit)"
            meta = self.lineage.get(gid_inner, {})
            if not meta.get("parents"):
                return f"Genome({gid_inner}) (G{meta.get('generation', 0)})"
            parents_str = " + ".join(_recurse(p, depth + 1) for p in meta["parents"])
            return f"Genome({gid_inner}) (G{meta.get('generation', 0)}) ← {parents_str}"

        return _recurse(gid, 0)

    def _allocate_instance_id(self) -> int:
        iid = self._next_instance_id
        self._next_instance_id += 1
        return iid

    def _resolve_parents(self, parents: Iterable[Union[int, Genome]], child_generation: int) -> list[int]:
        """
        Normalize parents into instance IDs, auto-adding genomes if needed.
        """
        resolved = []
        for p in parents:
            if p is None:
                continue
            if isinstance(p, int):
                resolved.append(p)
            elif isinstance(p, Genome):
                if getattr(p, "instance_id", None) not in self.members:
                    resolved.append(self.add_member(p, generation=max(0, child_generation - 1)))
                else:
                    resolved.append(p.instance_id)
        return resolved

    def _to_instance_id(self, genome_or_id: Union[int, Genome]) -> Optional[int]:
        """
        Convert a Genome or int into a valid instance ID (if possible).
        """
        if isinstance(genome_or_id, int):
            return genome_or_id
        return getattr(genome_or_id, "instance_id", None)

    def _get_generation(self, genome: Genome) -> int:
        """
        Fetch generation from lineage, fallback to 0.
        """
        return self.lineage.get(getattr(genome, "instance_id", None), {}).get("generation", 0)
