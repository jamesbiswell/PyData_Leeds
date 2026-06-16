import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import time  # Import time for performance measurement
    from pathlib import Path

    import fastavro  # Assuming fastavro is available for Avro handling
    import marimo as mo
    import msgpack
    import orjson
    import snappy
    import zstd

    return Path, fastavro, mo, msgpack, orjson, snappy, time, zstd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Comparison of Common Data Formats for Web Services Payloads

    Choosing the right data format for transmitting data is critical for performance, reliability, and ease of use when integrating services. This guide compares four popular formats: JSON, CSV, MessagePack, and Avro.

    ---

    ## 📐 Format Deep Dive

    ### 🌐 JSON (JavaScript Object Notation)
    JSON is a text-based, language-independent format that uses human-readable key-value pairs. Pretty much the de facto standard for modern APIs.

    There are a couple variations that you may come across and in certain contexts.

    Regular JSON
    ```json
    [
        {"name": "Alice Johnson", "age": 28, "department": "Engineering"},
        {"name": "Bob Smith", "age": 35, "department": "Marketing"},
        {"name": "Carol White", "age": 42, "department": "Sales", "extra":
            {
                "nested": [
                    {"types": "data"}
                ]
            }
        }
    ]
    ```

    JSON Lines (Mostly seen in events/logging)

    ```jsonl
    {"name": "Alice Johnson", "age": 28, "department": "Engineering"}
    {"name": "Bob Smith", "age": 35, "department": "Marketing"}
    {"name": "Carol White", "age": 42, "department": "Sales", "extra": {"nested": [{"types": "data"}]}}
    ```

    Choose JSON when:

        * Building APIs that return structured responses
        * Creating configuration files
        * Working with nested, hierarchical data
        * File size is manageable in memory
        * You need a single, self-contained data structure

    Choose JSONL when:

        * Processing large datasets that don’t fit in memory
        * Writing log files or event streams
        * You need append-only operations
        * Implementing data pipelines that benefit from streaming
        * Fault tolerance is important (partial file recovery)

    There is also [jsonc](https://jsonc.org/) an extension to json that is in proposal to allow for comments

    ```jsonc
    {
        // This is a single-line comment
        "name": "John Doe",
        "age": 30 // This is another single line comment
         /*
          This is a block comment
          that spans multiple lines
        */
    }
    ```

    **✅ Pros:**
    * **Readability:** Extremely human-readable and intuitive.
    * **Universality:** Supported natively by almost every programming language and web service.
    * **Ease of Use:** Simple structure (object/array) makes parsing straightforward.


    **❌ Cons:**

    * **Verbosity/Overhead:** Since it is text-based, it includes many delimiters, quotation marks, and whitespace, leading to larger payload sizes compared to binary formats.
    * **Strict Typing:** It does not inherently enforce schema (though tools like JSON Schema help).

    **💡 When to use it:**

    When readability, simplicity, and maximum compatibility across various systems are the top priorities (e.g., public APIs, configuration files, niche PaaS).

    ### 📄 CSV (Comma Separated Values)

    CSV is a plain text format that stores tabular data where each row is a data record, and fields are separated by a delimiter (usually a comma).

    ```csv
    ID,Status,IsActive,Cash
    1,Complete,true,"10,000.12"
    2,Pending,false,"12,000.39"
    3,In_Progress,true,"1,003.12"
    ```

    **✅ Pros:**

    * **Simplicity:** Extremely simple structure; nearly every spreadsheet program can read/write it.
    * **Compatibility:** Works well for simple, flat, homogeneous datasets (e.g., logs, basic data dumps).
    * **Compact (for simple data):** Can be very compact for uniformly structured data.
    * **At least it's better than Excel docs!**

    **❌ Cons:**

    * **Data Loss of Structure:** It is inherently difficult to represent complex, nested, or hierarchical data (like JSON objects).
    * **Ambiguity:** Handling non-text data, delimiters within data fields (e.g., commas containing text), and quoting rules can be complex and error-prone.
    * **Lack of Metadata:** No native way to describe the schema, types, or context of the data within the file itself. (leaning on something like pydantic to validate can be done if required.)

    **💡 When to use it:**

    For transferring simple, tabular datasets (e.g., CSV files uploaded to a service for batch processing). Generally discouraged for core, complex API payloads. (working with other departments that work primarily in excel, just have them send it to you as CSV and have them check it first)

    ### 📦 MsgPack (MessagePack)

    MsgPack is a binary serialization format. It aims to be faster and smaller than JSON by using binary representations for data types instead of text.

    It is still fundamentally like JSON though, which means that the schema can be whatever and the receiver will have to unpack the fields and check the values just like you would need to with JSON. (it's just a bit tinier!)

    **✅ Pros:**

    * **Efficiency:** Significantly more compact and faster to serialize/deserialize than JSON because it eliminates textual overhead.
    * **Speed:** Ideal for high-throughput, internal microservice communications where speed is paramount.
    * **Simplicity (Conceptually):** Maintains the key-value structure of JSON but in binary.

    **❌ Cons:**

    * **Readability:** Completely unreadable to humans without specialized tools.
    * **Adoption:** While gaining traction, it is less universally adopted than JSON, requiring stable libraries on both ends.

    **💡 When to use it:**

    When you want JSON but performance and payload size are major concerns (e.g., internal real-time data streams, remote regions with slow network speeds and large payloads. Every bit counts 😉)

    ### 🏛️ Avro (Apache Avro)

    Avro is a data serialization system that typically includes a robust schema definition language (JSON Schema) alongside the data. It is schema-based and optimised for dealing with complex, evolving data schemas.

    You'll have something like a `user.avsc` file which will define the schema to pack the data in...

    ```json
    {
      "type": "record",
      "name": "User",
      "namespace": "com.example",
      "fields": [
        {"name": "id", "type": "int"},
        {"name": "username", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "is_premium", "type": "boolean", "default": false}
      ]
    }
    ```

    How a schema evolution works more generally...

    1. On the Client (The Producer/Writer)

    The client is responsible for "packaging" the data according to a specific version of the schema.

        Step A: Schema Definition: The developer updates the schema (e.g., adding a field phone_number with a default value of null).

        Step B: Registration: In many production environments (like Kafka), the client sends this new schema to a Schema Registry. The registry gives this schema a unique ID.

        Step C: Serialization: The client converts the data into binary. It prepends the Schema ID to the front of the binary message.

        Step D: Transmission: The client sends the small binary package (ID + Data) to the receiver or a message broker.


    ```
    ┌────────────────────┐
    │ Dev Updated Schema │───┐
    └─────────┬──────────┘   │
              │              │
              ▼              │
     ┌────────────────┐  1. avro
     │Schema Registry │    file
     └────────────────┘      │
              ▲              │
         Get Schema          │
              │ ┌─────────┐  │
              └▶│ Server  │◀─┘
                └─────────┘
                     │
                     ▼
               ┌──────────┐
               │Data      │
               │Process / │
               │Storage   │
               └──────────┘
    ```

    The receiver’s job is to translate that binary back into something useful, even if the receiver is still using an older version of the code.

        Step A: Identification: The receiver sees the Schema ID at the start of the message.

        Step B: Fetching the Writer's Schema: If the receiver doesn't recognize that ID, it calls the Schema Registry to download the exact schema the client used.

        Step C: The "Resolution" Phase: This is where the magic happens. The receiver compares its Local Schema (what its code expects) with the Writer Schema (what was actually sent).

        Step D: Mapping: * New Field Added: If the writer sent a new field the reader doesn't know about, the reader simply ignores those extra bytes.

            Field Removed: If the writer stopped sending a field the reader expects, the reader looks at its local schema and fills in the Default Value.

        Step E: Deserialization: The data is converted into an object the receiver's application can understand.


    **✅ Pros:**

    * **Schema Evolution:** This is its biggest advantage. It handles schema changes (e.g., adding or removing fields) gracefully without breaking older consumers, making it perfect for long-lived APIs.
    * **Efficiency:** Highly efficient, schema-enforced binary serialization, often comparable to Protocol Buffers.
    * **Data Integrity:** The schema ensures that both the sender and receiver agree on how the data is structured, minimizing runtime errors.
    * **Deserialisation:** Can be much faster because it doesn't need to parse strings, it can use direct memory mapping based on the schema


    **❌ Cons:**

    * **Complexity:** Requires strict schema definition and implementation, adding initial complexity compared to JSON.
    * **Tooling:** While excellent, setting up the schema registry and serialization framework is more involved than just sending a JSON string.

    **💡 When to use it:**

    When reliability, schema enforcement, and the ability to change data structure over time (schema evolution) without service disruption are critical (e.g., streaming data pipelines, Kafka topics).



    ---

    ## 🚀 Comparison Summary Table

    | Feature | JSON | CSV | MsgPack | Avro |
    | :--- | :---: | :---: | :---: | :---: |
    k| **Readability** | Excellent | Excellent | Very Poor | Poor (Needs Schema) || **Payload Size** | Medium (High Overhead) | Low (Flat Data) | Very Low | Very Low |
    | **Structure Limit** | Nested/Complex | Flat Only | Nested/Complex | Nested/Complex |
    | **Schema Enforcement** | Low (Schema required via external tool) | None | Medium | High (Mandatory) |
    | **Schema Evolution** | Poor | None | Medium | Excellent |
    | **Use Case** | Public APIs | Simple Datasets/Logs | High-Speed Internal Transfer | Data Pipelines/Message Brokers |
    """)
    return


@app.cell
def _(Path, fastavro, msgpack, orjson, time):
    # --- 1. SETUP & MASSIVE DATA GENERATION ---
    def generate_complex_data(n=200_000):
        print(f"🛠️  Generating {n} records...")
        return {
            "company": "MegaTech Global",
            "stats": {"rank": 1, "active": True},
            # We use a list of dicts for the main records
            "records": [
                {
                    "id": i,
                    "email": f"user_{i}@megatech.global",
                    "zip": 10000 + (i % 9000),
                    # Metadata as a simple flat dict to keep Avro mapping happy
                    "metadata": {f"tag_{j}": i + j for j in range(3)},
                }
                for i in range(n)
            ],
        }

    sample_data = generate_complex_data(200_000)

    # Fixed Avro Schema to match the data structure exactly
    schema = {
        "type": "record",
        "name": "BigData",
        "fields": [
            {"name": "company", "type": "string"},
            {
                "name": "stats",
                "type": {
                    "type": "record",
                    "name": "Stat",
                    "fields": [
                        {"name": "rank", "type": "int"},
                        {"name": "active", "type": "boolean"},
                    ],
                },
            },
            {
                "name": "records",
                "type": {
                    "type": "array",
                    "items": {
                        "type": "record",
                        "name": "User",
                        "fields": [
                            {"name": "id", "type": "int"},
                            {"name": "email", "type": "string"},
                            {"name": "zip", "type": "int"},
                            {
                                "name": "metadata",
                                "type": {"type": "map", "values": "int"},
                            },
                        ],
                    },
                },
            },
        ],
    }

    # --- 2. THE BENCHMARK ENGINE ---
    def benchmark(name, filename, save_logic, load_logic):
        path = Path(filename)

        # --- WRITE TO DISK TIMER ---
        start_write = time.perf_counter()
        save_logic(sample_data, path)
        write_time = time.perf_counter() - start_write

        file_size_mb = path.stat().st_size / (1024 * 1024)

        # --- READ FROM DISK -> DICT TIMER ---
        # This captures the full deserialization pipeline
        start_read = time.perf_counter()
        _ = load_logic(path)
        read_total_time = time.perf_counter() - start_read

        if path.exists():
            path.unlink()

        return write_time, read_total_time, file_size_mb

    # --- 3. FORMAT WRAPPERS ---

    # ORJSON (The fastest JSON library for Python)
    def save_json(data, p):
        with open(p, "wb") as f:
            f.write(orjson.dumps(data))

    def load_json(p):
        with open(p, "rb") as f:
            return orjson.loads(f.read())

    # MSGPACK
    def save_msg(data, p):
        with open(p, "wb") as f:
            f.write(msgpack.packb(data))

    def load_msg(p):
        with open(p, "rb") as f:
            return msgpack.unpackb(f.read())

    # AVRO
    def save_avro(data, p):
        with open(p, "wb") as f:
            fastavro.writer(f, schema, [data])

    def load_avro(p):
        with open(p, "rb") as f:
            reader = fastavro.reader(f)
            return list(reader)[0]

    # --- 4. EXECUTION ---
    results = {}
    results["JSON (orjson)"] = benchmark("JSON", "test.json", save_json, load_json)
    results["MsgPack"] = benchmark("MsgPack", "test.msg", save_msg, load_msg)
    results["Avro"] = benchmark("Avro", "test.avro", save_avro, load_avro)

    # --- 5. RESULTS SUMMARY ---
    print("\n" + "=" * 70)
    print(
        f"{'Format':<15} | {'Write (s)':<12} | {'Read->Dict (s)':<15} | {'Size (MB)':<10}"
    )
    print("-" * 70)
    for fmt, (w, r, s) in results.items():
        print(f"{fmt:<15} | {w:<12.4f} | {r:<15.4f} | {s:<10.2f}")
    print("=" * 70)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. Write Speed: orjson often wins just because it is a raw speed demon that does not care about file size.

    2. Read Speed: MsgPack is usually the favorite for internal stuff because it is binary and very easy for the CPU to digest.

    3. File Size: Avro wins every time because it is smart enough not to repeat labels.

    All in all...
                                                                                                         In a real-world project, you would probably pick MsgPack if you want raw speed between your own services, or Avro if you are paying for every gigabyte of storage in a database.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### 💡 Why Avro Can Be Smaller Than MsgPack (The Structural Difference)

    The observed size difference between Avro and MsgPack is not necessarily a fixed rule, as it depends heavily on the *data being serialized* and the *specific version* of the format. However, Avro is fundamentally designed for **data stream efficiency, schema evolution, and bulk record processing**, giving it structural advantages that can result in a smaller file size compared to a general-purpose binary serializer like MsgPack.

    Here is a breakdown of the makeup and the source of the size difference:

    ---

    #### 📦 MsgPack: Self-Contained Data Serialization

    MsgPack is designed to serialize a structured object (like a Python dictionary -> pickle) into the most compact binary equivalent possible.

    How it works:

    1.  It treats the entire dataset as a single, cohesive object.
    2.  It replaces text strings, numbers, lists, and maps with their specific binary type identifiers.
    3.  The overhead is minimal (just the type markers and length prefixes).

    **Size implication:** The size is primarily dictated by the data payload itself. It is good at minimising overhead compared to JSON, but it still encodes the structure and keys for every single it serializes.

    ---

    #### 🏛️ Avro: Schema-Enforced, Streaming Serialization

    Avro is schema-based, it separates the schema from the data (the payload).

    How it works:

    1.  Avro requires a defined schema (`.avsc` or defined in code). This schema acts as the master reference for how the data is constructed.
    2. Avro doesn't just serialize one object; it is optimized for writing potentially millions of records sequentially (streaming).
    3. It's very efficient because the schema is defined and known beforehand (and often stored once or implied). Therefore, Avro does not need to repeatedly encode the field names or the data types for every single record.

    **Size implication:**

    * Minimal Redundancy: If you are writing 1,000 records, MsgPack effectively encodes "field\_a: type\_X" 1,000 times (even if implicitly). Avro, because it relies on the external schema, only has to encode the structural information once, allowing the data section to be much more dense and optimized.
    * Optimized Data Types: Avro's encoding can be highly optimized for the underlying type system, sometimes utilizing techniques—like reading structured data in a nearly columnar fashion—that achieve greater compression than MsgPack's general-purpose serialization.

    ---

    ### 📊 Summary of Size Drivers

    | Feature | MsgPack | Avro | Why the difference? |
    | :--- | :--- | :--- | :--- |
    | **Core Design Goal** | Compact object serialization | Data stream reliability & evolution | Different use cases lead to different optimizations. |
    | **Schema Handling** | Implicit (structure is encoded per message) | Explicit (fixed schema referenced) | Avro avoids repeating structural metadata. |
    | **Primary Overhead** | Type markers, array/map overhead | Often minimal, determined by data distribution | Avro's dedicated, stream-focused encoding is superior for bulk data. |
    | **Best for** | Single, complete payload transfer | Continuous, structured data pipelines (Kafka, etc.) | |
    """)
    return


@app.cell
def _(time):
    # This demonstration simulates Avro's use of a predefined Reader Schema when consuming a stream of records
    # written across different 'batches' (or files) that follow differing field structures.

    # --- 1. Setup and Data Simulation ---

    # Define the overall expected schema (The *Reader Schema* or *Target Schema*).
    # This schema dictates what the consumer expects the data structure to be, regardless of how it was written.
    # Let's define a target that has: 'id', 'name', 'age', 'city'
    TARGET_SCHEMA = {
        "id": "int",  # Always expected
        "name": "string",  # Always expected
        "age": "int",  # Expected, might be missing in older records
        "city": "string",  # Expected, might be missing
    }

    print("--- 📝 Stage 1: Simulation Setup ---")
    print(f"Target Schema (What the system expects): {TARGET_SCHEMA}")

    # --- 2. Batch 1: The Initial Schema (Only 'id' and 'name' exist) ---
    # Schema Used for writing: {id: int, name: string} (Minimal data set)
    batch_1_records = [
        {"id": 101, "name": "Alice"},
        {"id": 102, "name": "Bob"},
    ]
    print("\n[Batch 1 Written] Schema: id, name (Minimal structure)")

    # --- 3. Batch 2: Schema Evolution (Adding 'age') ---
    # Schema Used for writing: {id: int, name: string, age: int}
    # We add the 'age' field to the records.
    batch_2_records = [
        {"id": 201, "name": "Charles", "age": 30},
        {"id": 202, "name": "David", "age": 24},
    ]
    print("[Batch 2 Written] Schema: id, name, age (Field 'age' added)")

    # --- 4. Batch 3: Schema Drifting (Adding 'city', but dropping 'name' field temporarily is handled by default) ---
    # Schema Used for writing: {id: int, age: int, city: string}
    # Note: This batch writes the 'name' field but skips it to demonstrate handling changes.
    batch_3_records = [
        {"id": 301, "name": "Eve", "age": 45, "city": "New York"},
        {"id": 302, "name": "Frank", "age": 32, "city": "Boston"},
        {"id": 303, "name": "Grace", "age": 28, "city": "Austin"},
    ]
    print("[Batch 3 Written] Schema: id, name, age, city (Full structure achieved)")

    # --- 5. The Avro Reading Process (Conceptual Implementation) ---

    print("\n\n--- ⚙️ Stage 2: Structured Reading with Avro (Stream Processing) ---")
    print("--- Avro's Advantage: The Reader Schema handles compatibility. ---")

    all_records = []

    # Simulate reading Batch 1 using the TARGET_SCHEMA (which expects 'age' and 'city')
    print("Reading Batch 1 (Missing 'age' and 'city')...")
    start_time_1 = time.time()
    for record in batch_1_records:
        # Avro reader code automatically fills in defaults for missing fields
        # If 'age' was not available in the batch, it defaults it; if 'city' was missing, it defaults it.
        readable_record = {
            "id": record["id"],
            "name": record["name"],
            "age": record.get("age", None),  # Defaulting or handling nulls
            "city": None,  # Missing field defaults to None
        }
        all_records.append(readable_record)
        print(
            f"  -> Read {record['id']}: Name={record['name']}, Age={readable_record['age']} (Defaulted), City=None"
        )
    end_time_1 = time.time()
    print(
        f"\n[TIMING RESULT] Batch 1 Reading Time: {end_time_1 - start_time_1:.6f} seconds."
    )

    # Simulate reading Batch 2 using the TARGET_SCHEMA
    print("\nReading Batch 2 (Contains 'age', Missing 'city')...")
    start_time_2 = time.time()
    for record in batch_2_records:
        readable_record = {
            "id": record["id"],
            "name": record["name"],
            "age": record["age"],
            "city": None,  # Still missing, defaults to None
        }
        all_records.append(readable_record)
        print(
            f"  -> Read {record['id']}: Name={record['name']}, Age={readable_record['age']}, City=None"
        )
    end_time_2 = time.time()
    print(
        f"\n[TIMING RESULT] Batch 2 Reading Time: {end_time_2 - start_time_2:.6f} seconds."
    )

    # Simulate reading Batch 3 using the TARGET_SCHEMA
    print("\nReading Batch 3 (Complete structure)...\n")
    start_time_3 = time.time()
    for record in batch_3_records:
        readable_record = {
            "id": record["id"],
            "name": record["name"],
            "age": record["age"],
            "city": record["city"],
        }
        all_records.append(readable_record)
        print(
            f"  -> Read {record['id']}: Name={record['name']}, Age={readable_record['age']}, City={readable_record['city']}"
        )
    end_time_3 = time.time()
    print(
        f"\n[TIMING RESULT] Batch 3 Reading Time: {end_time_3 - start_time_3:.6f} seconds."
    )

    # --- 6. Final Result ---
    print("\n=================================================================")
    print(
        "✅ SUCCESS: All records, despite having differing structures, were successfully read!"
    )
    print(f"Total records processed: {len(all_records)}")
    print("Example final read format (homogeneous):")
    print(all_records)
    print("==================================================================")

    # --- 🚀 Contrast with JSON ---

    print("\n\n--- 💔 Contrast: JSON Approach ---")
    print("When using JSON, you must load and process the file boundaries manually.")
    print(
        "If the consumer logic assumes a structure (e.g., looking for 'age' in a record), and a file (like Batch 1) was generated without that field, the entire consuming application must handle the variation."
    )

    print(
        "\nScenario: You write all three batches to separate JSON files (file1.json, file2.json, file3.json)."
    )
    print("A consumer reading these files must implement complex logic like:")
    print(
        "1. Check if key 'age' exists in the current object. If not, assume a default (e.g., None)."
    )
    print("2. Handle potential type mismatches if a batch changes its output format.")
    print(
        "3. The coupling is tighter: the reader must know, or guess, the expected structure changes."
    )

    print("\n🔑 Key Takeaway:")
    print(
        "Avro's schema-based approach (Reader Schema) guarantees that the consumer always receives data conforming to the *target structure*, because the format handles the mapping (and defaulting) internally, invisible to the application code."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Compression

    1. Snappy: The Speed Demon

    Developed by Google, Snappy doesn't aim for maximum compression. Instead, it
    aims for speeds so high that you barely notice the CPU overhead.

        The Vibe: "I don't care if the file is still a bit big, just get it done
        now."

        Pros: Extremely fast compression and decompression; very stable; low CPU
        footprint.

        Cons: Poor compression ratios compared to the others.

        Ideal For: Internal RPCs, MapReduce jobs, and scenarios where disk I/O is
        faster than the time it takes to compress heavily.

    2. Zstd: The Modern Gold Standard

    Created by Facebook (Meta), Zstd is the "Swiss Army Knife." It is designed to
    scale from Snappy-like speeds to LZMA-level (7-Zip) compression ratios.

        The Vibe: "Why choose? I can be fast and small."

        Pros: Incredible flexibility (levels 1–22); provides a "Long Distance" mode
        for massive files; consistently outperforms Gzip in almost every metric.

        Cons: Slightly higher memory usage at very high compression levels.

        Ideal For: Almost everything. It’s replacing Gzip as the default in many
        Linux distributions and databases (like RocksDB or ClickHouse).

    3. Gzip: The Reliable Veteran

    Gzip (based on the DEFLATE algorithm) has been the industry standard for
    decades. While it’s being eclipsed by Zstd, it remains the most compatible.

        The Vibe: "I'm everywhere. Everyone knows how to talk to me."

        Pros: Built into every web browser, server, and OS by default.

        Cons: Slower than Zstd for the same compression ratio; showing its age on
        modern multi-core CPUs.

        Ideal For: Serving web content (HTML/JS/CSS) and situations where you aren't
        sure what software the recipient is using.

    Which one should you choose?

        Use Snappy if: You are managing a massive data pipeline (like Kafka or
        Spark) and the bottleneck is CPU time, not storage space.

        Use Zstd if: You want the best overall performance. It is the smartest
        choice for 90% of modern applications, especially if you can control both
        the compressor and the decompressor.

        Use Gzip if: You are sending data over the public internet to a browser, or
        working with legacy systems that don't support modern libraries.

    If you're using Zstd, there is a "dictionary compression" feature. It works to even be more effective at compressing very small, repetitive chunks of data (like JSON
    logs) by pre-training the algorithm on what your data looks like.

    WHOSE PAYING ATTENTION AND WANTS TO TRY DOING THAT AGAINST one of our generated files.

    When working with PySpark, the conversation changes from just "file size" to
    "distributed efficiency." In a big data environment, the most important
    factor is often whether a file is _splittable_.

    If a file is not splittable (like a standard Gzip-compressed CSV), Spark can
    only use **one CPU core** to read that entire file, even if you have a cluster
    of 100 machines.


    ---

    ## Comparison for PySpark (The "Splittability" Factor)

    | Format | Splittable? | Best Used With | Recommendation |
    | :--- | :--- | :--- | :--- |
    | **Snappy** | **No*** | Parquet / Avro | Use inside Parquet for the best balance. |
    | **Zstd** | **No*** | Parquet / ORC | Use inside Parquet for high-density storage. |
    | **Gzip** | **No** | Small CSV/JSON | Avoid for large datasets; creates "hot partitions." |
    | **Bzip2** | **Yes** | Large CSV/JSON | Use when you MUST store text files and save space. |
    | **LZ4** | **No** | Spark Shuffles | Great for high-speed temporary data. |

    > **\*Important Distinction:** While Snappy and Zstd are not "splittable" as raw
    files (e.g., `data.csv.snappy`), they **are** splittable when used as the
    compression codec inside a **Parquet** or **Avro** file. This is because those
    file formats handle the splitting at the block level.

    ---

    ## How to use them in PySpark

    To read or write these in PySpark, you generally set the `compression` option in your write command.

    ### Writing with Zstd (Recommended for Storage)
    ```python
    df.write.parquet("path/to/data", compression="zstd")
    ```

    ### Writing with Snappy (Spark Default)
    ```python
    df.write.parquet("path/to/data", compression="snappy")
    ```

    ### Dealing with "The Gzip Trap"

    If you receive a massive `10GB.csv.gz` file, PySpark will process it using only **one task**. To work around this, you might want to read it once, and immediately write it back out as **Snappy-compressed Parquet**. This changes the format of the the data so future jobs can process it in parallel.

    ```python
    # Step 1: Read the slow, non-splittable Gzip file
    df = spark.read.csv("massive_file.csv.gz")

    # Step 2: Write it as Parquet (now it's splittable and fast!)
    df.write.parquet("optimized_data", compression="snappy")
    ```
    """)
    return


@app.cell
def _(Path, snappy, time, zstd):
    # Setup data directory and extensions
    data_dir = Path("./data")
    extensions = ["avro", "msgpack", "json"]
    algorithms = [
        ("snappy", snappy.compress, snappy.decompress),
        ("zstd", zstd.compress, zstd.decompress),
    ]

    print(
        f"{'Ext':<8} | {'Algo':<8} | {'Encode+Write (s)':<18} | {'Load+Decode (s)':<18}"
    )
    print("-" * 60)

    for ext in extensions:
        input_path = data_dir / f"housing_test_1.{ext}"
        if not input_path.exists():
            continue

        for algo_name, compress_func, decompress_func in algorithms:
            output_path = data_dir / f"housing_test_1.{ext}.{algo_name}"

            # --- ENCODING & WRITE TO DISK ---
            start_enc = time.perf_counter()
            with input_path.open("rb") as f_in:
                raw_data = f_in.read()
                compressed_data = compress_func(raw_data)

            with output_path.open("wb") as f_out:
                f_out.write(compressed_data)
            end_enc = time.perf_counter()

            enc_time = end_enc - start_enc

            # --- LOAD & DECODING ---
            start_dec = time.perf_counter()
            with output_path.open("rb") as f_in_comp:
                loaded_data = f_in_comp.read()
                decompressed_data = decompress_func(loaded_data)
            end_dec = time.perf_counter()

            dec_time = end_dec - start_dec

            # --- OUTPUT RESULTS ---
            print(f"{ext:<8} | {algo_name:<8} | {enc_time:<18.6f} | {dec_time:<18.6f}")
    return


@app.cell
def _(Path):
    for e in ["avro", "msgpack", "json", "parquet"]:
        p = Path(f"./data/housing_test_1.{e}.snappy")
        fat = p.parent / p.stem
        if p.exists():
            p_size = p.stat().st_size
            if fat.exists():
                f_size = fat.stat().st_size
                print(
                    f"'{fat}' size: {f_size / 1_000} kb {((p_size - f_size) / f_size) * 100:.2f}%"
                )
            print(f"'{p}' size: {p_size / 1_000} kb")

        else:
            print(f"'{p}' not found.")

    p = Path("./data/housing_test_1.parquet.zst")
    print(f"'{p}' size: {p_size / 1_000} kb")
    return


@app.cell
def _(mo):
    # --- UI ELEMENTS ---
    mo.md("# Cloud Cost & Compression Simulator (AWS 2026)")

    # Global Settings
    requests_per_month = mo.ui.number(
        value=1_000_000, label="Requests per Month", step=100_000
    )
    memory_mb = mo.ui.slider(
        start=128, stop=10240, step=128, value=1024, label="Lambda Memory (MB)"
    )
    avg_revenue_per_user = mo.ui.number(value=50, label="Avg. Revenue per User ($)")

    # Infrastructure Toggles
    architecture = mo.ui.dropdown(
        options={"x86_64": 0.0000166667, "ARM64 (Graviton)": 0.0000133334},
        value="ARM64 (Graviton)",
        label="CPU Architecture (Price/GB-sec)",
    )
    region_egress = mo.ui.dropdown(
        options={
            "US-East (Standard)": 0.09,
            "Africa/South America (High)": 0.15,
            "Cloudfront/CDN (Low)": 0.02,
        },
        value="US-East (Standard)",
        label="AWS Egress Rate ($/GB)",
    )

    # Latency & Network
    latency_ms = mo.ui.slider(
        start=20, stop=2000, value=150, label="Base Network Latency (ms)"
    )
    inter_az_gb = mo.ui.slider(
        start=0, stop=1000, value=10, label="Monthly Inter-System Data (GB)"
    )

    # Define the sidebar
    sidebar = mo.sidebar(
        [
            mo.md("## 🛠️ Compute Settings"),
            requests_per_month,
            memory_mb,
            architecture,
            mo.md("---"),
            mo.md("## 🌐 Network & Region"),
            region_egress,
            latency_ms,
            inter_az_gb,
            mo.md("---"),
            mo.md("## 💰 Business Metrics"),
            avg_revenue_per_user,
        ]
    )

    # --- DATA TYPES & COMPRESSION MAPPING ---
    # Updated with 2026 standard Brotli/Zstd targets
    scenario_data = {
        "JSON (Raw)": {"size_kb": 500, "cpu_ms": 120, "color": "#f44336"},
        "JSON (Gzip)": {"size_kb": 120, "cpu_ms": 150, "color": "#e91e63"},
        "JSON (Brotli)": {"size_kb": 105, "cpu_ms": 180, "color": "#009688"},
        "Avro (Snappy)": {"size_kb": 90, "cpu_ms": 80, "color": "#9c27b0"},
        "MsgPack (Zstd)": {"size_kb": 75, "cpu_ms": 110, "color": "#3f51b5"},
    }

    # --- AWS PRICING CONSTANTS ---
    INTER_AZ_PER_GB = 0.01
    REQUEST_PRICE_PER_M = 0.20

    mo.as_html(sidebar)
    return (
        INTER_AZ_PER_GB,
        REQUEST_PRICE_PER_M,
        architecture,
        inter_az_gb,
        memory_mb,
        region_egress,
        requests_per_month,
        scenario_data,
    )


@app.cell
def _(
    INTER_AZ_PER_GB,
    REQUEST_PRICE_PER_M,
    architecture,
    inter_az_gb,
    memory_mb,
    mo,
    region_egress,
    requests_per_month,
    scenario_data,
):
    xxx = []
    for name, data in scenario_data.items():
        # Compute Cost: (Memory in GB) * (Time in Sec) * (Architecture Rate) * (Total Requests)
        compute_cost = (
            (memory_mb.value / 1024)
            * (data["cpu_ms"] / 1000)
            * architecture.value
            * requests_per_month.value
        )

        # Egress Cost: (Size in GB) * (Egress Rate)
        total_gb = (requests_per_month.value * data["size_kb"]) / (1024 * 1024)
        egress_cost = total_gb * region_egress.value

        # Request Cost
        request_cost = (requests_per_month.value / 1_000_000) * REQUEST_PRICE_PER_M

        # Total monthly cost
        total_cost = (
            compute_cost
            + egress_cost
            + request_cost
            + (inter_az_gb.value * INTER_AZ_PER_GB)
        )

        xxx.append(
            {
                "Format": name,
                "Monthly Cost ($)": round(total_cost, 2),
                "Payload Size (KB)": data["size_kb"],
                "CPU Time (ms)": data["cpu_ms"],
            }
        )

    # --- OUTPUTS ---
    mo.md(f"### Simulation Results for {requests_per_month.value:,} requests")
    mo.ui.table(xxx)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
