"""RAG and medical-imaging boundary.

Planned libraries: langchain, ollama, pydicom.
Embeddings belong on embedding_indexes.embedding (pgvector).
"""


class ClinicalRetrievalService:
    # مكان مخصص لاحقاً للإجابة من المعرفة الطبية.
    def answer(self, question: str, patient_id: str) -> dict:
        raise NotImplementedError("RAG is not enabled yet.")


class ImagingPreviewService:
    # مكان مخصص لاحقاً لتلخيص دراسة التصوير.
    def summarize_study(self, study_id: str) -> dict:
        raise NotImplementedError("Imaging AI is not enabled yet.")
