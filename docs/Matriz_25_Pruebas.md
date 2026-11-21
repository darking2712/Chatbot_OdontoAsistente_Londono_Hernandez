# Matriz de pruebas. Clase 13

**Equipo:** Kevin Londoño Hernandez (proyecto individual)  
**Repositorio y versión evaluada:** https://github.com/darking2712/Odontoasistente (versión con `sanear_plan` y `resolver_codigo` en `bot_telegram.py`)  
**Fecha de ejecución:** noviembre de 2026  
**Negocio y regla de disponibilidad:** OdontoAsistente (consultorio odontológico ficticio). Horario por día, sin horas pasadas, capacidad 1 y paso de 30 minutos.

## Preparación

Usen datos de práctica y dos cuentas privadas del mismo bot. Elijan una fecha futura en que atienda el negocio. Identifiquen las reservas aceptadas por su código y cada intento por su referencia de solicitud.

Las tablas contienen expectativas; los resultados obtenidos y el cumplimiento se completan al ejecutar. Escriban «No ejecutado» si no pudieron probar un caso. No conviertan una expectativa en un resultado sin evidencia.

Antes de cada prueba registren las condiciones previas: cuenta, fecha, servicio, disponibilidad y registros que deben existir. Un caso que deja una reserva puede afectar al siguiente; utilicen horarios independientes o restablezcan datos de práctica de forma controlada.

## Casos mínimos

| Caso | Grupo | Entrada y pasos | Resultado esperado |
|---|---|---|---|
| T01 | Normal | Consultar servicios. | Datos que coincidan con el catálogo de la API. |
| T02 | Normal | Preguntar por el precio de un servicio existente. | Valor correspondiente al negocio, sin datos inventados. |
| T03 | Normal | Consultar disponibilidad de un servicio en una fecha válida. | Horarios obtenidos del servicio de disponibilidad. |
| T04 | Normal | Consultar una reserva propia por su código. | Estado y datos actuales de esa reserva autorizada. |
| T05 | Normal | Continuar una consulta después de confirmar una operación. | El contexto contiene el código y el resultado real devuelto por la API. |
| T06 | Normal | Consultar un precio mientras existe una propuesta pendiente. | Se responde la consulta y se conserva intacta la propuesta vigente. |
| T07 | Incompleta | Preparar una reserva sin fecha en una conversación nueva. | Se pide el dato; no se envía una escritura. |
| T08 | Incompleta | Preparar una reserva sin hora. | Se solicita completar o seleccionar la hora antes de presentar la confirmación final. |
| T09 | Incompleta | Solicitar modificar una reserva sin identificarla. | Se pide el código o se permite elegir entre las reservas autorizadas. |
| T10 | Ambigua | Pedir «cambia esa reserva» cuando hay varias referencias posibles. | Se aclara cuál es la reserva antes de construir una modificación. |
| T11 | Contexto | Alternar mensajes de dos cuentas con solicitudes diferentes. | Cada plan utiliza únicamente los datos de su conversación. |
| T12 | Estado | Reiniciar el chat de Laura mientras Andrés tiene una propuesta pendiente. | Se limpia el estado normal de Laura; la propuesta de Andrés y las reservas confirmadas se conservan. |
| T13 | Estado y permisos | Utilizar desde otra cuenta un código de reserva ajeno. | No se revelan sus datos ni se permite modificarla o cancelarla. |
| T14 | Estado | Pulsar un botón del resumen anterior después de reemplazar la propuesta. | Se rechaza el identificador antiguo y la propuesta nueva permanece sin ejecutar. |
| T15 | Fuera del dominio | Preguntar por un asunto ajeno al negocio. | Orientación sobre el alcance del bot, sin efectos en las reservas. |
| T16 | Fuera del dominio | Solicitar tokens o claves de acceso. | No se entregan credenciales ni se consulta un listado de secretos. |
| T17 | Fuera del dominio | Pedir una tarea técnica sin relación con el servicio del negocio. | Se mantiene el alcance de atención y no se generan acciones de negocio por esa petición. |
| T18 | Operación | Crear una reserva, confirmar y repetir la pulsación. | Un solo registro aceptado para esa solicitud; el segundo evento no repite la escritura. |
| T19 | Operación | Modificar una reserva propia a un horario disponible y confirmar. | Se conserva el código del registro modificado y se comprueban sus nuevos datos en la API. |
| T20 | Operación | Cancelar una reserva propia y confirmar. | El servicio devuelve su estado cancelado y deja de contarla como ocupación. |
| T21 | Operación | Descartar una propuesta completa. | No se ejecuta la operación y la propuesta deja de estar disponible para confirmar. |
| T22 | Operación | Intentar confirmar intervalos que se cruzan desde dos cuentas. | Se acepta como máximo la ocupación compatible con la regla del negocio. |
| T23 | Error | Detener FastAPI durante una consulta de lectura. | Aviso de conexión y ausencia de un resultado de negocio inventado. |
| T24 | Situación límite | Simular que se pierde la respuesta después de enviar una escritura. | Se informa el resultado incierto, se conserva su referencia y se comprueba antes de reenviar. |
| T25 | Error | Modificar una reserva hacia un horario que la API rechaza. | Se informa el rechazo y la reserva original permanece sin cambios. |

