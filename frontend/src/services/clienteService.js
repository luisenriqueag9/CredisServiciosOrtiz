const API_URL = "http://localhost:8000/clientes";

// Obtener todos los clientes
export const getClientes = async () => {
  try {
    const res = await fetch(API_URL);
    return await res.json();
  } catch (error) {
    console.error("Error obteniendo clientes:", error);
    return [];
  }
};

// Crear cliente
export const createCliente = async (cliente) => {
  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(cliente),
    });

    return await res.json();
  } catch (error) {
    console.error("Error creando cliente:", error);
    return null;
  }
};

export const deleteCliente = async (id) => {
  try {
    const res = await fetch(`http://localhost:8000/clientes/${id}`, {
      method: "DELETE",
    });

    return await res.json();
  } catch (error) {
    console.error("Error eliminando cliente:", error);
    return null;
  }
};

// Obtener cliente por ID
export const getClienteById = async (id) => {
  try {
    const res = await fetch(`${API_URL}/${id}`);
    return await res.json();
  } catch (error) {
    console.error("Error obteniendo cliente:", error);
    return null;
  }
};

// Actualizar cliente
export const updateCliente = async (id, cliente) => {
  try {
    const res = await fetch(`${API_URL}/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(cliente),
    });

    return await res.json();
  } catch (error) {
    console.error("Error actualizando cliente:", error);
    return null;
  }
};