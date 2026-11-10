// Aplicación web: menú, enrutamiento (#/entidad), panel de inicio y vistas de cada entidad.

import { api } from "./api.js";
import { ENTIDADES, ESTADOS, MENU, PAGOS, TRANSICIONES, UBICACIONES } from "./entidades.js";
import { dinero, fecha, fechaHora, hora, hoyIso } from "./formato.js";
import { abrirFormulario } from "./formulario.js";
import { crearTabla, filtrarFilas, insigniaEstado } from "./tabla.js";
import {
  confirmar, dialogo, estadoCargando, estadoError, estadoVacio, h, icono, notificar, pintarIconos,
} from "./ui.js";

const vista = document.getElementById("vista");
const tituloVista = document.getElementById("titulo-vista");

// Lo elegido en cada vista (barbero del filtro, pestaña) se recuerda al volver a ella
const recordado = { filtros: {}, pestanas: {} };

const articulo = (def) => (def.femenino ? "una" : "un");
const este = (def) => (def.femenino ? "esta" : "este");

// ------------------------------------------------------------------
// Menú lateral y enrutamiento
// ------------------------------------------------------------------

function construirMenu() {
  const enlace = (clave, texto) =>
    h("a", { href: `#/${clave}`, class: "enlace-menu", "data-clave": clave }, icono(clave || "inicio"), h("span", {}, texto));
  document.getElementById("navegacion").replaceChildren(
    enlace("", "Inicio"),
    MENU.map(({ grupo, entidades }) => h("div", { class: "grupo-menu" },
      h("p", { class: "titulo-grupo" }, grupo),
      entidades.map((clave) => enlace(clave, ENTIDADES[clave].titulo)))));
}

function abrirMenuMovil(abrir) {
  document.body.classList.toggle("menu-abierto", abrir);
}

function enrutar() {
  const clave = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
  abrirMenuMovil(false);
  document.querySelectorAll(".enlace-menu").forEach((el) => {
    const activo = el.dataset.clave === (ENTIDADES[clave] ? clave : "");
    el.classList.toggle("activo", activo);
    if (activo) el.setAttribute("aria-current", "page");
    else el.removeAttribute("aria-current");
  });
  if (ENTIDADES[clave]) vistaEntidad(clave);
  else vistaInicio();
  vista.focus({ preventScroll: true });
  window.scrollTo(0, 0);
}

function ponerTitulo(texto) {
  tituloVista.textContent = texto;
  document.title = texto === "Inicio" ? "Barbershop" : `${texto} · Barbershop`;
}

// ------------------------------------------------------------------
// Acciones comunes
// ------------------------------------------------------------------

async function eliminarRegistro(def, fila, alTerminar) {
  const aceptado = await confirmar(
    `¿Eliminar ${este(def)} ${def.singular} (#${fila.id})? Esta acción no se puede deshacer.`,
    { titulo: `Eliminar ${def.singular}`, aceptar: "Eliminar", peligro: true });
  if (!aceptado) return;
  try {
    await api.eliminar(def.ruta, fila.id);
    notificar(`${def.singular.charAt(0).toUpperCase() + def.singular.slice(1)} eliminad${def.femenino ? "a" : "o"}.`);
    alTerminar();
  } catch (error) {
    notificar(error.message, "error");
  }
}

const TEXTO_ACCION_ESTADO = { Confirmed: "Confirmar", Completed: "Marcar como completada", Cancelled: "Cancelar la cita" };

function cambiarEstadoCita(cita, alTerminar) {
  const opciones = TRANSICIONES[cita.status] || [];
  const botones = opciones.map((estado) => h("button", {
    type: "button", class: `boton ${estado === "Cancelled" ? "peligro" : "primario"}`,
    onclick: async (ev) => {
      const boton = ev.currentTarget;
      boton.disabled = true;
      try {
        await api.cambiarEstadoCita(cita.id, estado);
        notificar(`La cita ahora está ${ESTADOS[estado].toLowerCase()}.`);
        d.cerrar();
        alTerminar();
      } catch (error) {
        notificar(error.message, "error");
        boton.disabled = false;
      }
    },
  }, TEXTO_ACCION_ESTADO[estado]));

  const d = dialogo({
    titulo: `Estado de la cita #${cita.id}`,
    contenido: [
      h("p", { class: "linea-estado" }, "Estado actual: ", insigniaEstado(cita.status)),
      h("p", { class: "texto-suave" }, `${cita.customer_name} con ${cita.barber_name}, ${fecha(cita.appointment_date)} a las ${hora(cita.start_time)}.`),
    ],
    pie: [h("button", { class: "boton", type: "button", onclick: () => d.cerrar() }, "Cerrar"), ...botones],
  });
}

