from pydantic import BaseModel
import enum


class TurnoPeriodo(enum.Enum):
    AB_TARDE = {"13:30~14:29", "14:30~15:30"}
    CD_TARDE = {"16:00~16:59", "17:00~18:00"}
    AB_NOITE = {"18:30~19:19", "19:20~20:10"}

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if value in member.value:
                return member

        return None


class HorarioItem(BaseModel):
    nome: str
    sigla: str


class HorarioPeriodoItem(BaseModel):
    cadeira: HorarioItem
    sala: HorarioItem


class HorarioDiaItem(BaseModel):
    items: dict[str, HorarioPeriodoItem | None]
