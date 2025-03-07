# Tournement manager

Este é um aplicativo Flask simples que fornece uma API para obter informações sobre jogos e rankings. O aplicativo é documentado usando Swagger para facilitar a compreensão e interação com as APIs.

## Pré-requisitos

Certifique-se de ter o Python instalado no seu sistema. Além disso, instale as dependências necessárias executando o seguinte comando:

```bash
pip install tabula-py==2.9.0 pandas 
```

- Java: [version "1.8.0_202"](https://www.oracle.com/br/java/technologies/javase/javase8-archive-downloads.html)

Para API:

```bash
pip install flask flask_cors flasgger fuzzywuzzy python-Levenshtein colorama
```

## Executando o Aplicativo

Caso queira gerar/atualizar os dados vá para a seção runners.

Para iniciar a api, execute o seguinte comando:

```bash
python api.py
```

O aplicativo será iniciado e estará disponível em `http://localhost:5001`.

## Endpoints

- A documentação Swagger pode ser acessada em `http://localhost:5001/apidocs` após iniciar o aplicativo.

## Notas Adicionais

- Certifique-se de ter os arquivos CSV necessários no diretório `files/` para que o aplicativo funcione corretamente.


## Runners

### update.py

```bash
python update.py
```

- Opção Z: Rodar quando for inicio de competição, com a definição dos grupos pronta no boletim

Ele irá identificar as páginas de cada modalidade e suas respectivas series, 
caso ocorra algum erro você pode apagar o arquivo files/futsal_series_info.json que ele gerará um novo de acordo com o arquivo files/Boletim.pdf 


- Opção G:

Rodar para atualizar os dados da fase de grupos, como jogos, atualização e listagem de confronto direto.

Ele irá identificar as páginas de cada modalidade e suas respectivas series através do arquivo files/futsal_series_info.json caso ocorra algum erro você pode apagar o arquivo files/futsal_series_info.json que ele gerará um novo de acordo com o arquivo files/Boletim.pdf 



## Arquivos relevantes

### fixes.py

Para corrigir algum dado que foi gerado incorreto deverá ser incluído no dict correction_teams para nome de atléticas
e no dict correction_local para locais de jogos, caso o local não esteja na lista de locations

-------------

TODO

- [X] Separar em runners
- [X] Funcionar zero.py
- [X] Funcionar group.py
- [ ] Funcionar playoff.py

- [ ] Pular uma modalidade caso encontre um erro