/** Ventana con el resumen de un registro y la lista de sus registros hijos (servicios de una cita, productos de una venta). */
function abrirDetalle({ padre, registro, hijo, campo, titulo, tituloHijo, resumen, editable, alCerrar }) {
  const defHijo = ENTIDADES[hijo];
  const zonaResumen = h("dl", { class: "resumen" });
  const zonaLista = h("div", { class: "detalle-lista" });
  let actual = registro;
  let huboCambios = false;

  const pintarResumen = () => zonaResumen.replaceChildren(
    resumen(actual).map(([etiqueta, valor]) => h("div", {}, h("dt", {}, etiqueta), h("dd", {}, valor))));

  const botonAgregar = h("button", {
    type: "button", class: "boton primario",
    onclick: async () => {
      if (await abrirFormulario(defHijo, null, { [campo]: registro.id })) {
        huboCambios = true;
        recargar(true);
      }
    },
  }, icono("mas"), `Agregar ${defHijo.singular.replace(/ de la cita$/, "")}`);

  async function recargar(refrescarPadre) {
    zonaLista.replaceChildren(estadoCargando());
    try {
      if (refrescarPadre) {
        actual = await api.obtener(padre, registro.id);
        pintarResumen();
      }
      const filas = await api.listar(hijo, { [campo]: registro.id });
      const puedeEditar = editable(actual);
      botonAgregar.hidden = !puedeEditar;
      const acciones = puedeEditar ? (fila) => [
        {
          icono: "editar", etiqueta: "Editar",
          ejecutar: async () => {
            if (await abrirFormulario(defHijo, fila)) { huboCambios = true; recargar(true); }
          },
        },
        {
          icono: "eliminar", etiqueta: "Quitar", peligro: true,
          ejecutar: () => eliminarRegistro(defHijo, fila, () => { huboCambios = true; recargar(true); }),
        },
      ] : null;
      zonaLista.replaceChildren(filas.length
        ? crearTabla({ columnas: defHijo.columnas.filter(([c]) => c !== "id"), filas, acciones })
        : estadoVacio(puedeEditar ? `Todavía no tiene ${tituloHijo.toLowerCase()}. Use «Agregar».` : `No tiene ${tituloHijo.toLowerCase()}.`, hijo));
    } catch (error) {
      zonaLista.replaceChildren(estadoError(error.message, () => recargar(true)));
    }
  }

  dialogo({
    titulo,
    ancho: true,
    contenido: [zonaResumen, h("div", { class: "detalle-cabecera" }, h("h3", {}, tituloHijo), botonAgregar), zonaLista],
    alCerrar: () => alCerrar?.(huboCambios),
  });
  pintarResumen();
  recargar(false);
}

function detalleCita(cita, alCerrar) {
  abrirDetalle({
    padre: "citas", registro: cita, hijo: "servicios-cita", campo: "appointment_id",
    titulo: `Cita #${cita.id}`, tituloHijo: "Servicios",
    editable: (c) => c.status in TRANSICIONES,
    resumen: (c) => [
      ["Cliente", c.customer_name],
      ["Barbero", c.barber_name],
      ["Fecha", fecha(c.appointment_date)],
      ["Horario", `${hora(c.start_time)} – ${hora(c.end_time)}`],
      ["Lugar", c.location_type === "Home" ? `A domicilio: ${c.home_address || "—"}` : UBICACIONES[c.location_type]],
      ["Estado", insigniaEstado(c.status)],
      ["Total", h("strong", {}, dinero(c.total_amount))],
    ],
    alCerrar,
  });
}

function detalleVenta(venta, alCerrar) {
  abrirDetalle({
    padre: "ventas", registro: venta, hijo: "detalle-ventas", campo: "product_sale_id",
    titulo: `Venta #${venta.id}`, tituloHijo: "Productos",
    editable: () => true,
    resumen: (v) => [
      ["Fecha", fechaHora(v.sale_datetime)],
      ["Cliente", v.customer_name || "Sin cliente"],
      ["Vendedor", v.seller_name],
      ["Pago", PAGOS[v.payment_method] ?? v.payment_method],
      ["Total", h("strong", {}, dinero(v.total_amount))],
    ],
    alCerrar,
  });
}

