# DGM
Deterministic Genome Model

A deterministic binary genome model to obtain genetic information in binary with lineage mechanics.  

### Foundation

```csv
Deterministic          : Same seed → identical genome every run.  
Bijective              : Unique tuple (S₁, S₂, S₃, S₄) ↔ unique seed.  
Controlled Inheritance : Bitmask ensures precise genetic transfer.  
Family Matrices        : Fields enable distance metrics, clustering, and tree construction.  
Inheritance Modifier   : Optional branch code control  
```

### Pipeline 

```py
Seed → Blocks → Bit Sums → Fields → Bitmask → Family[...]
```

### Fitness Metrics
> A control and sorting feature, or as pressure gate in selection process.  
> ```py
> sum(self.blocks) → counts the total number of 1s across all blocks.
> _analyze_block_patterns() → counts transitions between consecutive bits (1→0 or 0→1).
> ```
> High fitness → many 1s and/or diverse block patterns.  
> Low fitness → mostly 0s or uniform blocks.  

### Genetic Distance Metrics
Dendrogram-based family trees
```py
d(Gᵢ, Gⱼ) = Σ |fieldsᵢ - fieldsⱼ|
```
<img width="850" alt="Family Tree" src="https://github.com/user-attachments/assets/75e8f07e-afef-4289-82a0-9f2b60e6a93e" />

### Seed Decomposition (Base L+1) 
>- L = 8 → block length (number of bits per block).
>- base = L+1 = 9 → mathematical base for seed decomposition.
>- max_seed = base⁴ - 1 → maximum seed value.
>- seed = chosen number in [0, max_seed].
The seed is expressed in base (L+1) integer that encodes 4 parameters.  
>```py
>seed = S₁ + (L+1)·S₂ + (L+1)²·S₃ + (L+1)³·S₄
>where Sᵢ ∈ [0, L] (block sums)
>```
> 


### Block Generation
>```py
>Bᵢ = binary block of length L with exactly Sᵢ ones, (L-Sᵢ) zeros
>```

### Field Generation  
> Using `SHA256` to retain determinism.  
>```py
>fields = extract_16bit_chunks(SHA256(seed))
>```

### Bitmask Initialization
> Deterministic start
> ```py
> bitmask_state = sum(f & 0b1111 for f in fields) & 0b1111  
> next_bitmask() → evolves via linear congruential step
> ```
> Mutation bit, is the last bit of the last field (fields[-1]) `XOR → Inverted Bitmask`.  

### Test Run

Our fitness function:  
```py
def fitness_default(self, p: Phenotype) -> float:
    f_social = self.fitness_social(p)
    f_cautious = self.fitness_cautious(p)
    f_aggressive = self.fitness_aggressive(p)
    val = 0.45 * f_social + 0.45 * f_cautious - 0.25 * f_aggressive
    balance_penalty = abs(f_social - f_cautious) * 0.2
    val -= balance_penalty
    return max(0.0, min(1.0, val))
```

Output:
```py
pop = Population(population_size=256)
pop.run_generations(num_generations=64, fitness_func=pop.fitness_default)

* * * Population
* creating family cluster...
  selection: 49 | 66 = fitness 14.0
  selection: 6091 | 3435 = fitness 30.0
  selection: 1456 | 2001 = fitness 29.0
  selection: 5093 | 5543 = fitness 35.0
  selection: 5615 | 5958 = fitness 29.0
  selection: 3229 | 3369 = fitness 33.0
  selection: 4824 | 5131 = fitness 23.5
  ...
* creating family statistics...
Trait                Min     Mean      Max
------------------------------------------
polarity            0.00     0.48     1.00
mood                1.00     1.00     1.00
base_size           0.02     0.54     0.75
color_index        67.00   192.98   255.00
pattern_id          0.00     2.28     3.00
hair                0.00     0.56     1.00
speed               0.64     0.91     0.94
endurance           0.44     0.47     0.50
strength            0.88     0.95     1.00
lifespan           10.00    50.62    99.00
fertility           0.14     0.50     1.00
antagonism          0.00     0.75     3.00
```

Result:  
<img width="500" src="https://github.com/user-attachments/assets/10d66497-baf4-4b6b-87d1-fc72e01359aa" />
<img width="500" src="https://github.com/user-attachments/assets/96763aea-0baa-4a0f-a066-411d02021722" />

### Branch Code / Inheritance Modifier
> The `branch_code` is an optional integer passed to `crossover()` or `clone()` that modifies the random mask generation,  
> creating minor variations in inheritance patterns while keeping the genome deterministic:
> ```py
> # bitmask_state + branch_code → RNG seed → field inheritance mask
> child = parentA.crossover(parentB, branch_code=3)
> ```
> - Alters the RNG used to mix parent fields.  
> - Works together with the bitmask, giving multiple “branches” of offspring even from the same parents.  
> - Useful for generating distinct lineages without changing the fundamental seed/field content.  
> - Multiple children with the same parents + different branch_codes → different offspring fields.  
> - Ensures lineage diversity for dendrograms and family trees.  

### Cloning / Crossover Logic
> The bitmask driven inheritance uses a mutation bit that toggles an inversion pattern.
> ```py
>     def crossover(self, other, branch_code=0):
>        bitmask     = self.next_bitmask()
>        mut_self     = (self.fields[-1] >> (self.field_size - 1)) & 1
>        mut_other    = (other.fields[-1] >> (self.field_size - 1)) & 1
>        mutation    = mut_self ^ mut_other
>        if mutation:
>            bitmask = ~bitmask & 0b1111
>        rng = random.Random(self.seed + other.seed + bitmask + branch_code)
>        
>        new_fields = []
>        for i in range(4):
>            mask = rng.getrandbits(self.field_size)
>            if bitmask & (1 << i):
>                # inherit self with mask + mutation_bit
>                new_fields.append((self.fields[i] & mask) | (other.fields[i] & ~mask))
>            else:
>                # inherit spousse with mask + mutation_bit
>                new_fields.append((other.fields[i] & mask) | (self.fields[i] & ~mask))
>        new_seed = self._fields_to_seed(new_fields)
>        child = Genome(seed=new_seed, L=self.L, field_size=self.field_size)
>        child.fields = new_fields
>        return child
> ```


