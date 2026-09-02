import hashlib
from uuid import UUID

def assign_experiment_variant(recovery_case_id: UUID, experiment_id: UUID, variants: list[str]) -> str:
    """
    Deterministically assigns a variant based on the hash of the case ID and experiment ID.
    This guarantees that repeated calls for the same case/experiment return the same variant,
    without needing random assignment or state.
    """
    if not variants:
        raise ValueError("Must provide at least one variant")
        
    # Create a stable string representation
    stable_str = f"{str(recovery_case_id)}-{str(experiment_id)}"
    
    # MD5 is sufficient for uniform distribution in A/B testing
    hash_digest = hashlib.md5(stable_str.encode('utf-8')).hexdigest()
    
    # Convert first 8 hex characters to an integer
    hash_int = int(hash_digest[:8], 16)
    
    # Modulo by number of variants to get the bucket
    bucket = hash_int % len(variants)
    
    return variants[bucket]
