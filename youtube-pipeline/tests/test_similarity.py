from pipeline.similarity import jaccard, similarity_report, tokens


def test_tokens_strip_stopwords():
    assert "the" not in tokens("the history of the clock")
    assert "clock" in tokens("the history of the clock")


def test_identical_topics_score_high():
    assert jaccard("Why do clocks run clockwise?", "Why do clocks run clockwise?") == 1.0


def test_unrelated_topics_score_low():
    assert jaccard("Why do clocks run clockwise?", "The woman who mapped the ocean floor") < 0.1


def test_report_flags_near_duplicates():
    candidate = {"title": "Why clocks run clockwise", "angle": "sundials set the direction"}
    recent = [
        {"id": "t1", "title": "Why do clocks run clockwise?",
         "angle": "Sundials set the direction of clocks"},
        {"id": "t2", "title": "The Thames froze solid", "angle": "frost fairs"},
    ]
    report = similarity_report(candidate, recent, threshold=0.35)
    assert report["flagged"]
    assert report["flagged_matches"][0]["id"] == "t1"


def test_report_passes_distinct_topics():
    candidate = {"title": "The button that beat Napoleon", "angle": "tin pest in uniform buttons"}
    recent = [{"id": "t1", "title": "Why do clocks run clockwise?", "angle": "sundials"}]
    report = similarity_report(candidate, recent, threshold=0.35)
    assert not report["flagged"]
