// Formulario genérico para registrar o actualizar un registro de cualquier entidad.

import { api } from "./api.js";
import { vacio } from "./formato.js";
import { dialogo, h, notificar } from "./ui.js";

const TIPOS_INPUT = {
  texto: "text", email: "email", telefono: "tel", password: "password",
  entero: "number", decimal: "number", fecha: "date", hora: "time", fechaHora: "datetime-local",
};

function esObligatorio(campo, editando) {
  if (campo.obligatorio === "crear") return !editando;
  if (campo.obligatorio === "editar") return editando;
  return campo.obligatorio === true;
}

function crearControl(campo, id) {
  if (campo.tipo === "area") {
    return h("textarea", { id, name: campo.nombre, rows: 3, maxlength: campo.largo || null });
  }
  if (campo.tipo === "sino") return h("input", { id, name: campo.nombre, type: "checkbox" });
  if (campo.tipo === "opcion" || campo.tipo === "ref") {
    const select = h("select", { id, name: campo.nombre });
    if (campo.tipo === "opcion") {
      select.append(h("option", { value: "" }, "Seleccione…"),
        Object.entries(campo.opciones).map(([valor, texto]) => h("option", { value: valor }, texto)));
    }
    return select;
  }
  const input = h("input", { id, name: campo.nombre, type: TIPOS_INPUT[campo.tipo] || "text" });
  if (campo.largo) input.maxLength = campo.largo;
  if (campo.tipo === "password") {
    input.autocomplete = "new-password";
    if (campo.minimo) input.minLength = campo.minimo;
  }
  if (campo.tipo === "entero" || campo.tipo === "decimal") {
    input.step = campo.tipo === "entero" ? "1" : "0.01";
    input.inputMode = campo.tipo === "entero" ? "numeric" : "decimal";
    if (campo.minimo !== undefined) input.min = campo.minimo;
    if (campo.maximo !== undefined) input.max = campo.maximo;
  }
  if (campo.tipo === "telefono") {
    input.pattern = "[0-9+() \\-]{7,20}";
    input.title = "Entre 7 y 20 caracteres: dígitos, espacios, + - ( )";
  }
  return input;
}

/** Valor de la API -> valor del control. */
function escribir(campo, input, valor) {
  if (campo.tipo === "sino") {
    input.checked = !!Number(valor);
    return;
  }
  if (vacio(valor)) {
    input.value = "";
    return;
  }
  let texto = String(valor);
  if (campo.tipo === "hora") {
    const [hh, mm] = texto.split(":");
    texto = `${hh.padStart(2, "0")}:${mm}`;
  }
  if (campo.tipo === "fechaHora") texto = texto.replace(" ", "T").slice(0, 16);
  if (campo.tipo === "fecha") texto = texto.slice(0, 10);
  if (campo.tipo === "ref") input.dataset.valor = texto; // se aplica cuando cargan las opciones
  input.value = texto;
}

/** Valor del control -> valor para la API (los números se envían como texto y la API los convierte). */
function leer(campo, input) {
  if (campo.tipo === "sino") return input.checked ? 1 : 0;
  const texto = input.value.trim();
  if (texto === "") return null;
  if (campo.tipo === "ref" || campo.tipo === "entero") return Number(texto);
  return texto;
}

/**
 * Abre el formulario de la entidad. Resuelve con el registro guardado, o null si se cancela.
 * fijos: valores que no se piden (ej. { appointment_id: 5 } al agregar un servicio a una cita).
 */
