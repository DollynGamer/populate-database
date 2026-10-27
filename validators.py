import re

from sql_limits import validar_limites_coluna


IDENT = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*$"
)


def validar_config(tabela, colunas, quantidade):
    if not IDENT.fullmatch(tabela or ""):
        raise ValueError(
            'Nome da tabela inválido. Use letras, números '
            'e "_", começando por letra ou "_".'
        )

    if not colunas:
        raise ValueError(
            "Adicione pelo menos uma coluna."
        )

    quantidade = str(quantidade)

    if not quantidade.isdigit() or int(quantidade) < 1:
        raise ValueError(
            "A quantidade de registros deve ser "
            "um inteiro positivo."
        )

    nomes = set()

    for coluna in colunas:
        nome = coluna["name"]

        if not IDENT.fullmatch(nome or ""):
            raise ValueError(
                f"Nome de coluna inválido: {nome!r}."
            )

        if nome.lower() in nomes:
            raise ValueError(
                f"Nome de coluna repetido: {nome}."
            )

        nomes.add(nome.lower())

        validar_limites_coluna(coluna)

    return True
