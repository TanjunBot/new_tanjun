from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

OVERRIDES = {
    "math_name math_calc_name": case(
        "math_name math_calc_name",
        option_overrides={"equation": "2+2"},
        assert_profile="math",
    ),
    "math_name math_calculator_name": case(
        "math_name math_calculator_name",
        option_overrides={"expression": "2+2"},
        assert_profile="math",
    ),
    "math_name math_faculty_name": case(
        "math_name math_faculty_name",
        option_overrides={"number": 5},
    ),
    "math_name math_num2word_name": case(
        "math_name math_num2word_name",
        option_overrides={"number": 42},
    ),
    "math_name math_plotfunction_name": case(
        "math_name math_plotfunction_name",
        option_overrides={"func": "x"},
    ),
    "math_name math_randomnumber_name": case(
        "math_name math_randomnumber_name",
        option_overrides={"min": 1, "max": 10},
    ),
}
