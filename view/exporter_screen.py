
import asyncio
import flet as ft

from exporter import exportar, pasta_downloads


def construir_exportacao(obter_dados, atualizar):
    # obter_dados deve retornar: (config, quantidade)

    formato = ft.RadioGroup(
        value="db",
        content=ft.Column(
            controls=[
                ft.Radio(value="db", label="SQLite (.db)"),
                ft.Radio(value="sql", label="Arquivo SQL (.sql)"),
                ft.Radio(value="json", label="JSON (.json)"),
                ft.Radio(value="csv", label="CSV (.csv)"),
                ft.Radio(value="xlsx", label="Excel (.xlsx)"),
            ],
            spacing=8,
        ),
    )

    mensagem = ft.Text(
        "",
        selectable=True,
    )

    progresso = ft.ProgressRing(
        visible=False,
        width=24,
        height=24,
    )

    def fechar(e=None):
        painel.visible = False
        atualizar()

    async def confirmar(e):
        try:
            config, quantidade = obter_dados()

        except (ValueError, TypeError, OverflowError) as erro:
            mensagem.value = str(erro)
            mensagem.color = ft.Colors.RED_300
            atualizar()
            return

        botao_confirmar.disabled = True
        botao_cancelar.disabled = True
        progresso.visible = True

        mensagem.value = "Gerando arquivo. Aguarde..."
        mensagem.color = ft.Colors.BLUE_300

        atualizar()

        try:
            caminho = await asyncio.to_thread(
                exportar,
                config,
                quantidade,
                formato.value,
            )

            mensagem.value = (
                "Arquivo exportado com sucesso!\n"
                f"Salvo em: {caminho}"
            )

            mensagem.color = ft.Colors.GREEN_300

        except Exception as erro:
            mensagem.value = f"Erro ao exportar: {erro}"
            mensagem.color = ft.Colors.RED_300

        finally:
            progresso.visible = False
            botao_confirmar.disabled = False
            botao_cancelar.disabled = False

            atualizar()

    botao_confirmar = ft.Button(
        content="Confirmar exportação",
        icon=ft.Icons.DOWNLOAD,
        on_click=confirmar,
    )

    botao_cancelar = ft.OutlinedButton(
        content="Fechar",
        on_click=fechar,
    )

    painel = ft.Container(
        visible=False,
        border=ft.Border.all(
            1,
            ft.Colors.BLUE_GREY_700,
        ),
        border_radius=12,
        padding=20,

        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.DOWNLOAD,
                            size=25,
                        ),

                        ft.Text(
                            "Exportar registros",
                            size=21,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),

                ft.Text(
                    "Escolha o formato do arquivo que "
                    "deseja gerar."
                ),

                ft.Divider(),

                formato,

                ft.Divider(),

                ft.Text(
                    f"Destino: {pasta_downloads()}",
                    selectable=True,
                    color=ft.Colors.BLUE_GREY_300,
                ),

                ft.Row(
                    controls=[
                        botao_confirmar,
                        botao_cancelar,
                        progresso,
                    ],
                    spacing=12,
                    wrap=True,
                ),

                mensagem,
            ],
            spacing=15,
        ),
    )

    def abrir(e=None):
        painel.visible = True
        mensagem.value = ""
        atualizar()

    return painel, abrir
