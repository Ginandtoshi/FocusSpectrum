"""Results builder and simple summary exports."""
from __future__ import annotations

from typing import Dict


class ResultsBuilder:
    def __init__(self):
        self.data: Dict[str, object] = {}

    def add(self, name: str, result: Dict) -> None:
        self.data[name] = result

    def summarize(self) -> Dict:
        return {"games": list(self.data.keys()), "details": self.data}
