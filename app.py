from dash import Dash, html, dcc, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
from funciones import procesar_datos, municipios, piramide_pob, totales_pob  # Importar las funciones
import pandas as pd
import plotly.graph_objects as go
import io
import base64
import geopandas as gpd
import unidecode
import folium
import dash_leaflet as dl

# Llamar la función para obtener el DataFrame procesado
df_unidades_merge = procesar_datos()

# Llamar la función para obtener el DataFrame con la lista de municipios
df_municipios = municipios(df_unidades_merge)

# Llamar la función para obtener el DataFrame con la pirámide de población
df_poblacion_mpios_total = piramide_pob()
total_hombres, total_mujeres, poblacion_total = totales_pob(df_poblacion_mpios_total)

df_mpios_shape = gpd.read_file("files/mapa/muni_2018gw/muni_2018gw.shp", encoding="UTF-8")
df_mpios_shape["NOM_MUN"] = df_mpios_shape["NOM_MUN"].apply(lambda x: unidecode.unidecode(x.upper()))
df_mpios_shape = df_mpios_shape[df_mpios_shape["CVE_ENT"] == '13']



# Crear la aplicación Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
# Crear el encabezado con un Card
header_card = dbc.Card(
    dbc.CardBody(
        [
            html.H1("Información Municipal", className="display-3"),
            html.P(
                "Datos de establecimientos de salud por municipio",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P("Selecciona el municipio para desglosar la información."),
            dcc.Dropdown(
                id='dropdown-municipios',
                options=[{'label': row['nombre_municipio'], 'value': row['nombre_municipio']} for index, row in df_municipios.iterrows()],
                placeholder="Seleccione un municipio",
                style={'width': '50%'}  # Ajustar el ancho del Dropdown
            ),
            html.Div(id='output-container')  # Contenedor para mostrar el DataFrame filtrado
        ]
    ),
    className="mb-3"
)

# Definir el layout de la aplicación
app.layout = dbc.Container(
    [
        header_card,  # Encabezado
        dbc.Row(id='estadisticas-cards'),  # Contenedor para las tarjetas con datos importantes
        dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(
                            "Mapa Municipal",
                            className="card-title",
                            style={"textAlign": "center", "marginBottom": "20px"}
                        ),
                        dl.Map(
                            center=(20.12, -98.73),  # Coordenadas aproximadas de Hidalgo
                            zoom=100,
                            id="mapa",
                            style={
                                "height": "400px",  # Altura fija
                                "width": "100%",    # Ancho al 100%
                                "marginBottom": "20px"
                            }
                        )
                    ]
                ),
                className="h-100"
            ),
            width=6,  # Ajustar el ancho de la columna
            className="h-100",
            style={"height": "500px"}  # Altura fija para la columna
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='piramide-poblacional')  # Gráfica de pirámide poblacional
                ),
                className="h-100",
                style={
                    "height": "400px",  # Igual altura que el mapa
                    "width": "100%",    # Ancho al 100%
                    "marginBottom": "20px"
                }
            ),
            width=6,  # Ajustar el ancho de la columna
            className="h-100",
            style={"height": "500px"}  # Altura fija para la columna
        )
    ],
    className="h-100"
),
        # Nueva fila para el mapa interactivo
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dash_table.DataTable(
                                    id='table',
                                    columns=[
                                        {"name": col, "id": col}
                                        for col in ['CLUES', 'JURISDICCION', 'NOMBRE DE LA UNIDAD', 'HORARIO']
                                    ],
                                    data=df_unidades_merge[
                                        ['CLUES', 'JURISDICCION', 'NOMBRE DE LA UNIDAD', 'HORARIO']
                                    ].to_dict('records'),
                                    page_size=10,
                                    style_table={'overflowX': 'auto'},
                                    style_cell={
                                        'fontFamily': 'arial',
                                        'fontSize': '10px',
                                        'fontWeight': '100',
                                        'fontStyle': 'normal',
                                        'textAlign': 'center'
                                    },
                                    style_header={
                                        'backgroundColor': '#c5c3c6',
                                        'fontWeight': 'bold'
                                    }
                                    
                                ),
                                html.Button(
                                    "Descargar Excel",
                                    id="btn-download-excel",
                                    className="btn btn-primary mt-3"
                                ),
                                dcc.Download(id="download-dataframe-xlsx")
                            
                            ]
                        ),
                        className="h-100"
                    ),
                    width=12  # Ajustar el ancho de la columna
                )
            ],
            className="h-100"
        )
    ],
    className="h-100"
)
# Definir el callback para actualizar el DataFrame filtrado, la gráfica y las tarjetas
@app.callback(
    [Output('table', 'data'),
     Output('piramide-poblacional', 'figure'),
     Output('estadisticas-cards', 'children'),
     Output('mapa', 'children')],
    Input('dropdown-municipios', 'value')
)
def update_output(selected_municipio):
    if selected_municipio is None:
        table_data = df_unidades_merge[['CLUES', 'JURISDICCION', 'NOMBRE DE LA UNIDAD', 'HORARIO']].to_dict('records')
        fig = go.Figure()
        estadisticas_cards = [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Total de Unidades", className="card-title"),
                            html.P(f"{int(df_unidades_merge['CLUES'].nunique())}", className="card-text")
                        ]
                    ),
                    className="mb-3"
                ),
                width=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Total de Hombres", className="card-title"),
                            html.P(f"{int(total_hombres)}", className="card-text")
                        ]
                    ),
                    className="mb-3"
                ),
                width=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Total de Mujeres", className="card-title"),
                            html.P(f"{int(total_mujeres)}", className="card-text")
                        ]
                    ),
                    className="mb-3"
                ),
                width=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Poblacion Total", className="card-title"),
                            html.P(f"{int(poblacion_total)}", className="card-text")
                        ]
                    ),
                    className="mb-3"
                ),
                width=3
            ),
        ]
        mapa = [
            dl.Map(
                center=(20.12, -98.73),  # Coordenadas aproximadas de Hidalgo
                zoom=50,
                id="mapa",
                style={"height": "400px", "width": "600px", "marginTop": "20px"}
            )
        ]
        return table_data, fig, estadisticas_cards, mapa
    
    # Filtrar el DataFrame basado en el municipio seleccionado
    filtered_df = df_unidades_merge[df_unidades_merge['MUNICIPIO'] == selected_municipio]
    filtered_df = filtered_df[['CLUES', 'JURISDICCION', 'NOMBRE DE LA UNIDAD', 'HORARIO']]
    
    # Crear la gráfica de pirámide poblacional
    df_municipio = df_poblacion_mpios_total[df_poblacion_mpios_total['Nombre Municipio Unidad'] == selected_municipio]
    
    if df_municipio.empty:
        fig = go.Figure()
        estadisticas_cards = []
        mapa = []
        return filtered_df.to_dict('records'), fig, estadisticas_cards, mapa
    
    quinquenios = ['0-4 años', '5-9 años', '10-14 años', '15-19 años', '20-24 años', '25-29 años', '30-34 años', 
                   '35-39 años', '40-44 años', '45-49 años', '50-54 años', '55-59 años', '60-64 años', '65-69 años', 
                   '70-74 años', '75-79 años', '80-84 años', '85+ años', 'indefinido']
    
    poblacion_masculina = [-df_municipio[f'h{q}'].values[0] for q in quinquenios]  # Valores negativos para la gráfica
    poblacion_femenina = [df_municipio[f'm{q}'].values[0] for q in quinquenios]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=quinquenios,
        x=poblacion_masculina,
        name='Hombres',
        orientation='h',
        marker=dict(color='#e09f3e'),
        hovertemplate='%{y}: %{text}<extra></extra>',
        text=[abs(val) for val in poblacion_masculina]
    ))
    
    fig.add_trace(go.Bar(
        y=quinquenios,
        x=poblacion_femenina,
        name='Mujeres',
        orientation='h',
        marker=dict(color='#84a59d'),
        hovertemplate='%{y}: %{x}<extra></extra>',
        text=[abs(val) for val in poblacion_femenina]
    ))
    
    max_val = max(max(poblacion_femenina), abs(min(poblacion_masculina)))
    tickvals = [-max_val, -max_val/2, 0, max_val/2, max_val]
    ticktext = [str(int(abs(val))) for val in tickvals]
    
    fig.update_layout(
        title=f'Pirámide Poblacional de {selected_municipio}',
        xaxis_title='Población',
        yaxis_title='Edad',
        barmode='relative',
        bargap=0.1,
        bargroupgap=0,
        xaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext
        ),
        width=600,  # Ancho de la figura en píxeles
        height=600  # Altura de la figura en píxeles
    )
    
    # Calcular el total de hombres y mujeres para el municipio seleccionado
    df_municipio = df_municipio.apply(pd.to_numeric, errors='coerce')
    total_hombres_municipio = int(df_municipio.filter(like='h').sum().sum())
    total_mujeres_municipio = int(df_municipio.filter(like='m').sum().sum())
    poblacion_total_tot = total_hombres_municipio + total_mujeres_municipio
    # Crear el DataFrame con estadísticas basadas en el municipio seleccionado
    df_estadisticas = pd.DataFrame({
        'Indicador': ['Total de Unidades', 'Total de Hombres', 'Total de Mujeres', 'Poblacion Total'],
        'Valor': [
            int(filtered_df['CLUES'].nunique()),
            total_hombres_municipio,
            total_mujeres_municipio,
            poblacion_total_tot
        ]
    })
    
    # Crear las tarjetas
    estadisticas_cards = [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5(row['Indicador'], className="card-title card-title-custom"),
                        html.P(f"{int(row['Valor'])}", className="card-text card-text-custom")
                    ]
                ),
                className="mb-3",
                style={
                    'background-color': (
                        '#e09f3e' if row['Indicador'] == 'Total de Hombres' else
                        '#84a59d' if row['Indicador'] == 'Total de Mujeres' else
                        '#95b2ab' if row['Indicador'] == 'Total de Unidades' else
                        '#af751d'
                    )
                }
            ),
            width=3
        ) for index, row in df_estadisticas.iterrows()
    ]
    
    municipio_shape = df_mpios_shape[df_mpios_shape["NOM_MUN"] == selected_municipio]
    if municipio_shape.empty:
        mapa = []
    else:
        # Reproyectar a un CRS proyectado
        municipio_shape = municipio_shape.to_crs(epsg=32614)
        
        # Calcular centroide
        centroide = municipio_shape.geometry.centroid.iloc[0]
        lat, lon = centroide.y, centroide.x
        
        # Convertir la geometría a GeoJSON para el mapa (volver al CRS original si es necesario)
        municipio_shape = municipio_shape.to_crs(epsg=4326)
        geojson = municipio_shape.__geo_interface__

        # Crear el mapa con el centroide y la geometría
        mapa = [
            dl.TileLayer(),
            dl.GeoJSON(data=geojson, id="geojson", style={"color": "#e09f3e", "weight": 2}),
        ]

    # Centrar el mapa dinámicamente
    dl.Map(center=(lat, lon), zoom = 40)

    return filtered_df.to_dict('records'), fig, estadisticas_cards, mapa

# Callback para manejar la descarga del archivo Excel
@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn-download-excel", "n_clicks"),
    State('table', 'data'),
    prevent_initial_call=True
)
def download_excel(n_clicks, table_data):
    if n_clicks is None:
        return
    
    # Convertir los datos de la tabla a un DataFrame de pandas
    df = pd.DataFrame(table_data)
    
    # Crear un archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()  # Cerrar el escritor de Excel
    
    # Codificar el archivo Excel en base64
    output.seek(0)
    excel_data = output.read()
    b64 = base64.b64encode(excel_data).decode()
    
    return dcc.send_data_frame(df.to_excel, "data.xlsx", sheet_name="Sheet1")

if __name__ == "__main__":
    app.run_server(debug=True)