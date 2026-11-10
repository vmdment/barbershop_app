// Utilidades de interfaz: creación de elementos, íconos, notificaciones y diálogos.

/** Crea un elemento: h("button", { class: "boton", onclick }, "Texto", otroNodo) */
export function h(etiqueta, atributos = {}, ...hijos) {
  const el = document.createElement(etiqueta);
  for (const [clave, valor] of Object.entries(atributos || {})) {
    if (valor === null || valor === undefined || valor === false) continue;
    if (clave === "class") el.className = valor;
    else if (clave.startsWith("on")) el.addEventListener(clave.slice(2), valor);
    else if (clave === "value") el.value = valor;
    else if (clave === "checked") el.checked = valor;
    else if (valor === true) el.setAttribute(clave, "");
    else el.setAttribute(clave, valor);
  }
  for (const hijo of hijos.flat(Infinity)) {
    if (hijo === null || hijo === undefined || hijo === false) continue;
    el.append(hijo instanceof Node ? hijo : String(hijo));
  }
  return el;
}

const TRAZOS = {
  inicio: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
  roles: '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
  usuarios: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.5 3.4-5.5 6.5-5.5s5.7 2 6.5 5.5"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14.8c1.9.8 3.1 2.6 3.5 5.2"/>',
  barberias: '<path d="M3 9 4.5 4h15L21 9"/><path d="M3 9h18v1.5a3 3 0 0 1-6 0 3 3 0 0 1-6 0 3 3 0 0 1-6 0z"/><path d="M5 13v8h14v-8M10 21v-5h4v5"/>',
  barberos: '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4 8.1 15.9M14.5 14.5 20 20M8.1 8.1 12 12"/>',
  horarios: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  bloqueos: '<rect x="3" y="4.5" width="18" height="16.5" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4M10 13l4 4M14 13l-4 4"/>',
  servicios: '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
  "servicios-barbero": '<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/>',
  citas: '<rect x="3" y="4.5" width="18" height="16.5" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4M8 14h.01M12 14h.01M16 14h.01M8 17.5h.01M12 17.5h.01"/>',
  "servicios-cita": '<path d="M11 6h9M11 12h9M11 18h9"/><path d="m3.5 6 1.5 1.5L7.5 5M3.5 12l1.5 1.5L7.5 11M3.5 18l1.5 1.5 2.5-2.5"/>',
  productos: '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
  ventas: '<circle cx="9" cy="20" r="1.3"/><circle cx="18" cy="20" r="1.3"/><path d="M2.5 3H5l2.4 12h11.2l2-8H6"/>',
  "detalle-ventas": '<path d="M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2z"/><path d="M9 8h6M9 12h6M9 16h3"/>',
  proveedores: '<path d="M2 6h12v10H2zM14 9h4l4 4v3h-8"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>',
  compras: '<path d="M5 8h14l-1 13H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
  mas: '<path d="M12 5v14M5 12h14"/>',
  editar: '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
  eliminar: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
  cerrar: '<path d="M6 6l12 12M18 6 6 18"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  api: '<path d="m8 8-5 4 5 4M16 8l5 4-5 4M14 4l-4 16"/>',
  estado: '<path d="M4 12a8 8 0 0 1 14-5.3L20 9M20 4v5h-5M20 12a8 8 0 0 1-14 5.3L4 15M4 20v-5h5"/>',
  ver: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  alerta: '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
  buscar: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
};

/** Ícono SVG (trazos fijos definidos arriba, nunca datos del usuario). */
export function icono(nombre) {
  const span = document.createElement("span");
  span.className = "icono";
  span.setAttribute("aria-hidden", "true");
  span.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
    stroke-linecap="round" stroke-linejoin="round">${TRAZOS[nombre] || ""}</svg>`;
  return span;
}

/** Reemplaza cada [data-icono] estático del HTML por su SVG. */
export function pintarIconos(raiz = document) {
  raiz.querySelectorAll("[data-icono]").forEach((el) => {
    el.replaceWith(icono(el.dataset.icono));
  });
}

export function notificar(mensaje, tipo = "exito") {
  const caja = h("div", { class: `notificacion ${tipo}`, role: tipo === "error" ? "alert" : "status" },
    icono(tipo === "error" ? "alerta" : "roles"), h("span", {}, mensaje));
  document.getElementById("notificaciones").append(caja);
  setTimeout(() => caja.classList.add("saliendo"), tipo === "error" ? 6000 : 3500);
  setTimeout(() => caja.remove(), tipo === "error" ? 6400 : 3900);
}

/** Abre un diálogo modal. Devuelve { dialogo, cuerpo, cerrar }. */
export function dialogo({ titulo, contenido, pie = null, ancho = false, alCerrar }) {
  const cuerpo = h("div", { class: "dialogo-cuerpo" }, contenido);
  const dlg = h("dialog", { class: `dialogo${ancho ? " ancho" : ""}`, "aria-label": titulo },
    h("header", { class: "dialogo-cabecera" },
      h("h2", {}, titulo),
      h("button", { class: "boton-icono", type: "button", "aria-label": "Cerrar", onclick: () => dlg.close() },
        icono("cerrar"))),
    cuerpo,
    pie ? h("footer", { class: "dialogo-pie" }, pie) : null);
  dlg.addEventListener("close", () => {
    dlg.remove();
    alCerrar?.();
  });
  // Clic fuera del contenido cierra el diálogo
  dlg.addEventListener("mousedown", (ev) => {
    if (ev.target === dlg) dlg.close();
  });
  document.body.append(dlg);
  dlg.showModal();
  return { dialogo: dlg, cuerpo, cerrar: () => dlg.close() };
}

/** Diálogo de confirmación. Resuelve true si el usuario acepta. */
export function confirmar(mensaje, { titulo = "Confirmar", aceptar = "Aceptar", peligro = false } = {}) {
  return new Promise((resolver) => {
    let aceptado = false;
    const d = dialogo({
      titulo,
      contenido: h("p", { class: "texto-confirmacion" }, mensaje),
      pie: [
        h("button", { class: "boton", type: "button", onclick: () => d.cerrar() }, "Cancelar"),
        h("button", {
          class: `boton ${peligro ? "peligro" : "primario"}`, type: "button",
          onclick: () => { aceptado = true; d.cerrar(); },
        }, aceptar),
      ],
      alCerrar: () => resolver(aceptado),
    });
  });
}

export function estadoVacio(texto, iconoNombre = "buscar") {
  return h("div", { class: "estado-vacio" }, icono(iconoNombre), h("p", {}, texto));
}

export function estadoCargando() {
  return h("div", { class: "cargando", "aria-busy": "true" },
    h("span", { class: "giro" }), h("span", {}, "Cargando…"));
}

export function estadoError(mensaje, reintentar) {
  return h("div", { class: "estado-vacio error" }, icono("alerta"), h("p", {}, mensaje),
    reintentar ? h("button", { class: "boton", type: "button", onclick: reintentar }, "Reintentar") : null);
}
