from pathlib import Path

from gqqd.defaults import POSTPROCESSING_FILES


class Deduplicator:
    def __init__(self, filepath: Path) -> None:
        with open(filepath, "r") as f:
            self.duplicated_q_p_ids = {l for l in f.read().splitlines() if not l.startswith("#")}

    def is_duplicate(self, q_p_id: str) -> bool:
        return q_p_id in self.duplicated_q_p_ids


class MRCDeduplicator(Deduplicator):
    def __init__(self) -> None:
        super().__init__(POSTPROCESSING_FILES / "deduplication_kbqa.txt")


class KBQADeduplicator(Deduplicator):
    def __init__(self) -> None:
        super().__init__(POSTPROCESSING_FILES / "deduplication_mrc.txt")
