// Definición de las 15 entidades en la interfaz web (equivalente a menus.py de la consola).
//
// columnas: [campo, etiqueta, formato?]  (formato: dinero, hora, fecha, fechaHora, sino,
//           porcentaje, "estado" o un diccionario de traducción)
// campos:   { nombre, etiqueta, tipo, obligatorio, ... }
//   tipo: texto, area, entero, decimal, fecha, hora, fechaHora, email, telefono, password,
//         opcion (con opciones), sino, ref (con ref)
//   obligatorio: true | false | "crear" | "editar"
//   soloCrear / soloEditar: el campo solo aparece al registrar / al actualizar
//   visibleSi(valores): si devuelve false el campo se oculta y se envía null
// filtro:   campo obligatorio para listar (ej. el barbero de los horarios)

import { api } from "./api.js";
import { dinero, fechaHora, hora } from "./formato.js";

export const DIAS = {
  Monday: "Lunes", Tuesday: "Martes", Wednesday: "Miércoles", Thursday: "Jueves",
  Friday: "Viernes", Saturday: "Sábado", Sunday: "Domingo",
};
export const ESTADOS = { Pending: "Pendiente", Confirmed: "Confirmada", Completed: "Completada", Cancelled: "Cancelada" };
export const UBICACIONES = { Shop: "En barbería", Home: "A domicilio" };
export const PAGOS = { Cash: "Efectivo", Card: "Tarjeta", Transfer: "Transferencia" };

// Cambios de estado permitidos (los mismos que valida proc_update_appointment_status)
export const TRANSICIONES = { Pending: ["Confirmed", "Cancelled"], Confirmed: ["Completed", "Cancelled"] };

const PRECIO_MAX = 99999999.99;

// ------------------------------------------------------------------
// Listas para elegir registros relacionados (claves foráneas)
// ------------------------------------------------------------------

const R = {
  roles: { ruta: "roles", texto: (r) => r.name },
  usuarios: { ruta: "usuarios", texto: (r) => `${r.full_name} (${r.role_name})` },
  barberias: { ruta: "barberias", texto: (r) => `${r.name} - ${r.city}` },
  barberos: { ruta: "barberos", texto: (r) => r.barber_name + (r.is_active ? "" : " (inactivo)") },
  barberosActivos: { ruta: "barberos", texto: (r) => r.barber_name, filtrar: (r) => !!r.is_active },
  servicios: {
    ruta: "servicios",
    texto: (r) => `${r.name} - ${dinero(r.base_price)} / ${r.duration_minutes} min`,
  },
  citas: {
    ruta: "citas",
    texto: (r) => `${r.appointment_date} ${hora(r.start_time)} - ${r.customer_name} con ${r.barber_name} (${ESTADOS[r.status]})`,
  },
  productosConStock: {
    ruta: "productos/disponibles",
    texto: (r) => `${r.name} - ${dinero(r.selling_price)} (stock: ${r.stock_quantity})`,
  },
  ventas: {
    ruta: "ventas",
    texto: (r) => `${fechaHora(r.sale_datetime)} - ${r.customer_name || "Sin cliente"} - ${dinero(r.total_amount)}`,
  },
  proveedores: { ruta: "proveedores", texto: (r) => r.company_name },
};
R.citasAbiertas = { ...R.citas, filtrar: (r) => r.status in TRANSICIONES };

// Servicios que tiene asignados el barbero de la cita elegida
R.serviciosDeLaCita = {
  depende: "appointment_id",
  sinDependencia: "Elija primero la cita",
  id: "service_id",
  origen: async (valores) => {
    const cita = await api.obtener("citas", valores.appointment_id);
    return api.listar("servicios-barbero", { barber_id: cita.barber_id });
  },
  texto: (r) => `${r.service_name} - ${dinero(r.final_price)} / ${r.final_duration} min`,
  vacio: "El barbero de la cita no tiene servicios asignados (vea «Servicios por barbero»).",
};

const campoBarbero = (extra = {}) => ({ nombre: "barber_id", etiqueta: "Barbero", tipo: "ref", ref: R.barberos, ...extra });
const campoBarberia = (extra = {}) => ({ nombre: "barbershop_id", etiqueta: "Barbería", tipo: "ref", ref: R.barberias, ...extra });