export function abrirFormulario(def, registro = null, fijos = {}) {
  return new Promise((resolver) => {
    const editando = registro !== null;
    const campos = def.campos.filter(
      (c) => (editando ? !c.soloCrear : !c.soloEditar) && !(c.nombre in fijos));
    const controles = new Map();
    let guardado = null;

    const aviso = h("div", { class: "aviso-error", role: "alert", hidden: true });
    const rejilla = h("div", { class: "rejilla-campos" });

    for (const campo of campos) {
      const id = `campo-${campo.nombre}`;
      const input = crearControl(campo, id);
      const obligatorio = esObligatorio(campo, editando);
      if (obligatorio && campo.tipo !== "sino") input.required = true;

      const marca = obligatorio ? h("span", { class: "requerido", "aria-hidden": "true" }, " *") : null;
      const control = campo.tipo === "sino"
        ? h("label", { class: "casilla", for: id }, input, h("span", {}, campo.etiqueta))
        : [h("label", { for: id }, campo.etiqueta, marca), input];
      const envoltura = h("div", { class: `campo${campo.ancho || campo.tipo === "area" ? " ancho" : ""}` },
        control, campo.ayuda ? h("small", { class: "ayuda" }, campo.ayuda) : null);

      rejilla.append(envoltura);
      controles.set(campo.nombre, { campo, input, envoltura, obligatorio });
      escribir(campo, input, editando ? registro[campo.nombre] : campo.defecto);
    }

    const valores = () => {
      const datos = { ...fijos };
      for (const [nombre, { campo, input, envoltura }] of controles) {
        datos[nombre] = envoltura.hidden ? null : leer(campo, input);
      }
      return datos;
    };

    function actualizarVisibilidad() {
      const actuales = valores();
      for (const { campo, input, envoltura } of controles.values()) {
        const visible = campo.visibleSi ? campo.visibleSi(actuales) : true;
        envoltura.hidden = !visible;
        input.disabled = !visible || input.dataset.cargando === "1";
      }
    }

    async function cargarOpciones({ campo, input, obligatorio }) {
      const ref = campo.ref;
      const elegido = input.dataset.valor ?? input.value;
      const primera = obligatorio ? "Seleccione…" : "— Ninguno —";
      input.dataset.cargando = "1";
      input.disabled = true;
      input.replaceChildren(h("option", { value: "" }, "Cargando…"));
      try {
        if (ref.depende && vacio(valores()[ref.depende])) {
          input.replaceChildren(h("option", { value: "" }, ref.sinDependencia || "Complete el campo anterior"));
          return;
        }
        let filas = ref.origen ? await ref.origen(valores()) : await api.listar(ref.ruta);
        const idCol = ref.id || "id";
        // El valor actual se conserva aunque ya no cumpla el filtro (ej. un barbero ahora inactivo)
        if (ref.filtrar) filas = filas.filter((f) => ref.filtrar(f) || String(f[idCol]) === elegido);
        input.replaceChildren(
          h("option", { value: "" }, filas.length ? primera : ref.vacio || "No hay registros disponibles"),
          filas.map((f) => h("option", { value: String(f[idCol]) }, ref.texto(f))));
        input.value = elegido || "";
        if (input.value !== (elegido || "")) input.value = "";
      } catch (error) {
        input.replaceChildren(h("option", { value: "" }, "No se pudieron cargar las opciones"));
        mostrarError(error.message);
      } finally {
        delete input.dataset.valor;
        delete input.dataset.cargando;
        actualizarVisibilidad();
      }
    }

    function mostrarError(mensaje) {
      aviso.textContent = mensaje;
      aviso.hidden = false;
    }

    rejilla.addEventListener("change", (ev) => {
      const nombre = ev.target.name;
      actualizarVisibilidad();
      for (const ctrl of controles.values()) {
        if (ctrl.campo.tipo === "ref" && ctrl.campo.ref.depende === nombre) cargarOpciones(ctrl);
      }
    });

    const botonGuardar = h("button", { class: "boton primario", type: "submit" }, editando ? "Guardar cambios" : "Registrar");
    const formulario = h("form", { class: "formulario", novalidate: false },
      aviso, rejilla,
      h("div", { class: "dialogo-pie" },
        h("button", { class: "boton", type: "button", onclick: () => d.cerrar() }, "Cancelar"),
        botonGuardar));

    formulario.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      aviso.hidden = true;
      if (!formulario.reportValidity()) return;

      const datos = valores();
      // Al editar, una contraseña vacía significa "conservar la actual"
      for (const { campo } of controles.values()) {
        if (campo.tipo === "password" && datos[campo.nombre] === null) delete datos[campo.nombre];
      }
      botonGuardar.disabled = true;
      botonGuardar.textContent = "Guardando…";
      try {
        guardado = editando
          ? await api.actualizar(def.ruta, registro.id, datos)
          : await api.crear(def.ruta, datos);
        const final = def.femenino ? "a" : "o";
        const nombre = def.singular.charAt(0).toUpperCase() + def.singular.slice(1);
        notificar(`${nombre} ${editando ? "actualizad" : "registrad"}${final}.`);
        d.cerrar();
      } catch (error) {
        mostrarError(error.message);
        aviso.scrollIntoView({ block: "nearest" });
      } finally {
        botonGuardar.disabled = false;
        botonGuardar.textContent = editando ? "Guardar cambios" : "Registrar";
      }
    });

    const articulo = def.femenino ? "una" : "un";
    const d = dialogo({
      titulo: editando ? `Editar ${def.singular} #${registro.id}` : `Registrar ${articulo} ${def.singular}`,
      contenido: formulario,
      alCerrar: () => resolver(guardado),
    });

    actualizarVisibilidad();
    for (const ctrl of controles.values()) {
      if (ctrl.campo.tipo === "ref") cargarOpciones(ctrl);
    }
    // Foco en el primer campo editable
    requestAnimationFrame(() => formulario.querySelector("input:not([disabled]), select:not([disabled]), textarea")?.focus());
  });
}
