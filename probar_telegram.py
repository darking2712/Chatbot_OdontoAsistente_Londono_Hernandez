"""Prueba de las reglas del canal de Telegram sobre la agenda del consultorio. No usa Groq, Telegram ni reservas.db.

Ejecutar desde la carpeta del proyecto:  python probar_telegram.py
Complementa a probar_demo.py: llama a AgendaConsultorio.operar() igual que la ruta POST /telegram/operaciones.
No sustituye las pruebas reales con dos cuentas de Telegram de la matriz.
"""
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

os.environ.setdefault("CHATBOT_API_KEY", "clave-solo-para-pruebas-123")

import main  # noqa: E402
from almacen_sqlite import ReservaNoEncontrada  # noqa: E402
from api_telegram import Operacion  # noqa: E402

LAURA, ANDRES = 1001, 2002


def verificar(nombre, condicion, detalle=""):
    if not condicion:
        raise AssertionError(f"FALLÓ: {nombre}. {detalle}".strip())
    print(f"[OK] {nombre}")


def filas(ruta):
    con = sqlite3.connect(ruta)
    con.row_factory = sqlite3.Row
    try:
        return {f["codigo"]: dict(f) for f in con.execute("SELECT * FROM reservas")}
    finally:
        con.close()


def contar(ruta, tabla):
    con = sqlite3.connect(ruta)
    try:
        return con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    finally:
        con.close()


