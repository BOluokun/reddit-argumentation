import json
import os

from gradual_semantics import basic_tau, basic_eval_range, df_quad_semantics
from qbafs import QBAF


def build_qbaf_from(c_thread, parent_i, args, sups, atts, nr=False, level=None):
    if level is not None:
        if level == 0:
            return
        else:
            level -= 1

    if c_thread['relation'] == 'No' and nr:
        return

    info = {'text': c_thread['content'], 'score': c_thread['score']}

    args.append((c_thread['id'], info))

    # Treat the case of a no relation as a support when nr is False
    if c_thread['relation'] == 'Support' or c_thread['relation'] == 'No':
        sups.append((c_thread['id'], parent_i))
    elif c_thread['relation'] == 'Attack':
        atts.append((c_thread['id'], parent_i))

    for com in c_thread['comments']:
        build_qbaf_from(com, c_thread['id'], args, sups, atts, nr=nr, level=level)


def build_thread_qbaf(thread, tau_func: callable = basic_tau, nr=False, level=None):
    args, supports, attacks = [], [], []

    info = {'text': thread['post content']}

    args.append((thread['id'], info))
    supports.append((thread['id'], 0))

    for com in thread['comments']:
        build_qbaf_from(com, thread['id'], args, supports, attacks, nr=nr, level=level)

    qbaf = QBAF(
        explanandum={'text': "OP is NTA"}, arguments=args,
        tau=tau_func, eval_range=basic_eval_range, semantics=df_quad_semantics,
        supports=supports, attacks=attacks
    )

    return qbaf

