from typing import List
from pydantic import BaseModel


class Disciplina(BaseModel):
    idHabilitacao: int
    habilitacao: str
    idDisciplina: int
    disciplina: str
    numeroPeriodo: int
    cargaHoraria: int
    cargaHorariaPraticaProfissional: int
    credito: int
    sigla: str
    creditoRequisito: int
    optativa: bool
    tipo: int
    preRequisitosLista: List[str]
    preRequisitos: str
    coRequisitosLista: List
    coRequisitos: str
