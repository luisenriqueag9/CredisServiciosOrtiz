import { useEffect, useState } from "react";

export const useCredito = (creditoId) => {
    const [resumen, setResumen] = useState(null);
    const [loading, setLoading] = useState(true);
    const [pagando, setPagando] = useState(false);

    const fetchResumen = async () => {
        setLoading(true);

        try {
            const res = await fetch(
                `http://localhost:8000/creditos/${creditoId}/resumen`
            );

            if (!res.ok) throw new Error("Error en la petición");

            const data = await res.json();

            if (data.success) {
                setResumen(data.data);
            }
        } catch (error) {
            console.error("Error cargando crédito:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchResumen();
    }, [creditoId]);

    const pagar = async (payload) => {
        setPagando(true);

        try {
            const res = await fetch(`http://localhost:8000/pagos/rapido`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (!res.ok) throw new Error("Error en la petición");

            const data = await res.json();

            if (!data.success) {
                throw new Error("Error al registrar pago");
            }

            const nuevoPago = data.data;

            setResumen((prev) => {
                if (!prev) return prev;

                return {
                    ...prev,
                    pagos_list: [nuevoPago, ...(prev.pagos_list || [])],
                    pagos: {
                        ...prev.pagos,
                        total: (prev.pagos?.total || 0) + nuevoPago.monto_pagado,
                    },
                    credito: {
                        ...prev.credito,
                        saldo_actual:
                            (prev.credito?.saldo_actual || 0) - nuevoPago.capital_pagado,
                    },
                };
            });

            return { ok: true, pago: nuevoPago };

        } catch (error) {
            console.error(error);
            return { ok: false };
        } finally {
            setPagando(false);
        }
    };

    return {
        resumen,
        loading,
        refetch: fetchResumen,
        pagar,
        pagando,
    };
};