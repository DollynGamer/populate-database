# Populate Database

![Code Size](https://img.shields.io/github/languages/code-size/DollynGamer/populate-database?style=for-the-badge)
![Language Count](https://img.shields.io/github/languages/count/DollynGamer/populate-database?style=for-the-badge)
![Forks](https://img.shields.io/github/forks/DollynGamer/populate-database?style=for-the-badge)


<p align="center">
  <img src="logo.png" alt="Leandro" width="150">
</p>

> Cansou de fazer "INSERT INTO"? Use Populate Database. Um projeto em que recebe valores de um Banco de Dados e exporta em MySQL e CSV, com suporte de SQLite e .json.

## Ajustes e melhorias

O projeto ainda está em desenvolvimento e as próximas atualizações serão voltadas para as seguintes tarefas:

- [ ] Implementar TKinter/CustomTKinter (ou algo melhor)
- [ ] Detectar Primary Keys e Auto Increment
- [ ] Compatibilidade entre geradores e tipos SQL
- [ ] Respeitar o tamanho dos campos
- [ ] Detectar restrições UNIQUE e NOT NULL

> [!NOTE]
> O projeto foi modificado com o uso de inteligência artificial em diversos aspectos. Como não possuo experiência suficiente nessa área, peço que leve isso em consideração caso, por qualquer motivo, você não aprove o uso de IA.

## Pré-requisitos

Verifique se você atendeu aos seguintes requisitos:

- Você instalou `<Python 3.14.0 / Faker 40.43.0 / pip 25.2 / tzdata 2026.5>`
- Você tem uma máquina `Windows`.

## Usando Populate Database

> [!CAUTION]
> Tenha em mente que este projeto ainda está em um estágio inicial! Ele pode apresentar falhas em diversos aspectos, portanto, faça um backup do seu banco de dados se possível antes de utilizá-lo!

Para usar Populate Database, siga estas etapas:

```
Baixe o "populate-database-main.zip"
Extraia o arquivo .zip para qualquer local em sua máquina.
Abra o projeto em qualquer IDE que quiser, ou use o VSCode mesmo.
Baixe os requirements usando > pip install -r requirements.txt
Execute o "main.py".
```

Agora, caso queira importar um arquivo/estrutura para popular o seu Banco de Dados:

```
Importar arquivo JSON:

Selecione a opção "Importar arquivo JSON" digitando "2".
Digite o caminho do arquivo completo, exemplo:

(caso seu arquivo não esteja na mesma pasta):
C:\Users\SeuUsuario\Documents\Python\exemplo_banco.json

(caso seu arquivo esteja na mesma pasta, apenas digite o nome):
exemplo_banco.json

Após isso, escolha a quantidade de registros e como você quer salvar o arquivo.


Importar estrutura de tabela SQLite:

Você precisa de um banco SQLite ".db".
Digite o caminho do arquivo completo, exemplo:

(caso seu arquivo não esteja na mesma pasta):
C:\Users\SeuUsuario\Documents\Python\exemplo_banco.db

(caso seu arquivo esteja na mesma pasta, apenas digite o nome):
exemplo_banco.db

Após isso, escolha a quantidade de registros e como você quer salvar o arquivo.
```

> [!CAUTION]
> Tenha em mente que este projeto ainda está em um estágio inicial! Ele pode apresentar falhas em diversos aspectos, portanto, faça um backup do seu banco de dados se possível antes de utilizá-lo!