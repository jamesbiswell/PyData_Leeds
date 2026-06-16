from __future__ import annotations

import csv
import io
import json
import time
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import fastavro
import msgpack
import orjson
import ujson
import uvicorn
from litestar import Litestar, get, post
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import ClientException
from litestar.params import Body
from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)


class Base(DeclarativeBase): ...  # noqa: D101


class HousingData(Base):
    """Housing Data database table."""

    __tablename__ = "housing_data"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    num_rooms: Mapped[int]
    num_bathrooms: Mapped[float]
    sq_feet: Mapped[int]
    aesthetic: Mapped[str]
    price: Mapped[int] = mapped_column(index=True)
    address: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column(index=True)
    year_built: Mapped[int | None]
    is_available: Mapped[bool] = mapped_column(default=True)
    has_garage: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


# Get the directory where app.py is located
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pydata.sqlite"


engine = create_engine(
    f"sqlite+pysqlite:///{DB_PATH}",
    echo=False,  # Log all SQL commands to the console
    connect_args={
        "check_same_thread": False
    },  # Allows multi-threaded use (standard for web apps)
)


# 2. Create a Session factory
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


# 3. Dependency function to provide a session
def get_db_session() -> Generator[Session]:
    """
    Provide a database session.

    Yields:
        Session: The database session.

    """
    with SessionLocal() as session:
        yield session


database_dependencies = {"db_session": Provide(get_db_session)}


@get(
    path="/favicon.ico",
)
async def get_favicon() -> None:
    """Return an empty favicon."""
    return


@get(path="/housing")
async def get_housing(
    db_session: Session, page: int = 1, limit: int = 10
) -> list[HousingData]:
    """
    Fetch paginated housing data from the database.

    Args:
        db_session (Session): The database session used to execute the query.
        page (int): The page number to retrieve, starting from 1. Defaults to 1.
        limit (int): The maximum number of items to return per page. Defaults to 10.

    Returns:
        list[HousingData]: A list of housing data records for the specified page.

    """
    # Calculate how many records to skip
    offset = (page - 1) * limit

    # Construct the query with pagination
    stmt = select(HousingData).offset(offset).limit(limit)

    # Execute and return
    return list(db_session.scalars(stmt))


@post(path="/housing", media_type="text/html")
async def add_housing(
    db_session: Session,
    file_type: str,
    insert_mode: str,
    data: UploadFile = Body(media_type=RequestEncodingType.MULTI_PART),  # noqa: B008
) -> str:
    """
    Parse housing data from an uploaded file and insert it into the database.

    Args:
        db_session (Session): The database session to use for insertion.
        file_type (str): The format of the input file (e.g., json, csv, avro).
        insert_mode (str): The insertion strategy to use (orm or core).
        data (UploadFile): The uploaded file object containing the raw housing data.

    Returns:
        str: An HTML string summarizing the processing and insertion performance metrics

    Raises:
        ClientException: If the file type is unsupported, parsing fails,
            or the insert mode is invalid.

    Note:
        This function commits the transaction to the database.

    """
    start_deserialization = time.perf_counter()
    content = await data.read()
    # 1. Handle File Parsing with Case Match
    try:
        match file_type.lower():
            case "json":
                parsed_data = json.loads(content)
            case "orjson":
                parsed_data = orjson.loads(content)
            case "ujson":
                parsed_data = ujson.loads(content)
            case "msgpack":
                parsed_data = msgpack.unpackb(content)
            case "csv":
                stream = io.StringIO(content.decode("utf-8"))
                parsed_data = []
                for row in csv.DictReader(stream):
                    if row.get("is_available") == "True":
                        row["is_available"] = True
                    elif row.get("is_available") == "False":
                        row["is_available"] = False
                    if row.get("has_garage") == "True":
                        row["has_garage"] = True
                    elif row.get("has_garage") == "False":
                        row["has_garage"] = False
                    parsed_data.append(row)
            case "avro":
                # Requires fastavro
                housing_avro_schema = {
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
                        {
                            "name": "year_built",
                            "type": ["null", "int"],
                            "default": None,
                        },
                        {"name": "is_available", "type": "boolean", "default": True},
                    ],
                }

                fo = io.BytesIO(content)
                parsed_data = list(
                    fastavro.reader(fo, reader_schema=housing_avro_schema)
                )
            case _:
                raise ClientException(f"Unsupported file type: {file_type}")
    except Exception as e:
        raise ClientException(f"Failed to parse {file_type}: {e!s}") from e

    end_deserialization = time.perf_counter()
    deserialization_time = end_deserialization - start_deserialization

    # Ensure we are dealing with a list of dicts
    if isinstance(parsed_data, dict):
        parsed_data = [parsed_data]

    start_insertion = time.perf_counter()

    match insert_mode.lower():
        case "orm":
            # Create model instances and add to session
            instances = [HousingData(**item) for item in parsed_data]
            db_session.add_all(instances)
            db_session.flush()  # Sync with DB to get IDs

        case "core":
            # High-performance bulk insert
            db_session.execute(insert(HousingData), parsed_data)
            db_session.flush()

        case _:
            raise ClientException(f"Invalid insert_mode: {insert_mode}")

    db_session.commit()
    end_insertion = time.perf_counter()
    insertion_time = end_insertion - start_insertion

    return f"""
        File Type: {file_type}
        Insert Mode: {insert_mode}
        Records Count: {len(parsed_data)}
        Deserialization Time (s): {deserialization_time:.6f}
        Insertion Time (s): {insertion_time:.6f}
    """


app = Litestar(
    route_handlers=[get_housing, add_housing, get_favicon],
    debug=False,
    dependencies=database_dependencies,
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
