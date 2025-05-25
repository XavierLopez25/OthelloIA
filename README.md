# OthelloIA

# Guía de como levantar el juego de Othello

## Versión Vieja:

### Setup Inicial

> **No es necesario.**

### Levantar todo

#### Consola 1 (API):

- Correrlo en `Othello_server/api`

```bash

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

```

#### Consola 2 (UI Server):

- Correrlo en `Othello_server/app`

```bash

streamlit run .\streamlit_app.py

```

> **Nota**: Para iniciar un juego primero deberás ingresar el nombre de la sala y presionar ENTER.

#### Jugador 1:

- Correrlo en `OthelloClient/othello_client`

```bash

python .\othello_player_RAI.py <NOMBRE_TORNEO> RandomMovements

```

> **Nota**: .\othello_player.py hace movimentos randoms, pero válidos.

#### Jugador 2:

- Correrlo en `OthelloClient/othello_client`

```bash

python .\othello_player.py <NOMBRE_TORNEO> Minimax

```

> **Nota**: .\othello_player_minimax.py es nuestra IA implementada por nuestro grupo.

## Versión Nueva:

### Setup Inicial

Crea un `.env` con la siguiente estructura:

```bash

MONGO_CONNECTION:URL_PUEDE_SER_LOCAL_O_EN_ATLAS

```

Crea una `DB` en MongoDB llamada: `othello_tournament_db`

Luego crea las colecciones llamadas: `tournaments`, `boards`, `leaderboard`

### Levantar todo

#### Consola 1 (API):

- Correrlo en `Tournament/uvg-othello-server`

```bash

uvicorn main:app --reload

```

#### Consola 2 (UI Server):

- Correrlo en `Tournament/uvg-othello-server/frontend`

```bash

streamlit run .\app.py

```

> **Nota**: Para iniciar un juego primero deberás ingresar el nombre de la sala y presionar ENTER.

#### Jugador 1:

- Correrlo en `Tournament/uvg-othello-client`

```bash

python .\othello_player.py <NOMBRE_TORNEO> RandomMovements

```

> **Nota**: .\othello_player.py hace movimentos randoms, pero válidos.

#### Jugador 2:

- Correrlo en `Tournament/uvg-othello-client`

```bash

python .\othello_player_minimax.py <NOMBRE_TORNEO> Minimax

```

> **Nota**: .\othello_player_minimax.py es nuestra IA implementada por nuestro grupo.
