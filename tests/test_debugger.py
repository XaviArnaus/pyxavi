from pyxavi import dd
from collections import deque
import pytest


class ClassA:
    attribute_a: int
    attribute_b: str
    attribute_c: list

    def __init__(self, attr_a: int = 0, attr_b: str = "", attr_c: list = []) -> None:
        self.attribute_a = attr_a
        self.attribute_b = attr_b
        self.attribute_c = attr_c

    def my_method(self) -> None:
        pass


class ClassB(ClassA):
    attribute_x: dict


@pytest.mark.parametrize(
    argnames=('what', 'expected_result'),
    argvalues=[
        # Primitives (yeah, not in Python, but you get my point)
        ("I am a string", "(str[13])\"I am a string\""),
        (123, "(int)123"),
        (-123, "(int)-123"),
        (0, "(int)0"),
        (123.45, "(float)123.45"),
        (-123.45, "(float)-123.45"),
        (0.00, "(float)0.0"),
        (True, "(bool)True"),
        (False, "(bool)False"),
        (None, "(NoneType)None"),
        # Lists of primitives
        ([1, 2, 3], "(list[3])[(int)1, (int)2, (int)3]"),
        (["a", "b", "c"], "(list[3])[(str[1])\"a\", (str[1])\"b\", (str[1])\"c\"]"),
        (["a", 2, "c"], "(list[3])[(str[1])\"a\", (int)2, (str[1])\"c\"]"),
        ([], "(list[0])[]"),
        # Sets of primitives. By nature, sets do not guaranteee order.
        # (set([1,1,2]), "(set[2]){(int)1, (int)2}"),
        # (set(["a","a","b"]), "(set[2]){(str[1])\"a\", (str[1])\"b\"}"),
        # (set(["a","a",2]), "(set[2]){(str[1])\"a\", (int)2}"),
        (set([]), "(set[0]){}"),
        # Deques of primitives
        (deque([1, 2, 3]), "(deque[3])[(int)1, (int)2, (int)3]"),
        (deque(["a", "b", "c"]), "(deque[3])[(str[1])\"a\", (str[1])\"b\", (str[1])\"c\"]"),
        (deque(["a", 2, "c"]), "(deque[3])[(str[1])\"a\", (int)2, (str[1])\"c\"]"),
        (deque([]), "(deque[0])[]"),
        # Tuples of primitives
        ((1, 2, 3), "(tuple[3])[(int)1, (int)2, (int)3]"),
        (("a", "b", "c"), "(tuple[3])[(str[1])\"a\", (str[1])\"b\", (str[1])\"c\"]"),
        (("a", 2, "c"), "(tuple[3])[(str[1])\"a\", (int)2, (str[1])\"c\"]"),
        ((), "(tuple[0])[]"),
        # Dicts of primitives
        ({
            "a": 1, "b": 2, "c": 3
        }, "(dict[3]){\"a\": (int)1, \"b\": (int)2, \"c\": (int)3}"),
        (
            {
                "a": "aa", "b": "bb", "c": "cc"
            },
            "(dict[3]){\"a\": (str[2])\"aa\", \"b\": (str[2])\"bb\", \"c\": (str[2])\"cc\"}"
        ),
        (
            {
                "a": 1, "b": "bb", "c": 3
            },
            "(dict[3]){\"a\": (int)1, \"b\": (str[2])\"bb\", \"c\": (int)3}"
        ),
        ({}, "(dict[0]){}"),
        # Classes
        (
            ClassB(1, 2, 3),
            "(ClassB){\"attribute_a\": (int)1, \"attribute_b\": (int)2" +\
            ", \"attribute_c\": (int)3, class methods: my_method}"
        ),
        (
            ClassA(1, "b", [9, "x"]),
            "(ClassA){\n  \"attribute_a\": (int)1,\n  \"attribute_b\": (str[1])\"b\"," +\
            "\n  \"attribute_c\": (list[2])[(int)9, (str[1])\"x\"],\n  class methods" +\
            ": my_method\n}"
        ),
        # Complex Lists
        (
            [[1, 2], ["a", "b"], "x"],
            "(list[3])[\n  (list[2])[(int)1, (int)2],\n  (list[2])[(str[1])\"a\"" +\
            ", (str[1])\"b\"],\n  (str[1])\"x\"\n]"
        ),
        (
            [{
                "a": 1, "b": 2
            }, {
                "x": [9, 8]
            }],
            "(list[2])[\n  (dict[2]){\"a\": (int)1, \"b\": (int)2},\n  (dict[1]){" +\
            "\n    \"x\": (list[2])[(int)9, (int)8]\n  }\n]"
        ),
        (
            [{
                "x": [9, 8]
            }, {
                "y": [7, 6]
            }],
            "(list[2])[\n  (dict[1]){\n    \"x\": (list[2])[(int)9, (int)8]\n  }," +\
            "\n  (dict[1]){\n    \"y\": (list[2])[(int)7, (int)6]\n  }\n]"
        ),
        # Complex Dicts
        (
            {
                "a": {
                    "aa": {
                        "aaa": 1
                    }, "bb": {
                        "bbb": {
                            "bbbb": 2
                        }
                    }
                }, "c": 3
            },
            "(dict[2]){\n  \"a\": (dict[2]){\n    \"aa\": (dict[1]){\"aaa\": (int)1}," + \
            "\n    \"bb\": (dict[1]){\n      \"bbb\": (dict[1]){\"bbbb\": (int)2}" + \
            "\n    }\n  },\n  \"c\": (int)3\n}"
        ),
        # Maximum depth block. In the test is defined as 4
        (
            [[[[["a", "b"]], 3], 2], 1],
            "(list[2])[\n  (list[2])[\n    (list[2])[\n      (list[1])[\n        (list[2])" + \
            "Max recursion depth of 4 reached.\n      ],\n      (int)3\n    ]," + \
            "\n    (int)2\n  ],\n  (int)1\n]"
        )
    ],
)
def test_dd(what, expected_result):
    result = dd(what=what, export=True, max_depth=4, colorise=False)

    assert expected_result == result