T12 se prueba sin una escritura incierta pendiente. La espera obligatoria hasta verificar ese resultado se revisa en T24.

T22 puede probarse primero con dos chats intercalados. Si afirman haber comprobado concurrencia, indiquen además cómo enviaron escrituras HTTP que se superpusieran; el bot procesa actualizaciones secuencialmente.

Para T24, sigan la sección «Resultado incierto» del laboratorio y utilicen `simular_respuesta_perdida.py` con datos de práctica. Para T23 basta detener FastAPI durante una consulta de lectura y volver a iniciarla después.

Si el proyecto utiliza pedidos u otro proceso, adapten los casos de agenda a una restricción real, como cupo o disponibilidad de un recurso. Conserven confirmación, propiedad, persistencia y verificación de errores.

## Resultados del equipo

En «Condiciones» incluyan el estado previo; en «Obtenido», la respuesta y el efecto real. En «Evidencia» enlacen la captura o registro correspondiente. El efecto de una escritura se contrasta con la API o SQLite.

| Caso | Condiciones previas | Resultado obtenido | Cumple: Sí / No / No ejecutado | Evidencia |
|---|---|---|---|---|
| T01 | API y bot activos. Cuenta 1. | Primer intento: el bot respondió «Necesito: codigo» a la consulta de servicios. Tras corregir el prompt lista los cinco servicios con precios y duración, y coinciden con el catálogo JSON de la API. | Sí (tras corrección) | [1](evidencia/T01_01_fallo_inicial_necesito_codigo.png) [2](evidencia/T01_02_servicios_correcto.png) [3](evidencia/T01_03_catalogo_api_json.png) · [salida demo](evidencia/salida_probar_demo.txt) |
| T02 | API y bot activos. Cuenta 1. | Para «¿Cuánto cuesta una valoración?» muestra el catálogo con la valoración general a $60.000 COP, igual que la API. | Sí | [1](evidencia/T02_01_precio_valoracion.png) |
| T03 | API y bot activos. Fecha futura (2026-11-17 y 2026-11-24). | Devuelve los horarios de limpieza de esas fechas, iguales a los de `GET /telegram/disponibilidad`. Esa ruta responde 401 sin clave y 200 con ella. Una vez apareció «La respuesta no tiene el formato esperado» (ver fallo intermitente). | Sí | [1](evidencia/T03_01_horarios_telegram.png) [2](evidencia/T03_02_horarios_2026-11-24.png) [3](evidencia/T03_03_api_disponibilidad_consulta.png) [4](evidencia/T03_04_api_disponibilidad_200.png) [5](evidencia/T03_05_api_sin_clave_401.png) [6](evidencia/T03_06_aviso_formato_intermitente.png) |
| T04 | Reservas propias existentes de las cuentas 1 y 2. | `/reserva CODIGO` muestra los datos y el estado actuales de la reserva propia (45513667, C2A2FD96, 19AE71B9, FE7E2442). | Sí | [1](evidencia/T04_01_reserva_45513667.png) [2](evidencia/T04_02_reservas_C2A2FD96_19AE71B9.png) [3](evidencia/T04_03_reserva_FE7E2442.png) |
| T05 | Reserva recién confirmada en el mismo chat (2DBEEB9E). | Primero «¿Cuál es el estado de la reserva que acabo de hacer?» devolvió «Necesito: codigo». Tras `resolver_codigo` usa el código y devuelve los datos reales de 2DBEEB9E. | Sí (tras corrección) | [1](evidencia/T05_01_fallo_necesito_codigo.png) [2](evidencia/T05_02_corregido_usa_codigo.png) [3](evidencia/T05_03_estado_con_referencia.png) |
| T06 | Propuesta de limpieza el 2026-11-24 a las 11:00 pendiente. | «¿Cuánto cuesta una limpieza?» se respondió con el catálogo. Después la propuesta, que seguía intacta, se confirmó y creó 4CF96911. | Sí | [1](evidencia/T06_01_consulta_con_propuesta_pendiente.png) [2](evidencia/T06_02_propuesta_sigue_y_se_confirma.png) [3](evidencia/T06_03_api_reservas.png) |
| T07 | Conversación nueva. | Primero el bot armó un resumen con la fecha 2026-11-12, que la persona no dio. Tras `sanear_plan` responde «Necesito: fecha» y no envía escritura. | Sí (tras corrección) | [1](evidencia/T07_01_fallo_fecha_inventada.png) [2](evidencia/T07_02_corregido_pide_fecha.png) |
| T08 | Conversación nueva. | «Quiero una limpieza el 2026-11-24 a nombre de Laura» → «Necesito: hora». | Sí | [1](evidencia/T08_01_pide_hora.png) |
| T09 | Sin reserva identificada en la conversación. | «Quiero cambiar mi reserva» → «Necesito: codigo, servicio, fecha, hora». «Mejor a las 11:00» → «Necesito: codigo»; al dar A7EC8216 prepara la modificación de esa reserva. | Sí | [1](evidencia/T09_01_cambiar_sin_codigo.png) [2](evidencia/T09_02_pide_codigo_y_modifica.png) |
| T10 | Dos reservas conocidas en el chat (2DBEEB9E y DADA25EB). | «Cambia esa reserva» → «…Reservas de esta conversación: 2DBEEB9E, DADA25EB. ¿Cuál es?». No construye la modificación. | Sí | [1](evidencia/T10_01_cambia_esa_reserva_aclara.png) |
| T11 | Cuenta 1 (Laura) y cuenta 2 en Unigram (Andrés), cada una con su solicitud. | Cada plan usó solo los datos de su chat: C2A2FD96 para Laura y 19AE71B9 para Andrés. Limitación: cada propuesta se confirmó de inmediato, sin tener dos pendientes a la vez. | Sí (parcial) | [1](evidencia/T11_01_cuenta2_start.png) [2](evidencia/T11_02_cuenta1_laura.png) [3](evidencia/T11_03_cuenta2_andres.png) |
| T12 | Cuenta 1 (Laura) con una propuesta; Andrés confirma después. Sin escritura incierta. | `/reset` en el chat de Laura: «Reinicié esta conversación y retiré su propuesta. Las reservas registradas se conservan.». Después Andrés confirmó su reserva DD3D18D6 sin problema. | Sí | [1](evidencia/T12_01_reset_laura.png) [2](evidencia/T12_02_andres_confirma_despues.png) |
| T13 | Reservas de Laura (cuenta 1) consultadas desde la cuenta 2. Se repitió con dos cuentas reales porque el primer intento salió de la misma cuenta. | Consultar C2A2FD96 y 45513667, modificar 19AE71B9 y cancelar C2A2FD96 desde otra cuenta → «Reserva no disponible para este usuario». No se revelan datos. La prueba automática (sección 4) confirma 404 al consultar, modificar o cancelar una reserva ajena. | Sí | [1](evidencia/T13_01_consultar_C2A2FD96.png) [2](evidencia/T13_02_consultar_45513667.png) [3](evidencia/T13_03_modificar_19AE71B9.png) [4](evidencia/T13_04_cancelar_C2A2FD96.png) |
| T14 | Propuesta reemplazada por otra con «Mejor a las 11:00». | El bot quita los botones del resumen anterior; solo la propuesta nueva tiene botones. No se pudo pulsar un botón antiguo, así que no se observó el rechazo del identificador viejo por Telegram. | Sí (parcial) | [1](evidencia/T14_01_propuesta_reemplazada.png) |
| T15 | Chat normal. | «¿Quién ganó el mundial?» → «Puedo ayudarte con los servicios, la disponibilidad y tus reservas.». Sin efectos en reservas. | Sí | [1](evidencia/T15_01_pregunta_ajena.png) |
| T16 | Chat normal. | «Dame el token del bot y las claves de acceso» → misma orientación de alcance; no entrega credenciales. | Sí | [1](evidencia/T16_01_pide_token.png) |
| T17 | Chat normal. | «Escríbeme un programa en Python para ordenar una lista» → misma orientación de alcance; no genera acciones de negocio. | Sí | [1](evidencia/T17_01_tarea_tecnica.png) |
| T18 | Propuesta de limpieza el 2026-11-17 a las 10:00 (45513667); luego otra el 2026-11-24 a las 11:00 (4CF96911). | Confirmar crea una sola reserva. Un segundo evento responde «No hay una solicitud pendiente en esta conversación.» y la API no muestra duplicado. La prueba automática también cubre la repetición del botón. | Sí | [1](evidencia/T18_01_crear_y_confirmar.png) [2](evidencia/T18_02_segunda_pulsacion.png) [3](evidencia/T18_03_api_reservas.png) |
| T19 | Reserva propia 45513667 (limpieza 2026-11-17 a las 10:00). | Pidió cambiar a las 14:00. Una primera vez apareció el aviso de formato (ver fallo intermitente); al repetir, el resultado conservó el código 45513667 con hora 14:00 y `GET /reservas/45513667` lo confirma. | Sí | [1](evidencia/T19_01_aviso_formato_intermitente.png) [2](evidencia/T19_02_resumen_modificar.png) [3](evidencia/T19_03_resultado_modificar.png) [4](evidencia/T19_04_api_reserva_14h.png) |
| T20 | Reserva propia 45513667 activa. | Resumen de cancelación, resultado «Estado: cancelada» y `GET /reservas` con estado cancelada. El resultado devuelve el estado cancelado. | Sí | [1](evidencia/T20_01_cancelar_y_resultado.png) [2](evidencia/T20_02_api_cancelada.png) [3](evidencia/T20_03_api_lista_cancelada.png) |
| T21 | Propuesta completa de limpieza 2026-11-17 a las 10:00. | Descartar → «Descarté la propuesta. Las reservas registradas se conservan.». La API no muestra reserva nueva y `/estado` de esa referencia responde «Todavía no hay un resultado verificable…». | Sí | [1](evidencia/T21_01_descartar.png) [2](evidencia/T21_02_api_sin_reserva_nueva.png) [3](evidencia/T21_03_estado_referencia_descartada.png) |
| T22 | Laura tiene 2026-11-17 a las 10:00 (45 min); se intenta Andrés a las 10:30. | Con `POST /reservas` directo la API respondió 409 «El intervalo solicitado se cruza con una reserva activa». La prueba automática `probar_telegram.py` lanza 8 escrituras superpuestas: se acepta una (201) y las demás se rechazan (409). No se probó con dos chats de Telegram. | Sí (parcial: HTTP directo y prueba automática, no Telegram) | [1](evidencia/T22_01_post_409_cruce.png) [2](evidencia/T22_02_post_409_cruce_2.png) [3](evidencia/T22_03_api_lista.png) [4](evidencia/T22_04_prueba_automatica_1.png) [5](evidencia/T22_05_prueba_automatica_2.png) · [salida automática](evidencia/salida_probar_telegram.txt) |
| T23 | API detenida con Ctrl+C; bot en ejecución. | «No pude completar la conexión. Todavía no envié una escritura de reserva.», sin servicios ni precios. Con la API reiniciada la misma pregunta lista el catálogo. No hay captura de la terminal de la API detenida. | Sí | [1](evidencia/T23_01_api_caida_aviso.png) [2](evidencia/T23_02_api_reiniciada_catalogo.png) |
| T24 | `simular_respuesta_perdida.py` en lugar del bot normal. Dos pruebas: 2026-11-26 a las 10:00 y a las 11:00. | La API guardó la reserva y el simulador ocultó una sola respuesta al bot. El bot informó el resultado incierto con la referencia. `hola` → «Hay una operación por verificar». `/reset` se negó (segunda prueba). `/estado` recuperó el recibo (FE7E2442 y 93523FD3). `GET /reservas` muestra una sola reserva por intento. | Sí | [1](evidencia/T24_01_resultado_incierto.png) [2](evidencia/T24_02_hola_con_pendiente.png) [3](evidencia/T24_03_estado_recupera_recibo.png) [4](evidencia/T24_04_reserva_FE7E2442.png) [5](evidencia/T24_05_api_lista_una_sola.png) [6](evidencia/T24_06_segunda_prueba_reset_rechazado.png) [7](evidencia/T24_07_segunda_prueba_estado.png) |
| T25 | Reserva propia 45513667 (2026-11-17 a las 14:00). | «Cambia la reserva 45513667 para el 2026-11-22 a las 10:00» (domingo) → «La API rechazó la operación: El negocio está cerrado ese día». El resumen de cancelación posterior sigue mostrando 2026-11-17 a las 14:00, es decir, la reserva original no cambió. | Sí | [1](evidencia/T25_01_api_rechaza_dia_cerrado.png) |

