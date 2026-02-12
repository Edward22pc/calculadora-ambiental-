import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Eco-Consultor Pro | Edward Pérez", layout="wide")

# --- BARRA LATERAL (ORDEN INVERTIDO) ---
with st.sidebar:
    # A. Primero la funcionalidad
    st.header("⚙️ Configuración")
    archivo = st.file_uploader("Subir base de datos Consumos_2025.xlsx", type=["xlsx"])
    fe_personalizado = st.number_input("Factor de Emisión (tCO2e/MWh)", value=0.444, format="%.3f")
    st.caption("Nota: El factor 0.444 es el oficial 2024 para reportes 2025.")
    
    st.divider()
    
    # B. Segundo el autor
    st.markdown("### 👨‍💻 Responsable del Proyecto")
    try:
        st.image("mi_foto.jpg", width=150)
    except:
        st.image("mi_foto.jpg", width=100)
    
    st.markdown(f"""
    **Ing. Edward Pérez Coello**
    *Ingeniero en Tecnología Ambiental*
    
    Especialista en cumplimiento normativo (RENE/LGCC).
    """)
    st.link_button("🌐 LinkedIn", "https://www.linkedin.com/in/edward-perez-3b9005176/")
    st.link_button("📧 Contactar", "mailto:edwardperezcoello@outlook.com")

# 2. FUNCIONES DE APOYO
def evaluar_normativa(emisiones_totales):
    if emisiones_totales >= 25000:
        return "⚠️ OBLIGADO A REPORTE RENE", "error", "Su empresa excede las 25,000 tCO2e anuales. Requiere reporte obligatorio y verificación por un tercero."
    elif emisiones_totales >= 15000:
        return "🟡 PRECAUCIÓN", "warning", "Se encuentra en el rango preventivo. Se recomienda monitoreo mensual para evitar sanciones."
    else:
        return "✅ CUMPLIMIENTO VOLUNTARIO", "success", "Su empresa se encuentra por debajo del umbral de reporte obligatorio."

def to_excel(df, estatus_texto):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos_Emisiones')
        resumen = pd.DataFrame({
            'Concepto': ['Total Emisiones tCO2e', 'Estatus Normativo', 'Factor Emisión'],
            'Valor': [df['tCO2e'].sum(), estatus_texto, "0.444 (SEN 2024)"]
        })
        resumen.to_excel(writer, index=False, sheet_name='Resumen_Normativo')
    return output.getvalue()

# 3. INTERFAZ PRINCIPAL
st.title("🌱 Sistema de Gestión de Emisiones GEI")

if archivo is not None:
    # Cálculos
    df = pd.read_excel(archivo)
    df['tCO2e'] = df['Consumo_kWh'] * (fe_personalizado / 1000)
    total_emisiones = df['tCO2e'].sum()
    
    # --- SECCIÓN DE SEMÁFORO Y EXPLICACIÓN ---
    st.subheader("📋 Diagnóstico de Cumplimiento (Normatividad Mexicana)")
    
    # Cuadro explicativo de la simbología
    with st.expander("🔍 Ver Simbolismo del Semáforo Normativo"):
        col1, col2, col3 = st.columns(3)
        col1.error("**Rojo:** > 25,000 tCO2e\n(Reporte RENE Obligatorio)")
        col2.warning("**Amarillo:** 15,000 - 25,000 tCO2e\n(Rango de Vigilancia)")
        col3.success("**Verde:** < 15,000 tCO2e\n(Reporte Voluntario)")

    # Resultado del semáforo
    titulo_estatus, tipo_alerta, explicacion = evaluar_normativa(total_emisiones)
    
    if tipo_alerta == "error":
        st.error(f"### {titulo_estatus}\n{explicacion}")
    elif tipo_alerta == "warning":
        st.warning(f"### {titulo_estatus}\n{explicacion}")
    else:
        st.success(f"### {titulo_estatus}\n{explicacion}")

    # --- GRÁFICA ---
    st.subheader("📊 Análisis Comparativo de Emisiones")
    fig = px.bar(df, x='Mes', y='tCO2e', color='Planta', barmode='group',
                 text_auto='.2f', title="Toneladas de CO2e por Planta")
    st.plotly_chart(fig, use_container_width=True)

    # --- EXPORTAR ---
    excel_data = to_excel(df, titulo_estatus)
    st.download_button(
        label="📥 Descargar Reporte y Diagnóstico en Excel",
        data=excel_data,
        file_name="Reporte_Ambiental_EdwardPerez.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:

    st.info("👋 **Bienvenido!.** Por favor, carge el archivo Excel en el menú de la izquierda para generar el diagnóstico normativo.")
