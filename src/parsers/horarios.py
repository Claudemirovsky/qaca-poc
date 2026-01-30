from ..models import HorarioDiaItem, HorarioItem, HorarioPeriodoItem, TurnoPeriodo
from bs4 import BeautifulSoup


def parse_horarios(doc: BeautifulSoup) -> dict[str, HorarioDiaItem]:
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
            if len(col.text.strip()) == 0 or elemMateria is None or elemSala is None:
                continue
            cadeira = HorarioItem(
                nome=str(elemMateria["title"]), sigla=elemMateria.text.strip()
            )
            sala = HorarioItem(nome=str(elemSala["title"]), sigla=elemSala.text.strip())
            data[key].items[time] = HorarioPeriodoItem(cadeira=cadeira, sala=sala)
    return data
