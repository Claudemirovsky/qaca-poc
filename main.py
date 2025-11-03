from requests import Session
from login import BASE_URL, login


API_URL = f"{BASE_URL}/webapp/api"


def print_matriz(matriz):
    print("Matriz:", matriz["matriz"])
    print("Situação:", matriz["situacao"])
    print("Períodos:", matriz["numeroPeriodos"])
    hab = matriz["habilitacoes"][0]
    print("Carga horária (obrigatória):", int(hab["chObrigatoria"]))
    print("Carga horária (optativa):", int(hab["chOptativa"]))
    print("Carga horária (estágio):", int(hab["chEstagio"]))
    print("Carga horária (complementar):", int(hab["chComplementar"]))
    print("Carga horária (TOTAL):", int(hab["chTotal"]))


def print_cadeira(cadeira):
    print(f"\nNome: {cadeira['disciplina']} ({cadeira['sigla']})")
    if cadeira["preRequisitos"] != "":
        print("Pré requisitos:", cadeira["preRequisitos"])
    print("Período:", cadeira["numeroPeriodo"])
    print("Carga horária:", cadeira["cargaHoraria"])
    print("Créditos:", cadeira["credito"])
    print("Optativa?", "Sim" if cadeira["optativa"] else "Não")


def main():
    matricula = input("Matrícula: ")
    senha = input("Senha: ")

    session = Session()
    if not login(session, matricula, senha):
        print("Erro ao logar.")
        return

    matriz = session.get(f"{API_URL}/matriz-curricular/minha-matriz").json()
    print_matriz(matriz)

    cadeiras = session.get(
        f"{API_URL}/matriz-curricular/disciplinas",
        params={
            "idHabilitacao": matriz["habilitacoes"][0]["idHabilitacao"],
            "idMatrizCurricular": matriz["idMatriz"],
        },
    ).json()

    print()
    for cadeira in cadeiras:
        print_cadeira(cadeira)


if __name__ == "__main__":
    main()
