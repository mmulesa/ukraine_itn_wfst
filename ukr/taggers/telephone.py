"""
TelephoneFst: ITN теггер для українських телефонних номерів.

Вхід:  "нуль п'ятдесят сім сімсот сімдесят вісім нуль три тринадцять"
Вихід: telephone { number_part: "057-778-03-13" }

Формат UA мобільного: 0XX-XXX-XX-XX (10 цифр)

Важливо про TSV-файли:
  cardinals_ties.tsv:    2→двадцять  (множник десятків, не саме число)
  cardinals_hundred.tsv: 1→сто       (множник сотень, не саме число)
  Після pynini.invert:   двадцять→2, сто→1

  Тому для отримання "50" з "п'ятдесят" потрібно:
    invert(ties) дає "п'ятдесят"→"5"
    далі pynutil.insert("0") або + invert(digit)
"""
import pynini
from pynini.lib import pynutil
from ukr.graph_utils import GraphFst
from ukr.utils import get_abs_path


def _load(relative_path: str) -> pynini.Fst:
    """Завантажити TSV і зробити invert (слово → цифра/множник)."""
    return pynini.invert(
        pynini.string_file(get_abs_path(relative_path))
    )


class TelephoneFst(GraphFst):
    """
    ITN теггер телефонних номерів.

    Приклади:
      "нуль п'ятдесят сім сімсот сімдесят вісім нуль три тринадцять"
        -> telephone { number_part: "057-778-03-13" }

      "нуль шістдесят сім двісті тридцять чотири п'ятдесят шість сімдесят вісім"
        -> telephone { number_part: "067-234-56-78" }
    """

    def __init__(self):
        super().__init__(name="telephone", kind="classify")

        sp = pynutil.delete(" ")

        # ── Завантажуємо словники (після invert: слово → множник/цифра) ──────

        # "нуль"→"0", "нулі"→"0"
        zero = _load("data/numbers/cardinal/nominative/cardinals_zero.tsv")

        # "один"→"1" ... "дев'ять"→"9"
        digit = _load("data/numbers/cardinal/nominative/cardinals_digit.tsv")

        # "десять"→"10" ... "дев'ятнадцять"→"19"  (вже готові числа у TSV)
        teen = _load("data/numbers/cardinal/nominative/cardinals_teen.tsv")

        # "двадцять"→"2" ... "дев'яносто"→"9"  (множник!)
        ties = _load("data/numbers/cardinal/nominative/cardinals_ties.tsv")

        # "сто"→"1" ... "дев'ятсот"→"9"  (множник!)
        hundred = _load("data/numbers/cardinal/nominative/cardinals_hundred.tsv")

        # ── Базові числові блоки ─────────────────────────────────────────────

        # Одна цифра: 0–9
        d1 = zero | digit

        # Двозначне: 10–99
        #   teen:          "тринадцять"→"13"
        #   ties + digit:  "п'ятдесят"→"5" + "сім"→"7"  = "57"
        #   ties + "0":    "п'ятдесят"→"5" + "0"         = "50"
        d2 = (
            teen
            | ties + sp + digit
            | ties + pynutil.insert("0")
        )

        # Трицифрове: 100–999
        #   "сімсот сімдесят вісім" → "7"+"7"+"8" = "778"
        #   "сімсот тринадцять"     → "7"+"13"    = "713"
        #   "сімсот сімдесят"       → "7"+"7"+"0" = "770"
        #   "сімсот вісім"          → "7"+"0"+"8" = "708"
        #   "сімсот"                → "7"+"00"    = "700"
        d3 = (
            hundred + sp + ties + sp + digit
            | hundred + sp + teen
            | hundred + sp + ties + pynutil.insert("0")
            | hundred + pynutil.insert("0") + sp + digit
            | hundred + pynutil.insert("00")
        )

        # ── Групи для формату 0XX-XXX-XX-XX ──────────────────────────────────

        # Рівно 3 цифри у результаті:
        group3 = (
            d3                        # "сімсот сімдесят вісім"→"778"
            | d1 + sp + d2            # "нуль п'ятдесят сім"→"057"
            | d2 + sp + d1            # "двадцять три нуль"→"230"  (рідко)
            | d1 + sp + d1 + sp + d1  # "нуль п'ять сім"→"057"
        )

        # Рівно 2 цифри у результаті:
        group2 = (
            d2              # "тринадцять"→"13", "п'ятдесят шість"→"56"
            | d1 + sp + d1  # "нуль три"→"03"
        )

        # ── Фінальна збірка: 0XX-XXX-XX-XX ───────────────────────────────────
        number_part = (
            group3
            + pynutil.insert("-")
            + sp + group3
            + pynutil.insert("-")
            + sp + group2
            + pynutil.insert("-")
            + sp + group2
        )

        self.fst = (
            pynutil.insert("telephone { number_part: \"")
            + number_part
            + pynutil.insert("\" }")
        ).optimize()