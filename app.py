import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from io import BytesIO

# Configuración de página
st.set_page_config(
    
    page_title="Sistema de Gestión de Estabilidad",
    page_icon="📊",
    layout="wide"
)
st.markdown("""
<script>
    const html = window.parent.document.querySelector('html');
    html.lang = 'es';
</script>
""", unsafe_allow_html=True)

# Autenticación
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Iniciar Sesión")
        password = st.text_input("Contraseña", type="password")
        if password == "admin123":
            st.session_state.authenticated = True
            st.rerun()
        return False
    return True

# ==================== FUNCIONES DE CARGA Y GUARDADO ====================

def cargar_catalogo():
    """Carga el catálogo de productos"""
    try:
        if os.path.exists("data/catalogo.xlsx"):
            df = pd.read_excel("data/catalogo.xlsx", sheet_name="Catalogo")
            if len(df.columns) >= 3:
                nuevas_columnas = []
                for col in df.columns:
                    col_lower = str(col).lower().strip()
                    if 'cod' in col_lower or 'cód' in col_lower:
                        nuevas_columnas.append('Código')
                    elif 'producto' in col_lower or 'nombre' in col_lower:
                        nuevas_columnas.append('Producto')
                    elif 'forma' in col_lower or 'farmaceutica' in col_lower or 'farmac' in col_lower:
                        nuevas_columnas.append('Forma Farmacéutica')
                    else:
                        nuevas_columnas.append(col)
                df.columns = nuevas_columnas
            
            columnas_necesarias = ['Código', 'Producto', 'Forma Farmacéutica']
            for col in columnas_necesarias:
                if col not in df.columns:
                    df[col] = ''
            return df[columnas_necesarias].copy()
        else:
            return pd.DataFrame(columns=["Código", "Producto", "Forma Farmacéutica"])
    except Exception as e:
        st.error(f"Error al cargar catálogo: {e}")
        return pd.DataFrame(columns=["Código", "Producto", "Forma Farmacéutica"])

def guardar_catalogo(df_catalogo):
    """Guarda el catálogo de productos"""
    os.makedirs("data", exist_ok=True)
    with pd.ExcelWriter("data/catalogo.xlsx", engine="openpyxl") as writer:
        df_catalogo.to_excel(writer, sheet_name="Catalogo", index=False)

def cargar_datos():
    """Carga la base de datos de análisis"""
    try:
        if os.path.exists("data/estabilidad.xlsx"):
            df = pd.read_excel("data/estabilidad.xlsx", sheet_name="BaseDatos")
            if "Fecha Análisis" in df.columns:
                df["Fecha Análisis"] = pd.to_datetime(df["Fecha Análisis"], errors='coerce')
            if "Fecha Ingreso" in df.columns:
                df["Fecha Ingreso"] = pd.to_datetime(df["Fecha Ingreso"], errors='coerce')
            return df
        else:
            return pd.DataFrame(columns=[
                "Lote", "Fecha Ingreso", "Código", "Producto", 
                "Fecha Análisis", "Unidades", "Cantidad Total", "Unidad Medida",
                "Vto", "Observaciones", "Estado", 
                "Forma Farmacéutica", "Almacenamiento"
            ])
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame(columns=[
            "Lote", "Fecha Ingreso", "Código", "Producto", 
            "Fecha Análisis", "Unidades", "Cantidad Total", "Unidad Medida",
            "Vto", "Observaciones", "Estado", 
            "Forma Farmacéutica", "Almacenamiento"
        ])

