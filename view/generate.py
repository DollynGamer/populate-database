import flet as ft
from generator import gerar_amostra
from validators import validar_config
from view.exporter_screen import construir_exportacao
from catalog import (TIPOS_SQL, GERADORES, NUMERICOS, interpretar_tipo_sql, montar_tipo_sql, normalizar_coluna)


def construir_gerador(voltar, atualizar, config_inicial=None):
    linhas = []
    banco = ft.TextField(label='Nome do banco (referência)', hint_text='Ex.: empresa', width=330)
    tabela = ft.TextField(label='Nome da tabela', hint_text='Ex.: funcionarios', width=330)
    quantidade = ft.TextField(label='Quantidade de registros', hint_text='Ex.: 100', keyboard_type=ft.KeyboardType.NUMBER, width=240)
    colunas_view = ft.Column(spacing=12)
    mensagem = ft.Text('', selectable=True)
    amostra = ft.Column(spacing=8)

    def limpar_previa():
        mensagem.value = ''
        amostra.controls = []

    def adicionar_coluna(e=None, dados=None):
        dados = normalizar_coluna(dados or {})
        numero = len(linhas) + 1
        campo_nome = ft.TextField(
            label='Nome da coluna',
            hint_text='Ex.: nome_completo',
            value=dados.get('name', ''),
            width=420,
        )
        # recuperar o tipo SQL de uma configuracao importada
        tipo_importado = dados.get("type")

        if tipo_importado:
            tipo_inicial, parametros = interpretar_tipo_sql(
                tipo_importado
            )
        else:
            tipo_inicial, parametros = None, ()

        campo_tipo = ft.Dropdown(
            label="Tipo SQL",
            width=260,
            value=tipo_inicial,
            options=[
                ft.DropdownOption(key=x, text=x)
                for x in TIPOS_SQL
            ],
        )
        campo_tamanho = ft.TextField(
            label="Tamanho",
            hint_text="Ex.: 1000",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
            visible=False,
        )
        campo_escala = ft.TextField(
            label="Escala",
            hint_text="Ex.: 2",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
            visible=False,
        )
        parametros_view = ft.Row(
            controls=[
                campo_tamanho,
                campo_escala,
            ],
            spacing=12,
            visible=False,
        )
        
        def atualizar_parametros_tipo(preservar_valores=False):
            tipo = campo_tipo.value

            parametrizado = tipo in (
                "VARCHAR",
                "CHAR",
                "DECIMAL",
            )

            parametros_view.visible = parametrizado
            campo_tamanho.visible = parametrizado
            campo_escala.visible = tipo == "DECIMAL"

            if not preservar_valores:
                if tipo == "VARCHAR":
                    campo_tamanho.value = "100"
                    campo_escala.value = ""

                elif tipo == "CHAR":
                    campo_tamanho.value = "10"
                    campo_escala.value = ""

                elif tipo == "DECIMAL":
                    campo_tamanho.value = "10"
                    campo_escala.value = "2"

                else:
                    campo_tamanho.value = ""
                    campo_escala.value = ""

        def trocar_tipo(ev):
            atualizar_parametros_tipo()
            limpar_previa()
            atualizar()

        # recuperar parametros de um tipo SQL importado
        if tipo_inicial:
            atualizar_parametros_tipo()

            if tipo_inicial in ("VARCHAR", "CHAR"):
                campo_tamanho.value = str(parametros[0])

            elif tipo_inicial == "DECIMAL":
                campo_tamanho.value = str(parametros[0])
                campo_escala.value = str(parametros[1])

        campo_tipo.on_select = trocar_tipo

        campo_gerador = ft.Dropdown(
            label='Gerador',
            width=260,
            value=dados.get('generator'),
            options=[
                ft.DropdownOption(key=k, text=v)
                for k, v in GERADORES.items()
            ],
        )
        minimo = ft.TextField(label='Mínimo', hint_text='Ex.: 18', width=150, visible=False)
        maximo = ft.TextField(label='Máximo', hint_text='Ex.: 90', width=150, visible=False)
        opcoes_view = ft.Row(controls=[minimo, maximo], spacing=12, visible=False)

        # recuperar configuraçoes importadas
        opcoes_importadas = dados.get("options", {})
        gerador_inicial = dados.get("generator")

        if gerador_inicial in NUMERICOS:
            opcoes_view.visible = True
            minimo.visible = True
            maximo.visible = True

            minimo.value = str(
                opcoes_importadas.get("min", 0)
            )

            maximo.value = str(
                opcoes_importadas.get("max", 10000)
            )

        
        def trocar_gerador(ev):
            numerico = campo_gerador.value in NUMERICOS
            opcoes_view.visible = numerico
            minimo.visible = numerico
            maximo.visible = numerico

            if numerico:
                if not minimo.value:
                    minimo.value = "0"

                if not maximo.value:
                    maximo.value = "10000"

            limpar_previa()
            atualizar()

        campo_gerador.on_select = trocar_gerador
        bloco = ft.Container(
            border=ft.Border.all(1, ft.Colors.BLUE_GREY_700),
            border_radius=12, padding=18,
        )

        def remover(ev):
            linhas[:] = [item for item in linhas if item['bloco'] is not bloco]
            colunas_view.controls.remove(bloco)
            limpar_previa()
            atualizar()

        bloco.content = ft.Column(controls=[
            ft.Row(controls=[
                ft.Text(f'Coluna {numero}', size=17, weight=ft.FontWeight.BOLD),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip='Excluir coluna', on_click=remover),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            campo_nome,
            ft.Row(controls=[campo_tipo, campo_gerador], spacing=12, wrap=True),
            parametros_view,
            opcoes_view,
        ], spacing=12)
        linhas.append(dict(bloco=bloco, nome=campo_nome, tipo=campo_tipo, 
                           gerador=campo_gerador, minimo=minimo, maximo=maximo, tamanho=campo_tamanho, escala=campo_escala))
        colunas_view.controls.append(bloco)
        limpar_previa()
        atualizar()

    def obter_config():
        colunas = []
        for indice, linha in enumerate(linhas, 1):
            nome = (linha['nome'].value or '').strip()
            tipo_base = linha['tipo'].value            
            tipo = montar_tipo_sql(tipo_base, tamanho=linha["tamanho"].value, escala=linha["escala"].value)

            gerador = linha['gerador'].value
            if not nome or not tipo_base or not gerador:
                raise ValueError(f'Preencha nome, tipo SQL e gerador da coluna {indice}.')
            opcoes = {}
            if gerador in NUMERICOS:
                try:
                    if not linha['minimo'].value or not linha['maximo'].value:
                        raise ValueError
                    opcoes = {'min': float(linha['minimo'].value), 'max': float(linha['maximo'].value)}
                except (TypeError, ValueError):
                    raise ValueError(f'Informe mínimo e máximo válidos para a coluna {nome}.')
            colunas.append({'name': nome, 'type': tipo, 'generator': gerador, 'options': opcoes})
        nome_tabela = (tabela.value or '').strip()
        validar_config(nome_tabela, colunas, (quantidade.value or '').strip())
        return {'table': nome_tabela, 'columns': colunas}

    def obter_dados_exportacao():
        config = obter_config()

        total = int(
            (quantidade.value or "").strip()
        )

        return config, total

    def previsualizar(e):
        try:
            config = obter_config()
            registros = gerar_amostra(config, min(5, int(quantidade.value)))
            mensagem.value = f'Configuração válida. Prévia de {len(registros)} registro(s) dos {quantidade.value} solicitados.'
            mensagem.color = ft.Colors.GREEN_300
            amostra.controls = [
                ft.Text('Pré-visualização', size=19, weight=ft.FontWeight.BOLD),
                ft.Row(controls=[ft.DataTable(
                    columns=[ft.DataColumn(label=ft.Text(c['name'])) for c in config['columns']],
                    rows=[ft.DataRow(cells=[ft.DataCell(content=ft.Text(str(reg[c['name']]))) for c in config['columns']]) for reg in registros],
                )], scroll=ft.ScrollMode.AUTO),
            ]
        except (ValueError, TypeError, OverflowError) as erro:
            mensagem.value = str(erro)
            mensagem.color = ft.Colors.RED_300
            amostra.controls = []
        atualizar()

    # preencher formulario quando vier de uma importaçao
    if config_inicial:
        tabela.value = config_inicial.get('table', '')

        for coluna in config_inicial.get('columns', []):
            adicionar_coluna(dados=coluna)

    
    painel_exportacao, abrir_exportacao = construir_exportacao(
        obter_dados_exportacao,
        atualizar,
    )

    return ft.Column(controls=[
        ft.Row(controls=[ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip='Voltar', on_click=lambda e: voltar()), 
                         ft.Text('Gerar SQL', size=29, weight=ft.FontWeight.BOLD)]),
        ft.Text('Configure suas colunas antes de gerar a pré-visualização.', color=ft.Colors.BLUE_GREY_300),
        ft.Row(controls=[banco, tabela], wrap=True, spacing=12),
        quantidade,
        ft.Divider(),
        ft.Text('Colunas', 
            size=21, 
            weight=ft.FontWeight.BOLD),
        colunas_view,
        ft.OutlinedButton(content='Adicionar coluna', 
            icon=ft.Icons.ADD, 
            on_click=adicionar_coluna),
        ft.Divider(),
        ft.Row(controls=[
            ft.Button(content='Gerar pré-visualização', 
            icon=ft.Icons.PREVIEW, 
            on_click=previsualizar),
            ft.OutlinedButton(
            content="Exportar",
            icon=ft.Icons.DOWNLOAD,
            on_click=abrir_exportacao)
        ]),
        mensagem, amostra, painel_exportacao,
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=15)
