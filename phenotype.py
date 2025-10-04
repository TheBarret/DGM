import math
from typing import Dict, Any
from genome import Genome

class Phenotype:
    """
    Phenotype class wrapper for a single `Genome`.
    Extracts traits from the genome's fields.
    """

    def __init__(self, genome: Genome):
        self.genome = genome
        self.traits: Dict[str, Any] = self._map_traits(genome.fields)

    def _map_traits(self, fields: tuple[int, int, int, int]) -> Dict[str, Any]:
        f0, f1, f2, f3 = fields
        traits = {}
     
        # Identity
        traits["polarity"]      = 0 if (f0 & 1) else 1
        traits["mood"]          = (f0 >> 1) & 0b111             # 0..7
        traits["base_size"]     = ((f0 >> 4) & 0xFF) / 255.0    # normalized 0..1

        # Appearance
        traits["color_index"]   = f1 & 0xFF
        traits["pattern_id"]    = (f1 >> 8) & 0b11              # 0..3
        traits["hair"]          = ((f1 >> 10) & 0b111) / 7.0    # normalized 0..1

        # Performance
        traits["speed"]         = (f2 & 0x1FF) / 511.0          # normalized 0..1
        traits["endurance"]     = ((f2 >> 9) & 0xFF) / 255.0
        traits["strength"]      = ((f2 >> 8) & 0xFF) / 255.0    # use bits 8–15

        # Longevity
        traits["lifespan"]      = 10 + (f3 & 0xFF) % 90         # 10..99
        traits["fertility"]     = ((f3 >> 8) & 0x3F) / 63.0     # 0..1
        traits["antagonism"]    = (f3 >> 14) & 0b11             # 0..3 ordinal

        return traits

    def phenotype(self) -> Dict[str, Any]:
        """
        Return phenotype dictionary for inspection/logging.
        """
        return self.traits

    def __repr__(self) -> str:
        return (f"Phenotype(polarity={self.traits['polarity']}, "
                f"mood={self.traits['mood']}, "
                f"size={self.traits['base_size']:.2f}, "
                f"speed={self.traits['speed']:.2f}, "
                f"lifespan={self.traits['lifespan']})")
