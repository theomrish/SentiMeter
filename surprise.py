"""Compute the three facts about a scheduled economic release."""

# -------------- imports --------------
from dataclasses import dataclass

# -------------- definitions --------------
@dataclass
class ReleaseFacts:
    level: float
    move: float
    surprise: float



def surprise_calc(prior:float,consensus:float,actual:float) -> ReleaseFacts:
    """This function calculate the magnitude of economic surprise"""

    facts = ReleaseFacts(level=actual,move=(actual-prior),surprise=(actual-consensus))
    return facts




if __name__ == "__main__":
    facts = surprise_calc(prior=3.2, consensus=2.9, actual=3.0)
    print(f"Level:{facts.level:.2f}, Move:{facts.move:+.2f}, Surprise:{facts.surprise:+.2f}")
