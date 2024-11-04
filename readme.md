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
pip install flask flask_cors flasgger
```

## Executando o Aplicativo

Caso queira gerar os dados, execute o seguinte comando:
(Será gerado apenas os dados do futsal masculino serie A)

```bash
python ndu.py
```

Para iniciar a api, execute o seguinte comando:

```bash
python api.py
```

O aplicativo será iniciado e estará disponível em `http://localhost:5001`.

## Endpoints

- A documentação Swagger pode ser acessada em `http://localhost:5001/apidocs` após iniciar o aplicativo.

## Notas Adicionais

- Certifique-se de ter os arquivos CSV necessários no diretório `files/` para que o aplicativo funcione corretamente.