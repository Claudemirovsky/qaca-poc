from pydantic import BaseModel, Field


class Usuario(BaseModel):
    tipo_usuario: int = Field(alias="tipoUsuario")
    id_pessoa: int = Field(alias="idPessoa")
    id_professor: int = Field(alias="idProfessor")
    id_matricula: int = Field(alias="idMatricula")
    id_classificado: int = Field(alias="idClassificado")
    login: str
    nome_pessoa: str = Field(alias="nomePessoa")
    matricula: str = Field(alias="matricula")
    id_pedido_matricula: int = Field(alias="idPedidoMatricula")
    id_etapa_pedido_matricula: int = Field(alias="idEtapaPedidoMatricula")
    redefinicao_senha_obrigatoria: int = Field(alias="redefinicaoSenhaObrigatoria")
    sexo: str
    menor_de_idade: bool = Field(alias="menorDeIdade")
    id_curso: int = Field(alias="idCurso")
    desc_curso: str = Field(alias="descCurso")
    nivel_ensino: str = Field(alias="nivelEnsino")
