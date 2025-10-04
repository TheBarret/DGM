import random
import hashlib
from typing import Optional

class Genome:
    def __init__(self, seed=None, L=8, field_size=16):
        self.L = L
        self.field_size = field_size
        self.base = L + 1
        self.max_seed = self.base**4 - 1
        self.seed = seed if seed is not None else random.randint(0, self.max_seed)

        self.blocks = self._generate_blocks()               # core block array
        self.sums = self._compute_bit_sums()                # sum per block
        self.fields = self._generate_fields(self.seed)      # 4 fields from seed
        self.bitmask_state = 0                              # inheritance pattern bitmask
        self.canonical_id = self._compute_canonical_id()    # deterministic hash (canonical)
        self.instance_id: Optional[int] = None
        self._init_bitmask_state()                          # init bitmask state (required!)

    ### foundation
    def _compute_canonical_id(self) -> str:
        b = str(self.seed).encode()
        #b += b''.join(f.to_bytes((self.field_size + 7) // 8, 'big') for f in self.fields)
        #return hashlib.sha256(b).hexdigest()
        b = f"{self.seed}:{','.join(map(str, self.fields))}".encode()
        return hashlib.sha256(b).hexdigest()

    def _generate_blocks(self):
        S = [(self.seed // (self.base**i)) % self.base for i in range(4)]
        blocks = []
        for i, s in enumerate(S):
            block = [1]*s + [0]*(self.L-s)
            rng = random.Random(self.seed+i)
            rng.shuffle(block)
            blocks.extend(block)
        return blocks

    def _compute_bit_sums(self):
        return [sum(self.blocks[i*self.L:(i+1)*self.L]) for i in range(4)]

    def _generate_fields(self, seed):
        h = hashlib.sha256(str(seed).encode()).digest()
        hi = int.from_bytes(h, 'big')
        mask = (1 << self.field_size) - 1
        return [(hi >> (i*self.field_size)) & mask for i in range(4)]

    def _fields_to_seed(self, fields):
        accumulator = 0
        for f in fields:
            accumulator = (accumulator << self.field_size) | (f & ((1 << self.field_size) - 1))
        return accumulator % (self.max_seed + 1)

    def _analyze_block_patterns(self):
        return sum(self.blocks[i] != self.blocks[i+1] for i in range(len(self.blocks)-1))

    def _init_bitmask_state(self):
        self.bitmask_state = sum(f & 0b1111 for f in self.fields) & 0b1111  # init from fields

    ### publics
    def fitness(self):
        return sum(self.blocks) + self._analyze_block_patterns()

    def distance(self, other):
        f_dist = sum(abs(a-b) for a,b in zip(self.fields, other.fields))
        b_dist = sum(a!=b for a,b in zip(self.blocks, other.blocks))
        f_dist /= (len(self.fields) * (2**self.field_size))
        b_dist /= len(self.blocks)
        return 0.3*f_dist + 0.7*b_dist

    def next_bitmask(self) -> int:
        if not hasattr(self, "bitmask_state"):
            self._init_bitmask_state()
        a, c = 5, 3
        genome_hash = sum(f & 0b1111 for f in self.fields)
        # evolve mask
        #self.bitmask_state = (a * self.bitmask_state + c + genome_hash) & 0b1111
        #return self.bitmask_state
        self.bitmask_state = ((a * self.bitmask_state + c) ^ genome_hash) & 0xFFFF
        return self.bitmask_state & 0b1111

    def crossover(self, other, branch_code=0):
        bitmask     = self.next_bitmask()
        mut_self     = (self.fields[-1] >> (self.field_size - 1)) & 1
        mut_other    = (other.fields[-1] >> (self.field_size - 1)) & 1
        mutation    = mut_self ^ mut_other
        if mutation:
            bitmask = ~bitmask & 0b1111
        rng = random.Random(self.seed + other.seed + bitmask + branch_code)
        
        new_fields = []
        for i in range(4):
            mask = rng.getrandbits(self.field_size)
            if bitmask & (1 << i):
                # inherit self with mask + mutation_bit
                new_fields.append((self.fields[i] & mask) | (other.fields[i] & ~mask))
            else:
                # inherit spousse with mask + mutation_bit
                new_fields.append((other.fields[i] & mask) | (self.fields[i] & ~mask))

        new_seed = self._fields_to_seed(new_fields)
        child = Genome(seed=new_seed, L=self.L, field_size=self.field_size)
        child.fields = new_fields
        return child

    def clone(self, branch_code=0):
        bitmask = self.next_bitmask()
        rng = random.Random(self.seed + bitmask + branch_code)
        new_fields = [self.fields[i] if bitmask & (1<<i) else rng.getrandbits(self.field_size) for i in range(4)]
        new_seed = self._fields_to_seed(new_fields)
        g = Genome(seed=new_seed, L=self.L, field_size=self.field_size)
        g.fields = new_fields
        return g
