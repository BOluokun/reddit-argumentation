from qbafs import QBAF
from math import prod
from decimal import Decimal
import numpy as np


def basic_tau(node: tuple[int, dict], x=0.5):
    return x


# DF-QuAD Gradual Semantics

def basic_eval_range(score: float):
    if score <= 0.5:
        return -1
    elif score > 0.5:
        return 1
    else:
        return 0


def df_quad_strength_agg(vs: list[float]):
    n = len(vs)
    if n == 0:
        return 0.0
    elif n == 1:
        return vs[0]
    elif n == 2:
        val = vs[0] + vs[1] - vs[0] * vs[1]
        return val
    else:
        last = vs[-1]
        front = df_quad_strength_agg(vs[:-1])
        val = df_quad_strength_agg([front, last])
        return val


def df_quad_combine(v0, v_neg, v_pos):
    if v_neg < v_pos:
        return v0 + (1 - v0) * abs(v_pos - v_neg)
    else:
        return v0 - v0 * abs(v_pos - v_neg)


def df_quad_semantics(qbaf: QBAF, a: int):
    tau_a = qbaf.tau(a)
    attacker_evals = [df_quad_semantics(qbaf, b) for b in qbaf.get_attackers(a)]
    supporter_evals = [df_quad_semantics(qbaf, b) for b in qbaf.get_supporters(a)]
    df_combine = df_quad_combine(tau_a, df_quad_strength_agg(attacker_evals), df_quad_strength_agg(supporter_evals))
    return df_combine


# QuAD Semantics

def f_a(w: float, atts: list[float]):
    return w * prod([1 - a for a in atts])

def f_s(w: float, sups: list[float]):
    return 1 - (1 - w) * prod([1 - s for s in sups])

def quad_semantics(qbaf: QBAF, a: int):
    tau_a = qbaf.tau(a)
    attacker_evals = [quad_semantics(qbaf, b) for b in qbaf.get_attackers(a)]
    supporter_evals = [quad_semantics(qbaf, b) for b in qbaf.get_supporters(a)]
    if not attacker_evals and not supporter_evals:
        return tau_a
    elif not attacker_evals:
        return f_s(tau_a, supporter_evals)
    elif not supporter_evals:
        return f_a(tau_a, attacker_evals)
    else:
        return (f_a(tau_a, attacker_evals) + f_s(tau_a, supporter_evals)) / 2


# QEM Semantics

def qem_h(x: float):
    y = max(0, x)
    return (y ** 2) / (1 + y ** 2)


def qem_energy(qbaf: QBAF, a: int):
    attacker_evals = [qem_semantics(qbaf, b) for b in qbaf.get_attackers(a)]
    supporter_evals = [qem_semantics(qbaf, b) for b in qbaf.get_supporters(a)]
    return sum(supporter_evals) - sum(attacker_evals)


def qem_semantics(qbaf: QBAF, a: int):
    tau_a = qbaf.tau(a)
    e_j = qem_energy(qbaf, a)
    return tau_a + (1 - tau_a) * qem_h(e_j) - tau_a * qem_h(-e_j)


# REB (Ebs) Semantics

def reb_semantics(qbaf: QBAF, a: int):
    tau_a = qbaf.tau(a)
    attacker_evals = [reb_semantics(qbaf, b) for b in qbaf.get_attackers(a)]
    supporter_evals = [reb_semantics(qbaf, b) for b in qbaf.get_supporters(a)]
    E = sum(supporter_evals) - sum(attacker_evals)
    if E >= 0:
        numerator = 1 - tau_a * 2
        try:
            denominator = 1 + tau_a * np.exp(E * np.log(2))
        except:
            print(f"Overflow error for E = {E}, tau_a = {tau_a}")
            return 0
    else:
        # Handle negative E
        E_ = abs(E)
        try:
            numerator = np.exp(E_ * np.log(2)) * (1 - tau_a ** 2)
            denominator = np.exp(E_ * np.log(2)) + tau_a
        except:
            print(f"Overflow error for E = {E}, tau_a = {tau_a}")
            return 0
    return 1 - numerator / denominator



if __name__ == '__main__':
    args = [(1, {'label': 'a'}), (2, {'label': 'b'}), (3, {'label': 'c'})]
    sups = [(3, 1)]
    atts = [(1, 0), (2, 0), (3, 2)]
    ex_qbaf = QBAF({'text': 'this is a test'}, args, basic_tau, df_quad_semantics, basic_eval_range, atts, sups)

    print('For DF-QuAD:')
    print(f'Stance is: {ex_qbaf.get_stance()}')

    for i in range(4):
        print(f"Score for arg {i} is: {ex_qbaf.evaluate_argument(i)}")

    print('\nFor QEM:')
    ex_qbaf.update_semantics(qem_semantics)
    print(f'Stance is: {ex_qbaf.get_stance()}')

    for i in range(4):
        print(f"Score for arg {i} is: {ex_qbaf.evaluate_argument(i)}")
