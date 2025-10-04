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

<img width="500" src="https://github.com/user-attachments/assets/a492be9a-18a7-4151-8ba8-c3ef7b242ff1" />

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

### Test Run
> parameters: `Family(initial_count=25, offspring_count=9)`

```py
python run.py
* * * * Offspring Data:
  Pool       : 34

Genome(Seed=4694,Fs=16,L=8,Base=9)
  Blocks     : 32 | [5, 8, 3, 6]
  Fields     : [31154, 17905, 15227, 9711]
  Bitmask    : 0b1111
  Fitness    : 34
  Lineage    :
    Genome(30) (G2) ← Genome(26) (G1) ← Genome(19) (G0) + Genome(6) (G0) + Genome(25) (G0)

Genome(Seed=4737,Fs=16,L=8,Base=9)
  Blocks     : 32 | [3, 4, 4, 6]
  Fields     : [57507, 13904, 8095, 36171]
  Bitmask    : 0b110
  Fitness    : 34
  Lineage    :
    Genome(31) (G3) ← Genome(18) (G0) + Genome(28) (G2) ← Genome(9) (G0) + Genome(26) (G1) ← Genome(19) (G0) + Genome(6) (G0)

Genome(Seed=16,Fs=16,L=8,Base=9)
  Blocks     : 32 | [7, 1, 0, 0]
  Fields     : [62850, 28729, 4087, 22610]
  Bitmask    : 0b1101
  Fitness    : 13
  Lineage    :
    Genome(32) (G2) ← Genome(23) (G0) + Genome(29) (G1) ← Genome(22) (G0) + Genome(12) (G0)

Genome(Seed=724,Fs=16,L=8,Base=9)
  Blocks     : 32 | [4, 8, 8, 0]
  Fields     : [32564, 49873, 42655, 6492]
  Bitmask    : 0b100
  Fitness    : 27
  Lineage    :
    Genome(33) (G1) ← Genome(5) (G0) + Genome(21) (G0)

Genome(Seed=2055,Fs=16,L=8,Base=9)
  Blocks     : 32 | [3, 3, 7, 2]
  Fields     : [62548, 31005, 27891, 61250]
  Bitmask    : 0b100
  Fitness    : 29
  Lineage    :
    Genome(34) (G2) ← Genome(13) (G0) + Genome(29) (G1) ← Genome(22) (G0) + Genome(12) (G0)
  ```


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
> Bitmask-driven Inheritance
> ```py
> for i in fields:
>     if bitmask & (1 << i):
>         new_fields[i] = (parentA.fields[i] & rng_mask) | (parentB.fields[i] & ~rng_mask)
>     else:
>         new_fields[i] = (parentB.fields[i] & rng_mask) | (parentA.fields[i] & ~rng_mask)
> ```

