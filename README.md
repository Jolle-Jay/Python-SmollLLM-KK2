Välkommen till mitt Orakel.

Först av allt.

1. Installera UV skriv pip install uv i terminalen
Installerar uv som är en package manager som pip men snabbare.

2. Klona detta repot kör git clone 

3. I Terminalen kör uv sync
Då kommer alla dependencies från pyproject.toml att installeras av sig själv och en .venv kommer att skapas

4. uv run uvicorn app.main:app --reload
För att starta upp det du kommer få en http adress.

För att starta det med swagger skriv /docs i slutet klistra in i webbläsare och kör, du kommer att komma till en enkel hemsida där du kan gå igenom alla endpointsen samt ladda upp csv dokument.

5. Mina curl exempel
curl http://localhost:8000/health - Kollar om Endpointen fungerar och får 200

curl -X POST http://localhost:8000/data/upload \ -F "file=@dataset.csv"   
Låter dig ladda upp en CSV fil och låter dig se innehållet

curl http://localhost:8000/data/stats - Bryter ner datasetet och ger ut en dictionary av det

curl -X POST http://localhost:8000/ai/ask \ -H "Content-Type: application/json" \ -d '{"question": "Type question here"}'
  
  Låter dig fråga SMOLLLM om det finns ett CSV uppladdat