const COLUMNAS_CITA = [
  ["id", "ID"], ["customer_name", "Cliente"], ["barber_name", "Barbero"],
  ["appointment_date", "Fecha", "fecha"], ["start_time", "Inicio", "hora"], ["end_time", "Fin", "hora"],
  ["location_type", "Lugar", UBICACIONES], ["status", "Estado", "estado"], ["total_amount", "Total", "dinero"],
];

const COLUMNAS_PRODUCTO = [
  ["id", "ID"], ["name", "Producto"], ["selling_price", "Precio", "dinero"],
  ["stock_quantity", "Stock"], ["min_stock_level", "Mínimo"],
  ["barbershop_name", "Barbería"], ["barber_name", "Barbero"], ["description", "Descripción"],
];

// ------------------------------------------------------------------
// Entidades
// ------------------------------------------------------------------

export const ENTIDADES = {
  roles: {
    titulo: "Roles", singular: "rol",
    columnas: [["id", "ID"], ["name", "Nombre"]],
    campos: [{ nombre: "name", etiqueta: "Nombre del rol", largo: 50, obligatorio: true }],
  },

  usuarios: {
    titulo: "Usuarios", singular: "usuario",
    columnas: [["id", "ID"], ["full_name", "Nombre"], ["email", "Correo"], ["phone", "Teléfono"],
      ["role_name", "Rol"], ["created_at", "Creado", "fechaHora"]],
    campos: [
      { nombre: "role_id", etiqueta: "Rol", tipo: "ref", ref: R.roles, obligatorio: true },
      { nombre: "full_name", etiqueta: "Nombre completo", largo: 100, obligatorio: true },
      { nombre: "email", etiqueta: "Correo electrónico", tipo: "email", largo: 100, obligatorio: true },
      { nombre: "phone", etiqueta: "Teléfono", tipo: "telefono", obligatorio: true },
      {
        nombre: "password", etiqueta: "Contraseña", tipo: "password", obligatorio: "crear", minimo: 6,
        ayuda: "Mínimo 6 caracteres. Al editar, déjela vacía para conservar la actual.",
      },
    ],
  },

  barberias: {
    titulo: "Barberías", singular: "barbería", femenino: true,
    columnas: [["id", "ID"], ["name", "Nombre"], ["address", "Dirección"], ["city", "Ciudad"],
      ["phone", "Teléfono"], ["manager_name", "Administrador"]],
    campos: [
      { nombre: "manager_id", etiqueta: "Administrador", tipo: "ref", ref: R.usuarios, obligatorio: true },
      { nombre: "name", etiqueta: "Nombre", largo: 100, obligatorio: true },
      { nombre: "city", etiqueta: "Ciudad", largo: 50, obligatorio: true },
      { nombre: "address", etiqueta: "Dirección", largo: 150, obligatorio: true },
      { nombre: "phone", etiqueta: "Teléfono", tipo: "telefono", obligatorio: true },
    ],
  },

  barberos: {
    titulo: "Barberos", singular: "barbero",
    columnas: [["id", "ID"], ["barber_name", "Nombre"], ["barbershop_name", "Barbería"],
      ["provides_home_service", "Domicilio", "sino"], ["provides_shop_service", "En local", "sino"],
      ["commission_rate", "Comisión", "porcentaje"], ["is_active", "Activo", "sino"]],
    campos: [
      { nombre: "user_id", etiqueta: "Usuario", tipo: "ref", ref: R.usuarios, obligatorio: true },
      campoBarberia({ obligatorio: false, ayuda: "Vacío si solo atiende a domicilio." }),
      { nombre: "commission_rate", etiqueta: "Comisión (%)", tipo: "decimal", obligatorio: true, minimo: 0, maximo: 100 },
      { nombre: "provides_home_service", etiqueta: "Atiende a domicilio", tipo: "sino" },
      { nombre: "provides_shop_service", etiqueta: "Atiende en barbería", tipo: "sino", defecto: 1 },
      { nombre: "is_active", etiqueta: "Activo", tipo: "sino", soloEditar: true },
    ],
  },

  horarios: {
    titulo: "Horarios de barberos", singular: "horario",
    columnas: [["id", "ID"], ["day_of_week", "Día", DIAS], ["start_time", "Entrada", "hora"],
      ["end_time", "Salida", "hora"], ["lunch_start_time", "Almuerzo desde", "hora"],
      ["lunch_end_time", "Almuerzo hasta", "hora"]],
    filtro: campoBarbero(),
    campos: [
      campoBarbero({ obligatorio: true }),
      { nombre: "day_of_week", etiqueta: "Día de la semana", tipo: "opcion", opciones: DIAS, obligatorio: true },
      { nombre: "start_time", etiqueta: "Hora de entrada", tipo: "hora", obligatorio: true },
      { nombre: "end_time", etiqueta: "Hora de salida", tipo: "hora", obligatorio: true },
      { nombre: "lunch_start_time", etiqueta: "Inicio del almuerzo", tipo: "hora", ayuda: "Vacío si no tiene almuerzo." },
      {
        nombre: "lunch_end_time", etiqueta: "Fin del almuerzo", tipo: "hora", obligatorio: true,
        visibleSi: (v) => v.lunch_start_time != null,
      },
    ],
  },

  bloqueos: {
    titulo: "Bloqueos de agenda", singular: "bloqueo",
    columnas: [["id", "ID"], ["start_datetime", "Desde", "fechaHora"], ["end_datetime", "Hasta", "fechaHora"],
      ["reason", "Motivo"]],
    filtro: campoBarbero(),
    campos: [
      campoBarbero({ obligatorio: true }),
      { nombre: "start_datetime", etiqueta: "Inicio", tipo: "fechaHora", obligatorio: true },
      { nombre: "end_datetime", etiqueta: "Fin", tipo: "fechaHora", obligatorio: true },
      { nombre: "reason", etiqueta: "Motivo", largo: 255, ancho: true },
    ],
  },

  servicios: {
    titulo: "Servicios", singular: "servicio",
    columnas: [["id", "ID"], ["name", "Servicio"], ["base_price", "Precio", "dinero"],
      ["duration_minutes", "Duración (min)"], ["buffer_minutes", "Preparación (min)"], ["description", "Descripción"]],
    campos: [
      { nombre: "name", etiqueta: "Nombre", largo: 100, obligatorio: true, ancho: true },
      { nombre: "base_price", etiqueta: "Precio base", tipo: "decimal", obligatorio: true, minimo: 0, maximo: PRECIO_MAX },
      { nombre: "duration_minutes", etiqueta: "Duración (minutos)", tipo: "entero", obligatorio: true, minimo: 1, maximo: 600 },
      {
        nombre: "buffer_minutes", etiqueta: "Tiempo de preparación (minutos)", tipo: "entero", minimo: 0, maximo: 240,
        ayuda: "Vacío = 10 minutos.",
      },
      { nombre: "description", etiqueta: "Descripción", tipo: "area", largo: 1000, ancho: true },
    ],
  },

  "servicios-barbero": {
    titulo: "Servicios por barbero", singular: "asignación", femenino: true,
    columnas: [["id", "ID"], ["service_name", "Servicio"], ["custom_price", "Precio propio", "dinero"],
      ["custom_duration_minutes", "Duración propia"], ["final_price", "Precio final", "dinero"],
      ["final_duration", "Duración final"]],
    filtro: campoBarbero(),
    campos: [
      campoBarbero({ obligatorio: true }),
      { nombre: "service_id", etiqueta: "Servicio", tipo: "ref", ref: R.servicios, obligatorio: true },
      {
        nombre: "custom_price", etiqueta: "Precio personalizado", tipo: "decimal", minimo: 0, maximo: PRECIO_MAX,
        ayuda: "Vacío = precio base del servicio.",
      },
      {
        nombre: "custom_duration_minutes", etiqueta: "Duración personalizada (min)", tipo: "entero", minimo: 1, maximo: 600,
        ayuda: "Vacío = duración del servicio.",
      },
    ],
  },

  citas: {
    titulo: "Citas", singular: "cita", femenino: true,
    columnas: COLUMNAS_CITA,
    pestanas: [
      { etiqueta: "Todas" },
      { etiqueta: "Pendientes", filtrar: (r) => r.status === "Pending" },
      { etiqueta: "Confirmadas", filtrar: (r) => r.status === "Confirmed" },
      { etiqueta: "Completadas", filtrar: (r) => r.status === "Completed" },
      { etiqueta: "Canceladas", filtrar: (r) => r.status === "Cancelled" },
    ],
    campos: [
      { nombre: "customer_id", etiqueta: "Cliente", tipo: "ref", ref: R.usuarios, obligatorio: true },
      campoBarbero({ ref: R.barberosActivos, obligatorio: true }),
      { nombre: "location_type", etiqueta: "Lugar de atención", tipo: "opcion", opciones: UBICACIONES, obligatorio: true, defecto: "Shop" },
      campoBarberia({
        obligatorio: false, ayuda: "Vacío = la barbería del barbero.",
        visibleSi: (v) => v.location_type === "Shop",
      }),
      {
        nombre: "home_address", etiqueta: "Dirección del domicilio", largo: 200, obligatorio: true, ancho: true,
        visibleSi: (v) => v.location_type === "Home",
      },
      { nombre: "appointment_date", etiqueta: "Fecha", tipo: "fecha", obligatorio: true },
      { nombre: "start_time", etiqueta: "Hora de inicio", tipo: "hora", obligatorio: true },
      { nombre: "end_time", etiqueta: "Hora de fin", tipo: "hora", obligatorio: true },
    ],
  },

  "servicios-cita": {
    titulo: "Servicios de citas", singular: "servicio de la cita",
    columnas: [["id", "ID"], ["service_name", "Servicio"], ["applied_price", "Precio", "dinero"],
      ["applied_duration_minutes", "Duración (min)"]],
    filtro: { nombre: "appointment_id", etiqueta: "Cita", tipo: "ref", ref: R.citas },
    campos: [
      { nombre: "appointment_id", etiqueta: "Cita", tipo: "ref", ref: R.citasAbiertas, obligatorio: true, soloCrear: true, ancho: true },
      { nombre: "service_id", etiqueta: "Servicio", tipo: "ref", ref: R.serviciosDeLaCita, obligatorio: true, soloCrear: true, ancho: true },
      {
        nombre: "applied_price", etiqueta: "Precio", tipo: "decimal", obligatorio: "editar", minimo: 0, maximo: PRECIO_MAX,
        ayuda: "Vacío = precio del barbero para ese servicio.",
      },
      {
        nombre: "applied_duration_minutes", etiqueta: "Duración (min)", tipo: "entero", obligatorio: "editar", minimo: 1, maximo: 600,
        ayuda: "Vacío = duración del barbero para ese servicio.",
      },
    ],
  },

  productos: {
    titulo: "Productos", singular: "producto",
    columnas: COLUMNAS_PRODUCTO,
    pestanas: [
      { etiqueta: "Todos" },
      { etiqueta: "Disponibles", ruta: "productos/disponibles" },
      { etiqueta: "Stock bajo", ruta: "productos/stock-bajo" },
    ],
    campos: [
      { nombre: "name", etiqueta: "Nombre", largo: 100, obligatorio: true, ancho: true },
      campoBarberia({ etiqueta: "Barbería dueña", obligatorio: false, ayuda: "Vacío si pertenece a un barbero." }),
      campoBarbero({ etiqueta: "Barbero dueño", obligatorio: false }),
      { nombre: "selling_price", etiqueta: "Precio de venta", tipo: "decimal", obligatorio: true, minimo: 0, maximo: PRECIO_MAX },
      { nombre: "stock_quantity", etiqueta: "Stock", tipo: "entero", obligatorio: true, minimo: 0, maximo: 1000000 },
      { nombre: "min_stock_level", etiqueta: "Stock mínimo", tipo: "entero", minimo: 0, maximo: 1000000, ayuda: "Vacío = 5." },
      { nombre: "description", etiqueta: "Descripción", tipo: "area", largo: 1000, ancho: true },
    ],
  },

  ventas: {
    titulo: "Ventas de productos", singular: "venta", femenino: true,
    columnas: [["id", "ID"], ["sale_datetime", "Fecha", "fechaHora"], ["customer_name", "Cliente"],
      ["seller_name", "Vendedor"], ["payment_method", "Pago", PAGOS], ["total_amount", "Total", "dinero"]],
    campos: [
      {
        nombre: "customer_id", etiqueta: "Cliente", tipo: "ref", ref: R.usuarios, obligatorio: false,
        ayuda: "Vacío si el cliente no está registrado.",
      },
      { nombre: "seller_user_id", etiqueta: "Vendedor", tipo: "ref", ref: R.usuarios, obligatorio: true },
      { nombre: "payment_method", etiqueta: "Método de pago", tipo: "opcion", opciones: PAGOS, obligatorio: true },
    ],
  },

  "detalle-ventas": {
    titulo: "Detalle de ventas", singular: "detalle",
    columnas: [["id", "ID"], ["product_name", "Producto"], ["quantity", "Cantidad"],
      ["unit_price", "Precio unitario", "dinero"], ["subtotal", "Subtotal", "dinero"]],
    filtro: { nombre: "product_sale_id", etiqueta: "Venta", tipo: "ref", ref: R.ventas },
    campos: [
      { nombre: "product_sale_id", etiqueta: "Venta", tipo: "ref", ref: R.ventas, obligatorio: true, soloCrear: true, ancho: true },
      { nombre: "product_id", etiqueta: "Producto", tipo: "ref", ref: R.productosConStock, obligatorio: true, soloCrear: true, ancho: true },
      { nombre: "quantity", etiqueta: "Cantidad", tipo: "entero", obligatorio: true, minimo: 1, maximo: 1000000, defecto: 1 },
      {
        nombre: "unit_price", etiqueta: "Precio unitario", tipo: "decimal", obligatorio: "editar", minimo: 0, maximo: PRECIO_MAX,
        ayuda: "Vacío = precio de venta del producto.",
      },
    ],
  },

  proveedores: {
    titulo: "Proveedores", singular: "proveedor",
    columnas: [["id", "ID"], ["company_name", "Empresa"], ["contact_name", "Contacto"],
      ["phone", "Teléfono"], ["email", "Correo"], ["address", "Dirección"]],
    campos: [
      { nombre: "company_name", etiqueta: "Empresa", largo: 100, obligatorio: true },
      { nombre: "contact_name", etiqueta: "Persona de contacto", largo: 100 },
      { nombre: "phone", etiqueta: "Teléfono", tipo: "telefono", obligatorio: true },
      { nombre: "email", etiqueta: "Correo electrónico", tipo: "email", largo: 100 },
      { nombre: "address", etiqueta: "Dirección", largo: 150, ancho: true },
    ],
  },

  compras: {
    titulo: "Compras a proveedores", singular: "compra", femenino: true,
    columnas: [["id", "ID"], ["purchase_datetime", "Fecha", "fechaHora"], ["company_name", "Proveedor"],
      ["barber_name", "Barbero"], ["barbershop_name", "Barbería"], ["tools_description", "Descripción"],
      ["total_paid", "Total", "dinero"]],
    campos: [
      { nombre: "supplier_id", etiqueta: "Proveedor", tipo: "ref", ref: R.proveedores, obligatorio: true },
      { nombre: "total_paid", etiqueta: "Total pagado", tipo: "decimal", obligatorio: true, minimo: 0.01, maximo: PRECIO_MAX },
      campoBarbero({ obligatorio: false }),
      campoBarberia({ obligatorio: false }),
      { nombre: "tools_description", etiqueta: "Descripción de lo comprado", tipo: "area", largo: 1000, obligatorio: true, ancho: true },
    ],
  },
};

// Agrupación del menú lateral
export const MENU = [
  { grupo: "Agenda", entidades: ["citas", "horarios", "bloqueos", "servicios", "servicios-barbero", "servicios-cita"] },
  { grupo: "Ventas e inventario", entidades: ["ventas", "detalle-ventas", "productos", "compras", "proveedores"] },
  { grupo: "Administración", entidades: ["usuarios", "roles", "barberias", "barberos"] },
];

for (const [clave, def] of Object.entries(ENTIDADES)) def.ruta = clave;
