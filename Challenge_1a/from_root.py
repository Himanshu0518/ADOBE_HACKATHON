import os 

def from_root():
    """
    Constructs a path relative to the root of the project.
    """
    return os.path.join(os.path.dirname(__file__)) 

print(f"Root path: {from_root()}")