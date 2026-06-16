# 🏠 PyData Leeds: Data Formats & Performance 🚀

Welcome! This repository contains the code and resources for a **PyData Leeds**
talk on exploring different data formats, understanding their performance
trade-offs, and how they interact with modern Python tools.

## 🎯 Project Goals

- **Learn about Data Formats**: Compare common and specialized formats like
  JSON, orjson, ujson, MessagePack, CSV, and Avro.
- **Performance Benchmarking**: Measure how long it takes to serialize,
  deserialize, and store data.
- **Modern Python Stack**: See how these formats fit into a high-performance
  stack using Litestar, SQLAlchemy Core vs. ORM, and tools like Polars and
  DuckDB.
- **Practical Implementation**: A real-world-ish scenario involving housing
  data and a web API.

---

## 🛠️ Tech Stack

- **Framework**: [Litestar](https://litestar.dev/) (High-performance ASGI
  framework)
- **Database**: SQLite with [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (ORM
  & Core)
- **Data Analysis**: [Polars](https://pola.rs/),
  [Pandas](https://pandas.pydata.org/), [DuckDB](https://duckdb.org/)
- **Serialization**: `json`, `orjson`, `ujson`, `msgpack`, `fastavro`
- **Environment**: Managed by [uv](https://github.com/astral-sh/uv) and
  [mise](https://mise.jdx.dev/)
- **Interactive**: [Marimo](https://marimo.io/) notebooks

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have [uv](https://github.com/astral-sh/uv) installed.

### 2. Setup Environment

```bash
# Install dependencies and setup venv
uv sync

# (Optional) If using mise
mise install
```

### 3. Database Migrations

Set up the SQLite database schema using Alembic:

```bash
uv run alembic upgrade head
# Or
mise run setup
```

---

## 📊 Usage

### 🧪 Data Generation & Benchmarking

Generate 1,000 mock housing records in various formats and see the time it takes to save them:

```bash
# Generate all supported formats with multiple iterations, custom record count, and verbose size info
uv run generate_data.py --all --num-files 5 --num-records 5000 --verbose

# Or generate specific formats
uv run generate_data.py json csv avro --num-files 2 --num-records 100 --verbose
```

_Generated files are saved in the `data/` directory as `housing_test_{index}.{fmt}`.\_
_Results are sorted by total time (ascending)._

### 🌐 Running the Web API

Start the Litestar server to test data ingestion:

```bash
uv run app.py
```

#### API Endpoints:

- `GET /housing?page=1&limit=10`: Fetch paginated housing records.
- `POST /housing`: Upload data in different formats (`json`, `orjson`, `ujson`,
  `msgpack`, `csv`, `avro`) and choose an `insert_mode` (`orm` or `core`).

---

## 📈 Key Learnings

- **JSON vs. The World**: Why `orjson` and `ujson` are often preferred over the
  standard library `json`.
- **Binary Formats**: How `MessagePack` and `Avro` reduce file size and speed
  up parsing.
- **SQLAlchemy Core vs. ORM**: The performance impact of using high-level
  abstractions for bulk inserts.
- **Modern Notebooks**: Using `Marimo` for interactive data exploration that's
  reproducible and git-friendly.

---

## 🎤 About PyData Leeds

PyData Leeds is a community for users and developers of data analysis tools to
share ideas and learn from each other.

Join us for our next meetup! [PyData Leeds on
Meetup](https://www.meetup.com/pydata-leeds/)

---

_Happy Coding!_ 🐍💻
