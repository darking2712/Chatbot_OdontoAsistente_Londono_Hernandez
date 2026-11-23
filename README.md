# OdontoAsistente

Chatbot de reservas para un consultorio odontológico **ficticio** (Armenia, Quindío). Una persona conversa en español; el sistema interpreta lo que pide, valida las reglas del negocio y guarda las reservas en SQLite.

- **Curso:** Electiva II (EAM-2026II) · Segundo corte y, desde la clase 11–13, tercer corte (canal de Telegram)
- **Integrante:** Kevin Londoño Hernandez (trabajo individual)
- **Repositorio:** https://github.com/darking2712/Odontoasistente
- **Bot de Telegram:** [@odontoasistente_hernandez_bot](https://t.me/odontoasistente_hernandez_bot)

> Todos los datos (consultorio, dirección, clientes y reservas) son ficticios. No ingreses información personal real.

## Qué hace

- Informa servicios, precios, duración, horarios y ubicación.
- Consulta las horas libres para un servicio y una fecha.
- Crea, consulta, modifica y cancela reservas, siempre con una confirmación explícita antes de guardar.
- Rechaza las reservas que se cruzan con otra activa, que caen fuera del horario o en una fecha pasada.

Hay dos canales:

| Canal | Qué permite |
|---|---|
| **Gradio** (web) | Todo lo anterior: consultas y crear, modificar y cancelar reservas con confirmación. |
| **Telegram** (`bot_telegram.py`) | Consultas y también crear, modificar y cancelar: el bot presenta un resumen con una referencia de solicitud y botones **Confirmar** / **Descartar**. La API (rutas `/telegram`) comprueba la propiedad de la reserva, la disponibilidad y el estado actual antes de aplicar el cambio. |

**Límites:** no diagnostica, no recomienda tratamientos y no procesa pagos.

## Cómo está construido

```
Persona ──► Gradio (app_gradio.py)  ──┐
Persona ──► Telegram (bot_telegram.py) ┤  (solo consultas)
                                       │
                ┌──────────────────────┘
                ▼
        Python + Groq (chatbot_memoria.py, consulta_llm.py)
        interpreta el mensaje y devuelve un plan en JSON
                │  HTTP
                ▼
        FastAPI (main.py): reglas del negocio
                │
                ▼
        SQLite (almacen_sqlite.py → reservas.db)
```

| Herramienta | Para qué se usa |
|---|---|
| Gradio | Pantalla del chat y botones Confirmar / Descartar / Reiniciar |
| `python-telegram-bot` (v22) | Canal de Telegram: recibe los mensajes y responde en el mismo chat. Usa *long polling* |
| Groq (modelo de lenguaje) | Interpretar el mensaje: acción, servicio, fecha, hora, cliente y código |
| FastAPI | Ejecutar las operaciones del negocio y validar los datos |
| SQLite | Guardar las reservas de forma persistente |

El modelo **solo interpreta**; no puede guardar nada. Crear, modificar o cancelar exige pulsar **Confirmar operación** en Gradio o el botón **Confirmar** de Telegram. En Telegram la confirmación va ligada al resumen (identificador de solicitud, chat, usuario y vigencia de 10 minutos) y la API vuelve a validar todo: propiedad, horario, cruces y que la reserva no haya cambiado desde el resumen.

**Por qué *long polling*:** el computador del bot consulta a Telegram, así que FastAPI puede seguir en `127.0.0.1` y no hace falta una URL pública (un *webhook* sí la exigiría).

### Archivos

| Archivo | Contenido |
|---|---|
| `app_gradio.py` | Interfaz Gradio (puerto 7860) |
| `bot_telegram.py` | Canal de Telegram (clase 13): propuestas por chat, botones, `/reserva`, `/estado`, `/reintentar`, `/descartar`, `/reset` y verificación de resultados |
| `api_telegram.py` | Rutas protegidas `/telegram` y `AgendaTelegram` (propietarios de reservas y recibos de operaciones, en la misma transacción) |
| `probar_telegram.py` | Prueba automática de propiedad, cruces, resumen antiguo, repetición, recibos y escrituras superpuestas (base temporal) |
| `simular_respuesta_perdida.py` | Arranque opcional del bot para la prueba T24 (respuesta perdida controlada) |
| `chatbot_memoria.py` | Historial de la conversación y llamada a Groq por turno |
| `consulta_llm.py` | Prompt, llamada a Groq y llamadas a la API (`interpretar`, `ejecutar`) |
| `main.py` | API FastAPI (puerto 8011): servicios, disponibilidad y reservas |
| `almacen_sqlite.py` | Tabla `reservas`, transacciones y control de cruces |
| `negocio.json` | Catálogo, precios, duraciones y horarios |
| `reservas.db` | Base SQLite con reservas ficticias de prueba |
| `probar_demo.py` | Prueba automática (no toca `reservas.db`) |
| `docs/` | Bitácoras, presentación y evidencias |

Para la clase 13 se modificó `main.py` (`AgendaConsultorio` hereda de `AgendaTelegram` y se incluye el router `/telegram`) y se reemplazó `bot_telegram.py`. No se modificaron `consulta_llm.py`, `chatbot_memoria.py`, `almacen_sqlite.py` ni `app_gradio.py`; El bot ya no usa `chatbot_memoria.py` (maneja su propio historial y su propio intérprete en `bot_telegram.py`); Gradio conserva los suyos. Las reglas del negocio viven solo en la API.

Material de la versión anterior (Flowise + JSON), conservado solo para la comparación: `Demo*.json`, `puente_flowise.js`, `prompt_sistema.txt`, `reservas.json` y `main_sqlite_ejemplo.py`. **No forman parte de la versión del segundo corte.**

## Requisitos e instalación

- Python 3.10 o superior (desarrollado con Python 3.14).
- Una API key de [Groq](https://console.groq.com/).
- Para Telegram: un bot creado con [@BotFather](https://t.me/BotFather) y su token. `requirements.txt` incluye `python-telegram-bot>=22,<23`.

Desde la carpeta del repositorio (comandos para Windows PowerShell):

```powershell
git clone https://github.com/darking2712/Odontoasistente.git
cd Odontoasistente
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

En Linux o macOS usa `.venv/bin/python` en lugar de `.\.venv\Scripts\python.exe`.

## Configuración

| Variable | Obligatoria | Descripción |
|---|---|---|
| `GROQ_API_KEY` | Sí | Clave de Groq. **No la escribas en ningún archivo del repositorio.** |
| `GROQ_MODEL` | Sí | ID del modelo de Groq, por ejemplo `openai/gpt-oss-20b`. Verifica que Groq lo siga ofreciendo. |
| `CHATBOT_API_URL` | No | Dirección de FastAPI. Por defecto `http://127.0.0.1:8011`. |
| `CHATBOT_API_KEY` | Sí (API y bot de Telegram) | Clave privada compartida entre FastAPI y el bot: mínimo 16 caracteres ASCII, la misma en ambas terminales. No es el token de BotFather ni la clave de Groq. Sin ella la API **no inicia**. |
| `TELEGRAM_BOT_TOKEN` | Solo para el bot de Telegram | Token entregado por BotFather. Si no está definida, `bot_telegram.py` lo pide por teclado y no lo muestra (`getpass`). **No lo escribas en ningún archivo del repositorio ni lo muestres en capturas.** |

Se definen en la terminal donde se inicia Gradio o el bot de Telegram y solo duran esa sesión:

```powershell
$env:GROQ_API_KEY = "pega-aqui-tu-clave"
$env:GROQ_MODEL = "openai/gpt-oss-20b"
$env:CHATBOT_API_URL = "http://127.0.0.1:8011"
$env:TELEGRAM_BOT_TOKEN = "pega-aqui-el-token-de-botfather"
```

## Datos y ejecución

`reservas.db` se crea sola si no existe (tabla `reservas`). El repositorio incluye una con reservas ficticias de prueba.

Para importar el histórico de la versión JSON (opcional):

```powershell
.\.venv\Scripts\python.exe almacen_sqlite.py --migrar reservas.json
```

Se usan **hasta tres terminales**, todas desde la carpeta del proyecto: la API (obligatoria), Gradio (opcional si solo pruebas Telegram) y el bot de Telegram (opcional si solo pruebas Gradio).

**Terminal 1: API.** Debe ejecutarse con un solo proceso.

```powershell
$claveApiEquipo = Read-Host "Clave privada de la API del equipo" -AsSecureString
$env:CHATBOT_API_KEY = [System.Net.NetworkCredential]::new('', $claveApiEquipo).Password
.\.venv\Scripts\python.exe -m uvicorn main:app --port 8011
```

**Terminal 2: interfaz.**

```powershell
$env:GROQ_API_KEY = "pega-aqui-tu-clave"
$env:GROQ_MODEL = "openai/gpt-oss-20b"
$env:CHATBOT_API_URL = "http://127.0.0.1:8011"
.\.venv\Scripts\python.exe app_gradio.py
```

**Terminal 3: bot de Telegram.** Usa las mismas variables de Groq y la dirección de la API.

```powershell
$env:TELEGRAM_BOT_TOKEN = "pega-aqui-el-token-de-botfather"
$env:CHATBOT_API_KEY = "la-misma-clave-privada-de-la-api"
$env:GROQ_API_KEY = "pega-aqui-tu-clave"
$env:GROQ_MODEL = "openai/gpt-oss-20b"
$env:CHATBOT_API_URL = "http://127.0.0.1:8011"
.\.venv\Scripts\python.exe bot_telegram.py
```

Si `TELEGRAM_BOT_TOKEN` o `CHATBOT_API_KEY` no están definidas, el bot las pide por teclado sin mostrarlas. Debe haber un solo proceso de polling por token. Para la prueba T24 se inicia `simular_respuesta_perdida.py` en lugar de `bot_telegram.py`.

Debe aparecer `Bot en ejecución.` y el proceso tiene que seguir encendido mientras se usa el bot (Ctrl+C lo detiene). Si faltan `GROQ_API_KEY` o `GROQ_MODEL`, los comandos `/start`, `/help` y `/reset` funcionan, pero las consultas no.

Direcciones:

- Interfaz del chat: http://127.0.0.1:7860
- Documentación interactiva de la API: http://127.0.0.1:8011/docs (las rutas `/telegram` exigen `X-API-Key` y `X-Telegram-User`)
- Bot de Telegram: https://t.me/usuario_del_bot

## Comprobación

**1. Prueba automática** (no necesita Groq ni internet; usa una base temporal):

```powershell
.\.venv\Scripts\python.exe probar_demo.py
```

Resultado esperado: una línea `[OK]` por cada comprobación y, al final,

```
OK: validaciones, concurrencia, persistencia, cruces, modificación, cancelación, chat y errores.
```

**1b. Prueba automática del canal de Telegram** (base temporal, sin Groq ni Telegram):

```powershell
.\.venv\Scripts\python.exe probar_telegram.py
```

Debe terminar con `OK: propiedad, cruces, referencia de resumen, repetición, recibos y escrituras superpuestas.` No reemplaza las pruebas con dos cuentas reales (ver `docs/Matriz_25_Pruebas.md`).

**2. Prueba manual** con las dos terminales encendidas. En http://127.0.0.1:7860 escribe, con una fecha futura que sea día hábil:

> Quiero una valoración el AAAA-MM-DD a las 09:00 a nombre de Laura

El chat debe mostrar un resumen con el precio. Pulsa **Confirmar operación**: responde con un código de 8 caracteres. Compruébalo en http://127.0.0.1:8011/docs (`GET /reservas/{codigo}`).

**3. Prueba manual del bot de Telegram** con la API (terminal 1) y el bot (terminal 3) encendidos. Comandos: `/start`, `/help`, `/reserva CODIGO`, `/estado [REFERENCIA]`, `/reintentar`, `/descartar`, `/reset`. Para reservar, escribe por ejemplo `Quiero una limpieza el AAAA-MM-DD a las 10:00 a nombre de Laura`: aparece el resumen con **Confirmar** / **Descartar**. Comprueba además:

| Qué enviar | Resultado esperado |
|---|---|
| `/start` | Bienvenida de OdontoAsistente con el aviso de que no da diagnósticos |
| `/help` | Comandos, ejemplos, servicios y horario |
| `¿Qué servicios ofrecen y cuánto cuestan?` | Los cinco servicios con precio en COP, duración y ubicación |
| `¿Qué horas hay para una limpieza el 2026-11-03?` | Los horarios libres; deben coincidir con `GET /disponibilidad?fecha=2026-11-03&servicio=limpieza` en `/docs` |
| `Quiero una limpieza` y luego `2026-11-03` | Primero pide la fecha ("Necesito: fecha") y luego entrega las horas: el dato pendiente se completa en otro mensaje |
| `/start` en medio de una consulta | Muestra la bienvenida y **no** pierde el historial |
| `/reset` y luego solo `2026-11-03` | Reinicia el contexto: el bot vuelve a pedir el servicio |
| `/hola` | "Comando no disponible. Usa /help para ver las opciones." |
| Una foto | Pide un mensaje de texto |
| Detener FastAPI y repetir la consulta | "No pude completar la conexión. Intenta la consulta más tarde." Al encenderla otra vez, la misma consulta funciona |

Las escrituras (crear, modificar, cancelar) solo se ejecutan al pulsar **Confirmar** en el resumen vigente; un botón de un resumen anterior, un resumen vencido (10 min) o una pulsación repetida no crean otra operación.

### Errores frecuentes

| Mensaje | Causa y solución |
|---|---|
| `Configura GROQ_API_KEY y GROQ_MODEL e inicia de nuevo.` | Faltan las variables en la terminal 2. Defínelas y reinicia `app_gradio.py`. |
| `No pude conectar con Groq o FastAPI.` | La API no está encendida (terminal 1), el puerto o `CHATBOT_API_URL` no coinciden, o no hay internet. |
| `Error HTTP 401` o `403` | Clave de Groq incorrecta o bloqueada. |
| `Error HTTP 404` al interpretar | El modelo de `GROQ_MODEL` ya no existe en Groq. Cambia el ID. |
| `Error HTTP 409` al confirmar | Esa hora se ocupó después del resumen. Pide otra hora. |
| `Error HTTP 422` | Datos inválidos: fecha pasada, día cerrado, hora fuera del horario o del paso de 30 min. |
| `Error HTTP 503` | La API no pudo acceder a SQLite. Revisa que `reservas.db` no esté bloqueada por otro programa y reintenta. |
| `Address already in use` | El puerto 8011 o 7860 está ocupado. Cierra el otro proceso o cambia el puerto. |

Errores del bot de Telegram:

| Mensaje o síntoma | Causa y solución |
|---|---|
| `Token inválido. Comprueba la credencial entregada por BotFather.` (en la terminal) | `TELEGRAM_BOT_TOKEN` está mal copiado o fue revocado. Genera o copia de nuevo el token en BotFather. |
| `No fue posible iniciar la conexión con Telegram.` (en la terminal) | No hay internet o Telegram no es alcanzable. Revisa la conexión y vuelve a iniciar. |
| El bot no responde ni a `/start` | El proceso del bot no está encendido. Inicia `bot_telegram.py`: Telegram conserva los mensajes pendientes y el bot los recibe al reconectarse. |
| `Falta configurar GROQ_API_KEY o GROQ_MODEL en el servidor del bot.` | Faltan las variables de Groq en la terminal 3. Defínelas y reinicia el bot. |
| `No pude completar la conexión. Intenta la consulta más tarde.` | FastAPI está apagada, el puerto o `CHATBOT_API_URL` no coinciden, o falló Groq o internet. `/start` y `/help` siguen funcionando porque no usan la API. |
| `El servicio rechazó la consulta. Revisa la configuración o los datos.` | La API o Groq respondieron con un error HTTP (clave o modelo incorrectos, datos inválidos). |
| `La respuesta del servicio no tiene el formato esperado.` | La respuesta no coincide con lo que `formatear_resultado()` espera (`nombre`, `precio_cop`, `duracion_minutos`, `horarios`). La clase del error queda en la terminal del bot. |

## Reglas del negocio

- Lunes a viernes 08:00–18:00; sábado 08:00–13:00; domingo cerrado.
- Una persona atendida a la vez (capacidad 1). Las horas se ofrecen en pasos de 30 minutos.
- La atención debe terminar dentro del horario. Duraciones: valoración 30 min, limpieza 45, blanqueamiento 60, ortodoncia 30, extracción 45.
- Dos reservas activas no pueden cruzarse. Un intervalo que empieza justo cuando termina otro sí es válido.
- Cancelar libera el horario y conserva la fila con estado `cancelada`.
- La comprobación del horario y el guardado ocurren en la misma transacción de SQLite.

### Endpoints de la API

| Método y ruta | Operación |
|---|---|
| `GET /servicios` | Catálogo, precios y horarios |
| `GET /disponibilidad?fecha=AAAA-MM-DD&servicio=clave` | Horas libres |
| `GET /reservas` | Lista las reservas |
| `POST /reservas` | Crea (requiere `confirmado: true`) |
| `GET /reservas/{codigo}` | Consulta |
| `PUT /reservas/{codigo}` | Modifica servicio, fecha y hora (requiere `confirmado: true`) |
| `DELETE /reservas/{codigo}?confirmado=true` | Cancela |
| `POST /chat` | Puente de la versión Flowise; Gradio no lo usa |

## Limitaciones conocidas

- Solo las rutas `/telegram` exigen `X-API-Key`. Las rutas anteriores (`/reservas`, `/chat`, etc.) siguen sin autenticación y **permiten listar, modificar o cancelar cualquier reserva** sin pasar por la propiedad de Telegram: la API es solo para uso local; no la publiques en internet.
- Las reservas creadas por Gradio o por rutas anteriores no tienen propietario de Telegram: no se pueden consultar ni cambiar desde el bot.
- El historial y la solicitud pendiente de Gradio viven en memoria de esa pestaña: al recargar la página se pierden. Las reservas guardadas no.
- El modelo puede interpretar mal un mensaje ambiguo. Por eso la fecha se pide en formato AAAA-MM-DD y nada se guarda sin confirmar.
- La tabla guarda la duración de cada reserva, no el precio: el precio se toma del catálogo actual (`negocio.json`).
- Solo se atiende a una persona a la vez; el código no soporta varios profesionales.
- **Telegram:** el historial y la propuesta pendiente de cada chat viven en la memoria del proceso del bot: se pierden al reiniciarlo. Las reservas y los recibos de operaciones permanecen en la base; la referencia de solicitud permite recuperar el recibo con `/estado REFERENCIA`. El bot solo atiende chats privados, no grupos, y solo recibe texto.
- **Telegram:** el bot funciona mientras el proceso esté encendido en el computador que lo ejecuta. Si la API o Groq fallan, el mensaje de "No pude completar la conexión" puede venir de cualquiera de los dos.

## Documentación

Segundo corte:

- [Bitácora del segundo corte](docs/Bitacora_Segundo_Corte.md)
- [Presentación en PDF](docs/Presentacion_Segundo_Corte.pdf)

Tercer corte (clase 13, operaciones de Telegram y pruebas finales):

- [Bitácora de la clase 13](docs/C13_Telegram_Operaciones.md)
- [Matriz de 25 pruebas](docs/Matriz_25_Pruebas.md)

Evidencias de ambos cortes: [docs/evidencias/](docs/evidencias/)
