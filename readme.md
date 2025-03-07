# Tournement manager

Este é um aplicativo Flask simples que fornece uma API para obter informações sobre jogos e rankings. O aplicativo é documentado usando Swagger para facilitar a compreensão e interação com as APIs.

## Pré-requisitos

Certifique-se de ter o Python instalado no seu sistema. Além disso, instale as dependências necessárias executando o seguinte comando:

```bash
pip install tabula-py==2.9.0 pandas flask flask_cors flasgger fuzzywuzzy python-Levenshtein colorama
```

- Java: [version "1.8.0_202"](https://www.oracle.com/br/java/technologies/javase/javase8-archive-downloads.html)

- Salvar o boletim que deseja utilizar os dados na pasta `files` com nome `Boletim.pdf`

## Executando a API
Para iniciar a API, execute:

```bash
python api.py
```
A API estará disponível em http://localhost:5001.

Acesse a documentação Swagger em http://localhost:5001/apidocs.

## 📊 Atualização de Dados

Para gerar ou atualizar dados, use o script `update.py`:

```bash
python update.py
```

**Opções de Atualização**

| Opção | Descrição | Uso |
|-------|-----------|-----|
| G | Atualiza dados da fase de grupos | Para atualizar jogos, rankings e confrontos diretos |
| R | Atualiza ranking de uma modalidade específica | Quando precisar atualizar apenas uma modalidade |
| J | Atualiza jogos de todas as modalidades | Para atualização rápida de resultados |
| P | Atualiza dados dos playoffs (Beta) | Para fases eliminatórias |
| Z | Inicializa dados para nova competição | No início de um novo torneio |

<details>
<summary>Clique para ver mais detalhes sobre as opções</summary>

- **Opção G**: 
  *Rodar para atualizar os dados da fase de grupos, como jogos, atualização e listagem de confronto direto.* 
  Ele irá identificar as páginas de cada modalidade e suas respectivas séries através do arquivo `files/futsal_series_info.json`. 
  Caso ocorra algum erro, você pode apagar o arquivo `files/futsal_series_info.json` que ele gerará um novo de acordo com o arquivo `files/Boletim.pdf`.

- **Opção R**: 
  *Rodar para atualizar o ranking de uma modalidade específica. *
  Ele solicitará que você informe a modalidade (ex: FM/A) e atualizará o ranking para essa modalidade específica com base nos jogos registrados no Boletim.

- **Opção J**: 
  *Rodar para atualizar apenas os jogos de todas as modalidades. *
  Ele percorrerá todas as modalidades definidas em `files/futsal_series_info.json` e atualizará as informações dos jogos, sem modificar rankings ou dados de confronto direto.

- **Opção P** (Versão Beta): 
  *Rodar para atualizar os dados dos playoffs de todas as modalidades. *
  Ele processará as informações de playoff para todas as modalidades definidas em `files/futsal_series_info.json`. 
  Caso haja necessidade de atualizar uma modalidade específica, é possível descomentar o código relevante na função `update_playoff()`.

- **Opção Z**: 
  *Rodar quando for início de competição, com a definição dos grupos pronta no boletim. *
  Ele irá identificar as páginas de cada modalidade e suas respectivas séries. 
  Caso ocorra algum erro, você pode apagar o arquivo `files/futsal_series_info.json` que ele gerará um novo de acordo com o arquivo `files/Boletim.pdf`.

</details>