import re

TIPOS_SQL = [
    "SMALLINT",
    "INT",
    "BIGINT",
    "FLOAT",
    "DOUBLE",
    "DECIMAL",
    "VARCHAR",
    "CHAR",
    "TEXT",
    "BOOLEAN",
    "DATE",
    "DATETIME",
    "UUID",
]

TIPOS_PARAMETRIZADOS = {
    "VARCHAR",
    "CHAR",
    "DECIMAL",
}

PARAMETROS_PADRAO = {
    "VARCHAR": (100,),
    "CHAR": (10,),
    "DECIMAL": (10, 2),
}

GERADORES = {
    "auto": "Automático",
    "nome": "Nome completo",
    "email": "E-mail",
    "inteiro": "Inteiro",
    "decimal": "Decimal",
    "cidade": "Cidade",
    "texto": "Texto",
    "data": "Data",
    "booleano": "Booleano",
    "telefone": "Telefone",
    "uuid": "UUID",
}

NUMERICOS = {"inteiro", "decimal"}


def detectar_gerador(nome, tipo=None):
    nome = nome.lower()
    tipo = (tipo or "").upper().strip()
    tipo_base = tipo.split("(")[0].strip()

    regras = {
        "email": ("email", "e_mail"),
        "nome": ("nome", "name"),
        "inteiro": (
            "idade", "age", "quantidade",
            "qtd", "estoque"
        ),
        "cidade": ("cidade", "city"),
        "telefone": ("telefone", "celular", "phone"),
        "data": ("data", "date", "nascimento"),
        "uuid": ("uuid",),
        "booleano": ("ativo", "active", "habilitado"),
        "texto": (
            "descricao", "description", "observacao"
        ),
        "decimal": (
            "salario", "preco", "preço",
            "valor", "dinheiro", "saldo"
        ),
    }

    for gerador, palavras in regras.items():
        if any(palavra in nome for palavra in palavras):
            return gerador

    tipos_automaticos = {
        "INT": "inteiro",
        "INTEGER": "inteiro",
        "SMALLINT": "inteiro",
        "BIGINT": "inteiro",
        "FLOAT": "decimal",
        "DOUBLE": "decimal",
        "REAL": "decimal",
        "DECIMAL": "decimal",
        "NUMERIC": "decimal",
        "BOOLEAN": "booleano",
        "BOOL": "booleano",
        "DATE": "data",
        "DATETIME": "data",
        "TIMESTAMP": "data",
        "UUID": "uuid",
    }

    return tipos_automaticos.get(tipo_base)


def tipo_do_gerador(gerador):
    tipos = {
        "nome": "VARCHAR(100)",
        "email": "VARCHAR(100)",
        "cidade": "VARCHAR(100)",
        "telefone": "VARCHAR(100)",
        "texto": "TEXT",
        "inteiro": "INT",
        "decimal": "DECIMAL(10,2)",
        "data": "DATE",
        "booleano": "BOOLEAN",
        "uuid": "UUID",
    }

    return tipos.get(gerador, "VARCHAR(100)")


def normalizar_coluna(coluna):
    # converte configuracoes antigas para o formato atual, sem modificar o dicionario original

    resultado = dict(coluna)
    opcoes = dict(resultado.get("options") or {})

    if resultado.get("generator") == "idade":
        resultado["generator"] = "inteiro"

        opcoes.setdefault("min", 18)
        opcoes.setdefault("max", 90)

    resultado["options"] = opcoes

    return resultado


PADRAO_TIPO_SQL = re.compile(
    r"^\s*([A-Za-z]+)\s*(?:\(\s*(\d+)\s*(?:,\s*(\d+)\s*)?\))?\s*$"
)


def interpretar_tipo_sql(tipo):
    # converte uma string SQL em tipo base e parametros

    # Exemplos:
    #     VARCHAR(150) -> ("VARCHAR", (150,))
    #     DECIMAL(10,2) -> ("DECIMAL", (10, 2))
    #     INT -> ("INT", ())

    resultado = PADRAO_TIPO_SQL.fullmatch(tipo or "")

    if not resultado:
        raise ValueError(f"Tipo SQL inválido: {tipo!r}")

    base = resultado.group(1).upper()

    if base not in TIPOS_SQL:
        raise ValueError(f"Tipo SQL não suportado: {base}")

    parametros = tuple(
        int(valor)
        for valor in resultado.groups()[1:]
        if valor is not None
    )

    if base in ("VARCHAR", "CHAR"):
        if len(parametros) > 1:
            raise ValueError(
                f"{base} aceita apenas um parâmetro."
            )

        if not parametros:
            parametros = PARAMETROS_PADRAO[base]

    elif base == "DECIMAL":
        if not parametros:
            parametros = PARAMETROS_PADRAO["DECIMAL"]

        elif len(parametros) == 1:
            parametros = (parametros[0], 0)

    
    elif parametros:
        raise ValueError(
            f"O tipo {base} não aceita parâmetros."
        )

    if base in ("VARCHAR", "CHAR"):
        if parametros[0] < 1:
            raise ValueError(
                f"{base} exige tamanho maior que zero."
            )

    elif base == "DECIMAL":
        precisao, escala = parametros

        if precisao < 1:
            raise ValueError(
                "A precisão de DECIMAL deve ser "
                "maior que zero."
            )

        if escala < 0 or escala > precisao:
            raise ValueError(
                "A escala de DECIMAL deve estar "
                "entre zero e a precisão."
            )

    return base, parametros



def montar_tipo_sql(base, tamanho=None, escala=None):
    # monta e valida o tipo SQL

    base = (base or "").upper().strip()

    if base not in TIPOS_SQL:
        raise ValueError(
            f"Tipo SQL não suportado: {base}"
        )

    if base in ("VARCHAR", "CHAR"):
        try:
            tamanho = int(tamanho)
        except (TypeError, ValueError):
            raise ValueError(
                f"Informe um tamanho válido para {base}."
            )

        if tamanho < 1:
            raise ValueError(
                f"O tamanho de {base} deve ser maior que zero."
            )

        return f"{base}({tamanho})"

    if base == "DECIMAL":
        try:
            precisao = int(tamanho)
            escala = int(escala)
        except (TypeError, ValueError):
            raise ValueError(
                "Informe precisão e escala válidas."
            )

        if precisao < 1:
            raise ValueError(
                "A precisão deve ser maior que zero."
            )

        if escala < 0 or escala > precisao:
            raise ValueError(
                "A escala deve estar entre zero e a precisão."
            )

        return f"DECIMAL({precisao},{escala})"

    return base
