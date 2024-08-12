import re
from itertools import chain
from typing import TypedDict


class _WikiContext(TypedDict):
    start_idx: int
    end_idx: int
    wiki_link: str


class PassageConstructor:
    """
    The class is used to construct short passages from a long text.
    """

    def __init__(self, length: int, step: int, ensure_full_coverage: bool = True):
        """
        :param length: int
            length of sliding window
        :param step: int
            step of sliding window
        :param ensure_full_coverage: bool, optional
            flag that ensures full coverage of the given sequence when
            len(sequence.split()) % step != 0 or len(sequence.split()) < length
        """
        self.length = length
        self.step = step
        self.ensure_full_coverage = ensure_full_coverage

    def construct(
        self, sequence: str, links: list[_WikiContext]
    ) -> tuple[list[str], list[list[_WikiContext]]]:
        """
        The method slice long sequence using sliding window then assign links from wikipedia to
        each of them.
        :param sequence: a long sequence to slice
        :param links: a list of wiki links assigned to sequence
        :return: tuple of sliced text and list of lists of wiki links
        """
        links_map: dict[tuple[int, int], str] = {
            (x["start_idx"], x["end_idx"]): x["wiki_link"] for x in links
        }
        passages, split_idx = self.split_on_window(sequence)
        passages_links = []
        for passage, (start_idx, end_idx) in zip(passages, split_idx):
            single_passage_links = []
            for start_link_idx, end_link_idx in links_map.keys():
                if start_idx <= start_link_idx < end_idx and start_idx < end_link_idx <= end_idx:
                    link: _WikiContext = {
                        "start_idx": start_link_idx - start_idx,
                        "end_idx": end_link_idx - start_idx,
                        "wiki_link": links_map[(start_link_idx, end_link_idx)],
                    }
                    single_passage_links.append(link)
            passages_links.append(single_passage_links)
        return passages, passages_links

    def split_on_window(self, sequence: str) -> tuple[list[str], list[tuple[int, int]]]:
        """
        :param sequence: a long and stripped sequence to be sliced
        :return: tuple of sliced text and list of tuples with (start_idx, end_idx) of the
            long sequence.
        """
        if sequence.strip() != sequence:
            raise ValueError("Sequence has to be stripped.")
        split_text, split_idx = [], []
        split_sequence, whitespaces = self._deconstruct_sequence(sequence)
        last_end = 0
        for index in range(0, len(split_sequence) - self.length + 1, self.step):
            reconstructed_sequence = self._reconstruct_sequence(
                split_sequence[index : index + self.length],
                whitespaces[index : index + self.length - 1],
            )
            split_text.append(reconstructed_sequence)
            current_length = (
                len(
                    self._reconstruct_sequence(
                        split_sequence[:index],
                        whitespaces[: index - 1],
                    )
                )
                + 1
                if index > 0
                else 0
            )
            split_idx.append((current_length, current_length + len(split_text[-1])))
            last_end = index + self.length
        if self.ensure_full_coverage and last_end < len(split_sequence):
            reconstructed_sequence = self._reconstruct_sequence(
                split_sequence[max(0, len(split_sequence) - self.length) : len(split_sequence)],
                whitespaces[max(0, len(split_sequence) - self.length) : len(split_sequence) - 1],
            )
            split_text.append(reconstructed_sequence)
            current_length = (
                len(
                    self._reconstruct_sequence(
                        split_sequence[: -self.length],
                        whitespaces[: -self.length],
                    )
                )
                + 1
                if len(split_text) > 1
                else 0
            )
            split_idx.append((current_length, len(sequence)))
        return split_text, split_idx

    def _reconstruct_sequence(self, split_sequence: list[str], whitespaces: list[str]) -> str:
        if len(split_sequence) == len(whitespaces) == 0:
            return ""
        assert len(split_sequence) == len(whitespaces) + 1
        return "".join(chain.from_iterable(zip(split_sequence, whitespaces + [""])))

    def _deconstruct_sequence(self, sequence: str) -> tuple[list[str], list[str]]:
        if sequence == "":
            return [], []
        split = re.split(r"(\s+)", sequence)
        return split[::2], split[1::2]
