import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any

import fastavro
import msgpack
import orjson
import ujson
from faker import Faker

# Initialize Faker
fake = Faker()

# Schema mapping from your SQLAlchemy model
HOUSING_AVRO_SCHEMA = {
    "type": "record",
    "name": "HousingData",
    "fields": [
        {"name": "num_rooms", "type": "int"},
        {"name": "num_bathrooms", "type": "float"},
        {"name": "sq_feet", "type": "int"},
        {"name": "aesthetic", "type": "string"},
        {"name": "price", "type": "int"},
        {"name": "address", "type": "string"},
        {"name": "city", "type": "string"},
        {"name": "year_built", "type": ["null", "int"], "default": None},
        {"name": "is_available", "type": "boolean", "default": True},
        {"name": "has_garage", "type": "boolean", "default": False},
    ],
}


def generate_records(count: int = 10_000) -> list[dict[str, Any]]:
    """
    Generate a list of random real estate records.

    Args:
        count (int): The number of records to generate. Defaults to 10_000.

    Returns:
        list[dict]: A list of dictionaries containing random property data.

    """
    return [
        {
            "num_rooms": fake.random_int(min=1, max=10),
            "num_bathrooms": float(fake.random_int(min=1, max=5)),
            "sq_feet": fake.random_int(min=500, max=5000),
            "aesthetic": fake.word(),
            "price": fake.random_int(min=100000, max=2000000),
            "address": fake.address().replace("\n", ", "),
            "city": fake.city(),
            "year_built": int(fake.year()) if fake.boolean() else None,
            "is_available": fake.boolean(),
            "has_garage": fake.boolean(),
        }
        for _ in range(count)
    ]


def save_and_time(
    fmt: str, data: list, output_dir: Path, index: int = 1
) -> tuple[float, int]:
    """
    Save data in a specified format and measure the processing time and file size.

    Args:
        fmt (str): The serialization format to use (e.g., 'json', 'csv', 'avro').
        data (list): The list of data objects to be saved.
        output_dir (Path): The directory path where the output file will be created.
        index (int): An optional index for the filename. Defaults to 1.

    Returns:
        tuple[float, int]: A tuple containing the elapsed time in seconds
        and the file size in bytes.

    """
    file_path = output_dir / f"housing_test_{index}.{fmt}"

    start_time = time.perf_counter()
    match fmt:
        case "json":
            with file_path.open("w") as f:
                json.dump(data, f)

        case "orjson":
            with file_path.open("wb") as f:
                f.write(orjson.dumps(data))

        case "ujson":
            with file_path.open("w") as f:
                ujson.dump(data, f)

        case "msgpack":
            with file_path.open("wb") as f:
                f.write(msgpack.packb(data))

        case "csv":
            with file_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

        case "avro":
            with file_path.open("wb") as f:
                fastavro.writer(f, HOUSING_AVRO_SCHEMA, data)

    end_time = time.perf_counter()
    file_size = file_path.stat().st_size
    return end_time - start_time, file_size


def main() -> None:
    """
    Generate and benchmark mock housing data across multiple formats.

    Parse command-line arguments to configure data generation, iterate through
    the specified formats, and display performance statistics for timing and size.

    Args:
        None

    Returns:
        None

    """
    supported = ["json", "orjson", "ujson", "msgpack", "csv", "avro"]

    parser = argparse.ArgumentParser(
        description="Generate and time mock housing data generation."
    )
    parser.add_argument("--all", action="store_true", help="Generate all formats")
    parser.add_argument(
        "--num-files",
        type=int,
        default=1,
        help="Number of files to generate per format",
    )
    parser.add_argument(
        "--num-records",
        type=int,
        default=10_000,
        help="Number of records to generate per file",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show file size information"
    )
    parser.add_argument(
        "formats", nargs="*", help=f"Individual formats: {', '.join(supported)}"
    )

    args = parser.parse_args()
    selected_formats = supported if args.all else args.formats
    valid_formats = [f for f in selected_formats if f in supported]

    if not valid_formats:
        print(f"No valid formats selected. Use --all or one of: {supported}")
        return

    output_path = Path("data")
    output_path.mkdir(parents=True, exist_ok=True)

    results = {fmt: {"durations": [], "sizes": []} for fmt in valid_formats}

    for i in range(1, args.num_files + 1):
        print(
            f"Iteration {i}/{args.num_files}: Generating {args.num_records} records..."
        )
        records = generate_records(args.num_records)

        for fmt in valid_formats:
            duration, file_size = save_and_time(fmt, records, output_path, index=i)
            results[fmt]["durations"].append(duration)
            results[fmt]["sizes"].append(file_size)
            print(f"Finished {fmt}...")

    # Calculate statistics and sort by total time
    stats = []
    for fmt, data in results.items():
        total_time = sum(data["durations"])
        avg_time = total_time / len(data["durations"])
        avg_size = sum(data["sizes"]) / len(data["sizes"])
        stats.append(
            {
                "fmt": fmt,
                "total_time": total_time,
                "avg_time": avg_time,
                "avg_size": avg_size,
            }
        )

    stats.sort(key=lambda x: x["total_time"])

    print("\n" + "=" * 65)
    header = f"{'Format':<10} | {'Avg Time (s)':<15} | {'Total Time (s)':<15}"
    if args.verbose:
        header += f" | {'Avg Size (KB)':<15}"
    print(header)
    print("-" * 65)
    for s in stats:
        row = f"{s['fmt']:<10} | {s['avg_time']:<15.6f} | {s['total_time']:<15.6f}"
        if args.verbose:
            row += f" | {s['avg_size'] / 1024:<15.2f}"
        print(row)
    print("=" * 65)


if __name__ == "__main__":
    main()
