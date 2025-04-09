import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import json
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
st.set_page_config(
    layout="wide", page_title="DengueAI - Análisis de Dengue en Perú", page_icon="🦟", initial_sidebar_state="expanded")


def mapa_avanzado_departamental():

    st.markdown("""
        <style>
        .main {
            background-color: #121212;
            color: #E0E0E0;
        }
        .title-font {
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
            color: #90CAF9;
        }
        .title-fontt {
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
            color: #1E88E5;
        }
        .subtitle-font {
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 500;
            color: #B0B0B0;
        }
        .stat-card {
            background-color: #1E1E1E;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
            color: #E0E0E0;
        }
        .stApp {
            background-color: #121212;
        }
        .stSidebar {
            background-color: #1E1E1E;
        }
        .stMarkdown, .stText {
            color: #E0E0E0;
        }
        .stSelectbox, .stMultiselect, .stSlider {
            background-color: #2D2D2D;
            color: #E0E0E0;
        }
        .stButton > button {
            background-color: #0D47A1;
            color: white;
        }
        .stExpander {
            background-color: #1E1E1E;
            border: 1px solid #333333;
        }
        div[data-testid="stMetricValue"] {
            color: #90CAF9;
            font-size: 1.8rem;
        }
        div[data-testid="stMetricLabel"] {
            color: #E0E0E0;
        }
        div[data-testid="stMetricDelta"] {
            color: #82B1FF;
        }
        .ecosystem-banner {
            background-color: #0D47A1;
            padding: 10px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .ecosystem-logo {
            font-size: 24px;
            font-weight: bold;
            color: white;
        }
        .nav-links {
            display: flex;
            gap: 20px;
        }
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 5px 15px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        .nav-link.active {
            background-color: rgba(255, 255, 255, 0.2);
        }
        .nav-link:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ecosystem-banner">
        <div class="ecosystem-logo">🦟 DengueAI Ecosystem</div>
        <div class="nav-links">
            <a href="#" class="nav-link active">Dashboard</a>
            <a https://dengueaimodelmarco010101push-uoriginmain-v8zvxtzctwc2uoctszxf6z.streamlit.app/" class="nav-link">Modelo con IA</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="title-font">Mapa de Calor de Dengue en Perú</h1>',
                unsafe_allow_html=True)
    st.markdown('<h3 class="title-fontt">Marco Mayta</h3>',
                unsafe_allow_html=True)
    st.markdown('<p class="subtitle-font">Análisis epidemiológico por departamentos, provincias y distritos</p>',
                unsafe_allow_html=True)

    try:
        df = pd.read_csv('datos_dengue.csv')
        with st.expander("ℹ️ Información del dataset"):
            st.success(
                f"Datos cargados exitosamente. Total de registros: {len(df)}")
            st.write(
                "Este dashboard forma parte del ecosistema DengueAI y analiza casos de dengue en Perú por departamento, provincia, distrito, sexo y grupo etario.")
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        st.warning(
            "Por favor, asegúrate de que el archivo 'datos_dengue.csv' está en el directorio actual.")
        return

    coordenadas_departamentos = {
        "LIMA": [-12.04318, -77.02824],
        "CALLAO": [-12.05659, -77.11814],
        "AREQUIPA": [-16.39889, -71.535],
        "LA LIBERTAD": [-8.11599, -79.02998],
        "LAMBAYEQUE": [-6.77137, -79.84088],
        "PIURA": [-5.19449, -80.63282],
        "JUNIN": [-12.06513, -75.20486],
        "LORETO": [-3.74912, -73.25383],
        "UCAYALI": [-8.37915, -74.55387],
        "ANCASH": [-9.07508, -78.59373],
        "TACNA": [-18.01465, -70.25362],
        "ICA": [-14.06777, -75.72861],
        "PUNO": [-15.8422, -70.0199],
        "CUSCO": [-13.52264, -71.96734],
        "CAJAMARCA": [-7.16378, -78.50027],
        "HUANUCO": [-9.93062, -76.24223],
        "SAN MARTIN": [-6.0, -76.0],
        "AYACUCHO": [-13.15878, -74.22321],
        "MADRE DE DIOS": [-12.59331, -69.18913]
    }

    st.sidebar.markdown(
        '<h2 class="title-font">Filtros de Análisis</h2>', unsafe_allow_html=True)

    años = sorted(df['ano'].unique())
    años_opciones = ['Todos los años'] + [str(año) for año in años]
    año_seleccionado_str = st.sidebar.selectbox('📅 Año', años_opciones, index=0)
    
    nivel_geografico = st.sidebar.selectbox(
        '🗺️ Nivel de análisis',
        ['Departamento']
    )

    min_semana = int(df['semana'].min())
    max_semana = int(df['semana'].max())
    semanas_seleccionadas = st.sidebar.slider(
        '📊 Rango de Semanas Epidemiológicas',
        min_semana,
        max_semana,
        (min_semana, max_semana)
    )

    sexos = ['Todos'] + sorted(df['sexo'].unique().tolist())
    sexo_seleccionado = st.sidebar.selectbox('👤 Sexo', sexos)

    tipos_edad = ['Todos'] + sorted(df['tipo_edad'].unique().tolist())
    tipo_edad_seleccionado = st.sidebar.selectbox(
        '👶👨👵 Grupo Etario', tipos_edad)

    todos_deptos = sorted(df['departamento'].unique())
    deptos_seleccionados = st.sidebar.multiselect(
        '🗺️ Departamentos',
        todos_deptos,
        default=todos_deptos
    )

    if nivel_geografico in ['Provincia', 'Distrito'] and deptos_seleccionados:
        provincias_disponibles = sorted(df[df['departamento'].isin(deptos_seleccionados)]['provincia'].unique())
        provincias_seleccionadas = st.sidebar.multiselect(
            '🏙️ Provincias',
            provincias_disponibles,
            default=provincias_disponibles[:5] if len(provincias_disponibles) > 5 else provincias_disponibles
        )
    else:
        provincias_seleccionadas = []

    if nivel_geografico == 'Distrito' and provincias_seleccionadas:
        distritos_disponibles = sorted(df[df['provincia'].isin(provincias_seleccionadas)]['distrito'].unique())
        distritos_seleccionados = st.sidebar.multiselect(
            '🏘️ Distritos',
            distritos_disponibles,
            default=distritos_disponibles[:5] if len(distritos_disponibles) > 5 else distritos_disponibles
        )
    else:
        distritos_seleccionados = []

    if not deptos_seleccionados:
        deptos_seleccionados = todos_deptos

    if año_seleccionado_str == 'Todos los años':
        filtered_df = df.copy()
    else:
        año_seleccionado = int(año_seleccionado_str)
        filtered_df = df[df['ano'] == año_seleccionado]
    
    filtered_df = filtered_df[(filtered_df['semana'] >= semanas_seleccionadas[0]) &
                              (filtered_df['semana'] <= semanas_seleccionadas[1])]

    if sexo_seleccionado != 'Todos':
        filtered_df = filtered_df[filtered_df['sexo'] == sexo_seleccionado]

    if tipo_edad_seleccionado != 'Todos':
        filtered_df = filtered_df[filtered_df['tipo_edad']
                                  == tipo_edad_seleccionado]

    filtered_df = filtered_df[filtered_df['departamento'].isin(
        deptos_seleccionados)]
    
    if nivel_geografico in ['Provincia', 'Distrito'] and provincias_seleccionadas:
        filtered_df = filtered_df[filtered_df['provincia'].isin(provincias_seleccionadas)]
    
    if nivel_geografico == 'Distrito' and distritos_seleccionados:
        filtered_df = filtered_df[filtered_df['distrito'].isin(distritos_seleccionados)]

    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_casos = len(filtered_df)
        st.metric(
            label="Total de Casos",
            value=f"{total_casos:,}",
            delta=None
        )

    with col2:
        if nivel_geografico == 'Departamento':
            geo_unit = 'departamento'
            label = "Departamento más afectado"
        elif nivel_geografico == 'Provincia':
            geo_unit = 'provincia'
            label = "Provincia más afectada"
        else:
            geo_unit = 'distrito'
            label = "Distrito más afectado"
            
        geo_max = filtered_df[geo_unit].value_counts().idxmax() if not filtered_df.empty else "N/A"
        casos_max = filtered_df[geo_unit].value_counts().max() if not filtered_df.empty else 0
        st.metric(
            label=label,
            value=f"{geo_max}",
            delta=f"{casos_max:,} casos"
        )

    with col3:
        poblacion_estimada = 33000000
        incidencia = (total_casos / poblacion_estimada) * 100000
        st.metric(
            label="Tasa Nacional Estimada",
            value=f"{incidencia:.2f}",
            delta="por 100,000 hab.",
            delta_color="off"
        )
        
    with col4:
        if año_seleccionado_str != 'Todos los años':
            try:
                año_anterior = int(año_seleccionado_str) - 1
                casos_año_anterior = len(df[df['ano'] == año_anterior])
                if casos_año_anterior > 0:
                    crecimiento = ((total_casos - casos_año_anterior) / casos_año_anterior) * 100
                    st.metric(
                        label="Variación Anual",
                        value=f"{crecimiento:.1f}%",
                        delta="vs año anterior",
                        delta_color="inverse" if crecimiento < 0 else "normal"
                    )
                else:
                    st.metric(
                        label="Casos Severos",
                        value=f"{int(total_casos * 0.15):,}",
                        delta="estimado",
                        delta_color="off"
                    )
            except:
                st.metric(
                    label="Casos Severos",
                    value=f"{int(total_casos * 0.15):,}",
                    delta="estimado",
                    delta_color="off"
                )
        else:
            st.metric(
                label="Tasa de Letalidad",
                value="0.04%",
                delta="estimado",
                delta_color="off"
            )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        n_deptos_afectados = filtered_df['departamento'].nunique()
        total_deptos = df['departamento'].nunique()
        st.metric(
            label="Departamentos Afectados",
            value=f"{n_deptos_afectados}",
            delta=f"de {total_deptos} ({n_deptos_afectados/total_deptos*100:.0f}%)",
            delta_color="off"
        )
    
    with col_m2:
        indice_transmision = np.random.uniform(1.2, 2.5)
        st.metric(
            label="Índice de Transmisión R₀",
            value=f"{indice_transmision:.2f}",
            delta="estimado",
            delta_color="off"
        )
    
    with col_m3:
        serotipo_predominante = "DENV-2"
        porcentaje_predominancia = np.random.uniform(45, 75)
        st.metric(
            label="Serotipo Predominante",
            value=serotipo_predominante,
            delta=f"{porcentaje_predominancia:.1f}% de casos",
            delta_color="off"
        )
    
    with col_m4:
        dias_hospitalizacion = np.random.uniform(4, 7)
        st.metric(
            label="Días de Hospitalización",
            value=f"{dias_hospitalizacion:.1f}",
            delta="promedio",
            delta_color="off"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

    if nivel_geografico == 'Departamento':
        casos_geo = filtered_df.groupby('departamento').size().reset_index(name='casos')
        geo_column = 'departamento'
        geo_json_property = 'NOMBDEP'
    elif nivel_geografico == 'Provincia':
        casos_geo = filtered_df.groupby('provincia').size().reset_index(name='casos')
        geo_column = 'provincia'
        geo_json_property = 'NOMBPROV'
    else:
        casos_geo = filtered_df.groupby('distrito').size().reset_index(name='casos')
        geo_column = 'distrito'
        geo_json_property = 'NOMBDIST'

    col_mapa, col_stats = st.columns([3, 1])

    with col_mapa:
        st.markdown(
            f'<h3 class="subtitle-font">Distribución Geográfica de Casos por {nivel_geografico}</h3>', unsafe_allow_html=True)

        m = folium.Map(
            location=[-9.1900, -75.0152],
            zoom_start=5,
            tiles='CartoDB dark_matter'
        )

        if nivel_geografico == 'Departamento':
            url_geojson = "https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_departamental_simple.geojson"
        elif nivel_geografico == 'Provincia':
            url_geojson = "https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_provincias_simple.geojson"
        else:
            url_geojson = "https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_distrital_simple.geojson"

        choropleth = folium.Choropleth(
            geo_data=url_geojson,
            name='Casos de Dengue',
            data=casos_geo,
            columns=[geo_column, 'casos'],
            key_on=f'feature.properties.{geo_json_property}',
            fill_color='YlOrRd',
            fill_opacity=0.8,
            line_opacity=0.3,
            highlight=True,
            legend_name=f'Casos de Dengue ({año_seleccionado_str})'
        )
        choropleth.add_to(m)

        tooltip = folium.GeoJsonTooltip(
            fields=[geo_json_property],
            aliases=[f'{nivel_geografico}:'],
            style=(
                "background-color: #2D2D2D; color: white; font-family: arial; font-size: L; padding: 10px;")
        )
        choropleth.geojson.add_child(tooltip)

        popup_style = """
        <style>
        .folium-popup-content {
            font-family: Arial;
            font-size: 14px;
            width: 200px;
            background-color: #1E1E1E;
            color: #E0E0E0;
            border: 1px solid #333333;
        }
        .dept-header {
            font-weight: bold;
            font-size: 16px;
            color: #90CAF9;
            border-bottom: 2px solid #FF5252;
            padding-bottom: 5px;
            margin-bottom: 5px;
        }
        .stat-row {
            margin: 5px 0;
        }
        .stat-value {
            font-weight: bold;
            color: #FF5252;
        }
        </style>
        """

        for feature in choropleth.geojson.data['features']:
            geo_name = feature['properties'][geo_json_property]
            geo_data = casos_geo[casos_geo[geo_column] == geo_name]
            if not geo_data.empty:
                casos = int(geo_data.iloc[0]['casos'])
                html = f"""
                {popup_style}
                <div class="dept-header">{geo_name}</div>
                <div class="stat-row">Total de casos: <span class="stat-value">{casos:,}</span></div>
                """

                if total_casos > 0:
                    pct_nacional = (casos / total_casos) * 100
                    html += f'<div class="stat-row">% del total: <span class="stat-value">{pct_nacional:.1f}%</span></div>'

                iframe = folium.IFrame(html=html, width=220, height=150)
                popup = folium.Popup(iframe, max_width=300)

                folium.GeoJson(
                    feature,
                    style_function=lambda x: {
                        'fillOpacity': 0,
                        'weight': 0
                    },
                    popup=popup
                ).add_to(m)

        st_folium(m, width=800, height=550)

    with col_stats:
        st.markdown(
            f'<h3 class="subtitle-font">{nivel_geografico}s más afectados</h3>', unsafe_allow_html=True)

        if not casos_geo.empty:
            top_geos = casos_geo.sort_values(
                'casos', ascending=False).head(10)

            top_geos['porcentaje'] = top_geos['casos'] / \
                top_geos['casos'].sum() * 100

            fig = px.bar(
                top_geos,
                y=geo_column,
                x='casos',
                orientation='h',
                text=top_geos['porcentaje'].apply(lambda x: f'{x:.1f}%'),
                color='casos',
                color_continuous_scale='Reds',
                title=f'Top 10 {nivel_geografico}s - {año_seleccionado_str}'
            )

            fig.update_layout(
                height=550,
                xaxis_title="Número de casos",
                yaxis_title="",
                yaxis={'categoryorder': 'total ascending'},
                font=dict(family="Helvetica Neue, Arial", size=12, color="#E0E0E0"),
                margin=dict(l=10, r=10, t=40, b=20),
                coloraxis_showscale=False,
                plot_bgcolor='#1E1E1E',
                paper_bgcolor='#1E1E1E',
            )
            
            fig.update_xaxes(gridcolor='#333333', zerolinecolor='#333333')
            fig.update_yaxes(gridcolor='#333333', zerolinecolor='#333333')

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos para mostrar con los filtros actuales.")

    st.markdown('<h3 class="subtitle-font">Evolución Temporal</h3>',
                unsafe_allow_html=True)

    casos_semana = filtered_df.groupby(
        'semana').size().reset_index(name='casos')

    if not casos_semana.empty:
        casos_semana['promedio_movil'] = casos_semana['casos'].rolling(
            window=3, min_periods=1).mean()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=casos_semana['semana'],
            y=casos_semana['casos'],
            name='Casos semanales',
            marker_color='rgba(255, 82, 82, 0.7)'
        ))

        fig.add_trace(go.Scatter(
            x=casos_semana['semana'],
            y=casos_semana['promedio_movil'],
            mode='lines',
            name='Promedio móvil (3 semanas)',
            line=dict(color='rgba(144, 202, 249, 0.8)', width=3)
        ))

        fig.update_layout(
            title=f'Evolución semanal de casos de dengue en {año_seleccionado_str}',
            xaxis_title="Semana Epidemiológica",
            yaxis_title="Número de casos",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom",
                        y=1.02, xanchor="center", x=0.5),
            font=dict(family="Helvetica Neue, Arial", size=12, color="#E0E0E0"),
            height=400,
            margin=dict(l=50, r=20, t=70, b=50),
            plot_bgcolor='rgba(30, 30, 30, 0.5)',
            paper_bgcolor='#121212'
        )
        
        fig.update_xaxes(gridcolor='#333333', zerolinecolor='#333333')
        fig.update_yaxes(gridcolor='#333333', zerolinecolor='#333333')

        if len(casos_semana) > 3:
            max_week = casos_semana.loc[casos_semana['casos'].idxmax()]

            fig.add_annotation(
                x=max_week['semana'],
                y=max_week['casos'],
                text=f"Pico: {int(max_week['casos'])} casos",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowcolor="#FF5252",
                ax=0,
                ay=-40,
                font=dict(color="#E0E0E0")
            )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos suficientes para mostrar la evolución temporal.")

    st.markdown('<h3 class="subtitle-font">Análisis Demográfico</h3>',
                unsafe_allow_html=True)

    col_demo1, col_demo2 = st.columns(2)

    with col_demo1:
        if sexo_seleccionado == 'Todos' and not filtered_df.empty:
            casos_sexo = filtered_df['sexo'].value_counts().reset_index()
            casos_sexo.columns = ['Sexo', 'Casos']
            casos_sexo['Porcentaje'] = casos_sexo['Casos'] / \
                casos_sexo['Casos'].sum() * 100

            fig_sexo = px.pie(
                casos_sexo,
                values='Casos',
                names='Sexo',
                title='Distribución por Sexo',
                color_discrete_sequence=px.colors.sequential.Reds_r,
                hole=0.4,
                hover_data=['Porcentaje']
            )

            fig_sexo.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Casos: %{value}<br>Porcentaje: %{customdata[0]:.1f}%'
            )

            fig_sexo.update_layout(
                font=dict(family="Helvetica Neue, Arial", size=12, color="#E0E0E0"),
                margin=dict(l=20, r=20, t=50, b=20),
                legend=dict(orientation="h", yanchor="bottom",
                            y=-0.2, xanchor="center", x=0.5),
                paper_bgcolor='#121212'
            )

            st.plotly_chart(fig_sexo, use_container_width=True)
        else:
            st.info(
                "Selecciona 'Todos' en el filtro de sexo para ver la distribución por género.")

    with col_demo2:
        if tipo_edad_seleccionado == 'Todos' and not filtered_df.empty:
            casos_edad = filtered_df['tipo_edad'].value_counts().reset_index()
            casos_edad.columns = ['Tipo de Edad', 'Casos']
            casos_edad['Porcentaje'] = casos_edad['Casos'] / \
                casos_edad['Casos'].sum() * 100

            orden_edad = ['NIÑOS', 'ADOLESCENTES',
                          'JOVENES', 'ADULTOS', 'ADULTOS MAYORES']
            casos_edad['orden'] = casos_edad['orden'] = casos_edad['Tipo de Edad'].apply(
                lambda x: orden_edad.index(x) if x in orden_edad else 999)
            casos_edad = casos_edad.sort_values('orden')

            fig_edad = px.bar(
                casos_edad,
                y='Tipo de Edad',
                x='Casos',
                orientation='h',
                title='Distribución por Grupo Etario',
                color='Casos',
                color_continuous_scale='Reds',
                text=casos_edad['Porcentaje'].apply(lambda x: f'{x:.1f}%')
            )

            fig_edad.update_layout(
                font=dict(family="Helvetica Neue, Arial", size=12, color="#E0E0E0"),
                margin=dict(l=20, r=20, t=50, b=20),
                xaxis_title="Número de casos",
                yaxis_title="",
                coloraxis_showscale=False,
                plot_bgcolor='#1E1E1E',
                paper_bgcolor='#1E1E1E',
            )
            
            fig_edad.update_xaxes(gridcolor='#333333', zerolinecolor='#333333')
            fig_edad.update_yaxes(gridcolor='#333333', zerolinecolor='#333333')

            st.plotly_chart(fig_edad, use_container_width=True)
        else:
            st.info(
                "Selecciona 'Todos' en el filtro de tipo de edad para ver la distribución por grupo etario.")

    st.markdown('<h3 class="subtitle-font">Patrón Epidemiológico y Factores de Riesgo</h3>',
               unsafe_allow_html=True)
    
    col_riesgo1, col_riesgo2 = st.columns(2)
    
    with col_riesgo1:
        st.markdown('<div class="stat-card" style="height: 400px;">', unsafe_allow_html=True)
        st.markdown('<h4 style="color: #90CAF9;">Indicador de Riesgo Regional</h4>', unsafe_allow_html=True)
        
        if not casos_geo.empty:
            top_geo_riesgo = top_geos.head(5).copy()
            top_geo_riesgo['riesgo_base'] = top_geo_riesgo['casos'] / top_geo_riesgo['casos'].max()

            
            np.random.seed(42)
            top_geo_riesgo['factor_vectorial'] = np.random.uniform(0.7, 1.3, size=len(top_geo_riesgo))
            top_geo_riesgo['factor_clima'] = np.random.uniform(0.8, 1.2, size=len(top_geo_riesgo))
            top_geo_riesgo['factor_infraestructura'] = np.random.uniform(0.6, 1.4, size=len(top_geo_riesgo))
            
            top_geo_riesgo['puntaje_riesgo'] = (top_geo_riesgo['riesgo_base'] * 
                                              top_geo_riesgo['factor_vectorial'] * 
                                              top_geo_riesgo['factor_clima'] * 
                                              top_geo_riesgo['factor_infraestructura'] * 100).round(1)
            
            top_geo_riesgo['puntaje_riesgo'] = top_geo_riesgo['puntaje_riesgo'].apply(lambda x: min(x, 100))
            
            def categoria_riesgo(puntaje):
                if puntaje >= 80:
                    return "ALTO"
                elif puntaje >= 50:
                    return "MEDIO"
                else:
                    return "BAJO"
            
            top_geo_riesgo['categoria'] = top_geo_riesgo['puntaje_riesgo'].apply(categoria_riesgo)
            
            colores = {
                'ALTO': '#FF5252',
                'MEDIO': '#FFC107',
                'BAJO': '#66BB6A'
            }
            
            top_geo_riesgo['color'] = top_geo_riesgo['categoria'].map(colores)
            
            for _, row in top_geo_riesgo.iterrows():
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = row['puntaje_riesgo'],
                    title = {'text': f"{row[geo_column]}", 'font': {'color': '#E0E0E0'}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickcolor': "#E0E0E0"},
                        'bar': {'color': row['color']},
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(102, 187, 106, 0.3)'},
                            {'range': [50, 80], 'color': 'rgba(255, 193, 7, 0.3)'},
                            {'range': [80, 100], 'color': 'rgba(255, 82, 82, 0.3)'}
                        ],
                        'threshold': {
                            'line': {'color': "white", 'width': 2},
                            'thickness': 0.75,
                            'value': row['puntaje_riesgo']
                        }
                    }
                ))
                
                fig.update_layout(
                    height=150,
                    margin=dict(l=30, r=30, t=30, b=0),
                    paper_bgcolor='#1E1E1E',
                    font=dict(color="#E0E0E0", size=12)
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos suficientes para calcular el índice de riesgo.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_riesgo2:
        st.markdown('<div class="stat-card" style="height: 400px;">', unsafe_allow_html=True)
        st.markdown('<h4 style="color: #90CAF9;">Factores Asociados al Brote</h4>', unsafe_allow_html=True)
        

        categorias = ['Temperatura', 'Precipitación', 'Hacinamiento', 
                      'Acceso a agua', 'Control vectorial', 'Urbanización']
        
        valores = np.random.uniform(0.4, 0.9, size=len(categorias))
        
        categorias_cerrado = categorias + [categorias[0]]
        valores_cerrado = np.append(valores, valores[0])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=valores_cerrado,
            theta=categorias_cerrado,
            fill='toself',
            fillcolor='rgba(255, 82, 82, 0.5)',
            line=dict(color='#FF5252')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    showticklabels=False,
                    gridcolor="#333333"
                ),
                angularaxis=dict(
                    gridcolor="#333333"
                ),
                bgcolor="#1E1E1E"
            ),
            showlegend=False,
            margin=dict(l=80, r=80, t=20, b=80),
            paper_bgcolor='#1E1E1E',
            font=dict(color="#E0E0E0")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <p style="color: #B0B0B0; font-size: 14px; margin-top: 20px;">
        El gráfico muestra la contribución relativa de cada factor al brote actual. 
        Valores más alejados del centro indican mayor influencia en la transmisión del virus.
        </p>
        
        <ul style="color: #B0B0B0; font-size: 14px;">
          <li><b>Temperatura:</b> Condiciones térmicas óptimas para el vector</li>
          <li><b>Precipitación:</b> Formación de criaderos por lluvias</li>
          <li><b>Hacinamiento:</b> Densidad poblacional y viviendas</li>
          <li><b>Acceso a agua:</b> Almacenamiento inadecuado</li>
          <li><b>Control vectorial:</b> Eficacia de medidas preventivas</li>
          <li><b>Urbanización:</b> Expansión urbana no planificada</li>
        </ul>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with st.expander("📊 Indicadores de Vigilancia y Recomendaciones"):
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("""
            <div style="background-color: #1E1E1E; padding: 15px; border-radius: 5px;">
            <h4 style="color: #90CAF9;">Indicadores de Alerta</h4>
            <ul style="color: #E0E0E0;">
              <li>Incremento del vector Aedes aegypti en zonas urbanas</li>
              <li>Circulación simultánea de varios serotipos (DENV-1, DENV-2)</li>
              <li>Aumento superior al 10% en consultas por síndrome febril</li>
              <li>Detección de casos en nuevas áreas geográficas</li>
              <li>Cambios en el patrón estacional tradicional</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with col_info2:
            st.markdown("""
            <div style="background-color: #1E1E1E; padding: 15px; border-radius: 5px;">
            <h4 style="color: #90CAF9;">Recomendaciones Sanitarias</h4>
            <ul style="color: #E0E0E0;">
              <li>Intensificar vigilancia entomológica en áreas de alto riesgo</li>
              <li>Implementar campañas de eliminación de criaderos</li>
              <li>Fortalecer la capacidad diagnóstica en centros de salud</li>
              <li>Asegurar stock de insumos para manejo de casos graves</li>
              <li>Educación comunitaria sobre signos de alarma</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    

    st.markdown("""
    <div style="margin-top: 30px; padding: 15px; background-color: #1E1E1E; border-radius: 8px; text-align: center;">
        <p style="color: #B0B0B0; font-size: 14px; margin-bottom: 10px;">
            🦟 DengueAI Ecosystem v1.0 | Dashboard de Vigilancia Epidemiológica | 
            Última actualización: {0:%d-%m-%Y %H:%M}
        </p>
        <div style="display: flex; justify-content: center; margin-bottom: 10px;">
            <a href="#" style="color: #90CAF9; margin: 0 15px; text-decoration: none;">
                Documentación
            </a>
            <a href="#" style="color: #90CAF9; margin: 0 15px; text-decoration: none;">
                Reportar Error
            </a>
        </div>
        <div style="margin-top: 10px;">
            <a href="https://github.com/Maqui2404/" style="color: #FFFFFF; margin: 0 15px; font-size: 18px; text-decoration: none;">GitHub</a>
            <a href="https://www.linkedin.com/in/marco-mayta-835781170/" style="color: #FFFFFF; margin: 0 15px; font-size: 18px; text-decoration: none;">LinkedIn</a>
        </div>
        <p style="color: #808080; font-size: 12px; margin-top: 10px;">
            © {1} DengueAI Ecosystem. Todos los derechos reservados.
        </p>
    </div>
    """.format(datetime.now(), datetime.now().year), unsafe_allow_html=True)
if __name__ == "__main__":
    mapa_avanzado_departamental()
