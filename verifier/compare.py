import math


def numbers_match(a: float, b: float, rel_tol=1e-6, abs_tol=0.01) -> bool:
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)