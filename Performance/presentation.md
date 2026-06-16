---
title: "We Talkin' About Data?"
sub_title: |
    _- Allen Iverson_
event: PyData Leeds
date: 2026-04-28
authors:
  - Michael Park
theme:
  name: catppuccin-mocha
---

Who Am I
===

- Currently a Principal Data Engineer @ Hippo Digital
- Work primarily in Python  & SQL but use , , , 󱁢,  ...
- Self-taught over the last 11-ish years
- TUI Enthusiast, I use `neovim` btw...
- Into basketball 🏀 & golf ⛳
- Can read more or see ways to contact me here  `mhpark.me`
- 🇬🇧 🇺🇸 Dual National

<!-- end_slide -->

Agenda
===

I'd like to talk about a few things today

- file formats for data transmission, storage, and processing
- encryption formats for the above
- data for endpoints vs. data for analysis and OLAP
- a little benchmarking
- hopefully have some discussions around them where we can share experiences

### Tech we're going to use today

```toml
[project]
dependencies = [
    "alembic>=1.18.4",
    "duckdb>=1.5.2",
    "faker>=40.13.0",
    "fastavro>=1.12.1",
    "litestar[standard]>=2.21.1",
    "marimo[recommended]>=0.23.1",
    "msgpack>=1.1.2",
    "orjson>=3.11.8",
    "pandas>=3.0.2",
    "polars>=1.39.3",
    "python-snappy>=0.7.3",
    "sqlalchemy>=2.0.49",
    "ujson>=5.12.0",
    "zstd>=1.5.7.3",
]
```

<!-- end_slide -->

Interrupt, Ask Questions, Add Your Own Insights
===

My experience in certain parts of this talk varies from extensive to
exploratory, if you know something I don't, let me know!

<!-- end_slide -->

Let's git crackin'
===

You can code along with me, play around, try new things.

- `git clone https://github.com/KingMichaelPark/pydata-april-2026`
- `cd pydata-april-2026`

1. If you already have uv

```bash
uv sync
source .venv/bin/activate
```

2. If you already have python

```bash
python -m pip install uv
# Step 1
```

3. If you already have mise but if you don't have python or uv installed

```bash
# If you don't have mise
curl https://mise.run | sh

mise install
# Step 2
```

<!-- end_slide -->

Data Formats for transmission
===

- Avro
- CSV
- JSON
- Msgpack

Not Discussed

- OCR
- XML

<!-- end_slide -->

Data Formats for transmission
===

Stay Away

- Excel (No matter what the accountant says!)
- PDF

<!-- end_slide -->

Web
===

- Demo 1

<!-- end_slide -->


Data Formats
===

- Demo 2

<!-- end_slide -->

Data Compression
===

- Demo 3

<!-- end_slide -->

Why does this matter
===

- Demo 4

AI will do what you tell it, you just need to be aware of
what you need to consider before you tell it what to do. There
are real costs, performance penalties, all that can be hidden
away from a commit with passing unit tests and functioning code.
