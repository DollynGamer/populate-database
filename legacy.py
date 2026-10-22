import csv
import json
import random
import re
import sqlite3
import uuid

from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from faker import Faker


fake = Faker("pt_BR")
random.seed()

# isso aqui são os tipos de um valor pode ter
TIPOS = [
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


GERADORES = [
    "auto",
    "nome",
    "email",
    "idade",
    "inteiro",
    "decimal",
    "cidade",
    "texto",
    "data",
    "booleano",
    "telefone",
    "uuid",
]

IDENTIFICADOR = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validar_identificador(nome):
    if not IDENTIFICADOR.fullmatch(nome):
        raise ValueError(
            f"Identificador invalido: {nome!r}"
        )
    return nome


def validar_nome_coluna(nome):
    nome = nome.strip()

    if not IDENTIFICADOR.fullmatch(nome):
        print("Nome de coluna invalido. Tente novamente.\n")
        return False

    nome_lower = nome.lower()

    if (
        nome_lower == "id"
        or nome_lower.startswith("id_")
    ):
        print(
            f'\n"{nome}" eh um identificador que normalmente '
            "eh gerado automaticamente (primary key).\n"
            "Ele sera ignorado pelo gerador de dados. "
            "Informe outro nome de coluna:\n"
        )
        return False

    return True


def validar_tipo(tipo):
    tipo = tipo.strip().upper()

    padrao = (
        r"^(INT|INTEGER|BIGINT|SMALLINT|FLOAT|REAL|"
        r"DOUBLE|DECIMAL|NUMERIC|VARCHAR|CHAR|TEXT|"
        r"BOOLEAN|BOOL|DATE|DATETIME|TIMESTAMP|UUID)"
        r"(\s*\(\s*\d+(\s*,\s*\d+)?\s*\))?$"
    )

    if not re.fullmatch(padrao, tipo):
        raise ValueError(f"Tipo SQL nao permitido: {tipo}")

    return tipo


def ler_inteiro(mensagem, minimo=1):
    while True:
        try:
            valor = int(input(mensagem))
            if valor >= minimo:
                return valor
            print(f"Digite um numero maior ou igual a {minimo}.")
        except ValueError:
            print("Digite um numero inteiro valido.")


# isso aqui é para a pessoa conseguir configurar a própria tabela no terminal
def configurar_interativamente():
    print("\n=== CONFIGURAR TABELA ===")

    tabela = validar_identificador(
        input("Nome da tabela: ").strip()
    )

    quantidade = ler_inteiro("Quantidade de colunas: ")
    colunas = []

    for i in range(quantidade):
        print(f"\n--- Coluna {i + 1} ---")

        while True:
            nome = input("Nome da coluna: ").strip()

            if validar_nome_coluna(nome):
                break

        print("Tipos:", ", ".join(TIPOS))
        tipo = validar_tipo(input("Tipo SQL: "))

        print("Geradores:", ", ".join(GERADORES))
        gerador = input(
            "Gerador desejado [auto]: "
        ).strip().lower() or "auto"

        if gerador not in GERADORES:
            print("Gerador desconhecido. Usando auto.")
            gerador = "auto"

        opcoes = {}

        if gerador in ("idade", "inteiro", "decimal"):
            try:
                opcoes["min"] = float(
                    input("Valor minimo [0]: ") or 0
                )
                opcoes["max"] = float(
                    input("Valor maximo [10000]: ") or 10000
                )

                if opcoes["min"] > opcoes["max"]:
                    raise ValueError

            except ValueError:
                print("Intervalo invalido. Usando 0 a 10000.")
                opcoes = {"min": 0, "max": 10000}

        colunas.append({
            "name": nome,
            "type": tipo,
            "generator": gerador,
            "options": opcoes,
        })

    return {"table": tabela, "columns": colunas}



# isso aqui é para a pessoa conseguir importar as configurações em json
def importar_json(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        config = json.load(arquivo)

    validar_identificador(config["table"])

    if not config.get("columns"):
        raise ValueError("A configuracao precisa ter colunas.")

    nomes = set()

    for coluna in config["columns"]:
        validar_identificador(coluna["name"])
        coluna["type"] = validar_tipo(coluna["type"])

        if coluna["name"] in nomes:
            raise ValueError("Existem nomes de colunas repetidos.")
        nomes.add(coluna["name"])

        coluna.setdefault("generator", "auto")
        coluna.setdefault("options", {})

        if coluna["generator"] not in GERADORES:
            raise ValueError(
                f"Gerador desconhecido: {coluna['generator']}"
            )

    return config


# aqui é para importar os arquivos da tabela sqlite
def importar_sqlite(caminho, tabela):
    validar_identificador(tabela)

    conexao = sqlite3.connect(caminho)

    try:
        linhas = conexao.execute(
            f'PRAGMA table_info("{tabela}")'
        ).fetchall()

        if not linhas:
            raise ValueError("Tabela nao encontrada no SQLite.")

        colunas = []

        for linha in linhas:
            nome = linha[1]
            tipo = (linha[2] or "TEXT").upper()

            # a versao inicial importa tipos comuns
            tipo_base = tipo.split("(")[0].strip()

            if tipo_base not in TIPOS:
                tipo = "TEXT"

            colunas.append({
                "name": nome,
                "type": tipo,
                "generator": "auto",
                "options": {},
            })

        return {"table": tabela, "columns": colunas}

    finally:
        conexao.close()


# se deus quiser isso aqui vai ser a detecção automatica
def detectar_gerador(nome, tipo):
    nome = nome.lower()
    tipo = tipo.upper()

    regras = [
        (("email", "e_mail"), "email"),
        (("nome", "name"), "nome"),
        (("idade", "age"), "idade"),
        (("cidade", "city"), "cidade"),
        (("telefone", "celular", "phone"), "telefone"),
        (("data", "date", "nascimento"), "data"),
        (("uuid",), "uuid"),
        (("ativo", "active", "habilitado"), "booleano"),
        (("descricao", "description", "observacao"), "texto"),
        (("salario", "preco", "preço", "valor", "dinheiro"), "decimal"),
        (("quantidade", "qtd", "estoque"), "inteiro"),
    ]

    for palavras, gerador in regras:
        if any(palavra in nome for palavra in palavras):
            return gerador

    if tipo in ("BOOLEAN", "BOOL"):
        return "booleano"
    if tipo in ("DATE", "DATETIME", "TIMESTAMP"):
        return "data"
    if tipo in ("INT", "INTEGER", "BIGINT", "SMALLINT"):
        return "inteiro"
    if tipo in ("FLOAT", "DOUBLE", "REAL", "DECIMAL", "NUMERIC"):
        return "decimal"
    if tipo == "UUID":
        return "uuid"

    return "texto"


# gerar valores
def gerar_valor(coluna):
    nome = coluna["name"]
    tipo = coluna["type"].upper()
    gerador = coluna.get("generator", "auto")
    opcoes = coluna.get("options", {})

    if gerador == "auto":
        gerador = detectar_gerador(nome, tipo)

    minimo = opcoes.get("min", 0)
    maximo = opcoes.get("max", 10000)

    if gerador == "nome":
        return fake.name()

    if gerador == "email":
        return fake.email()

    if gerador == "idade":
        return random.randint(
            int(opcoes.get("min", 18)),
            int(opcoes.get("max", 90)),
        )

    if gerador == "inteiro":
        return random.randint(int(minimo), int(maximo))

    if gerador == "decimal":
        return round(
            random.uniform(float(minimo), float(maximo)), 2
        )

    if gerador == "cidade":
        return fake.city()

    if gerador == "texto":
        return fake.sentence(nb_words=6)

    if gerador == "data":
        inicio = date(2000, 1, 1)
        fim = date.today()
        dias = (fim - inicio).days
        data = inicio + timedelta(days=random.randint(0, dias))

        if tipo in ("DATETIME", "TIMESTAMP"):
            return f"{data.isoformat()} 12:00:00"

        return data.isoformat()

    if gerador == "booleano":
        return random.choice([True, False])

    if gerador == "telefone":
        return fake.phone_number()

    if gerador == "uuid":
        return str(uuid.uuid4())

    # fallback pelo tipo SQL, caso a regra seja desconhecida
    if tipo in ("INT", "INTEGER", "BIGINT", "SMALLINT"):
        return random.randint(0, 1000)

    if tipo in ("FLOAT", "DOUBLE", "REAL", "DECIMAL", "NUMERIC"):
        return round(random.uniform(0, 10000), 2)

    if tipo in ("BOOLEAN", "BOOL"):
        return random.choice([True, False])

    return fake.word()


# gerar registros
def gerar_registros(config, quantidade):
    registros = []

    for _ in range(quantidade):
        registro = {}

        for coluna in config["columns"]:
            registro[coluna["name"]] = gerar_valor(coluna)

        registros.append(registro)

    return registros


# gerar o sql finalmente
def escapar_identificador(nome, banco="generico"):
    validar_identificador(nome)

    if banco == "mysql":
        return f"`{nome}`"

    if banco == "sqlserver":
        return f"[{nome}]"

    return f'"{nome}"'


def formatar_sql(valor, tipo):
    if valor is None:
        return "NULL"

    if isinstance(valor, bool):
        return "TRUE" if valor else "FALSE"

    if isinstance(valor, (int, float, Decimal)):
        return str(valor)

    texto = str(valor).replace("'", "''")
    return f"'{texto}'"


def exportar_sql(config, registros, caminho, banco="generico"):
    tabela = escapar_identificador(config["table"], banco)
    nomes = [c["name"] for c in config["columns"]]
    tipos = {c["name"]: c["type"] for c in config["columns"]}

    colunas_sql = ", ".join(
        escapar_identificador(nome, banco) for nome in nomes
    )

    with open(caminho, "w", encoding="utf-8") as arquivo:
        for registro in registros:
            valores_sql = ", ".join(
                formatar_sql(registro[nome], tipos[nome])
                for nome in nomes
            )

            arquivo.write(
                f"INSERT INTO {tabela} ({colunas_sql}) "
                f"VALUES ({valores_sql});\n"
            )


# exportar em csv
def exportar_csv(config, registros, caminho):
    nomes = [c["name"] for c in config["columns"]]

    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=nomes,
            delimiter=";",
        )

        escritor.writeheader()
        escritor.writerows(registros)


# aqui é pra incluir no sqlite
def inserir_sqlite(config, registros, caminho):
    tabela = escapar_identificador(config["table"])
    nomes = [c["name"] for c in config["columns"]]

    colunas_sql = ", ".join(
        escapar_identificador(nome) for nome in nomes
    )
    placeholders = ", ".join("?" for _ in nomes)

    comando = (
        f"INSERT INTO {tabela} ({colunas_sql}) "
        f"VALUES ({placeholders})"
    )

    conexao = sqlite3.connect(caminho)

    try:
        conexao.executemany(
            comando,
            [
                tuple(registro[nome] for nome in nomes)
                for registro in registros
            ],
        )
        conexao.commit()
        print(f"{len(registros)} registros inseridos no SQLite.")

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


# o menu principal da resenha
def main():
    print("=" * 60)
    print("       GERADOR DE DADOS ALEATORIOS PARA SQL")
    print("=" * 60)

    print("\nComo deseja configurar as colunas?")
    print("1 - Configurar pelo terminal")
    print("2 - Importar arquivo JSON")
    print("3 - Importar estrutura de tabela SQLite")

    modo = input("Escolha: ").strip()

    try:
        if modo == "1":
            config = configurar_interativamente()

        elif modo == "2":
            caminho = input("Caminho do arquivo JSON: ").strip()
            config = importar_json(caminho)

        elif modo == "3":
            caminho = input("Caminho do banco SQLite: ").strip()
            tabela = input("Nome da tabela existente: ").strip()
            config = importar_sqlite(caminho, tabela)

        else:
            print("Opcao invalida.")
            return

        quantidade = ler_inteiro(
            "\nQuantos registros deseja gerar? "
        )

        registros = gerar_registros(config, quantidade)

        print("\nComo deseja salvar os dados?")
        print("1 - Arquivo SQL")
        print("2 - Arquivo CSV")
        print("3 - Inserir diretamente em um banco SQLite")
        print("4 - Gerar SQL e CSV")

        saida = input("Escolha: ").strip()

        if saida in ("1", "4"):
            banco = input(
                "Dialeto SQL [generico/mysql/sqlserver]: "
            ).strip().lower() or "generico"

            if banco not in ("generico", "mysql", "sqlserver"):
                print("Dialeto desconhecido; usando generico.")
                banco = "generico"

            exportar_sql(config, registros, "saida.sql", banco)
            print("Arquivo saida.sql criado.")

        if saida in ("2", "4"):
            exportar_csv(config, registros, "saida.csv")
            print("Arquivo saida.csv criado.")

        if saida == "3":
            caminho = input(
                "Caminho do banco SQLite de destino: "
            ).strip()
            inserir_sqlite(config, registros, caminho)

        if saida not in ("1", "2", "3", "4"):
            print("Opcao invalida.")

    except (ValueError, KeyError, OSError, sqlite3.Error) as erro:
        print(f"\nErro: {erro}")


if __name__ == "__main__":
    main()

