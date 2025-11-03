# E-Shop Brasil — Aplicação Prática (MongoDB + Streamlit + Docker)

## Descrição
Aplicação para gestão e análise de dados da E-Shop Brasil, integrando **MongoDB**, **Streamlit** e **Docker**.  
Permite inserção, consulta, transformação e visualização de dados.

## Tecnologias
- Docker / Docker Compose
- MongoDB
- Streamlit (Python)
- PyMongo, Pandas, Plotly, Faker

## Como executar
1. Clonar este repositório
2. No terminal, executar:
   ```bash
   docker-compose up --build
   ```
3. Acessar no navegador: [http://localhost:8501](http://localhost:8501)

Para popular o banco de dados:
```bash
docker-compose exec app python populate_db.py
```

## Funcionalidades
- Inserção manual de dados
- Consulta por nome/e-mail
- Concatenação de campos (transformação)
- Visualização interativa com gráficos
- Popular banco com dados falsos

## Estrutura
```
├── Dockerfile
├── docker-compose.yml
├── app.py
├── utils.py
├── populate_db.py
├── requirements.txt
└── README.md
```

## Autor
Vivian Duarte
Link do YOUTUBE de apresentação do projeto https://youtu.be/aOm0hc_2PsI
