"""Expert-system boundary for clinical rules.

Planned library: experta.
Rule authoring stays in the governance tables until this module is approved.
"""


class ClinicalExpertService:
    # مكان مخصص لاحقاً لتقييم الحالة بقواعد الخبرة.
    def evaluate(self, facts: dict) -> list[dict]:
        raise NotImplementedError("The expert system is not enabled yet.")
