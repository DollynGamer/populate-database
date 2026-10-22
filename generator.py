# ponte provisória para o motor original sem alterar o arquivo legado
from legacy import gerar_registros


def gerar_amostra(config, quantidade=5):
    return gerar_registros(config, quantidade)