// Acciones adicionales por fila y qué hacer después de registrar, por entidad
const EXTRAS = {
  citas: {
    acciones: (fila, recargar) => [
      { icono: "ver", etiqueta: "Ver servicios", ejecutar: () => detalleCita(fila, (cambio) => cambio && recargar()) },
      { icono: "estado", etiqueta: "Cambiar estado", visible: fila.status in TRANSICIONES, ejecutar: () => cambiarEstadoCita(fila, recargar) },
    ],
    despuesDeCrear: (cita, recargar) => detalleCita(cita, recargar),
  },
  ventas: {
    acciones: (fila, recargar) => [
      { icono: "ver", etiqueta: "Ver productos", ejecutar: () => detalleVenta(fila, (cambio) => cambio && recargar()) },
    ],
    despuesDeCrear: (venta, recargar) => detalleVenta(venta, recargar),
  },
};

// ------------------------------------------------------------------
// Vista de una entidad: filtro, pestañas, búsqueda y tabla
// ------------------------------------------------------------------

function vistaEntidad(clave) {
  const def = ENTIDADES[clave];
  const extras = EXTRAS[clave] || {};
  ponerTitulo(def.titulo);

  let filas = [];
  let busqueda = "";
  let orden = null;
  let pestana = recordado.pestanas[clave] ?? 0;

  const zonaTabla = h("div", { class: "tarjeta zona-tabla" });
  const contador = h("p", { class: "contador", "aria-live": "polite" });

  const buscador = h("input", {
    type: "search", class: "entrada-busqueda", placeholder: "Buscar…", "aria-label": `Buscar en ${def.titulo}`,
    oninput: (ev) => { busqueda = ev.target.value; pintar(); },
  });

  const botonNuevo = h("button", { type: "button", class: "boton primario", onclick: nuevo },
    icono("mas"), h("span", {}, "Nuevo"));

  // Filtro obligatorio (ej. barbero de los horarios)
  let selectorFiltro = null;
  if (def.filtro) {
    selectorFiltro = h("select", {
      class: "selector-filtro", "aria-label": def.filtro.etiqueta,
      onchange: (ev) => { recordado.filtros[clave] = ev.target.value; cargar(); },
    }, h("option", { value: "" }, "Cargando…"));
  }

  // Pestañas (ej. citas por estado, productos con stock bajo)
  let zonaPestanas = null;
  if (def.pestanas) {
    zonaPestanas = h("div", { class: "pestanas", role: "tablist" });
    const pintarPestanas = () => zonaPestanas.replaceChildren(def.pestanas.map((p, i) => h("button", {
      type: "button", role: "tab", class: `pestana${i === pestana ? " activa" : ""}`,
      "aria-selected": i === pestana ? "true" : "false",
      onclick: () => {
        const cambiaRuta = (def.pestanas[i].ruta || "") !== (def.pestanas[pestana].ruta || "");
        pestana = i;
        recordado.pestanas[clave] = i;
        pintarPestanas();
        if (cambiaRuta) cargar(); else pintar();
      },
    }, p.etiqueta)));
    pintarPestanas();
  }

  vista.replaceChildren(
    h("div", { class: "barra-herramientas" },
      selectorFiltro ? h("label", { class: "filtro" }, h("span", {}, `${def.filtro.etiqueta}:`), selectorFiltro) : null,
      h("div", { class: "caja-busqueda" }, icono("buscar"), buscador),
      botonNuevo),
    zonaPestanas,
    contador,
    zonaTabla);

  const valorFiltro = () => (selectorFiltro ? selectorFiltro.value : "");

  function acciones(fila) {
    return [
      ...(extras.acciones?.(fila, cargar) || []),
      {
        icono: "editar", etiqueta: "Editar",
        ejecutar: async () => { if (await abrirFormulario(def, fila)) cargar(); },
      },
      { icono: "eliminar", etiqueta: "Eliminar", peligro: true, ejecutar: () => eliminarRegistro(def, fila, cargar) },
    ];
  }

  async function nuevo() {
    const fijos = def.filtro && valorFiltro() ? { [def.filtro.nombre]: Number(valorFiltro()) } : {};
    const guardado = await abrirFormulario(def, null, fijos);
    if (!guardado) return;
    await cargar();
    extras.despuesDeCrear?.(guardado, cargar);
  }

  function pintar() {
    const p = def.pestanas?.[pestana];
    let visibles = p?.filtrar ? filas.filter(p.filtrar) : filas;
    visibles = filtrarFilas(visibles, def.columnas, busqueda);
    contador.textContent = visibles.length === filas.length
      ? `${filas.length} registro${filas.length === 1 ? "" : "s"}`
      : `${visibles.length} de ${filas.length} registros`;

    if (!visibles.length) {
      const texto = filas.length
        ? "Ningún registro coincide con la búsqueda."
        : `No hay ${def.titulo.toLowerCase()} registrados. Use «Nuevo» para agregar ${articulo(def)} ${def.singular}.`;
      zonaTabla.replaceChildren(estadoVacio(texto, filas.length ? "buscar" : clave));
      return;
    }
    zonaTabla.replaceChildren(crearTabla({
      columnas: def.columnas, filas: visibles, acciones, orden,
      alOrdenar: (campo) => {
        orden = orden?.campo === campo ? { campo, asc: !orden.asc } : { campo, asc: true };
        pintar();
      },
    }));
  }

  async function cargar() {
    if (def.filtro && !valorFiltro()) {
      contador.textContent = "";
      zonaTabla.replaceChildren(estadoVacio(`Elija ${def.filtro.etiqueta.toLowerCase()} para ver sus ${def.titulo.toLowerCase()}.`, clave));
      return;
    }
    zonaTabla.replaceChildren(estadoCargando());
    try {
      const ruta = def.pestanas?.[pestana]?.ruta || def.ruta;
      filas = def.filtro
        ? await api.listar(def.ruta, { [def.filtro.nombre]: valorFiltro() })
        : await api.listar(ruta);
      pintar();
    } catch (error) {
      contador.textContent = "";
      zonaTabla.replaceChildren(estadoError(error.message, cargar));
    }
  }

  async function cargarFiltro() {
    const ref = def.filtro.ref;
    try {
      const opciones = await api.listar(ref.ruta);
      selectorFiltro.replaceChildren(
        h("option", { value: "" }, opciones.length ? "Seleccione…" : "No hay registros"),
        opciones.map((o) => h("option", { value: String(o.id) }, ref.texto(o))));
      // Se recuerda la última elección; si no hay, se elige la primera opción
      const previo = recordado.filtros[clave];
      selectorFiltro.value = opciones.some((o) => String(o.id) === previo) ? previo : String(opciones[0]?.id ?? "");
      recordado.filtros[clave] = selectorFiltro.value;
    } catch (error) {
      selectorFiltro.replaceChildren(h("option", { value: "" }, "Error al cargar"));
      zonaTabla.replaceChildren(estadoError(error.message, cargarFiltro));
      return;
    }
    cargar();
  }

  if (def.filtro) cargarFiltro();
  else cargar();
}

