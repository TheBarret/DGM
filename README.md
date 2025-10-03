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

>```py
>Seed → Blocks → Bit Sums → Fields → Bitmask → Family[...]
>```

Seed Decomposition (Base L+1)
>```py
>seed = S₁ + (L+1)·S₂ + (L+1)²·S₃ + (L+1)³·S₄
>where Sᵢ ∈ [0, L] (block sums)
>```

### Block Generation
>```py
>Bᵢ = binary block of length L with exactly Sᵢ ones, (L-Sᵢ) zeros
>```

### Field Generation  
>Length: 16  
>Determinism: SHA256  
>```py
>fields = extract_16bit_chunks(SHA256(seed))
>```

### Bitmask Initialization
> Deterministic start
> ```py
> bitmask_state = sum(f & 0b1111 for f in fields) & 0b1111  
> next_bitmask() → evolves via linear congruential step
> ```

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

### Genetic Distance Metrics
Dendrogram-based family trees
```py
d(Gᵢ, Gⱼ) = Σ |fieldsᵢ - fieldsⱼ|
```
<img width="850" alt="Family Tree" src="https://github.com/user-attachments/assets/75e8f07e-afef-4289-82a0-9f2b60e6a93e" />




