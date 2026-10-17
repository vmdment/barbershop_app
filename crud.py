"""Motor genérico de menús CRUD sobre los procedimientos almacenados."""
from dataclasses import dataclass, field
from typing import Any, Callable

import validaciones as v
from conexion import ErrorBD, conexion

# ------------------------------------------------------------------
# Presentación
# ------------------------------------------------------------------

ANCHO_MAX_COLUMNA = 30


def titulo(texto: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {texto.upper()}")
    print("=" * 60)


def exito(texto: str) -> None:
    print(f"\n  [OK] {texto}")


def error(texto: str) -> None:
    print(f"\n  [ERROR] {texto}")


def aviso(texto: str) -> None:
    print(f"\n  [i] {texto}")


def pausa() -> None:
    input("\n  Presione Enter para continuar...")


def mostrar_tabla(filas: list[dict], columnas: list[tuple]) -> None:
    """columnas: [(clave, título) o (clave, título, formateador)]"""
    if not filas:
        aviso("No hay registros para mostrar.")
        return
    datos = []
    for fila in filas:
        datos.append([_celda(fila, columna) for columna in columnas])
    titulos = [columna[1] for columna in columnas]
    anchos = [max(len(t), *(len(d[i]) for d in datos)) for i, t in enumerate(titulos)]
    print()
    print("  " + " | ".join(t.ljust(anchos[i]) for i, t in enumerate(titulos)))
    print("  " + "-+-".join("-" * a for a in anchos))
    for d in datos:
        print("  " + " | ".join(c.ljust(anchos[i]) for i, c in enumerate(d)))
    print(f"\n  Total: {len(filas)} registro(s)")


def mostrar_ficha(fila: dict, columnas: list[tuple]) -> None:
    ancho = max(len(columna[1]) for columna in columnas)
    print()
    for columna in columnas:
        print(f"  {columna[1].ljust(ancho)} : {_celda(fila, columna, recortar=False)}")


def _celda(fila: dict, columna: tuple, recortar: bool = True) -> str:
    valor = fila.get(columna[0])
    texto = columna[2](valor) if len(columna) > 2 and valor is not None else v.formatear(valor)
    texto = " ".join(str(texto).split())
    if recortar and len(texto) > ANCHO_MAX_COLUMNA:
        texto = texto[: ANCHO_MAX_COLUMNA - 3] + "..."
    return texto


def si_no(valor) -> str:
    return "Sí" if valor else "No"


# ------------------------------------------------------------------
# Definición de campos y entidades
# ------------------------------------------------------------------

@dataclass
class Referencia:
    """Lista de registros entre los que el usuario elige un ID."""
    proc: str
    texto: str | Callable[[dict], str]     # columna o función que describe la fila
    nombre: str                            # para mensajes: "usuarios", "barberos"...
    id_col: str = "id"
    params: Callable[[dict], tuple] | None = None   # parámetros según lo ya ingresado
    filtrar: Callable[[dict], bool] | None = None   # deja solo las filas elegibles

    def obtener(self, valores: dict) -> list[dict]:
        params = self.params(valores) if self.params else ()
        filas = conexion.call(self.proc, params)
        return [fila for fila in filas if self.filtrar(fila)] if self.filtrar else filas

    def describir(self, fila: dict) -> str:
        return self.texto(fila) if callable(self.texto) else v.formatear(fila.get(self.texto))


@dataclass
class Campo:
    nombre: str              # columna / parámetro del procedimiento
    etiqueta: str
    tipo: str = "texto"      # texto, entero, decimal, fecha, hora, fechahora, email,
                             # telefono, opcion, sino, ref, password
    obligatorio: bool = True
    largo: int = 0
    minimo: Any = None
    maximo: Any = None
    opciones: dict = field(default_factory=dict)
    referencia: Referencia | None = None
    condicion: Callable[[dict], bool] | None = None   # si devuelve False el campo va NULL
    ayuda: str = ""


@dataclass
class Entidad:
    titulo: str
    singular: str
    columnas: list[tuple]
    campos: list[Campo]
    proc_listar: str
    proc_buscar: str
    proc_insertar: str | None = None
    proc_actualizar: str | None = None
    proc_eliminar: str | None = None
    campos_actualizar: list[Campo] | None = None
    parametros: list[str] | None = None                # orden de parámetros si difiere de "campos"
    filtro: Campo | None = None                        # parámetro obligatorio para listar
    validar: Callable[[dict], str | None] | None = None
    despues_de_insertar: Callable[[int, dict], None] | None = None
    extras: list[tuple[str, Callable[[], None]]] = field(default_factory=list)
    femenino: bool = False

    # Concordancia de género: "del usuario" / "de la barbería", "registrado" / "registrada"
    @property
    def del_(self) -> str:
        return f"de la {self.singular}" if self.femenino else f"del {self.singular}"

    @property
    def este(self) -> str:
        return f"esta {self.singular}" if self.femenino else f"este {self.singular}"

    @property
    def un(self) -> str:
        return f"una {self.singular}" if self.femenino else f"un {self.singular}"

    def participio(self, verbo: str) -> str:
        return f"{self.singular.capitalize()} {verbo}{'a' if self.femenino else 'o'}"


# ------------------------------------------------------------------
# Lectura de campos
# ------------------------------------------------------------------

def pedir_campo(campo: Campo, valores: dict, actual=None, actualizando=False):
    if campo.ayuda:
        print(f"    ({campo.ayuda})")
    etiqueta, oblig = campo.etiqueta, campo.obligatorio
    if campo.tipo == "texto":
        return v.pedir_texto(etiqueta, oblig, campo.largo, actual)
    if campo.tipo == "entero":
        return v.pedir_entero(etiqueta, oblig, campo.minimo, campo.maximo, actual)
    if campo.tipo == "decimal":
        return v.pedir_decimal(etiqueta, oblig, campo.minimo, campo.maximo, actual)
    if campo.tipo == "fecha":
        return v.pedir_fecha(etiqueta, oblig, actual)
    if campo.tipo == "hora":
        return v.pedir_hora(etiqueta, oblig, actual)
    if campo.tipo == "fechahora":
        return v.pedir_fecha_hora(etiqueta, oblig, actual)
    if campo.tipo == "email":
        return v.pedir_email(etiqueta, oblig, actual)
    if campo.tipo == "telefono":
        return v.pedir_telefono(etiqueta, oblig, actual)
    if campo.tipo == "sino":
        return v.pedir_si_no(etiqueta, actual)
    if campo.tipo == "opcion":
        print(f"  {etiqueta}:")
        return v.pedir_opcion("Opción", campo.opciones, oblig, actual)
    if campo.tipo == "password":
        return v.pedir_password(nueva_opcional=actualizando)
    if campo.tipo == "ref":
        return pedir_referencia(campo, valores, actual)
    raise ValueError(f"Tipo de campo desconocido: {campo.tipo}")


def pedir_referencia(campo: Campo, valores: dict, actual=None):
    ref = campo.referencia
    filas = ref.obtener(valores)
    if not filas:
        if campo.obligatorio:
            raise v.Cancelado(f"No hay {ref.nombre} disponibles. Regístrelos primero.")
        aviso(f"No hay {ref.nombre} disponibles; el campo quedará vacío.")
        return None
    print(f"  {campo.etiqueta} - opciones:")
    for fila in filas:
        print(f"    {str(fila[ref.id_col]).rjust(4)}  {ref.describir(fila)}")
    ids = {fila[ref.id_col] for fila in filas}
    # Si el valor actual ya no está en la lista se permite conservarlo igual
    if actual is not None:
        ids.add(actual)
    return v.pedir_id(f"ID de {campo.etiqueta.lower()}", ids, campo.obligatorio, actual)


def pedir_formulario(campos: list[Campo], actuales: dict | None = None,
                     fijos: dict | None = None, actualizando=False) -> dict:
    valores = dict(fijos or {})
    for campo in campos:
        if campo.nombre in valores:
            continue
        if campo.condicion and not campo.condicion(valores):
            valores[campo.nombre] = None
            continue
        actual = actuales.get(campo.nombre) if actuales else None
        valores[campo.nombre] = pedir_campo(campo, valores, actual, actualizando)
    return valores


# ------------------------------------------------------------------
# Acciones CRUD genéricas
# ------------------------------------------------------------------

def buscar_por_id(entidad: Entidad, id_: int) -> dict | None:
    filas = conexion.call(entidad.proc_buscar, (id_,))
    return filas[0] if filas else None


def obtener_listado(entidad: Entidad, valor_filtro=None) -> list[dict]:
    if entidad.filtro:
        return conexion.call(entidad.proc_listar, (valor_filtro,))
    return conexion.call(entidad.proc_listar)


def listar(entidad: Entidad) -> None:
    valor_filtro = None
    if entidad.filtro:
        valor_filtro = pedir_campo(entidad.filtro, {})
    mostrar_tabla(obtener_listado(entidad, valor_filtro), entidad.columnas)


def buscar(entidad: Entidad) -> None:
    id_ = v.pedir_id(f"ID {entidad.del_}")
    fila = buscar_por_id(entidad, id_)
    if fila is None:
        aviso(f"No existe {entidad.un} con ID {id_}.")
    else:
        mostrar_ficha(fila, entidad.columnas)


def elegir_registro(entidad: Entidad, accion: str) -> dict:
    """Muestra los registros y pide el ID de uno de ellos."""
    valor_filtro = pedir_campo(entidad.filtro, {}) if entidad.filtro else None
    filas = obtener_listado(entidad, valor_filtro)
    if not filas:
        raise v.Cancelado(f"No hay registros para {accion}.")
    mostrar_tabla(filas, entidad.columnas)
    print()
    id_ = v.pedir_id(f"ID {entidad.del_} a {accion}", {fila["id"] for fila in filas})
    fila = buscar_por_id(entidad, id_)
    if fila is None:
        raise v.Cancelado(f"El registro con ID {id_} ya no existe.")
    return fila


def _validar(entidad: Entidad, valores: dict) -> None:
    if entidad.validar:
        mensaje = entidad.validar(valores)
        if mensaje:
            raise v.Cancelado(mensaje)


def _parametros(campos: list[Campo], orden: list[str] | None, valores: dict) -> tuple:
    return tuple(valores[nombre] for nombre in (orden or [c.nombre for c in campos]))


def registrar(entidad: Entidad, fijos: dict | None = None) -> int | None:
    print("  (Escriba 'cancelar' en cualquier momento para abortar)\n")
    valores = pedir_formulario(entidad.campos, fijos=fijos)
    _validar(entidad, valores)
    filas = conexion.call(entidad.proc_insertar, _parametros(entidad.campos, entidad.parametros, valores))
    nuevo_id = filas[0]["id"] if filas else None
    exito(f"{entidad.participio('registrad')} con ID {nuevo_id}.")
    if entidad.despues_de_insertar and nuevo_id is not None:
        entidad.despues_de_insertar(nuevo_id, valores)
    return nuevo_id


def actualizar(entidad: Entidad) -> None:
    fila = elegir_registro(entidad, "actualizar")
    campos = entidad.campos_actualizar or entidad.campos
    orden = None if entidad.campos_actualizar else entidad.parametros
    print("\n  (Enter conserva el valor actual entre [ ], '-' borra un campo opcional,")
    print("   'cancelar' aborta)\n")
    valores = pedir_formulario(campos, actuales=fila, actualizando=True)
    _validar(entidad, valores)
    conexion.call(entidad.proc_actualizar, (fila["id"],) + _parametros(campos, orden, valores))
    exito(f"{entidad.participio('actualizad')} correctamente.")


def eliminar(entidad: Entidad) -> None:
    fila = elegir_registro(entidad, "eliminar")
    mostrar_ficha(fila, entidad.columnas)
    print()
    if not v.confirmar(f"¿Seguro que desea eliminar {entidad.este}?"):
        aviso("No se eliminó nada.")
        return
    conexion.call(entidad.proc_eliminar, (fila["id"],))
    exito(f"{entidad.participio('eliminad')} correctamente.")


def ejecutar_accion(accion: Callable[[], None]) -> None:
    """Ejecuta una acción del menú atrapando cancelaciones y errores de BD."""
    try:
        accion()
    except v.Cancelado as e:
        aviso(str(e))
    except ErrorBD as e:
        error(str(e))
    pausa()


def elegir_opcion(opciones: list[str], texto_salir: str = "Volver") -> int:
    for i, opcion in enumerate(opciones, start=1):
        print(f"  {str(i).rjust(2)}. {opcion}")
    print(f"   0. {texto_salir}")
    while True:
        texto = input("\n  Seleccione una opción: ").strip()
        if texto.isdigit() and 0 <= int(texto) <= len(opciones):
            return int(texto)
        print(f"    [!] Opción inválida. Ingrese un número entre 0 y {len(opciones)}.")


def menu_entidad(entidad: Entidad) -> None:
    acciones: list[tuple[str, Callable[[], None]]] = [
        ("Listar", lambda: listar(entidad)),
        ("Buscar por ID", lambda: buscar(entidad)),
    ]
    if entidad.proc_insertar:
        acciones.append(("Registrar", lambda: registrar(entidad)))
    if entidad.proc_actualizar:
        acciones.append(("Actualizar", lambda: actualizar(entidad)))
    if entidad.proc_eliminar:
        acciones.append(("Eliminar", lambda: eliminar(entidad)))
    acciones += entidad.extras

    while True:
        titulo(entidad.titulo)
        opcion = elegir_opcion([nombre for nombre, _ in acciones])
        if opcion == 0:
            return
        ejecutar_accion(acciones[opcion - 1][1])
