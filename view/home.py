import flet as ft


def construir_home(abrir_gerador, abrir_importacao):

    def criar_opcao(icone, titulo, descricao, botao, acao):
        return ft.Container(
            width=400,
            padding=25,
            border=ft.Border.all(
                1,
                ft.Colors.BLUE_GREY_700,
            ),
            border_radius=14,
            content=ft.Column(
                controls=[
                    ft.Icon(
                        icone,
                        size=40,
                        color=ft.Colors.BLUE_300,
                    ),

                    ft.Text(
                        titulo,
                        size=23,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),

                    ft.Text(
                        descricao,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.BLUE_GREY_300,
                    ),

                    ft.Container(height=10),

                    ft.Button(
                        content=botao,
                        icon=ft.Icons.ARROW_FORWARD,
                        width=230,
                        on_click=lambda e: acao(),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
        )
    
    return ft.Column(
        controls=[
            ft.Text(
                "Populate Database",
                size=36,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),

            ft.Text(
                "Popular seu Banco de Dados com valores aleatórios sem precisar fazer isso manualmente.",
                size=15,
                color=ft.Colors.BLUE_GREY_300,
                text_align=ft.TextAlign.CENTER,
            ),

            ft.Container(height=20),

            criar_opcao(
                ft.Icons.ADD_CIRCLE_OUTLINE,
                "Gerar SQL",
                "Configure suas colunas e gere dados fictícios.",
                "Criar configuração",
                abrir_gerador,
            ),

            criar_opcao(
                ft.Icons.UPLOAD_FILE,
                "Importar banco",
                "Importe JSON, SQLite, CSV ou Excel.",
                "Selecionar arquivo",
                abrir_importacao,
            ),
        ],

        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
