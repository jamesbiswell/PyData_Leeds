import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md("# Data Warehouse Query & Storage Simulator (AWS 2026)")

    # --- SLIDERS & INPUTS ---
    sidebar_header = mo.md("## 📊 Workload Settings")

    raw_data_tb = mo.ui.slider(
        start=1,
        stop=1000,
        step=10,
        value=100,
        label="Raw Uncompressed Data Volume (TB)",
    )

    queries_per_month = mo.ui.number(
        value=5000, label="Monthly Analytical Queries", step=500
    )

    # --- NEW: EXPLICIT DATA MODELING TOGGLES ---
    columns_accessed_pct = mo.ui.slider(
        start=1, stop=100, value=15, label="Avg % of Columns Read (Columnar Savings)"
    )

    partition_pruning_pct = mo.ui.slider(
        start=0,
        stop=99,
        value=80,
        label="Partition Pruning (% of S3 files skipped by WHERE clause)",
    )

    z_ordering_pct = mo.ui.slider(
        start=0,
        stop=95,
        value=50,
        label="Predicate Pushdown (% of internal file chunks skipped due to sorting)",
    )

    # AWS Pricing Constants
    s3_storage_price_tb = mo.ui.number(
        value=23.55, label="S3 Standard Price per TB/mo ($)"
    )

    athena_scan_price_tb = mo.ui.number(
        value=5.00, label="Athena Price per TB Scanned ($)"
    )

    sidebar = mo.sidebar(
        [
            sidebar_header,
            raw_data_tb,
            queries_per_month,
            mo.md("---"),
            mo.md("## 🏗️ Data Architecture"),
            mo.md("*Only applies to columnar formats:*"),
            columns_accessed_pct,
            z_ordering_pct,
            mo.md("*Applies to all formats:*"),
            partition_pruning_pct,
            mo.md("---"),
            mo.md("## 💰 AWS Rates"),
            s3_storage_price_tb,
            athena_scan_price_tb,
        ]
    )

    # --- FORMAT & COMPRESSION SCENARIOS ---
    # is_columnar: Unlocks column skipping AND internal file chunk
    # skipping (predicate pushdown)
    scenario_data = {
        "JSON (Raw)": {
            "size_multiplier": 1.0,
            "is_columnar": False,
            "color": "#f44336",
        },
        "JSON (Gzip)": {
            "size_multiplier": 0.35,
            "is_columnar": False,
            "color": "#e91e63",
        },
        "Parquet (Uncompressed)": {
            "size_multiplier": 0.60,
            "is_columnar": True,
            "color": "#ff9800",
        },
        "Parquet (Snappy)": {
            "size_multiplier": 0.25,
            "is_columnar": True,
            "color": "#9c27b0",
        },
        "Parquet (Zstd)": {
            "size_multiplier": 0.15,
            "is_columnar": True,
            "color": "#3f51b5",
        },
    }
    mo.as_html(sidebar)
    return (
        athena_scan_price_tb,
        columns_accessed_pct,
        mo,
        partition_pruning_pct,
        queries_per_month,
        raw_data_tb,
        s3_storage_price_tb,
        scenario_data,
        z_ordering_pct,
    )


@app.cell
def _(
    athena_scan_price_tb,
    columns_accessed_pct,
    mo,
    partition_pruning_pct,
    queries_per_month,
    raw_data_tb,
    s3_storage_price_tb,
    scenario_data,
    z_ordering_pct,
):
    # --- CALCULATION ENGINE ---
    results = []
    for name, data in scenario_data.items():
        # 1. Storage Costs
        stored_tb = raw_data_tb.value * data["size_multiplier"]
        storage_cost = stored_tb * s3_storage_price_tb.value

        # 2. Query/Scan Volume Calculation
        base_scan_tb = stored_tb

        # Apply Partition Pruning
        # (Works for both JSON and Parquet if S3 folders are organized)
        pruned_scan_tb = base_scan_tb * (1 - (partition_pruning_pct.value / 100.0))
        actual_scan_tb_per_query = pruned_scan_tb

        # Apply Columnar and Sorting Savings (Parquet ONLY)
        if data["is_columnar"]:
            # Skip unneeded columns
            actual_scan_tb_per_query = actual_scan_tb_per_query * (
                columns_accessed_pct.value / 100.0
            )
            # Skip unneeded chunks inside the file using min/max metadata
            # (Because data is ordered)
            actual_scan_tb_per_query = actual_scan_tb_per_query * (
                1 - (z_ordering_pct.value / 100.0)
            )

        # 3. Query Costs
        monthly_scan_tb = actual_scan_tb_per_query * queries_per_month.value
        query_cost = monthly_scan_tb * athena_scan_price_tb.value

        total_cost = storage_cost + query_cost

        results.append(
            {
                "Storage Format": name,
                "Storage Cost ($)": f"${storage_cost:,.2f}",
                "Query Cost ($)": f"${query_cost:,.2f}",
                "Total Monthly ($)": f"${total_cost:,.2f}",
                "TB Scanned / Query": f"{actual_scan_tb_per_query:.4f} TB",
            }
        )

    # --- OUTPUTS ---

    mo.md(
        f"### Data Lake Economics: {raw_data_tb.value} TB Raw Data | {queries_per_month.value} Queries/mo"  # noqa: E501
    )
    mo.ui.table(results)
    return


app._unparsable_cell(
    r"""
    data/year=2020/month=01
    """,
    name="_"
)


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
