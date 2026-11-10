// Tabla de registros con búsqueda, orden por columna y acciones por fila.

import { ESTADOS } from "./entidades.js";
import { formatear, vacio } from "./formato.js";
import { h, icono } from "./ui.js";

const NUMERICOS = new Set(["dinero", "porcentaje"]);

const normalizar = (texto) => texto.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");

export function insigniaEstado(estado) {
  return h("span", { class: `insignia estado-${estado}` }, ESTADOS[estado] ?? estado);
}

function contenidoCelda(fila, [campo, , formato]) {
  if (formato === "estado") return insigniaEstado(fila[campo]);
  return formatear(fila[campo], formato === "estado" ? null : formato);
}

/** Texto plano de la fila (para la búsqueda). */
function textoFila(fila, columnas) {
  return normalizar(columnas.map(([campo, , formato]) =>
    formato === "estado" ? ESTADOS[fila[campo]] ?? "" : formatear(fila[campo], formato)).join(" "));
}

function comparar(a, b) {
  if (vacio(a)) return vacio(b) ? 0 : 1;
  if (vacio(b)) return -1;
  if (typeof a === "number" && typeof b === "number") return a - b;
  return String(a).localeCompare(String(b), "es", { numeric: true });
}

/** Filtra las filas por el texto buscado (en lo que se ve en pantalla, sin tildes). */
export function filtrarFilas(filas, columnas, busqueda) {
  const termino = normalizar(busqueda.trim());
  return termino ? filas.filter((f) => textoFila(f, columnas).includes(termino)) : filas;
}

/**
 * columnas: [campo, etiqueta, formato]; acciones(fila) -> [{ icono, etiqueta, ejecutar, peligro, visible }]
 * orden: { campo, asc } y alOrdenar(campo) para ordenar al hacer clic en el encabezado.
 */
export function crearTabla({ columnas, filas, acciones = null, orden = null, alOrdenar = null }) {
  let datos = filas;
  if (orden?.campo) {
    datos = [...filas].sort((a, b) => comparar(a[orden.campo], b[orden.campo]) * (orden.asc ? 1 : -1));
  }

  const encabezados = columnas.map(([campo, etiqueta, formato]) => {
    const activo = orden?.campo === campo;
    const contenido = alOrdenar
      ? h("button", { type: "button", class: "orden", onclick: () => alOrdenar(campo) },
        etiqueta, h("span", { class: "flecha", "aria-hidden": "true" }, activo ? (orden.asc ? "▲" : "▼") : ""))
      : etiqueta;
    return h("th", {
      scope: "col", class: NUMERICOS.has(formato) ? "num" : null,
      "aria-sort": activo ? (orden.asc ? "ascending" : "descending") : null,
    }, contenido);
  });
  if (acciones) encabezados.push(h("th", { scope: "col", class: "acciones" }, h("span", { class: "oculto" }, "Acciones")));

  const cuerpo = datos.map((fila) => {
    const celdas = columnas.map((columna) => {
      const [campo, , formato] = columna;
      const numerico = NUMERICOS.has(formato) || (campo === "id");
      return h("td", { class: numerico ? "num" : null, "data-etiqueta": columna[1] }, contenidoCelda(fila, columna));
    });
    if (acciones) {
      const botones = acciones(fila).filter((a) => a.visible !== false).map((accion) =>
        h("button", {
          type: "button", class: `boton-icono${accion.peligro ? " peligro" : ""}`,
          title: accion.etiqueta, "aria-label": `${accion.etiqueta} (#${fila.id})`,
          onclick: accion.ejecutar,
        }, icono(accion.icono)));
      celdas.push(h("td", { class: "acciones" }, h("div", { class: "grupo-acciones" }, botones)));
    }
    return h("tr", {}, celdas);
  });

  return h("div", { class: "tabla-desplazable" },
    h("table", { class: "tabla" }, h("thead", {}, h("tr", {}, encabezados)), h("tbody", {}, cuerpo)));
}
