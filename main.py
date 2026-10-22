import flet as ft

from view.home import construir_home
from view.generate import construir_gerador
from view.import_database import construir_importacao


async def main(page: ft.Page):
    page.title = "Populate Database"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 24

    page.window.width = 1280
    page.window.height = 720

    page.update()

    await page.window.center()

    conteudo = ft.Container(expand=True)

    def mostrar_home():
        conteudo.content = construir_home(
            mostrar_gerador,
            mostrar_importacao,
        )
        page.update()

    def mostrar_gerador(config=None):
        conteudo.content = construir_gerador(
            mostrar_home,
            page.update,
            config_inicial=config,
        )
        page.update()

    def mostrar_importacao():
        conteudo.content = construir_importacao(
            mostrar_home,
            mostrar_gerador,
            page.update,
        )
        page.update()

    page.add(conteudo)

    mostrar_home()


if __name__ == "__main__":
    ft.run(main)