// ------------------------------------------------------------------
// Inicio: indicadores del día, próximas citas y stock bajo
// ------------------------------------------------------------------

async function vistaInicio() {
  ponerTitulo("Inicio");
  vista.replaceChildren(estadoCargando());

  const [citas, stockBajo, ventas] = await Promise.allSettled([
    api.listar("citas"), api.listar("productos/stock-bajo"), api.listar("ventas"),
  ]);
  if (tituloVista.textContent !== "Inicio") return; // el usuario ya cambió de vista
  const fallo = [citas, stockBajo, ventas].find((r) => r.status === "rejected");
  if (fallo && [citas, stockBajo, ventas].every((r) => r.status === "rejected")) {
    vista.replaceChildren(estadoError(fallo.reason.message, vistaInicio));
    return;
  }
  const valor = (r) => (r.status === "fulfilled" ? r.value : []);
  const listaCitas = valor(citas);
  const listaStock = valor(stockBajo);
  const listaVentas = valor(ventas);

  const hoy = hoyIso();
  const ahora = new Date().toTimeString().slice(0, 5);
  const citasHoy = listaCitas.filter((c) => c.appointment_date === hoy && c.status !== "Cancelled");
  const pendientes = listaCitas.filter((c) => c.status === "Pending");
  const ventasHoy = listaVentas.filter((v) => String(v.sale_datetime).slice(0, 10) === hoy);
  const totalHoy = ventasHoy.reduce((suma, v) => suma + Number(v.total_amount || 0), 0);

  const proximas = listaCitas
    .filter((c) => c.status in TRANSICIONES
      && (c.appointment_date > hoy || (c.appointment_date === hoy && hora(c.end_time) >= ahora)))
    .sort((a, b) => `${a.appointment_date} ${hora(a.start_time)}`.localeCompare(`${b.appointment_date} ${hora(b.start_time)}`))
    .slice(0, 8);

  const indicador = (etiqueta, valorTexto, detalle, destino, alerta = false) =>
    h("a", { class: `indicador${alerta ? " alerta" : ""}`, href: destino },
      h("span", { class: "indicador-etiqueta" }, etiqueta),
      h("span", { class: "indicador-valor" }, valorTexto),
      h("span", { class: "indicador-detalle" }, detalle));

  const recargar = () => vistaInicio();

  const accionesRapidas = h("div", { class: "acciones-rapidas" },
    h("button", {
      type: "button", class: "boton primario",
      onclick: async () => {
        const cita = await abrirFormulario(ENTIDADES.citas);
        if (cita) detalleCita(cita, recargar);
      },
    }, icono("citas"), "Nueva cita"),
    h("button", {
      type: "button", class: "boton",
      onclick: async () => {
        const venta = await abrirFormulario(ENTIDADES.ventas);
        if (venta) detalleVenta(venta, recargar);
      },
    }, icono("ventas"), "Nueva venta"));

  const tablaProximas = proximas.length
    ? crearTabla({
      columnas: [["appointment_date", "Fecha", "fecha"], ["start_time", "Hora", "hora"],
        ["customer_name", "Cliente"], ["barber_name", "Barbero"], ["status", "Estado", "estado"]],
      filas: proximas,
      acciones: (fila) => [
        { icono: "ver", etiqueta: "Ver servicios", ejecutar: () => detalleCita(fila, (c) => c && recargar()) },
        { icono: "estado", etiqueta: "Cambiar estado", ejecutar: () => cambiarEstadoCita(fila, recargar) },
      ],
    })
    : estadoVacio("No hay citas pendientes ni confirmadas próximamente.", "citas");

  const tablaStock = listaStock.length
    ? crearTabla({
      columnas: [["name", "Producto"], ["stock_quantity", "Stock"], ["min_stock_level", "Mínimo"]],
      filas: listaStock,
    })
    : estadoVacio("Todos los productos tienen stock suficiente.", "productos");

  const avisoParcial = fallo
    ? h("div", { class: "aviso-error", role: "alert" }, `Parte de la información no se pudo cargar: ${fallo.reason.message}`)
    : null;

  vista.replaceChildren(
    h("div", { class: "cabecera-inicio" },
      h("div", {},
        h("p", { class: "saludo" }, new Date().toLocaleDateString("es-CO", { weekday: "long", day: "numeric", month: "long" })),
        h("p", { class: "texto-suave" }, "Resumen del día en la barbería")),
      accionesRapidas),
    avisoParcial,
    h("section", { class: "indicadores", "aria-label": "Indicadores" },
      indicador("Citas de hoy", String(citasHoy.length), `${citasHoy.filter((c) => c.status === "Completed").length} completadas`, "#/citas"),
      indicador("Por confirmar", String(pendientes.length), "citas pendientes", "#/citas", pendientes.length > 0),
      indicador("Ventas de hoy", dinero(totalHoy), `${ventasHoy.length} venta${ventasHoy.length === 1 ? "" : "s"}`, "#/ventas"),
      indicador("Stock bajo", String(listaStock.length), "productos por reponer", "#/productos", listaStock.length > 0)),
    h("div", { class: "paneles" },
      h("section", { class: "tarjeta panel" },
        h("header", { class: "panel-cabecera" }, h("h2", {}, "Próximas citas"), h("a", { href: "#/citas" }, "Ver todas")),
        tablaProximas),
      h("section", { class: "tarjeta panel" },
        h("header", { class: "panel-cabecera" }, h("h2", {}, "Productos con stock bajo"), h("a", { href: "#/productos" }, "Ver inventario")),
        tablaStock)));
}

// ------------------------------------------------------------------
// Arranque
// ------------------------------------------------------------------

construirMenu();
pintarIconos();
document.getElementById("abrir-menu").addEventListener("click", () => abrirMenuMovil(true));
document.getElementById("fondo-lateral").addEventListener("click", () => abrirMenuMovil(false));
window.addEventListener("hashchange", enrutar);
enrutar();
