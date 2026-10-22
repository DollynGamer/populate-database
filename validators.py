import re

IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def validar_config(tabela, colunas, quantidade):
    if not IDENT.fullmatch(tabela):
        raise ValueError('Nome da tabela inválido. Use letras, números e "_", começando por letra ou "_".')
    if not colunas:
        raise ValueError('Adicione pelo menos uma coluna.')
    if not quantidade.isdigit() or int(quantidade) < 1:
        raise ValueError('A quantidade de registros deve ser um inteiro positivo.')
    nomes = set()
    for col in colunas:
        nome = col['name']
        if not IDENT.fullmatch(nome):
            raise ValueError(f'Nome de coluna inválido: {nome!r}.')
        if nome.lower() in nomes:
            raise ValueError(f'Nome de coluna repetido: {nome}.')
        nomes.add(nome.lower())
        if col['generator'] in ('idade', 'inteiro', 'decimal'):
            op = col['options']
            if op['min'] > op['max']:
                raise ValueError(f'O mínimo é maior que o máximo em {nome}.')
    return True
