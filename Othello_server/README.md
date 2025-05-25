# Othello_server
Othello Game Coordinator for a 1v1 tournament

### Disclaimer
El contenido de este repositorio se encuentra en constante desarrollo, por lo que se recomienda hacer pulls requests constantes para mantenerlo al día.

## Instalación

Luego de clonar el repositorio, 

- Abra una terminal y dirigase a la carpeta `Othelo_server` 
- corra el siguiente comando:

```bash
pip install -r requirements.txt 
```
Este comando busca instalar las dependencias del código especificadas en el archivo `requirements.txt`. Es posible que necesite instalar algunas otras librerías dependiendo de su distribución local de Python, por lo que necesitará resolver esas dependencias antes de proseguir.  

## Uso

El servidor de torneos de othello consta de 2 partes: 

- Backend:
  - Maneja la lógica del juego
  - Construido sobre FastAPI 
  - Toda comunicacioón con este modulo es por medio de POST request. 

- Frontend:
  - Interfaz visual para el monitoreo del estado del torneo 
  - Construido sobre Streamlit

### Backend 

Para correr el backend: 

- Abra una terminal y dirigase a la carpeta `Othelo_server > api`  (asegurese que se encuentra en la carpeta que contiene el archivo `main.py`)
- corra el siguiente comando:

```bash
uvicorn main:app --reload --host 0.0.0.0
```
Debería ver algo similar a esto en su consola: 

![Captura de Pantalla 2024-05-24 a la(s) 22.42.47.png](..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fvar%2Ffolders%2Frl%2Fm1h3n2216rj8tsy10_f09lqm0000gn%2FT%2FTemporaryItems%2FNSIRD_screencaptureui_qcbKSx%2FCaptura%20de%20Pantalla%202024-05-24%20a%20la%28s%29%2022.42.47.png)

En esta consola podrá monitorear el tráfico de consultas que le lleguen a su API. 

Para verificar que todo este funcionando bien, pueden ingresar el siguiente link  en su navegador: 

```http request
http://localhost:8000/root
```

Si ve en su pantalla el mensaje "Contemplating existence. Also, kind of active". Todo está bien 👍

### Frontend 

Para correr el frontend: 

- Abra una terminal y dirigase a la carpeta `Othelo_server > app`  (asegurese que se encuentra en la carpeta que contiene el archivo `streamlit_app.py`)
- corra el siguiente comando:

```bash
streamlit run streamlit_app.py
```
Debería ver algo similar a esto en su consola: 

![Captura de Pantalla 2024-05-24 a la(s) 22.47.51.png](..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fvar%2Ffolders%2Frl%2Fm1h3n2216rj8tsy10_f09lqm0000gn%2FT%2FTemporaryItems%2FNSIRD_screencaptureui_np78tH%2FCaptura%20de%20Pantalla%202024-05-24%20a%20la%28s%29%2022.47.51.png)

En esta consola podrá monitorear el estado de la app. 

Para verificar que todo este funcionando bien, pueden ingresar el siguiente link  en su navegador: 

```http request
http://localhost:8501
```

Eso debería habilitarle la interfaz de manejo del torneo de Othello. 

## Uso de torneo

![Captura de Pantalla 2024-05-24 a la(s) 22.52.22.png](..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fvar%2Ffolders%2Frl%2Fm1h3n2216rj8tsy10_f09lqm0000gn%2FT%2FTemporaryItems%2FNSIRD_screencaptureui_EgX6Zx%2FCaptura%20de%20Pantalla%202024-05-24%20a%20la%28s%29%2022.52.22.png)

#### Crear un nuevo torneo:

1. Ingrese un nombre unico para el torneo
2. Presione el boton **Start Game**

#### Crear usuarios: 

1. En su archivo othello_client.py asegurese que la variable host_name tenga el valor del localhost:8000 
```python
host_name = 'http://localhost:8000'
```
2. Abra una terminal y dirijase a la carpeta donde se encuentre el archivo `othello_client.py` y corra el siguiente commando: 
```bash
python othello_client.py SESSION_NAME USER_NAME
```
Donde, 

`SESSION_NAME` = Nombre del torneo que acaba de crear

`USER_NAME` = Nombre del usuario en el torneo 

3. Verifique la creación del nuevo jugador precionando el boton **Refresh** de la tabla de clasificación 

4. Cuando ya este listo para empezar el torneo (todos los jugadores ingresaron), presione el boton **Pair**. Esto empezará una ronda del torneo que podrá monitorear al presionar el botón Refresh de la tabla de Matches.  

## Archivos relevantes 

`Othello_server/api/othello_game.py` : contiene toda la lógica detras del juego de othello. Manejo de tablero, movimientos validos, puntuaciones, etc. 

`Othello_server/api/main.py` : maneja la lógica del torneo. Registros, turnos, resultados. 

`Othello_server/app/streamlit_app.py` : interfaz grafica del torneo. 

## License

[MIT](https://choosealicense.com/licenses/mit/)

