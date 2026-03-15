import pynini
from pynini.lib import pynutil
from ukr.graph_utils import GraphFst, delete_space

class TelephoneFst(GraphFst):
    def __init__(self):
        super().__init__(name="telephone", kind="verbalize")

        # Символи що можуть бути в номері: цифри, дефіс, плюс
        phone_char = pynini.closure(
            pynini.union("0","1","2","3","4","5","6","7","8","9","-","+"), 1
        )

        # Вхід на цьому етапі вже: number_part: "050-778-03-13"
        # (зовнішні tokens { telephone { } } вже прибрані)
        number = (
            pynutil.delete("number_part: \"")
            + phone_char
            + pynutil.delete("\"")
        )

        self.fst = self.delete_tokens(number).optimize()