import random
import hashlib
from collections import defaultdict
from typing import Iterable, Tuple, Optional

from genome import Genome
from family import Family

if __name__ == "__main__":
    fam = Family()
    all_members = fam.create_family(initial_count=25, offspring_count=9)
    
    print('* * * * Offspring Data:')
    print(f'  Pool       : {len(fam.members)}')
    print()
    
    for member in all_members[-5:]:
        print(f'Genome(Seed={member.seed},Fs={member.field_size},L={member.L},Base={member.base})')
        print(f'  Blocks     : {len(member.blocks)} | {member.sums}')
        print(f'  Fields     : {member.fields}')
        print(f'  Bitmask    : {bin(member.bitmask_state)}')
        print(f'  Fitness    : {member.fitness()}')
        print(f'  Lineage    : {fam.ancestry(member)}')
        print()