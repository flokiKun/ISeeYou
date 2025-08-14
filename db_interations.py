from models import Line, TrainType
from sqlalchemy import Connection, text

LINE_CHECK_STATEMENT = text("select display_name, color, icon, display from `Lines` where gmod_name = :line and map = :map;")
LINE_ADD_STATEMENT = text("INSERT INTO `Lines` (`map`, gmod_name) VALUES(:map, :name);")
TRAIN_CHECK_STATEMENT = text("select full_name, short_name from TrainNormalization where ent_class = :ent_class;")
TRAIN_ADD_STATEMENT = text("INSERT INTO TrainNormalization (ent_class) VALUES(:ent_class);")


def check_line_in_db(connection: Connection, line: Line, server_map: str) -> bool:
    result = connection.execute(LINE_CHECK_STATEMENT, {"line": line.name, "map": server_map})
    for dn, col, sym, display in result:
        line.name = dn or line.name
        line.color = col or line.color
        line.symbols = sym or line.symbols
        line.display = bool(display)
        return True
    return False


def add_new_line_in_db(connection: Connection, line: Line, server_map: str):
    connection.execute(LINE_ADD_STATEMENT, {"map": server_map, "name": line.name})


def check_traintype_in_db(connection: Connection, train_type: TrainType) -> bool:
    result = connection.execute(TRAIN_CHECK_STATEMENT, {"ent_class": train_type.name})
    for full_name, short_name in result:
        train_type.name = full_name or short_name or train_type.name
        train_type.shortName = short_name or full_name or train_type.name
        return True
    return False


def add_new_train_in_db(connection: Connection, train_type: TrainType):
    connection.execute(TRAIN_ADD_STATEMENT, {"ent_class": train_type.typeName})
