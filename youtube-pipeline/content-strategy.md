# Content Strategy

## Target audience

Curious generalists, 18–45, who watch channels like *history explainer / edutainment*
content on lunch breaks and before bed. They are not history buffs; they click on a
specific, concrete promise ("this button…", "one map error…") rather than broad topics
("The History of France"). English-speaking, worldwide, majority US/UK/CA/AU traffic —
which is also where the affiliate programs pay.

## Content pillars

| # | Pillar | What it is | Example topics | Affiliate mapping |
|---|--------|------------|----------------|-------------------|
| 1 | **Objects with a past** | Micro-history of one everyday object | Why clocks run clockwise; the button and Napoleon's army; the shipping container | History books on the object's era; museum-quality replicas |
| 2 | **The day everything changed** | One dated day, hour by hour | The day the Thames froze solid; the 1858 Great Stink; the night the lights went on at Menlo Park | Narrative-history books; documentary streaming trials |
| 3 | **Forgotten figures** | People the textbooks skipped | The woman who mapped the ocean floor; the clerk who saved the Domesday Book | Biographies; audiobook trials (Audible-style) |
| 4 | **How did they actually…?** | Practical/engineering history | How did they build cathedrals without cranes? How did sailors navigate before longitude? | Maker/model kits; engineering-history books |
| 5 | **Myths vs. records** | Pop-history claims vs. primary sources | Vikings and horned helmets; Einstein failed math; medieval people thought Earth was flat | Source-criticism / "how history works" books |

Every video belongs to exactly one pillar. The backlog manager records the pillar and
the weekly summary reports performance per pillar so emphasis can shift with data.

## Posting cadence

- **Long-form:** 2 per week (Tue + Sat, 15:00 UTC — prime US morning / EU evening).
- **Shorts:** 3–5 per week, each cut from a recent or upcoming long-form video,
  scheduled on the days without a long-form upload.
- Cadence is enforced by the scheduler defaults in `config/settings.yml`; the review
  CLI assigns the next open slot when a video is approved.

## How pillars map to affiliate offers

- The link registry (`config/links.yml`) tags each affiliate link with the pillars it
  fits. The metadata generator only inserts links whose tags match the video's pillar —
  a cathedral-engineering video gets the engineering-history book, not a generic list.
- 2–3 links max per description. Relevance beats volume; irrelevant links depress
  click-through and trust.
- Every description containing an affiliate link carries the FTC disclosure — this is
  enforced in code (`metadata_generator.py` refuses to emit links without it), not by
  convention.

## Growth logic

- Shorts are the discovery engine → each Short's pinned comment and end-text points to
  the long-form video it was cut from.
- Long-form watch time is the monetization engine (YPP) and the affiliate conversion
  surface (descriptions).
- The weekly summary (`pipeline/reporting/weekly_summary.py`) recommends the next
  week's pillar emphasis from views, retention, and affiliate CTR — a human decides;
  the pipeline only suggests.
