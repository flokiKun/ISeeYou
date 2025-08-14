import json
import os
import time
from typing import Annotated, Dict, Optional

from fastapi import FastAPI, Form
from pydantic import parse_obj_as
from sqlalchemy import create_engine

from db_interations import check_line_in_db, add_new_line_in_db, check_traintype_in_db, add_new_train_in_db
from gm_models import GMStatus
from models import ServerStatus, Line, TrainType

app = FastAPI()
db = create_engine(os.environ.get('DB_URL'))

debug = True
server_status_cache: Optional[ServerStatus] = None
received_time = .0


async def xdd_line(checked_lines, conn, normalized_status, train):
    # Lines
    line = train.position.line
    if not line: return
    name = line.name
    if name not in checked_lines and check_line_in_db(conn, line, normalized_status.map):
        checked_lines[name] = line
    elif name in checked_lines:
        l = checked_lines[line.name]
        line.name = l.name
        line.color = l.color
        line.symbols = l.symbol
    else:
        add_new_line_in_db(conn, line, normalized_status.map)
        checked_lines[name] = line


async def xdd_trains(checked_trains, conn, type_struct):
    # Trains
    if type_struct.typeName in checked_trains:
        type_name_ = checked_trains[type_struct.typeName]
        type_struct.name = type_name_.name
        type_struct.shortName = type_name_.shortName
    elif check_traintype_in_db(conn, type_struct):
        checked_trains[type_struct.typeName] = type_struct
    else:
        add_new_train_in_db(conn, type_struct)
        checked_trains[type_struct.typeName] = type_struct


@app.post("/api/v1/send_server_status")
async def receive_server_status(status: Annotated[str, Form()]):
    parsed_status = parse_obj_as(GMStatus, json.loads(status))

    if debug:
        print(f"{parsed_status}")

    normalized_status = ServerStatus.create_from_gm(parsed_status)

    # Read lines for map and, from local dict cache
    checked_lines: Dict[str, Line] = {}
    checked_traintype: Dict[str, TrainType] = {}
    with db.connect() as conn:
        with conn.begin():
            for ply in normalized_status.players:
                for train in ply.trains:
                    await xdd_line(checked_lines, conn, normalized_status, train)
                    for type_struct in train.types:
                        await xdd_trains(checked_traintype, conn, type_struct)
                    await xdd_trains(checked_traintype, conn, train.name)

    normalized_status.lines = list(checked_lines.values())
    # TODO: Mb redis? IDK lol, are we a high-load? Yes, just use egg lol
    global server_status_cache, received_time
    server_status_cache = normalized_status
    received_time = time.time()
    return f"[INFO-API] Successfully received status"


@app.get("/api/v1/status")
async def get_all_players_data(lang: str = "ru"):
    status = server_status_cache.model_copy(deep=True) if server_status_cache else None
    if time.time() - received_time >= 30.0 and status:
        status.uptime = -1
    return status