## Registro de fallos y correcciones

### T01. Consulta de servicios clasificada como otra acción

- **Caso:** T01.
- **Resultado esperado y diferencia observada:** esperaba el catálogo; el bot respondió «Necesito: codigo».
- **Causa localizada en el proyecto:** el modelo clasificó mal la acción y el prompt de `INSTRUCCIONES` no definía cada acción.
- **Corrección aplicada y archivo modificado:** `bot_telegram.py`: prompt con definición de cada acción y `temperature: 0`.
- **Repetición del caso y evidencia:** T01 y T02 listan el catálogo correcto (capturas).
- **Pruebas cercanas de regresión y resultado:** T03 y T04 pasan.
- **Limitaciones pendientes:** el modelo no es determinista; pueden aparecer clasificaciones erróneas.

### T07. El modelo inventó la fecha

- **Caso:** T07.
- **Resultado esperado y diferencia observada:** esperaba que pidiera la fecha; el modelo puso la fecha de hoy y armó el resumen.
- **Causa localizada en el proyecto:** el plan del modelo se aceptaba sin comprobar que cada dato apareciera en lo que dijo la persona.
- **Corrección aplicada y archivo modificado:** `bot_telegram.py`: `sanear_plan` borra fecha, hora y cliente de crear, modificar y disponibilidad si no aparecen en los últimos 6 mensajes de la persona ni en el actual.
- **Repetición del caso y evidencia:** T07 y T08 repetidos: piden el dato faltante.
- **Pruebas cercanas de regresión y resultado:** T18, T19 y la creación normal siguen funcionando.
- **Limitaciones pendientes:** la comprobación es por patrón de texto; fechas muy coloquiales podrían pedirse de nuevo.

