
import flet as ft

from importer import importar_arquivo


def construir_importacao(voltar, continuar, atualizar):
    caminho = ft.TextField(
        label="Caminho do arquivo",
        hint_text="Selecione um arquivo ou informe o caminho",
        expand=True,
    )

    tabela = ft.Dropdown(
        label="Tabela do SQLite",
        width=350,
        visible=False,
    )

    mensagem = ft.Text("", selectable=True)

    def mostrar_erro(erro):
        mensagem.value = str(erro)
        mensagem.color = ft.Colors.RED_300
        atualizar()

    async def selecionar_arquivo(e):
        try:
            arquivos = await ft.FilePicker().pick_files(
                dialog_title="Importar banco de dados",
                allow_multiple=False,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=[
                    "json", "db", "csv", "xlsx"
                ],
            )

            if arquivos:
                caminho.value = arquivos[0].path
                tabela.visible = False
                tabela.value = None
                mensagem.value = ""
                atualizar()

                verificar_arquivo()

        except Exception as erro:
            mostrar_erro(erro)

    def verificar_arquivo(e=None):
        try:
            resultado = importar_arquivo(
                (caminho.value or "").strip()
            )

            if "tables" in resultado:
                tabelas = resultado["tables"]

                if not tabelas:
                    raise ValueError(
                        "Nenhuma tabela encontrada no SQLite."
                    )

                tabela.options = [
                    ft.DropdownOption(key=x, text=x)
                    for x in tabelas
                ]

                tabela.value = None
                tabela.visible = True

                mensagem.value = (
                    "Banco identificado. Escolha a tabela "
                    "que deseja importar."
                )

            else:
                tabela.visible = False
                mensagem.value = (
                    f"Arquivo identificado: "
                    f"{len(resultado['columns'])} colunas."
                )

            mensagem.color = ft.Colors.GREEN_300

        except Exception as erro:
            tabela.visible = False
            mostrar_erro(erro)

        atualizar()

    def confirmar(e):
        try:
            arquivo = (caminho.value or "").strip()

            if not arquivo:
                raise ValueError("Selecione um arquivo.")

            if arquivo.lower().endswith(".db"):
                if not tabela.value:
                    verificar_arquivo()

                    if not tabela.visible:
                        return

                    raise ValueError(
                        "Selecione uma tabela para continuar."
                    )

                config = importar_arquivo(
                    arquivo,
                    tabela=tabela.value
                )

            else:
                config = importar_arquivo(arquivo)

            continuar(config)

        except Exception as erro:
            mostrar_erro(erro)

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="Voltar",
                        on_click=lambda e: voltar(),
                    ),
                    ft.Text(
                        "Importar banco",
                        size=29,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),

            ft.Text(
                "Importe a estrutura de um arquivo existente "
                "e configure os dados que deseja gerar.",
                color=ft.Colors.BLUE_GREY_300,
            ),

            ft.Container(height=15),

            ft.Container(
                padding=20,
                border=ft.Border.all(
                    1, ft.Colors.BLUE_GREY_700
                ),
                border_radius=12,
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Selecionar arquivo",
                            size=19,
                            weight=ft.FontWeight.BOLD,
                        ),

                        ft.Text(
                            "Formatos aceitos: JSON, SQLite, "
                            "CSV e Excel (.xlsx)."
                        ),

                        ft.Row(
                            controls=[
                                caminho,

                                ft.IconButton(
                                    icon=ft.Icons.FOLDER_OPEN,
                                    tooltip="Procurar arquivo",
                                    on_click=selecionar_arquivo,
                                ),
                            ],
                        ),

                        ft.OutlinedButton(
                            content="Verificar arquivo",
                            icon=ft.Icons.SEARCH,
                            on_click=verificar_arquivo,
                        ),

                        tabela,

                        mensagem,

                        ft.Divider(),

                        ft.Button(
                            content="Continuar configuração",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=confirmar,
                        ),
                    ],
                    spacing=15,
                ),
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=15,
    )
