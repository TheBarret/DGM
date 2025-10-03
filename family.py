import random
import hashlib
from collections import defaultdict
from typing import Iterable, Tuple, Optional

from genome import Genome
        
class Family:
    def __init__(self):
        self._next_instance_id = 1
        self.members: dict[int, Genome] = {}            # instance_id -> Genome
        self.lineage: dict[int, dict] = {}              # instance_id -> metadata
        self.by_canonical: defaultdict = defaultdict(list)  # canonical_id -> [instance_id...]

    def add_member(self, genome: Genome, parents: Iterable = (), branch_code: int = 0, generation: int = 0) -> int:
        # If genome already added, return its existing instance id
        if getattr(genome, "instance_id", None) is not None and genome.instance_id in self.members:
            return genome.instance_id

        # Ensure canonical_id exists (Genome should already provide it)
        if not hasattr(genome, "canonical_id"):
            genome.canonical_id = genome._compute_canonical_id()

        instance_id = self._next_instance_id
        self._next_instance_id += 1

        genome.instance_id = instance_id
        self.members[instance_id] = genome
        self.by_canonical[genome.canonical_id].append(instance_id)

        # resolve parents: allow passing Genome objects or instance ids
        resolved_parents = []
        for p in parents:
            if p is None:
                continue
            if isinstance(p, int):
                resolved_parents.append(p)
            elif hasattr(p, "instance_id") and p.instance_id in self.members:
                resolved_parents.append(p.instance_id)
            else:
                # if parent Genome object not yet in family, add it first (generation guessed)
                resolved_parents.append(self.add_member(p, generation=max(0, generation - 1)))

        self.lineage[instance_id] = {
            "parents": tuple(resolved_parents),
            "canonical": genome.canonical_id,
            "bitmask": getattr(genome, "bitmask_state", 0),
            "branch_code": branch_code,
            "generation": generation
        }
        return instance_id

    def mate(self, parent_a: Genome, parent_b: Genome, branch_id: int = 0) -> Genome:
        # produce child genome
        child = parent_a.crossover(parent_b, branch_code=branch_id)

        # determine parent generations (0 if unknown)
        gen_a = self.lineage.get(getattr(parent_a, "instance_id", None), {}).get("generation", 0)
        gen_b = self.lineage.get(getattr(parent_b, "instance_id", None), {}).get("generation", 0)
        gen = max(gen_a, gen_b) + 1

        # add child and return child object (family metadata stored)
        self.add_member(child, parents=(parent_a, parent_b), branch_code=branch_id, generation=gen)
        return child

    def create_family(self, initial_count: int = 4, offspring_count: int = 10):
        members_list = []
        for _ in range(initial_count):
            g = Genome(seed=random.randint(0, 512))
            self.add_member(g, generation=0)
            members_list.append(g)

        for _ in range(offspring_count):
            p1, p2 = random.sample(members_list, 2)
            child = self.mate(p1, p2)
            members_list.append(child)
        return members_list

    def ancestry(self, genome_or_id, _depth_limit: int = 50) -> str:
        # accept instance id or Genome object
        gid = genome_or_id if isinstance(genome_or_id, int) else getattr(genome_or_id, "instance_id", None)
        if gid is None or gid not in self.lineage:
            return " ? "

        # safe recursion with simple depth guard
        def _recurse(gid_inner, depth):
            if depth > _depth_limit:
                return "… (depth limit)"
            meta = self.lineage.get(gid_inner)
            if not meta:
                return " ? "
            if not meta["parents"]:
                return f"Genome({gid_inner}) (G{meta['generation']})"
            parents_str = " + ".join(_recurse(p, depth + 1) for p in meta["parents"])
            return f"Genome({gid_inner}) (G{meta['generation']}) ← {parents_str}"

        return _recurse(gid, 0)