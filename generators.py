
import random
import uuid

from datetime import date, timedelta
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR

from faker import Faker

from catalog import (
    interpretar_tipo_sql,
    normalizar_coluna,
)

from sql_limits import (
    ajustar_texto,
    gerador_efetivo,
    validar_limites_coluna,
)


fake = Faker("pt_BR")


def gerar_inteiro(opcoes):
    minimo = int(opcoes.get("min", 0))
    maximo = int(opcoes.get("max", 10000))

    return random.randint(minimo, maximo)


def gerar_decimal(opcoes, tipo_sql):
    tipo, parametros = interpretar_tipo_sql(tipo_sql)

    minimo = Decimal(str(opcoes.get("min", 0)))
    maximo = Decimal(str(opcoes.get("max", 10000)))

    if tipo == "DECIMAL":
        _, escala = parametros

        fator = Decimal(10) ** escala

        inicio = int(
            (minimo * fator).to_integral_value(
                rounding=ROUND_CEILING
            )
        )

        fim = int(
            (maximo * fator).to_integral_value(
                rounding=ROUND_FLOOR
            )
        )

        valor = Decimal(
            random.randint(inicio, fim)
        ) / fator

        # float para compatibilidade com o exportador SQLite e os demais formatos
        return float(valor)

    return round(
        random.uniform(float(minimo), float(maximo)),
        2,
    )


def gerar_valor(coluna):
    coluna = normalizar_coluna(coluna)

    validar_limites_coluna(coluna)

    nome = coluna["name"]
    tipo_sql = coluna["type"]
    tipo, _ = interpretar_tipo_sql(tipo_sql)

    gerador = gerador_efetivo(coluna)
    opcoes = coluna.get("options") or {}

    if gerador == "nome":
        valor = fake.name()

    elif gerador == "email":
        valor = fake.email()

    elif gerador == "inteiro":
        valor = gerar_inteiro(opcoes)

    elif gerador == "decimal":
        valor = gerar_decimal(opcoes, tipo_sql)

    elif gerador == "cidade":
        valor = fake.city()

    elif gerador == "texto":
        valor = fake.sentence(nb_words=6)

    elif gerador == "data":
        inicio = date(2000, 1, 1)
        fim = date.today()

        dias = (fim - inicio).days

        data = inicio + timedelta(
            days=random.randint(0, dias)
        )

        if tipo == "DATETIME":
            valor = f"{data.isoformat()} 12:00:00"
        else:
            valor = data.isoformat()

    elif gerador == "booleano":
        valor = random.choice([True, False])

    elif gerador == "telefone":
        valor = fake.phone_number()

    elif gerador == "uuid":
        valor = str(uuid.uuid4())

    else:
        raise ValueError(
            f"Gerador desconhecido na coluna "
            f"'{nome}': {gerador!r}"
        )

    # todos os geradores de texto passam pelo mesmo ajuste
    return ajustar_texto(valor, tipo_sql)


def iterar_registros(config, quantidade):
    # gera registros progressivamente, a validacao acontece antes do primeiro registro

    quantidade = int(quantidade)

    if quantidade < 1:
        raise ValueError(
            "A quantidade deve ser maior que zero."
        )

    colunas = [
        normalizar_coluna(coluna)
        for coluna in config["columns"]
    ]

    for coluna in colunas:
        validar_limites_coluna(coluna)

    for _ in range(quantidade):
        registro = {}

        for coluna in colunas:
            registro[coluna["name"]] = gerar_valor(
                coluna
            )

        yield registro


def gerar_registros(config, quantidade):
    # versao em lista para pre-visu e testes

    return list(
        iterar_registros(config, quantidade)
    )
