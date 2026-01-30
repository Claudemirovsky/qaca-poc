import re
import requests
import urllib.parse
from src.models.coeficiente import Coeficiente
from src.exceptions import LoginError, ApiError
from .models import (
    Disciplina,
    Matriz,
    Usuario,
    HorarioItem,
    HorarioDiaItem,
    HorarioPeriodoItem,
    TurnoPeriodo,
    PeriodoLetivo,
    BoletimItem,
)
from bs4 import BeautifulSoup
from pydantic import TypeAdapter


class QAcademico:
    BASE_URL = "https://antigo.qacademico.ifce.edu.br"
    __REGEX_RSA = re.compile(r'new RSAKeyPair\(.*"(\w+)",.*"(\w+)"', re.DOTALL)
    API_URL = f"{BASE_URL}/webapp/api"
    __disciplinas_ta = TypeAdapter(list[Disciplina])
    __periodos_ta = TypeAdapter(list[PeriodoLetivo])
    __boletim_ta = TypeAdapter(list[BoletimItem])

    def __init__(self) -> None:
        self.__session = requests.Session()
        self.__session.headers = {
            "Referer": f"{self.BASE_URL}/qacademico/index.asp?t=1001",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__session.close()

    def __encrypt(self, input, exp_hex, mod_hex):
        n = int(mod_hex, 16)
        e = int(exp_hex, 16)

        key_size = (n.bit_length() + 7) // 8

        encoded = input.encode("utf-8")

        padded = encoded + (b"\x00" * (key_size - len(encoded)))

        m = int.from_bytes(padded, byteorder="little")

        encrypted = pow(m, e, n)
        return hex(encrypted)[2:]

    def login(self, matricula: str, senha: str):
        qaca_url = f"{self.BASE_URL}/qacademico"
        # só pra pegar os cookies iniciais mesmo
        self.__session.get(f"{qaca_url}/index.asp", params={"t": 1001})
        rsa_res = self.__session.get(
            f"{qaca_url}/lib/rsa/gerador_chaves_rsa.asp",
            params={"form": "frmLogin", "action": "/qacademico/lib/validalogin.asp"},
        )
        if not rsa_res.ok:
            raise LoginError(
                f"Falha ao obter as chaves RSA: HTTP {rsa_res.status_code}"
            )

        if (search := self.__REGEX_RSA.search(rsa_res.text)) is None:
            raise LoginError("Falha ao extrair as chaves RSA da página.")
        exp, mod = search.groups()

        data = {
            "LOGIN": self.__encrypt(matricula, exp, mod),
            "SENHA": self.__encrypt(senha, exp, mod),
            "TIPO_USU": self.__encrypt("1", exp, mod),
            "SUbmit": self.__encrypt("OK", exp, mod),
        }

        self.__session.headers["Referer"] = f"{qaca_url}/index.asp?t=1001"
        res = self.__session.post(
            f"{qaca_url}/lib/validalogin.asp",
            data=data,
            allow_redirects=False,
        )

        if res.status_code != 302 or "Location" not in res.headers:
            raise LoginError("Erro ao processar resposta do endpoint de login.")

        new_url = urllib.parse.urlparse(res.headers["Location"])
        queries = urllib.parse.parse_qs(new_url.query)
        if "t" not in queries:
            raise LoginError("Erro ao processar código de resposta do login.")
        code = queries["t"][0]

        match code:
            case "2000":  # Sucesso
                pass
            case "1":
                raise LoginError("Credenciais inválidas.")
            case "2044":
                raise LoginError(
                    "Alteração de cadastro necessária. Abra o QAcadêmico web."
                )
            case _:
                raise LoginError(f"Erro desconhecido. Resposta do QAcadêmico: {code}")

    def matriz(self) -> Matriz:
        response = self.__session.get(f"{self.API_URL}/matriz-curricular/minha-matriz")
        if not response.ok:
            raise ApiError("a matriz", response)

        return Matriz.model_validate_json(response.text)

    def disciplinas(self, matriz: Matriz) -> list[Disciplina]:
        response = self.__session.get(
            f"{self.API_URL}/matriz-curricular/disciplinas",
            params={
                "idMatrizCurricular": matriz.id_matriz,
                "idHabilitacao": matriz.habilitacoes[0].id_habilitacao,
            },
        )
        if not response.ok:
            raise ApiError("a lista de disciplinas", response)

        return self.__disciplinas_ta.validate_json(response.text)

    def usuario(self) -> Usuario:
        response = self.__session.get(
            f"{self.API_URL}/autenticacao/usuario-autenticado"
        )
        if not response.ok:
            raise ApiError("dados do usuário", response)

        return Usuario.model_validate_json(response.text)

    def horarios(self, periodo: PeriodoLetivo) -> dict[str, HorarioDiaItem]:
        params = {"t": 2010}
        if periodo is not None:
            params = {
                **params,
                "Exibir": "OK",
                "COD_MATRICULA": -1,
                "cmbanos": periodo.ano,
                "cmbperiodos": periodo.periodo,
            }
        response = self.__session.get(
            f"{self.BASE_URL}/qacademico/index.asp", params=params
        )
        if not response.ok:
            raise ApiError("dados dos horários", response)
        doc = BeautifulSoup(response.text, "html.parser")
        return self.__horarios(doc)

    def __horarios(self, doc: BeautifulSoup) -> dict[str, HorarioDiaItem]:
        table = doc.select_one("table.conteudoTitulo + br + table")
        assert table is not None
        lines = table.select("tr")
        titles = [x.text.strip() for x in lines[0].select("font")]
        data = {x: HorarioDiaItem(items={}) for x in titles[1:]}
        for line in table.select("tr")[1:]:
            cols = line.select("td font")
            time = TurnoPeriodo(cols[0].text.strip()).name
            del cols[0]
            for i in range(0, len(cols)):
                key = titles[i + 1]
                data[key].items[time] = None
                col = cols[i]
                elemMateria = col.select_one("div:has(+br)")
                elemSala = col.select_one("div + br + div:has(+br)")
                if (
                    len(col.text.strip()) == 0
                    or elemMateria is None
                    or elemSala is None
                ):
                    continue
                cadeira = HorarioItem(
                    nome=str(elemMateria["title"]), sigla=elemMateria.text.strip()
                )
                sala = HorarioItem(
                    nome=str(elemSala["title"]), sigla=elemSala.text.strip()
                )
                data[key].items[time] = HorarioPeriodoItem(cadeira=cadeira, sala=sala)
        return data

    def periodos_letivos(self) -> list[PeriodoLetivo]:
        response = self.__session.get(f"{self.API_URL}/boletim/periodos-letivos")
        if not response.ok:
            raise ApiError("a lista de períodos letivos", response)

        return self.__periodos_ta.validate_json(response.text)

    def boletim(self, periodo: PeriodoLetivo) -> list[BoletimItem]:
        response = self.__session.get(
            f"{self.API_URL}/boletim/disciplinas",
            params=periodo.model_dump(by_alias=True),
        )
        if not response.ok:
            raise ApiError("o boletim", response)

        return self.__boletim_ta.validate_json(response.text)

    def coeficiente(self) -> Coeficiente:
        response = self.__session.get(
            f"{self.API_URL}/dashboard/aluno/grafico-rendimento"
        )
        if not response.ok:
            raise ApiError("coeficiente", response)

        return Coeficiente.model_validate_json(response.text, by_alias=True)
