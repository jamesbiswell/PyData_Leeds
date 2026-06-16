import asyncio
import time
from pathlib import Path

import httpx

# List of files in the /data folder
# Configuration
DATA_DIR = Path("data")
API_URL = "http://0.0.0.0:8000/housing"  # Assuming the service runs on localhost:8000
INSERT_MODES = ["orm", "core"]

file_list: list[Path] = [x for x in Path(DATA_DIR).iterdir() if x.is_file()]


async def process_file(
    file_path: Path, file_type: str, insert_mode: str
) -> tuple[bool, int | None]:
    """
    Processes a file by reading its content and submitting it to an API.

    Args:
        file_path: The local path to the file to be processed.
        file_type: The type of the file (e.g., 'text', 'image').
        insert_mode: The mode in which the content should be inserted.

    Returns:
        A tuple containing a boolean success status and the HTTP status code (or None).

    """  # noqa: D401
    try:
        print(f"Processing {file_path} (Type: {file_type}, Mode: {insert_mode})...")

        # Read the file content as bytes
        with file_path.open("rb") as f:
            data_bytes = f.read()

        async with httpx.AsyncClient(timeout=30.0) as client:
            # The API expects 'data' as bytes, and 'file_type' and
            # 'insert_mode' as params
            files = {"data": (file_path.name, data_bytes, "application/octet-stream")}

            start_request = time.perf_counter()
            response = await client.post(
                API_URL,
                files=files,
                params={"file_type": file_type, "insert_mode": insert_mode},
            )
            end_request = time.perf_counter()
            response.raise_for_status()
            print(
                f"""
                SUCCESS: {file_path}
                Status: {response.status_code}
                Time: {end_request - start_request}"""
            )
            print(f"  {response.text}")
            return True, response.status_code
    except FileNotFoundError:
        print(f"  ERROR: File not found at {file_path}. Skipping.")
        return False, None
    except httpx.HTTPStatusError as e:
        print(
            f"""  ERROR: HTTP error for {file_path}.
            Status: {e.response.status_code}.
            Response: {e.response.text}"""
        )
        return False, e.response.status_code
    except Exception as e:
        print(f"  CRITICAL ERROR processing {file_path}: {e}")
        return False, None


async def main() -> None:
    """Orchestrate all API calls."""
    print("Starting data ingestion script...")

    results = []
    for file in file_list:
        # 1. Determine file type from extension
        file_type = file.suffix.lstrip(".")

        # 3. Process all insert modes
        for mode in INSERT_MODES:
            results.append(await process_file(file, file_type, mode))  # noqa: PERF401

    successful_calls = sum(1 for success, _ in results if success)
    total_calls = len(results)

    print("\n--- Script Summary ---")
    print(f"Total attempts: {total_calls}")
    print(f"Successful uploads: {successful_calls}")


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    asyncio.run(main())
