from typing import List

from pydantic import BaseModel, Field


class Habilitacao(BaseModel):
    id_habilitacao: int = Field(alias="idHabilitacao")
    habilitacao: str
    ch_obrigatoria: float = Field(alias="chObrigatoria")
    ch_optativa: float = Field(alias="chOptativa")
    ch_eletiva: float = Field(alias="chEletiva")
    ch_pratica_profissional: float = Field(alias="chPraticaProfissional")
    ch_estagio: float = Field(alias="chEstagio")
    ch_projeto_final: float = Field(alias="chProjetoFinal")
    ch_complementar: float = Field(alias="chComplementar")
    ch_total: float = Field(alias="chTotal")


class Matriz(BaseModel):
    id_curso: int = Field(alias="idCurso")
    id_matriz: int = Field(alias="idMatriz")
    matriz: str
    data_matriz: str = Field(alias="dataMatriz")
    numero_periodos: int = Field(alias="numeroPeriodos")
    situacao: str
    numero_habilitacoes: int = Field(alias="numeroHabilitacoes")
    habilitacoes: List[Habilitacao]
