import { useNavigate, useParams } from "react-router-dom";
import { getClienteById } from "../../clientes/services/clienteService";
import React, { useEffect, useState } from "react";


export default function CreditoFormWrapper() {
    const { cliente_id } = useParams();
    const navigate = useNavigate();

    const formatearIdentidad = (valor) => {
        const limpio = valor.replace(/\D/g, "").slice(0, 13);

        if (limpio.length <= 4) return limpio;
        if (limpio.length <= 8) return `${limpio.slice(0, 4)}-${limpio.slice(4)}`;
        return `${limpio.slice(0, 4)}-${limpio.slice(4, 8)}-${limpio.slice(8)}`;
    };

    const formatearTelefono = (valor) => {
        const limpio = valor.replace(/\D/g, "").slice(0, 8);

        if (limpio.length <= 4) return limpio;
        return `${limpio.slice(0, 4)}-${limpio.slice(4)}`;
    };

    const [monto, setMonto] = useState("");
    const [plazo, setPlazo] = useState("");
    const [tasa, setTasa] = useState("");
    const [tipoPeriodo, setTipoPeriodo] = useState("MENSUAL");
    const [tipoPlan, setTipoPlan] = useState("CUOTA_FIJA");
    const [cliente, setCliente] = useState(null);
    const [avalNombre, setAvalNombre] = useState("");
    const [avalIdentidad, setAvalIdentidad] = useState("");
    const [garantias, setGarantias] = useState([]);
    const [usarGarantias, setUsarGarantias] = useState(false);
    const [resumen, setResumen] = useState(null);
    const [paso, setPaso] = useState(1);
    const [refinanciar, setRefinanciar] = useState(false);
    const [estadoRefinanciar, setEstadoRefinanciar] = useState(null);
    const [pagoMensual, setPagoMensual] = useState("");
    const [avalTelefono, setAvalTelefono] = useState("");
    const [avalDireccion, setAvalDireccion] = useState("");
    const [resultado, setResultado] = useState(null);

    useEffect(() => {
        const fetchCliente = async () => {
            const data = await getClienteById(cliente_id);
            setCliente(data);
        };

        fetchCliente();
    }, [cliente_id]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        const data = {
            credito: {
                monto: Number(monto),
                tasa: Number(tasa),
                ...(tipoPlan === "CUOTA_FIJA" && {
                    cuotas: Number(plazo),
                }),
                ...(tipoPlan === "CAPITAL_FIJO" && {
                    pago_mensual: Number(pagoMensual),
                }),
                fecha_inicio: new Date().toISOString().split("T")[0],
                tipo_periodo: tipoPeriodo,
                tipo_plan: tipoPlan,
                aval: avalNombre && avalIdentidad
                    ? {
                        nombre: avalNombre,
                        identidad: avalIdentidad.replace(/\D/g, ""),
                        telefono: avalTelefono.replace(/\D/g, ""),
                        direccion: avalDireccion
                    }
                    : null,
                garantias: garantias.map(g => ({
                    tipo: g.tipo,
                    descripcion: g.descripcion
                })),
                refinanciar: refinanciar,
            },
            cliente: cliente
        };

        try {
            const res = await fetch("http://localhost:8000/creditos/procesar", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await res.json();

            if (result.success) {
                setResultado(result.data); // 👈 guardar resultado

            } else {
                alert("❌ " + (result.detail || result.message || "Error al crear crédito"));
            }

        } catch (error) {
            console.error(error);
        }
    };

    const agregarGarantia = () => {
        setGarantias([
            ...garantias,
            { tipo: "", descripcion: "" }
        ]);
    };

    const actualizarGarantia = (index, campo, valor) => {
        const nuevas = [...garantias];
        nuevas[index][campo] = valor;
        setGarantias(nuevas);
    };

    const handleSimular = async () => {
        try {
            const credito = {
                monto: Number(monto),
                tasa: Number(tasa),
                tipo_plan: tipoPlan,
                tipo_periodo: tipoPeriodo
            };

            if (tipoPlan === "CUOTA_FIJA") {
                credito.cuotas = Number(plazo);
            }

            if (tipoPlan === "CAPITAL_FIJO") {
                credito.pago_mensual = Number(pagoMensual);
            }

            const res = await fetch("http://localhost:8000/planes/simular-resumen", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ credito })
            });

            const data = await res.json();

            if (data.success) {
                setResumen(data.data);
            } else {
                alert(data.message || data.detail || "Error al simular");
            }

        } catch (error) {
            console.error(error);
        }
    };
    const verificarRefinanciamiento = async () => {
        try {
            const res = await fetch(`http://localhost:8000/creditos/cliente/${cliente_id}`);
            const data = await res.json();

            if (data.success && data.data.length > 0) {
                const credito = data.data[0];

                const monto = Number(credito.monto);
                const saldo = Number(credito.saldo_actual);

                const pagado = monto - saldo;
                const porcentaje = (pagado / monto) * 100;

                if (porcentaje >= 70) {
                    setEstadoRefinanciar({
                        tipo: "ok",
                        mensaje: "Este cliente puede refinanciar crédito"
                    });
                } else {
                    setEstadoRefinanciar({
                        tipo: "error",
                        mensaje: `No puede refinanciar (solo ha pagado ${porcentaje.toFixed(2)}%)`
                    });
                }
            }

        } catch (error) {
            console.error(error);
        }
    };
    return (
        <div className="card">

            <button onClick={() => navigate(`/clientes/${cliente_id}`)}>
                ← Volver
            </button>

            <h2>Nuevo Crédito</h2>

            <form onSubmit={handleSubmit}>

                {/* 🔹 PRIMERO: TIPO DE PLAN */}
                <div style={{ marginBottom: "20px" }}>
                    <label>Tipo de plan</label>

                    <select
                        value={tipoPlan}
                        onChange={(e) => {
                            const nuevoTipo = e.target.value;

                            setTipoPlan(nuevoTipo);
                            setResumen(null);

                            // 🔥 LIMPIAR CAMPOS SEGÚN PLAN
                            setPlazo("");
                            setPagoMensual("");
                        }}
                    >
                        <option value="CUOTA_FIJA">Cuota fija</option>
                        <option value="CAPITAL_FIJO">Capital fijo</option>
                    </select>
                </div>

                {/* 🔹 MENSAJE (FUERA DEL SELECT) */}
                {tipoPlan === "CAPITAL_FIJO" && (
                    <div style={{
                        background: "#fef9c3",
                        padding: "10px",
                        borderRadius: "6px",
                        marginBottom: "10px"
                    }}>
                        En este plan el capital no cambia, solo varían los intereses.
                    </div>
                )}

                {tipoPlan === "CUOTA_FIJA" && (
                    <div style={{
                        background: "#e0f2fe",
                        padding: "10px",
                        borderRadius: "6px",
                        marginBottom: "10px"
                    }}>
                        En este plan pagarás la misma cuota en todas las fechas.
                    </div>
                )}

                {/* 🔹 FORMULARIO SOLO SI ELIGE PLAN */}
                {tipoPlan && (
                    <div className="form-grid">

                        <input
                            type="number"
                            placeholder="Monto del crédito"
                            value={monto}
                            onChange={(e) => {
                                setMonto(e.target.value);
                                setResumen(null);
                            }}
                        />

                        {tipoPlan === "CUOTA_FIJA" && (
                            <input
                                type="number"
                                placeholder="Plazo (cuotas)"
                                value={plazo}
                                onChange={(e) => {
                                    setPlazo(e.target.value);
                                    setResumen(null);
                                }}
                            />
                        )}

                        {tipoPlan === "CAPITAL_FIJO" && (
                            <input
                                type="number"
                                placeholder="¿Cuánto puede pagar por cuota?"
                                value={pagoMensual}
                                onChange={(e) => {
                                    setPagoMensual(e.target.value);
                                    setResumen(null);
                                }}
                            />
                        )}

                        <input
                            type="number"
                            placeholder="Tasa de interés (%)"
                            value={tasa}
                            onChange={(e) => {
                                setTasa(e.target.value);
                                setResumen(null);
                            }}
                        />

                        <select
                            value={tipoPeriodo}
                            onChange={(e) => {
                                setTipoPeriodo(e.target.value);
                                setResumen(null);
                            }}
                        >
                            <option value="MENSUAL">Mensual</option>
                            <option value="SEMANAL">Semanal</option>
                        </select>

                        <div style={{ marginTop: "10px" }}>
                            <label>
                                <input
                                    type="checkbox"
                                    checked={refinanciar}
                                    onChange={(e) => setRefinanciar(e.target.checked)}
                                />
                                Refinanciar crédito
                            </label>
                        </div>

                    </div>
                )}
                <div style={{ marginTop: "15px" }}>
                    <button
                        type="button"
                        onClick={() => {
                            handleSimular();
                            /*verificarRefinanciamiento();*/
                        }}
                    >
                        Simular Crédito
                    </button>

                    {estadoRefinanciar && (
                        <div
                            style={{
                                marginTop: "10px",
                                padding: "10px",
                                borderRadius: "6px",
                                background:
                                    estadoRefinanciar.tipo === "ok" ? "#dcfce7" : "#fee2e2",
                                color:
                                    estadoRefinanciar.tipo === "ok" ? "#166534" : "#991b1b"
                            }}
                        >
                            {estadoRefinanciar.mensaje}
                        </div>
                    )}
                </div>

                {resumen && (
                    <div className="card" style={{ marginTop: "20px" }}>
                        <h3>Resumen del Crédito</h3>

                        <div className="detail-grid">
                            <div>
                                <label>Cuota</label>
                                <p>L {resumen.cuota}</p>
                            </div>

                            <div>
                                <label>Total a pagar</label>
                                <p>L {resumen.total_pagar}</p>
                            </div>

                            <div>
                                <label>Total interés</label>
                                <p>L {resumen.total_interes}</p>
                            </div>

                            <div>
                                <label>Número de cuotas</label>
                                <p>{resumen.cuotas}</p>
                            </div>

                            <div>
                                <label>Tasa</label>
                                <p>{tasa}% {tipoPeriodo.toLowerCase()}</p>
                            </div>

                            <div>
                                <label>Tipo de plan</label>
                                <p>{tipoPlan}</p>
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={() => setPaso(2)}
                            style={{ marginTop: "15px" }}
                        >
                            Continuar
                        </button>
                    </div>
                )}
                {paso >= 2 && (
                    <>
                        {/* 🔹 AVAL */}
                        <h3 style={{ marginTop: "20px" }}>Aval</h3>

                        <div className="form-grid">

                            <input
                                type="text"
                                placeholder="Nombre completo del aval"
                                value={avalNombre}
                                onChange={(e) => setAvalNombre(e.target.value)}
                            />

                            <input
                                type="text"
                                placeholder="Número de identidad"
                                value={formatearIdentidad(avalIdentidad)}
                                onChange={(e) =>
                                    setAvalIdentidad(e.target.value.replace(/\D/g, ""))
                                }
                            />

                            <input
                                type="text"
                                placeholder="Teléfono"
                                value={formatearTelefono(avalTelefono)}
                                onChange={(e) =>
                                    setAvalTelefono(e.target.value.replace(/\D/g, ""))
                                }
                            />

                            <input
                                type="text"
                                placeholder="Dirección"
                                value={avalDireccion || ""}
                                onChange={(e) => setAvalDireccion(e.target.value)}
                            />

                        </div>

                        {/* 🔹 GARANTÍAS */}
                        <h3 style={{ marginTop: "20px" }}>Garantías</h3>

                        <button
                            type="button"
                            onClick={() => {
                                setUsarGarantias(true);

                                if (garantias.length === 0) {
                                    agregarGarantia();
                                }
                            }}
                        >
                            + Agregar Garantía
                        </button>

                        <button
                            onClick={() => {
                                const telefono = "504" + cliente.telefono;
                                const mensaje = `Hola ${cliente.nombre}, aquí está su contrato: ${resultado.contrato_url}`;
                                const url = `https://wa.me/${telefono}?text=${encodeURIComponent(mensaje)}`;

                                window.open(url);
                            }}
                        >
                            Enviar por WhatsApp
                        </button>

                        {usarGarantias && garantias.map((g, index) => (
                            <div key={index} className="form-grid" style={{ marginTop: "10px" }}>
                                <input
                                    type="text"
                                    placeholder="Tipo"
                                    value={g.tipo}
                                    onChange={(e) =>
                                        actualizarGarantia(index, "tipo", e.target.value)
                                    }
                                />

                                <input
                                    type="text"
                                    placeholder="Descripción"
                                    value={g.descripcion}
                                    onChange={(e) =>
                                        actualizarGarantia(index, "descripcion", e.target.value)
                                    }
                                />
                            </div>
                        ))}

                        {/* 🔥 BOTÓN FINAL CORRECTO */}
                        <div style={{ marginTop: "30px" }}>
                            {resumen && (
                                <div style={{ marginTop: "30px" }}>
                                    <button type="submit">
                                        Finalizar Crédito
                                    </button>
                                </div>
                            )}
                        </div>
                    </>
                )}
            </form>

            {resultado && (
                <div style={{
                    marginTop: "20px",
                    padding: "15px",
                    borderRadius: "8px",
                    background: "#dcfce7"
                }}>
                    <h3>✅ Crédito creado correctamente</h3>

                    <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>

                        <button onClick={() => window.open(resultado.plan_url)}>
                            Ver Plan
                        </button>

                        <button onClick={() => window.open(resultado.pagare_url)}>
                            Ver Pagaré
                        </button>

                        <button onClick={() => window.open(resultado.contrato_url)}>
                            Ver Contrato
                        </button>

                    </div>
                </div>
            )}

            <p>Cliente ID: {cliente_id}</p>
        </div>
    );
}