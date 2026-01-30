# src/analytics/conflict_resolver.py

from typing import Dict, List


def resolve_conflicts(
    conflicts: Dict,
    scores: Dict[str, int],
) -> Dict[str, List[str]]:
    """
    CONFLICT RESOLUTION LOGIC
    =========================

    After hard contradictions are detected, this module decides
    which claims should be removed from which summaries.

    Strategy:
        • Each summary has a total evidence score
          (credibility + agreement support)
        • When two summaries conflict, the lower-scoring one loses
        • Only the specific conflicting claim is removed
          (not the entire summary)

    This enables *surgical correction* rather than deleting evidence.

    Parameters
    ----------
    conflicts : Dict
        Output of conflict detector:
        {
          "conflicts": [
            {
              "ids": ["S1", "S2"],
              "claim_a": "...",
              "claim_b": "..."
            }
          ]
        }

    scores : Dict[str, int]
        Mapping summary ID → total evidence score.

    Returns
    -------
    Dict[str, List[str]]
        Mapping:
            summary_id → list of claims to remove
    """

    removals: Dict[str, List[str]] = {}

    # No conflicts → nothing to resolve
    if not conflicts or "conflicts" not in conflicts:
        return removals

    # Process each detected contradiction
    for conflict in conflicts.get("conflicts", []):

        ids = conflict.get("ids")
        claim_a = conflict.get("claim_a")
        claim_b = conflict.get("claim_b")

        # Skip malformed entries
        if not ids or len(ids) != 2:
            continue

        if not claim_a or not claim_b:
            continue

        s1, s2 = ids

        # Retrieve evidence scores
        score1 = scores.get(s1, 0)
        score2 = scores.get(s2, 0)

        # If scores are equal, system does not arbitrate
        if score1 == score2:
            continue

        # Lower-scoring summary loses its conflicting claim
        if score1 > score2:
            loser, claim = s2, claim_b
        else:
            loser, claim = s1, claim_a

        removals.setdefault(loser, []).append(claim)

    return removals
