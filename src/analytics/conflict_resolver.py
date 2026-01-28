from typing import Dict, List


def resolve_conflicts(
    conflicts: Dict,
    scores: Dict[str, int],
) -> Dict[str, List[str]]:

    removals: Dict[str, List[str]] = {}

    if not conflicts or "conflicts" not in conflicts:
        return removals

    for conflict in conflicts.get("conflicts", []):

        ids = conflict.get("ids")
        claim_a = conflict.get("claim_a")
        claim_b = conflict.get("claim_b")

        if not ids or len(ids) != 2:
            continue

        if not claim_a or not claim_b:
            continue

        s1, s2 = ids

        score1 = scores.get(s1, 0)
        score2 = scores.get(s2, 0)

        if score1 == score2:
            continue

        if score1 > score2:
            loser, claim = s2, claim_b
        else:
            loser, claim = s1, claim_a

        removals.setdefault(loser, []).append(claim)

    return removals