def guardar_datos(df):
    """Guarda la base de datos de análisis"""
    os.makedirs("data", exist_ok=True)
    with pd.ExcelWriter("data/estabilidad.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="BaseDatos", index=False)
    st.cache_data.clear()

def exportar_datos(df):
    """Exporta datos a Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="BaseDatos", index=False)
    return output.getvalue()

# ==================== DATOS ESTÁTICOS ====================

PERIODOS = [
    {"nombre": "1 MES", "meses": 1, "texto": "1 mes"},
    {"nombre": "2 MESES", "meses": 2, "texto": "2 meses"},
    {"nombre": "3 MESES", "meses": 3, "texto": "3 meses"},
    {"nombre": "4 MESES", "meses": 4, "texto": "4 meses"},
    {"nombre": "5 MESES", "meses": 5, "texto": "5 meses"},
    {"nombre": "6 MESES", "meses": 6, "texto": "6 meses"},
    {"nombre": "9 MESES", "meses": 9, "texto": "9 meses"},
    {"nombre": "12 MESES", "meses": 12, "texto": "12 meses"},
    {"nombre": "18 MESES", "meses": 18, "texto": "18 meses"},
    {"nombre": "24 MESES", "meses": 24, "texto": "2 años"},
    {"nombre": "36 MESES", "meses": 36, "texto": "3 años"},
    {"nombre": "48 MESES", "meses": 48, "texto": "4 años"},
    {"nombre": "60 MESES", "meses": 60, "texto": "5 años"}
]

FORMAS_FARMACEUTICAS = ["Jarabe", "Solución Oral", "Tableta", "Cápsula", "Crema", "Inyectable", "Polvo"]
ALMACENAMIENTOS = ["30°C - 65%HR", "25°C - 60%HR", "40°C - 75%HR", "2°C - 8°C", "Nevera", "Ambiente"]
UNIDADES_MEDIDA = ["Cajas", "Ampollas", "Blister", "Frasco", "Tabletas", "Cápsulas", "mL", "Gramos", "Unidades"]
ESTADOS = ["PENDIENTE", "COMPLETADO", "CULMINADO"]
MESES = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

if not check_password():
    st.stop()

# Cargar datos
df = cargar_datos()
df_catalogo = cargar_catalogo()

# Menú lateral
menu = st.sidebar.selectbox(
    "📋 MENÚ PRINCIPAL",
    ["📝 Ingresar Lote", "🔍 Buscar Productos", "📚 Administrar Catálogo", "📤 Exportar Datos"]
)

# ==================== INGRESAR LOTE ====================
if menu == "📝 Ingresar Lote":
    st.title("📝 INGRESAR NUEVO LOTE")
    st.markdown("---")
    
    codigos_disponibles = df_catalogo["Código"].astype(str).tolist() if not df_catalogo.empty else []
    
    if not codigos_disponibles:
        st.warning("⚠️ El catálogo está vacío. Ve a 'Administrar Catálogo' para agregar productos.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        lote = st.text_input("LOTE *", key="lote")
        fecha_ingreso = st.date_input("FECHA INGRESO *", datetime.now(), key="fecha_ingreso")
    
    with col2:
        if codigos_disponibles:
            codigo_seleccionado = st.selectbox(
                "CÓDIGO PRODUCTO", 
                ["(Nuevo)"] + codigos_disponibles,
                key="codigo_select"
            )
        else:
            codigo_seleccionado = "(Nuevo)"
        
        if codigo_seleccionado == "(Nuevo)":
            codigo = st.text_input("NUEVO CÓDIGO", key="codigo_nuevo")
        else:
            codigo = codigo_seleccionado
    
    with col3:
        producto_valor = ""
        forma_valor = FORMAS_FARMACEUTICAS[0]

        if codigo_seleccionado != "(Nuevo)" and codigos_disponibles:
            producto_info = df_catalogo[df_catalogo["Código"].astype(str) == codigo_seleccionado]
            
            if not producto_info.empty:
                producto_valor = str(producto_info.iloc[0]["Producto"]) if pd.notna(producto_info.iloc[0]["Producto"]) else ""
                forma_temp = str(producto_info.iloc[0]["Forma Farmacéutica"]) if pd.notna(producto_info.iloc[0]["Forma Farmacéutica"]) else ""
                
                if forma_temp in FORMAS_FARMACEUTICAS:
                    forma_valor = forma_temp

        if codigo_seleccionado != "(Nuevo)":
            st.session_state["producto"] = producto_valor
            st.session_state["forma"] = forma_valor
        else:
            if "producto" not in st.session_state:
                st.session_state["producto"] = ""
            if "forma" not in st.session_state:
                st.session_state["forma"] = FORMAS_FARMACEUTICAS[0]

        producto = st.text_input("PRODUCTO *", key="producto")

        forma = st.selectbox(
            "FORMA FARMACÉUTICA",
            FORMAS_FARMACEUTICAS,
            index=FORMAS_FARMACEUTICAS.index(st.session_state["forma"]) 
            if st.session_state["forma"] in FORMAS_FARMACEUTICAS else 0,
            key="forma"
        )
    
    almacenamiento = st.selectbox("ALMACENAMIENTO *", ALMACENAMIENTOS, key="almacenamiento")
    
    st.markdown("---")
    st.subheader("📋 PROGRAMACIÓN DE ANÁLISIS")
    st.caption("Complete solo los períodos que va a analizar")
    
    periodos_data = []
    
    for i, periodo in enumerate(PERIODOS):
        with st.container():
            col_a, col_b, col_c, col_d, col_e, col_f, col_g = st.columns([1, 1.5, 0.8, 0.8, 1, 1.5, 1.2])
            
            with col_a:
                st.write(f"**{periodo['nombre']}**")
            
            with col_b:
                fecha_analisis = fecha_ingreso + timedelta(days=periodo['meses'] * 30)
                fecha_seleccionada = st.date_input(
                    "", 
                    fecha_analisis, 
                    key=f"fecha_{i}",
                    label_visibility="collapsed"
                )
            
            with col_c:
                unidades = st.number_input(
                    "", 
                    min_value=0, 
                    value=0, 
                    key=f"unidades_{i}",
                    label_visibility="collapsed"
                )
            
            with col_d:
                cantidad = st.number_input(
                    "", 
                    min_value=0, 
                    value=0, 
                    key=f"cantidad_{i}",
                    label_visibility="collapsed"
                )
            
            with col_e:
                unidad_medida = st.selectbox(
                    "", 
                    UNIDADES_MEDIDA, 
                    index=0,
                    key=f"umedida_{i}",
                    label_visibility="collapsed"
                )
            
            with col_f:
                vto_options = ["---", "1 mes", "2 meses", "3 meses", "4 meses", "5 meses", 
                               "6 meses", "9 meses", "12 meses", "18 meses", "2 años", 
                               "3 años", "4 años", "5 años"]
                vto = st.selectbox(
                    "", 
                    vto_options, 
                    index=0,
                    key=f"vto_{i}",
                    label_visibility="collapsed"
                )
            
            with col_g:
                estado = st.selectbox(
                    "", 
                    ESTADOS, 
                    index=0,
                    key=f"estado_{i}",
                    label_visibility="collapsed"
                )
            
            observaciones = st.text_input(
                f"📝 Observaciones para {periodo['nombre']}",
                placeholder="Escriba observaciones aquí...",
                key=f"obs_{i}",
                label_visibility="collapsed"
            )
            
            if unidades > 0 or cantidad > 0:
                periodos_data.append({
                    "Lote": lote,
                    "Fecha Ingreso": fecha_ingreso,
                    "Código": codigo,
                    "Producto": producto,
                    "Fecha Análisis": fecha_seleccionada,
                    "Unidades": unidades,
                    "Cantidad Total": cantidad,
                    "Unidad Medida": unidad_medida,
                    "Vto": vto,
                    "Observaciones": observaciones,
                    "Estado": estado,
                    "Forma Farmacéutica": forma,
                    "Almacenamiento": almacenamiento
                })
            
            st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 GUARDAR LOTE", type="primary", use_container_width=True):
            if not lote:
                st.error("❌ Complete el campo LOTE")
            elif not producto:
                st.error("❌ Complete el campo PRODUCTO")
            elif not almacenamiento:
                st.error("❌ Complete el campo ALMACENAMIENTO")
            elif len(periodos_data) == 0:
                st.error("❌ Debe completar al menos un período con Unidades o Cantidad Total > 0")
            else:
                df_nuevo = pd.DataFrame(periodos_data)
                df_actualizado = pd.concat([df, df_nuevo], ignore_index=True)
                guardar_datos(df_actualizado)
                
                if codigo_seleccionado == "(Nuevo)" and codigo:
                    nuevo_producto = pd.DataFrame([{
                        "Código": codigo,
                        "Producto": producto,
                        "Forma Farmacéutica": forma
                    }])
                    df_catalogo_actualizado = pd.concat([df_catalogo, nuevo_producto], ignore_index=True)
                    guardar_catalogo(df_catalogo_actualizado)
                    st.success(f"✅ Lote {lote} guardado. Producto {codigo} agregado al catálogo.")
                else:
                    st.success(f"✅ Lote {lote} guardado con {len(periodos_data)} períodos")
                st.rerun()
    
    with col2:
        if st.button("🗑️ LIMPIAR FORMULARIO", use_container_width=True):
            if "producto" in st.session_state:
                st.session_state["producto"] = ""
            if "forma" in st.session_state:
                st.session_state["forma"] = FORMAS_FARMACEUTICAS[0]
            st.rerun()

# ==================== BUSCAR PRODUCTOS ====================
elif menu == "🔍 Buscar Productos":
    st.title("🔍 BUSCAR PRODUCTOS")
    st.markdown("---")
    
    if not df.empty:
        st.subheader("📅 FILTROS DE BÚSQUEDA")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            busqueda = st.text_input("Buscar por LOTE, PRODUCTO o CÓDIGO", placeholder="Ej: 2100000")
        
        with col2:
            mes_filtro = st.selectbox("Mes de Análisis", MESES, key="mes_filtro")
        
        with col3:
            años = ["Todos"] + sorted(df["Fecha Análisis"].dt.year.unique().tolist()) if not df.empty else ["Todos"]
            año_filtro = st.selectbox("Año de Análisis", años, key="año_filtro")
        
        with col4:
            periodo_filtro = st.selectbox("Período", ["Todos"] + [p["nombre"] for p in PERIODOS], key="periodo_filtro")
        
        resultados = df.copy()
        
        resultados = resultados.dropna(subset=["Fecha Análisis"])
        
        if busqueda:
            busqueda_lower = busqueda.lower()
            resultados = resultados[
                resultados["Lote"].astype(str).str.lower().str.contains(busqueda_lower, na=False) |
                resultados["Producto"].astype(str).str.lower().str.contains(busqueda_lower, na=False) |
                resultados["Código"].astype(str).str.lower().str.contains(busqueda_lower, na=False)
            ]
        
        if mes_filtro != "Todos":
            mes_num = MESES.index(mes_filtro)
            resultados = resultados[resultados["Fecha Análisis"].dt.month == mes_num]
        
        if año_filtro != "Todos":
            resultados = resultados[resultados["Fecha Análisis"].dt.year == int(año_filtro)]
        
        if periodo_filtro != "Todos":
            periodo_texto = [p["texto"] for p in PERIODOS if p["nombre"] == periodo_filtro]
            if periodo_texto:
                resultados = resultados[resultados["Vto"] == periodo_texto[0]]
        
        st.markdown("---")
        st.markdown(f"**🔍 {len(resultados)} resultados encontrados**")
        st.markdown("---")
        
        if not resultados.empty:
            lotes_unicos = resultados["Lote"].unique()
            
            for lote in lotes_unicos:
                df_lote = resultados[resultados["Lote"] == lote]
                
                with st.expander(f"📦 LOTE: {lote} - {df_lote.iloc[0]['Producto']}", expanded=True):
                    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                    with col_info1:
                        fecha_ingreso = df_lote.iloc[0]['Fecha Ingreso']
                        fecha_str = fecha_ingreso.strftime('%d/%m/%Y') if pd.notna(fecha_ingreso) else '-'
                        st.write(f"**Fecha Ingreso:** {fecha_str}")
                    with col_info2:
                        st.write(f"**Código:** {df_lote.iloc[0]['Código'] if pd.notna(df_lote.iloc[0]['Código']) else '-'}")
                    with col_info3:
                        st.write(f"**Forma:** {df_lote.iloc[0]['Forma Farmacéutica']}")
                    with col_info4:
                        st.write(f"**Almacenamiento:** {df_lote.iloc[0]['Almacenamiento']}")
                    
                    st.write("---")
                    
                    tabla_mostrar = df_lote[[
                        "Vto", "Fecha Análisis", "Unidades", "Cantidad Total", 
                        "Unidad Medida", "Observaciones", "Estado"
                    ]].copy()
                    
                    tabla_mostrar.columns = ["Período", "Fecha Análisis", "Unidades", "Cantidad", "Unidad Medida", "Observaciones", "Estado"]
                    tabla_mostrar["Fecha Análisis"] = tabla_mostrar["Fecha Análisis"].dt.strftime("%d/%m/%Y")
                    
                    st.dataframe(tabla_mostrar, use_container_width=True)
                    
                    st.write("---")
                    if st.button(f"✏️ Editar {lote}", key=f"edit_{lote}"):
                        st.session_state.editando = lote
                        st.session_state.datos_edicion = df_lote.to_dict('records')
                        st.rerun()
            
            if st.button("📥 Exportar resultados actuales", use_container_width=True):
                excel_data = exportar_datos(resultados)
                st.download_button(
                    label="📥 DESCARGAR EXCEL",
                    data=excel_data,
                    file_name=f"resultados_busqueda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No se encontraron resultados. Cambie los filtros de búsqueda.")
    else:
        st.info("No hay datos cargados. Ingrese un lote primero.")

# ==================== ADMINISTRAR CATÁLOGO ====================
elif menu == "📚 Administrar Catálogo":
    st.title("📚 ADMINISTRAR CATÁLOGO DE PRODUCTOS")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📋 Ver Catálogo", "➕ Agregar Producto", "✏️ Editar/Eliminar"])
    
    with tab1:
        st.subheader("Productos Registrados")
        if not df_catalogo.empty:
            st.dataframe(df_catalogo, use_container_width=True)
            st.caption(f"Total de productos: {len(df_catalogo)}")
        else:
            st.info("No hay productos en el catálogo.")
    
    with tab2:
        st.subheader("Agregar Nuevo Producto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nuevo_codigo = st.text_input("CÓDIGO *", key="nuevo_codigo")
            nuevo_producto = st.text_input("PRODUCTO *", key="nuevo_producto_nombre")
        
        with col2:
            nueva_forma = st.selectbox("FORMA FARMACÉUTICA", FORMAS_FARMACEUTICAS, key="nueva_forma")
        
        if st.button("💾 Guardar Producto en Catálogo", type="primary"):
            if not nuevo_codigo:
                st.error("❌ Complete el campo CÓDIGO")
            elif not nuevo_producto:
                st.error("❌ Complete el campo PRODUCTO")
            else:
                if not df_catalogo.empty and nuevo_codigo in df_catalogo["Código"].astype(str).values:
                    st.error(f"❌ El código {nuevo_codigo} ya existe")
                else:
                    nuevo_registro = pd.DataFrame([{
                        "Código": nuevo_codigo,
                        "Producto": nuevo_producto,
                        "Forma Farmacéutica": nueva_forma
                    }])
                    df_catalogo_actualizado = pd.concat([df_catalogo, nuevo_registro], ignore_index=True)
                    guardar_catalogo(df_catalogo_actualizado)
                    st.success(f"✅ Producto {nuevo_codigo} agregado")
                    st.rerun()
    
    with tab3:
        st.subheader("Editar o Eliminar Producto")
        
        if not df_catalogo.empty:
            codigos_lista = df_catalogo["Código"].astype(str).tolist()
            codigo_editar = st.selectbox("Seleccionar producto", codigos_lista, key="codigo_editar")
            
            producto_seleccionado = df_catalogo[df_catalogo["Código"].astype(str) == codigo_editar].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                edit_codigo = st.text_input("Código", value=producto_seleccionado["Código"], key="edit_codigo")
                edit_producto = st.text_input("Producto", value=producto_seleccionado["Producto"], key="edit_producto")
            
            with col2:
                edit_forma = st.selectbox("Forma Farmacéutica", FORMAS_FARMACEUTICAS, 
                                           index=FORMAS_FARMACEUTICAS.index(producto_seleccionado["Forma Farmacéutica"]) if producto_seleccionado["Forma Farmacéutica"] in FORMAS_FARMACEUTICAS else 0,
                                           key="edit_forma")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Guardar Cambios", use_container_width=True):
                    df_catalogo.loc[df_catalogo["Código"].astype(str) == codigo_editar, "Código"] = edit_codigo
                    df_catalogo.loc[df_catalogo["Código"].astype(str) == edit_codigo, "Producto"] = edit_producto
                    df_catalogo.loc[df_catalogo["Código"].astype(str) == edit_codigo, "Forma Farmacéutica"] = edit_forma
                    guardar_catalogo(df_catalogo)
                    st.success("✅ Producto actualizado")
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Eliminar Producto", use_container_width=True):
                    if st.checkbox("Confirmar eliminación"):
                        df_catalogo = df_catalogo[df_catalogo["Código"].astype(str) != codigo_editar]
                        guardar_catalogo(df_catalogo)
                        st.success(f"✅ Producto eliminado")
                        st.rerun()
        else:
            st.info("No hay productos en el catálogo.")

# ==================== EXPORTAR DATOS ====================
elif menu == "📤 Exportar Datos":
    st.title("📤 EXPORTAR DATOS")
    st.markdown("---")
    
    if not df.empty:
        st.subheader("Resumen de datos")
        st.write(f"**Total registros:** {len(df)}")
        st.write(f"**Lotes únicos:** {df['Lote'].nunique()}")
        
        if not df_catalogo.empty:
            st.write(f"**Productos en catálogo:** {len(df_catalogo)}")
        
        st.markdown("---")
        st.subheader("Vista previa")
        st.dataframe(df.tail(20), use_container_width=True)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 EXPORTAR TODOS", type="primary", use_container_width=True):
                excel_data = exportar_datos(df)
                st.download_button(
                    label="📥 DESCARGAR",
                    data=excel_data,
                    file_name=f"exportacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col2:
            st.write("**Exportar por mes/año:**")
            mes_export = st.selectbox("Mes", MESES, key="mes_export")
            año_export = st.selectbox("Año", ["Todos"] + sorted(df["Fecha Análisis"].dt.year.unique().tolist()), key="año_export")
            
            if mes_export != "Todos" or año_export != "Todos":
                df_filtrado = df.copy()
                df_filtrado = df_filtrado.dropna(subset=["Fecha Análisis"])
                if mes_export != "Todos":
                    mes_num = MESES.index(mes_export)
                    df_filtrado = df_filtrado[df_filtrado["Fecha Análisis"].dt.month == mes_num]
                if año_export != "Todos":
                    df_filtrado = df_filtrado[df_filtrado["Fecha Análisis"].dt.year == int(año_export)]
                
                if not df_filtrado.empty:
                    st.write(f"**{len(df_filtrado)} registros**")
                    if st.button("📥 EXPORTAR FILTRADO", use_container_width=True):
                        excel_data = exportar_datos(df_filtrado)
                        st.download_button(
                            label="📥 DESCARGAR",
                            data=excel_data,
                            file_name=f"exportacion_filtrada_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("No hay datos para el filtro")
    else:
        st.info("No hay datos para exportar")

# ==================== EDITAR ANÁLISIS ====================
if 'editando' in st.session_state:
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"✏️ Editando: {st.session_state.editando}")
    
    datos_edicion = st.session_state.datos_edicion
    
    for i, analisis in enumerate(datos_edicion):
        fecha_str = analisis['Fecha Análisis'].strftime('%d/%m/%Y') if pd.notna(analisis['Fecha Análisis']) else '-'
        with st.sidebar.expander(f"{analisis['Vto']} - {fecha_str}"):
            nuevas_unidades = st.number_input("Unidades", value=int(analisis['Unidades']), key=f"edit_u_{i}")
            nuevas_cantidad = st.number_input("Cantidad Total", value=int(analisis['Cantidad Total']), key=f"edit_c_{i}")
            nueva_unidad_medida = st.selectbox("Unidad Medida", UNIDADES_MEDIDA, 
                                                index=UNIDADES_MEDIDA.index(analisis['Unidad Medida']) if analisis['Unidad Medida'] in UNIDADES_MEDIDA else 0, 
                                                key=f"edit_um_{i}")
            nuevas_obs = st.text_input("Observaciones", value=analisis['Observaciones'] if pd.notna(analisis['Observaciones']) else "", key=f"edit_o_{i}")
            nuevo_estado = st.selectbox("Estado", ESTADOS, 
                                         index=ESTADOS.index(analisis['Estado']) if analisis['Estado'] in ESTADOS else 0, 
                                         key=f"edit_e_{i}")
            
            if st.button(f"💾 Guardar {analisis['Vto']}", key=f"save_{i}"):
                idx = df[(df["Lote"] == analisis['Lote']) & (df["Vto"] == analisis['Vto'])].index
                if len(idx) > 0:
                    df.loc[idx, "Unidades"] = nuevas_unidades
                    df.loc[idx, "Cantidad Total"] = nuevas_cantidad
                    df.loc[idx, "Unidad Medida"] = nueva_unidad_medida
                    df.loc[idx, "Observaciones"] = nuevas_obs
                    df.loc[idx, "Estado"] = nuevo_estado
                    guardar_datos(df)
                    st.sidebar.success(f"✅ Guardado")
                    st.rerun()
    
    if st.sidebar.button("❌ Cerrar edición", use_container_width=True):
        del st.session_state.editando
        del st.session_state.datos_edicion
        st.rerun()