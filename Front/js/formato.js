// Formato de los valores que devuelve la API para mostrarlos en pantalla.

const numero = new Intl.NumberFormat("es-CO", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export const vacio = (valor) => valor === null || valor === undefined || valor === "";

export function dinero(valor) {
  return vacio(valor) ? "—" : `$${numero.format(Number(valor))}`;
}

export function hora(valor) {
  if (vacio(valor)) return "—";
  const [h, m] = String(valor).split(":");
  return `${h.padStart(2, "0")}:${(m || "00").padStart(2, "0")}`;
}

export function fecha(valor) {
  if (vacio(valor)) return "—";
  const [a, m, d] = String(valor).slice(0, 10).split("-");
  return `${d}/${m}/${a}`;
}

export function fechaHora(valor) {
  if (vacio(valor)) return "—";
  const texto = String(valor).replace("T", " ");
  return `${fecha(texto)} ${hora(texto.slice(11, 16))}`;
}

export const sino = (valor) => (vacio(valor) ? "—" : Number(valor) ? "Sí" : "No");

export const porcentaje = (valor) => (vacio(valor) ? "—" : `${Number(valor).toLocaleString("es-CO")} %`);

const FORMATOS = { dinero, hora, fecha, fechaHora, sino, porcentaje };

/** Texto de una celda: formato puede ser el nombre de un formato o un diccionario de traducción. */
export function formatear(valor, formato) {
  if (formato && typeof formato === "object") return formato[valor] ?? (vacio(valor) ? "—" : String(valor));
  if (FORMATOS[formato]) return FORMATOS[formato](valor);
  return vacio(valor) ? "—" : String(valor);
}

/** Fecha local de hoy en formato AAAA-MM-DD (igual que la API). */
export function hoyIso() {
  const ahora = new Date();
  const m = String(ahora.getMonth() + 1).padStart(2, "0");
  const d = String(ahora.getDate()).padStart(2, "0");
  return `${ahora.getFullYear()}-${m}-${d}`;
}
