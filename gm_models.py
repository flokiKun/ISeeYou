from typing import Optional, List

from pydantic import BaseModel

class GMPosition(BaseModel):
    line: Optional[str] = None
    station: Optional[str] = None
    prev_station: Optional[str] = None
    next_station: Optional[str] = None
    path: Optional[int] = None


class GMTrain(BaseModel):
    heads: List[int]  # ID энтити голов
    inters: List[int] # ID энтити промежуточных вагонов
    wagons: List[int] # ID энтити всех вагонов
    types: List[str] # Типы классов вагонов, в том же порядке, что и wagons
    head_type: str # Тип одной из голов - считать типом поезда
    owner_steamid: str # SteamID64 заспавнившего игрока
    owner_name: str  # Его ник
    owner_disconnected: bool # Отключился ли он с сервера
    route_number: str | int # Номер маршрута
    position: GMPosition

class GMPlayer(BaseModel):
  steamid: str
  name: str
  rank: str
  color: str
  current_role: Optional[str] = None
  session_time: int  # in seconds
  active_train: Optional[int] = None  # index of the following list
  trains: List[GMTrain]   # GMTrain struct not changed


class GMStatus(BaseModel):
  uptime: int  # in seconds since server start
  svtime: int  # UTC time on server, in millis since epoch
  max_wagons: int
  map: str
  players: List[GMPlayer]
  asnp_list: List[dict]  # always empty for now
  stations: List[dict]  # same here