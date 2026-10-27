
from decimal import Decimal, InvalidOperation

from catalog import (
    interpretar_tipo_sql,
    detectar_gerador,
    normalizar_coluna,
)


LIMITES_INTEIROS = {
    "SMALLINT": (-32768, 32767),
    "INT": (-2147483648, 2147483647),
    "BIGINT": (
        -9223372036854775808,
        9223372036854775807,
    ),
}

TIPOS_INTEIROS = set(LIMITES_INTEIROS)

TIPOS_DECIMAIS = {
    "DECIMAL", "FLOAT", "DOUBLE",
}

TIPOS_TEXTO = {
    "VARCHAR", "CHAR", "TEXT",
}

GERADORES_TEXTO = {
    "nome", "email", "cidade",
    "texto", "telefone", "uuid",
}

COMPATIBILIDADE = {
    "inteiro": TIPOS_INTEIROS,
    "decimal": TIPOS_DECIMAIS,
    "booleano": {"BOOLEAN"},
    "data": {"DATE", "DATETIME"},
    "nome": TIPOS_TEXTO,
    "email": TIPOS_TEXTO,
    "cidade": TIPOS_TEXTO,
    "texto": TIPOS_TEXTO,
    "telefone": TIPOS_TEXTO,
    "uuid": TIPOS_TEXTO | {"UUID"},
}


def decimal_valido(valor, nome):
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(
            f"{nome}: informe um número válido."
        )

    if not numero.is_finite():
        raise ValueError(
            f"{nome}: o número deve ser finito."
        )

    return numero


def gerador_efetivo(coluna):
    coluna = normalizar_coluna(coluna)
    gerador = coluna.get("generator") or "auto"

    if gerador == "auto":
        gerador = detectar_gerador(
            coluna["name"],
            coluna["type"],
        )

    if gerador is None:
        tipo, _ = interpretar_tipo_sql(coluna["type"])

        if tipo in TIPOS_TEXTO:
            return "texto"

        if tipo == "UUID":
            return "uuid"

        raise ValueError(
            f"Coluna '{coluna['name']}': "
            "não foi possível detectar um gerador."
        )

    return gerador

def validar_limites_coluna(coluna):
    coluna = normalizar_coluna(coluna)

    nome = coluna["name"]
    tipo, parametros = interpretar_tipo_sql(
        coluna["type"]
    )

    gerador = gerador_efetivo(coluna)
    opcoes = coluna.get("options") or {}

    permitidos = COMPATIBILIDADE.get(gerador)

    if permitidos is None:
        raise ValueError(
            f"Coluna '{nome}': gerador desconhecido: "
            f"{gerador!r}."
        )

    if tipo not in permitidos:
        raise ValueError(
            f"Coluna '{nome}': o gerador '{gerador}' "
            f"não é compatível com {tipo}."
        )

    if tipo in ("VARCHAR", "CHAR"):
        tamanho = parametros[0]

        if tamanho < 1:
            raise ValueError(
                f"Coluna '{nome}': tamanho inválido."
            )

    if tipo == "DECIMAL":
        precisao, escala = parametros

        if precisao < 1 or escala < 0 or escala > precisao:
            raise ValueError(
                f"Coluna '{nome}': precisão ou escala inválida."
            )

    if gerador not in ("inteiro", "decimal"):
        return True

    minimo = decimal_valido(
        opcoes.get("min", 0),
        f"Coluna '{nome}', mínimo",
    )

    maximo = decimal_valido(
        opcoes.get("max", 10000),
        f"Coluna '{nome}', máximo",
    )

    if minimo > maximo:
        raise ValueError(
            f"Coluna '{nome}': mínimo maior que máximo."
        )

    if tipo in LIMITES_INTEIROS:
        limite_min, limite_max = LIMITES_INTEIROS[tipo]

        if (
            minimo != minimo.to_integral_value()
            or maximo != maximo.to_integral_value()
        ):
            raise ValueError(
                f"Coluna '{nome}': {tipo} exige "
                "limites inteiros."
            )

        if minimo < limite_min or maximo > limite_max:
            raise ValueError(
                f"Coluna '{nome}': {tipo} aceita valores "
                f"entre {limite_min} e {limite_max}."
            )

    elif tipo == "DECIMAL":
        precisao, escala = parametros

        passo = Decimal(1).scaleb(-escala)

        limite = (
            Decimal(10) ** (precisao - escala)
        ) - passo

        if minimo < -limite or maximo > limite:
            raise ValueError(
                f"Coluna '{nome}': DECIMAL"
                f"({precisao},{escala}) aceita valores "
                f"entre {-limite} e {limite}."
            )

        # verifica se existe pelo menos um valor representavel entre os limites informados
        primeiro = minimo.quantize(
            passo,
            rounding="ROUND_CEILING",
        )

        ultimo = maximo.quantize(
            passo,
            rounding="ROUND_FLOOR",
        )

        if primeiro > ultimo:
            raise ValueError(
                f"Coluna '{nome}': não existe valor "
                f"com {escala} casas decimais dentro "
                "do intervalo informado."
            )

    return True



def ajustar_texto(valor, tipo_sql):
    tipo, parametros = interpretar_tipo_sql(tipo_sql)

    if valor is None:
        return None

    # somente tipos textuais devem ser convertidos para string
    if tipo not in ("VARCHAR", "CHAR", "TEXT"):
        return valor

    texto = str(valor)

    if tipo == "VARCHAR":
        return texto[:parametros[0]]

    if tipo == "CHAR":
        tamanho = parametros[0]
        return texto[:tamanho].ljust(tamanho)

    return texto
