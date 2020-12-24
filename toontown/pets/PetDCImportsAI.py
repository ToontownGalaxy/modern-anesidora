"""This file allows us to conditionally import pet-related modules for the DC
"""

if simbase.wantPets:
    from . import DistributedPetAI
