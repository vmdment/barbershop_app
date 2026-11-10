// Cliente de la API REST (/api). Devuelve el contenido de "Respuesta" o lanza ErrorApi con el "Error".

export class ErrorApi extends Error {
  constructor(mensaje, codigo) {
    super(mensaje);
    this.codigo = codigo;
  }
}

async function peticion(metodo, ruta, cuerpo) {
  const opciones = { method: metodo, headers: {} };
  if (cuerpo !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(cuerpo);
  }
  let respuesta;
  try {
    respuesta = await fetch(`/api/${ruta}`, opciones);
  } catch {
    throw new ErrorApi("No se pudo conectar con el servidor. Verifique que api.py esté corriendo.", 0);
  }
  let datos = null;
  try {
    datos = await respuesta.json();
  } catch {
    /* respuesta sin JSON */
  }
  if (!respuesta.ok) {
    throw new ErrorApi(datos?.Error || `Error ${respuesta.status} del servidor.`, respuesta.status);
  }
  return datos?.Respuesta;
}

export const api = {
  listar: (ruta, parametros) =>
    peticion("GET", ruta + (parametros ? `?${new URLSearchParams(parametros)}` : "")),
  obtener: (ruta, id) => peticion("GET", `${ruta}/${id}`),
  crear: (ruta, datos) => peticion("POST", ruta, datos),
  actualizar: (ruta, id, datos) => peticion("PUT", `${ruta}/${id}`, datos),
  eliminar: (ruta, id) => peticion("DELETE", `${ruta}/${id}`),
  cambiarEstadoCita: (id, status) => peticion("PATCH", `citas/${id}/estado`, { status }),
};
