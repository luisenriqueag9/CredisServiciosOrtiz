export default function PagosList({ pagos, onVerRecibo }) {
    return (
        <>
            <h3 style={{ marginTop: "30px" }}>Pagos realizados</h3>

            <table style={{ width: "100%", marginTop: "10px" }}>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Monto</th>
                        <th>Capital</th>
                        <th>Interés</th>
                        <th>Recibo</th>
                    </tr>
                </thead>

                <tbody>
                    {pagos?.length > 0 ? (
                        pagos.map((pago) => (
                            <tr key={pago.id}>
                                <td>
                                    {new Date(pago.fecha_pago).toLocaleDateString()}
                                </td>
                                <td>L {pago.monto_pagado}</td>
                                <td>L {pago.capital_pagado}</td>
                                <td>L {pago.interes_pagado}</td>
                                <td>
                                    <button onClick={() => onVerRecibo(pago.id)}>
                                        📄 Recibo
                                    </button>
                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="5">No hay pagos aún</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </>
    );
}