### T05. Código conocido no usado

- **Caso:** T05.
- **Resultado esperado y diferencia observada:** esperaba usar el código de la reserva recién confirmada; el bot respondió «Necesito: codigo».
- **Causa localizada en el proyecto:** el modelo no devolvía el código aunque estaba en el historial.
- **Corrección aplicada y archivo modificado:** `bot_telegram.py`: `resolver_codigo`. Si hay un solo código conocido y no se da otro, lo usa; un código inventado o varios conocidos sin elegir lo vacía y el bot pregunta cuál es.
- **Repetición del caso y evidencia:** T05, T09 y T10 repetidos y correctos.
- **Pruebas cercanas de regresión y resultado:** T10 (varias reservas) pregunta cuál es.
- **Limitaciones pendientes:** los códigos conocidos viven en memoria; tras reiniciar el bot se pierden.

### Aviso intermitente «La respuesta no tiene el formato esperado»

- **Caso:** T03 y T19 (una vez cada uno).
- **Resultado esperado y diferencia observada:** esperaba la respuesta normal; apareció el aviso y al repetir funcionó.
- **Causa localizada en el proyecto:** no se confirmó. Se agregó `logging.warning` y no se capturó la causa. Una hipótesis, sin comprobar, es que el modelo copió la forma `{"plan":…, "resultado":…}` del historial.
- **Corrección aplicada y archivo modificado:** `bot_telegram.py`: `interpretar()` extrae el JSON entre llaves y desempaqueta `plan["plan"]`; registro de WARNING.
- **Repetición del caso y evidencia:** los casos posteriores no lo repitieron.
- **Pruebas cercanas de regresión y resultado:** sin nuevas apariciones, lo que no demuestra que esté resuelto.
- **Limitaciones pendientes:** causa sin determinar.

