from pyxavi.media import Media

FIXTURES = [
    ["<a><p src=\"image_1.png\">whatever</p>", None, None],
    [
        "<b><img src=\"image_1.png\" /></b>", [{
            "src": "image_1.png"
        }], [{
            "url": "image_1.png", "alt_text": None
        }]
    ],
    [
        "<b><img src=\"image_1.png\" /><img src=\"image_2.png\" alt=\"Test\" /></b>",
        [{
            "src": "image_1.png"
        }, {
            "src": "image_2.png", "alt": "Test"
        }],
        [{
            "url": "image_1.png", "alt_text": None
        }, {
            "url": "image_2.png", "alt_text": "Test"
        }]
    ]
]


def test_parser_detects_img_tag():
    for fixture in FIXTURES:

        assert fixture[2] == Media().get_media_url_from_text(fixture[0])
