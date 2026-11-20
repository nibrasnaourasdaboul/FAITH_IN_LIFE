"""Machine-learning boundary for relapse risk and progress models.

Planned libraries: torch, scikit-learn.
"""


class RiskModelService:
    # مكان مخصص لاحقاً لتقدير درجة الخطر من البيانات.
    def score(self, features: dict) -> dict:
        raise NotImplementedError("Machine learning models are not enabled yet.")
