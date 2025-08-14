from typing import Optional, List

from pydantic import BaseModel

from gm_models import GMStatus, GMPlayer, GMTrain


class Line(BaseModel):
    name: str
    color: str = "#cccccc"
    symbols: str = "?"
    display: bool = False


class Position(BaseModel):
    line: Optional[Line] = None
    station: Optional[str] = None
    prevStation: Optional[str] = None
    nextStation: Optional[str] = None
    path: Optional[int] = None


class TrainType(BaseModel):
    typeName: str
    name: str
    shortName: str


class Train(BaseModel):
    heads: List[int]
    inters: List[int]
    entIds: List[int]
    types: List[TrainType]
    name: TrainType
    position: Position
    routeNumber: int

    @classmethod
    def create_from_gm(cls, gm_train: GMTrain):
        placeholder_type = TrainType(typeName=gm_train.head_type,name=gm_train.head_type,shortName=gm_train.head_type)
        placeholder_line = Line(name=gm_train.position.line) if gm_train.position.line else None
        placeholder_pos = Position(line=placeholder_line, station=gm_train.position.station,
                                   prevStation=gm_train.position.prev_station,
                                   nextStation=gm_train.position.next_station, path=gm_train.position.path)
        return cls(heads=gm_train.heads, inters=gm_train.inters, entIds=gm_train.wagons,
                   types=[TrainType(typeName=x, name=x, shortName=x) for x in gm_train.types],
                   name=placeholder_type, position=placeholder_pos, routeNumber=gm_train.route_number)


class AsnpData(BaseModel):
    active: bool
    routeNumber: int
    topLine: Optional[str] = None
    bottomLine: Optional[str] = None
    auxiliaryString: Optional[str] = None


class StationStatus(BaseModel):
    name: str
    intervals: List[int]
    arrivalClocks: List[int]


class Player(BaseModel):
    steamid: str
    name: str
    rank: str
    color: str
    currentRole: Optional[str] = None
    trains: List[Train]
    activeTrain: Optional[int] = None
    sessionTime: int

    @classmethod
    def create_from_gm(cls, gm_player: GMPlayer):
        trains = [Train.create_from_gm(train) for train in gm_player.trains]

        return cls(steamid=gm_player.steamid, name=gm_player.name,
                   rank=gm_player.rank, color=gm_player.color,
                   currentRole=gm_player.current_role, trains=trains,
                   activeTrain=(gm_player.active_train - 1) if gm_player.active_train else None,
                   sessionTime=gm_player.session_time)

class ServerStatus(BaseModel):
    players: List[Player]
    uptime: int  # -1 if server is down
    svtime: int
    maxWagons: int
    map: Optional[str] = None  # None only if server is down
    lines: List[Line]
    stations: List[StationStatus] = []
    asnpList: List[AsnpData] = []

    @classmethod
    def create_from_gm(cls, gm_status: GMStatus):
        players = [Player.create_from_gm(ply) for ply in gm_status.players]
        return cls(players=players, uptime=gm_status.uptime, svtime=gm_status.svtime, maxWagons=gm_status.max_wagons,
                   map=gm_status.map, lines=[], stations=[], asnpList=[])