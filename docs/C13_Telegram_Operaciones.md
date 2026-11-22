# Bitácora clase 13. Operaciones de Telegram y pruebas finales

**Integrante:** Kevin Londoño Hernandez · **Repositorio:** https://github.com/darking2712/Chatbot_OdontoAsistente_Londono_Hernandez

## 1. Qué añadió el canal

| Pieza | Archivo | Qué hace |
|---|---|---|
| Propuestas y botones | `bot_telegram.py` | Interpreta el mensaje (Groq), prepara un resumen con referencia de solicitud y botones Confirmar / Descartar. Estado por chat en memoria, vigencia de 10 min. |
| Cliente de la API | `bot_telegram.py` (`ClienteAPI`) | Envía `X-API-Key` (servicio) y `X-Telegram-User` (quién actúa). |
| Rutas protegidas | `api_telegram.py` (`crear_router`) | `/telegram/servicios`, `/disponibilidad`, `/reservas/{codigo}`, `/operaciones`, `/operaciones/{id}`. |
| Propiedad y recibos | `api_telegram.py` (`AgendaTelegram`) | Tablas `propietarios_telegram` y `operaciones_telegram`, escritas en la misma transacción que la reserva. |
| Reglas del consultorio | `main.py` (`AgendaConsultorio(AgendaTelegram)`) | Horario por día, no reservar horas pasadas, cruces (capacidad 1). Las reutilizan Gradio, `/reservas` y Telegram. |

## 2. Dónde se valida cada operación

| Comprobación | Dónde |
|---|---|
| Que lo confirme el mismo chat y usuario, con el identificador vigente, sin vencer ni estar en proceso | `bot_telegram.py`: `motivo_rechazo()` |
| Clave del servicio (401) e identidad del usuario | `api_telegram.py`: `autenticar()` / `identidad()` |
| Propiedad de la reserva (404 si no es suya) | `AgendaTelegram._propia()` |
| Reserva sin cambios desde el resumen (409) | `operar()`: compara `huella(actual)` con `referencia` |
| Fecha, horario, paso de 30 min, cruce con otra reserva activa | `AgendaConsultorio.validar_intervalo()` y `AgendaSQLite.ocupado()` dentro de `BEGIN IMMEDIATE` |
| Reenvío de la misma confirmación | `operar()`: mismo `solicitud_id` y misma huella devuelve el recibo guardado; otros datos dan 409 |

## 3. Adaptaciones al proyecto

- `AgendaConsultorio` pasó de heredar de `AgendaSQLite` a `AgendaTelegram` (que hereda de `AgendaSQLite`); las reglas propias no cambiaron.
- `bot_telegram.py` del paquete traía el negocio del ejemplo («Salón Aurora», claves `precio`): se cambió a OdontoAsistente (bienvenida, ayuda, claves de servicio `valoracion`…`extraccion`, `precio_cop`, formato de COP, normalización de servicio/código y extracción robusta del JSON del modelo).
- `probar_demo.py` define una clave de práctica para poder importar `main` (que ahora exige `CHATBOT_API_KEY`).
- Se añadió `probar_telegram.py` (prueba automática de las reglas del canal sobre una base temporal).

## 4. Cómo se comprobaron los resultados

- **Automático:** `probar_demo.py` y `probar_telegram.py` (base temporal; no tocan `reservas.db`). Ambas pasan; las salidas están en `salida_probar_demo.txt` y `salida_probar_telegram.txt`.
- **Manual con dos cuentas:** ver `Matriz_25_Pruebas.md`. Cada escritura se contrasta en `/docs` (`GET /reservas/{codigo}`) o en SQLite.
- Escrituras concurrentes: `probar_telegram.py` sección 8 lanza 8 hilos sobre el mismo horario. El bot procesa los mensajes en secuencia, así que dos chats de Telegram no la demuestran por sí solos.

## 5. Correcciones registradas

Detalle en «Registro de fallos y correcciones» de `Matriz_25_Pruebas.md`.

- **T01:** el modelo clasificaba mal la consulta de servicios. Se amplió el prompt y se fijó `temperature: 0`.
- **T07:** el modelo inventó la fecha. `sanear_plan` descarta fecha, hora y cliente que la persona no mencionó.
- **T05:** no usaba el código conocido. `resolver_codigo` lo toma si hay uno solo e ignora los inventados.
- **Aviso intermitente de formato (T03, T19):** causa no determinada. Se agregó el registro de WARNING y el desempaquetado de `{"plan":…}`.

## 6. Resultado de las pruebas

Los 25 casos se ejecutaron con dos cuentas reales de Telegram (cuenta 1 original y cuenta 2 en Unigram). T11, T14 y T22 quedan como parciales; los motivos están en la matriz. T24 se probó dos veces con `simular_respuesta_perdida.py`: la API guardó la reserva, se ocultó una sola respuesta al bot, `/reset` se negó hasta verificar y `/estado` recuperó el recibo sin duplicar la reserva.

## 7. Limitaciones

- Las rutas anteriores (`/reservas`, `/chat`) siguen sin autenticación y permiten listar, modificar o cancelar cualquier reserva sin pasar por la propiedad de Telegram. Solo uso local.
- Las reservas creadas antes (Gradio, `reservas.db` actual) no tienen propietario de Telegram: no se pueden consultar ni cambiar desde el bot.
- Historial y propuestas del bot viven en memoria; los recibos y reservas, en SQLite.
- T22 no se demostró con dos chats de Telegram: se usó `POST /reservas` directo y la prueba automática de 8 hilos.
- El aviso intermitente de formato (T03, T19) quedó sin causa confirmada.
- No se ejecutaron el vencimiento de 10 minutos ni la recuperación de recibo tras reiniciar el bot.