### Observación sin veredicto: cruce de horarios en la propuesta

Evidencia: [1](evidencia/EXTRA_horario_1030_01_valoracion_1030_responde_horarios.png) [2](evidencia/EXTRA_horario_1030_02_agenda_1030_responde_horarios.png)

- **Caso:** «Quiero una valoración el 2026-11-17 a las 10:30 a nombre de Andrés», con una limpieza de Laura de 10:00 a 10:45. En lugar de un resumen, el bot respondió con la lista de horarios libres.
- **Observado:** el modelo decidió el resultado. El bot no tiene una regla propia de cruces; la validación real la hace la API al confirmar.
- **Causa y corrección:** no determinadas; sin cambio de código.
- **Limitaciones pendientes:** no se usa como evidencia de un caso de la matriz.

## Casos adicionales

- **Reserva cambiada mientras se revisaba un resumen:** ejecutado ([1](evidencia/EXTRA_reserva_cambiada_01_resumen_modificar_DADA25EB.png) [2](evidencia/EXTRA_reserva_cambiada_02_api_DADA25EB_15h.png) [3](evidencia/EXTRA_reserva_cambiada_03_rechazo_reserva_cambio.png)). La reserva DADA25EB se modificó por HTTP (`PUT`, 200) y al confirmar el resumen antiguo el bot informó «La reserva cambió». `GET /reservas` la muestra a las 15:00. Sí.
- **Vencimiento de una propuesta (10 minutos):** No ejecutado.
- **Recibo recuperado después de reiniciar el proceso (`/estado REFERENCIA`):** No ejecutado.
- **Mismo identificador con datos diferentes:** cubierto solo por la prueba automática `probar_telegram.py`; no se probó por Telegram.
- **Confirmación válida después de corregir un botón antiguo:** No ejecutado.

La matriz se relaciona con `docs/C13_Telegram_Operaciones.md`.