def probar():
    with TemporaryDirectory() as carpeta:
        ruta = Path(carpeta) / "telegram_prueba.db"
        agenda = main.AgendaConsultorio(
            ruta, main.NEGOCIO["servicios"],
            apertura=min(h[0] for h in main.NEGOCIO["horarios"].values()),
            cierre=max(h[1] for h in main.NEGOCIO["horarios"].values()),
            dias=tuple(main.HORARIOS), paso=main.NEGOCIO["paso_minutos"])

        fecha = datetime.now(main.ZONA).date() + timedelta(days=3)
        while fecha.weekday() > 4:
            fecha += timedelta(days=1)
        dia = fecha.isoformat()

        def op(accion, usuario, sid=None, referencia="", **datos):
            solicitud = Operacion(solicitud_id=sid or uuid4().hex, accion=accion,
                                  datos=datos, referencia=referencia, confirmada=True)
            return agenda.operar(solicitud, usuario)

        print("== 1. Crear y propiedad ==")
        sid = uuid4().hex
        datos = dict(cliente="Laura", servicio="limpieza", fecha=dia, hora="10:00")
        estado, r = op("crear", LAURA, sid, **datos)
        verificar("Laura crea una limpieza 10:00-10:45 (201)", estado == 201 and r["ok"])
        a = r["reserva"]["codigo"]
        verificar("la fila existe en SQLite", filas(ruta)[a]["hora"] == "10:00" and len(filas(ruta)) == 1)
        verificar("Laura puede consultarla", agenda.consultar_propia(a, LAURA)["reserva"]["codigo"] == a)

        print("\n== 2. Repetición de la misma confirmación ==")
        estado2, r2 = op("crear", LAURA, sid, **datos)
        verificar("misma solicitud: misma respuesta y mismo código", (estado2, r2["reserva"]["codigo"]) == (201, a))
        verificar("no se creó otra fila", len(filas(ruta)) == 1)
        estado3, _ = op("crear", LAURA, sid, **{**datos, "hora": "11:00"})
        verificar("mismo identificador con datos distintos: 409", estado3 == 409 and len(filas(ruta)) == 1)
        verificar("otro usuario no puede leer esa solicitud", op("crear", ANDRES, sid, **datos)[0] == 404)

        print("\n== 3. Cruce entre cuentas ==")
        antes = filas(ruta)
        estado, r = op("crear", ANDRES, cliente="Andrés", servicio="valoracion", fecha=dia, hora="10:30")
        verificar("Andrés 10:30 se cruza con 10:00-10:45 (409)", estado == 409 and not r["ok"])
        verificar("el cruce no cambió ninguna fila", filas(ruta) == antes)
        estado, r = op("crear", ANDRES, cliente="Andrés", servicio="valoracion", fecha=dia, hora="11:00")
        verificar("Andrés 11:00 (empieza al terminar la otra) sí se registra", estado == 201)
        b = r["reserva"]["codigo"]

        print("\n== 4. Acceso a la reserva ajena ==")
        try:
            agenda.consultar_propia(a, ANDRES)
            verificar("Andrés no consulta la reserva de Laura", False)
        except ReservaNoEncontrada:
            verificar("Andrés no consulta la reserva de Laura", True)
        antes = filas(ruta)
        ref_a = agenda.consultar_propia(a, LAURA)["referencia"]
        verificar("Andrés no puede modificar la de Laura (404)", op("modificar", ANDRES, referencia=ref_a, codigo=a, servicio="limpieza", fecha=dia, hora="14:00")[0] == 404)
        verificar("Andrés no puede cancelar la de Laura (404)", op("cancelar", ANDRES, referencia=ref_a, codigo=a)[0] == 404)
        verificar("la reserva de Laura quedó igual", filas(ruta) == antes)

        print("\n== 5. Modificar ==")
        estado, r = op("modificar", LAURA, referencia=ref_a, codigo=a, servicio="limpieza", fecha=dia, hora="14:00")
        verificar("Laura mueve su reserva a 14:00 conservando el código (200)", estado == 200 and r["reserva"]["codigo"] == a and filas(ruta)[a]["hora"] == "14:00")
        verificar("resumen antiguo (referencia vieja) rechazado (409)", op("modificar", LAURA, referencia=ref_a, codigo=a, servicio="limpieza", fecha=dia, hora="15:00")[0] == 409)
        verificar("la reserva sigue en 14:00", filas(ruta)[a]["hora"] == "14:00")
        ref_a = agenda.consultar_propia(a, LAURA)["referencia"]
        antes = filas(ruta)
        estado, r = op("modificar", LAURA, referencia=ref_a, codigo=a, servicio="limpieza", fecha=dia, hora="11:00")
        verificar("modificar a un horario ocupado por Andrés: 409", estado == 409 and not r["ok"])
        verificar("la reserva original permanece sin cambios", filas(ruta) == antes)

        print("\n== 6. Cancelar ==")
        ref_a = agenda.consultar_propia(a, LAURA)["referencia"]
        estado, r = op("cancelar", LAURA, referencia=ref_a, codigo=a)
        verificar("Laura cancela (200, estado cancelada)", estado == 200 and filas(ruta)[a]["estado"] == "cancelada")
        verificar("la cancelación libera 14:00", "14:00" in agenda.disponibilidad(dia, "valoracion")["horas"])
        verificar("cancelar otra vez: 409", op("cancelar", LAURA, referencia=agenda.consultar_propia(a, LAURA)["referencia"], codigo=a)[0] == 409)

        print("\n== 7. Recibos ==")
        codigo_http, recibo = agenda.consultar_operacion(sid, LAURA)
        verificar("el recibo de la creación se recupera", codigo_http == 201 and recibo["reserva"]["codigo"] == a)
        try:
            agenda.consultar_operacion(sid, ANDRES)
            verificar("el recibo ajeno no se entrega", False)
        except ReservaNoEncontrada:
            verificar("el recibo ajeno no se entrega", True)
        reiniciada = main.AgendaConsultorio(ruta, main.NEGOCIO["servicios"], apertura="08:00", cierre="18:00",
                                            dias=tuple(main.HORARIOS), paso=30)
        verificar("tras reiniciar el almacén el recibo sigue ahí", reiniciada.consultar_operacion(sid, LAURA)[1]["reserva"]["codigo"] == a)

        print("\n== 8. Escrituras HTTP que se superponen (mismo horario, 8 hilos) ==")
        antes_activas = sum(f["estado"] == "activa" for f in filas(ruta).values())
        with ThreadPoolExecutor(max_workers=8) as pool:
            res = list(pool.map(lambda i: op("crear", LAURA if i % 2 else ANDRES, cliente=f"Prueba{i}", servicio="valoracion", fecha=dia, hora="16:00"), range(8)))
        codigos = sorted(e for e, _ in res)
        verificar("exactamente una se registra (201) y el resto se rechaza (409)", codigos == [201] + [409] * 7, str(codigos))
        verificar("SQLite tiene una sola reserva activa nueva", sum(f["estado"] == "activa" for f in filas(ruta).values()) == antes_activas + 1)
        verificar("hay un recibo por cada intento", contar(ruta, "operaciones_telegram") >= 8)
        print("\nOK: propiedad, cruces, referencia de resumen, repetición, recibos y escrituras superpuestas.")


if __name__ == "__main__":
    probar()
