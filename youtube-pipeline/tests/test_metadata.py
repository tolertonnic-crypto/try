import pytest

from pipeline.metadata_generator import build_description, pick_links, utm_tag

CFG = {
    "max_links_per_video": 2,
    "ftc_disclosure": "Some links are affiliate links.",
    "amazon_tag": "chan-20",
    "links": [
        {"id": "a", "label": "Book A", "url": "https://www.amazon.com/dp/X",
         "pillars": ["forgotten-figures"], "kind": "amazon"},
        {"id": "b", "label": "Book B", "url": "https://example.com/b",
         "pillars": ["forgotten-figures", "myths-vs-records"], "kind": "generic"},
        {"id": "c", "label": "Book C", "url": "https://example.com/c",
         "pillars": ["forgotten-figures"], "kind": "generic"},
    ],
}


def test_utm_params_added():
    url = utm_tag("https://example.com/b", "my-video")
    assert "utm_source=youtube" in url
    assert "utm_medium=description" in url
    assert "utm_campaign=my-video" in url


def test_amazon_tag_only_on_amazon_urls():
    assert "tag=chan-20" in utm_tag("https://www.amazon.com/dp/X", "v", "chan-20")
    assert "tag=chan-20" not in utm_tag("https://example.com/b", "v", "chan-20")


def test_pick_links_filters_by_pillar_and_caps():
    links = pick_links("forgotten-figures", CFG)
    assert len(links) == 2  # max_links_per_video
    assert pick_links("the-day-everything-changed", CFG) == []


def test_ftc_disclosure_always_present_with_links():
    desc = build_description("About the video.", "forgotten-figures", "slug", CFG)
    assert "affiliate links" in desc
    assert "utm_campaign=slug" in desc


def test_no_links_no_disclosure_needed():
    desc = build_description("About.", "the-day-everything-changed", "slug", CFG)
    assert "affiliate" not in desc


def test_refuses_links_without_disclosure():
    bad = dict(CFG, ftc_disclosure="")
    with pytest.raises(ValueError):
        build_description("About.", "forgotten-figures", "slug", bad)
