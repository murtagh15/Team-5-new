def calculate_total_score(*, math: int, rus: int, phys: int, inf: int, eng: int, ach: int) -> int:
    return int(math) + int(rus) + int(phys) + int(inf) + int(eng) + int(ach)


# alias (можно оставить, чтобы старый код не ломался)
def total_score(*, math: int, rus: int, phys: int, inf: int, eng: int, ach: int) -> int:
    return calculate_total_score(math=math, rus=rus, phys=phys, inf=inf, eng=eng, ach=ach)