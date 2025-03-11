
from . import ERC224
from . import ECC133
from . import silvacoVD
from . import characterization
from . import semi_physics

__version__ = "0.1.0"
__author__ = "Eugene Hsu"

def info():
    return "TTLAB Semiconductor analysis and simulation package"

# Ensure all key modules are included in API docs
__all__ = [
    "ERC224",
    "ECC133",
    "silvacoVD",
    "characterization",
    "semi_physics",
]