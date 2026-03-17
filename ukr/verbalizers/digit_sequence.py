"""
DigitSequenceFst verbalizer:
  digit_sequence { value: "1234" } -> "1234"
"""
import pynini
from pynini.lib import pynutil

from ukr.graph_utils import GraphFst, delete_space, NEMO_NOT_QUOTE


class DigitSequenceFst(GraphFst):
    def __init__(self):
        super().__init__(name="digit_sequence", kind="verbalize")

        graph = (
            pynutil.delete("value:")
            + delete_space
            + pynutil.delete("\"")
            + pynini.closure(NEMO_NOT_QUOTE, 1)
            + pynutil.delete("\"")
        )

        self.fst = self.delete_tokens(graph).optimize()