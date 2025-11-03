import requests
import re

BASE_URL = "https://antigo.qacademico.ifce.edu.br"
REGEX_RSA = re.compile(r'new RSAKeyPair\(.*"(\w+)",.*"(\w+)"', re.DOTALL)


# Implementação da criptografia RSA, usando o método de padding do
# "Ohdave", que é inseguro e é o gore que o QAcadêmico usa no login.
def encrypt(input, exp_hex, mod_hex):
    n = int(mod_hex, 16)
    e = int(exp_hex, 16)

    key_size = (n.bit_length() + 7) // 8

    encoded = input.encode("utf-8")

    padded = encoded + (b"\x00" * (key_size - len(encoded)))

    m = int.from_bytes(padded, byteorder="little")

    encrypted = pow(m, e, n)

    return hex(encrypted)[2:]


def login(session: requests.Session, matricula: str, senha: str):
    # só pra pegar os cookies iniciais mesmo
    session.get(f"{BASE_URL}/qacademico/index.asp", params={"t": 1001})
    rsa_req = session.get(
        f"{BASE_URL}/qacademico/lib/rsa/gerador_chaves_rsa.asp",
        params={"form": "frmLogin", "action": "/qacademico/lib/validalogin.asp"},
    )
    if not rsa_req.ok:
        return False

    if (search := REGEX_RSA.search(rsa_req.text)) is None:
        return False
    exp, mod = search.groups()

    data = {
        "LOGIN": encrypt(matricula, exp, mod),
        "SENHA": encrypt(senha, exp, mod),
        "TIPO_USU": encrypt("1", exp, mod),
        "SUbmit": encrypt("OK", exp, mod),
    }

    session.headers["Referer"] = f"{BASE_URL}/qacademico/index.asp?t=1001"
    res = session.post(
        f"{BASE_URL}/qacademico/lib/validalogin.asp", data=data, allow_redirects=False
    )

    return res.status_code == 302 and res.text.find("?t=2000") != -1
