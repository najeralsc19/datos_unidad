import dash
from dash import dcc, html, Input, Output
import dash_leaflet as dl
import geopandas as gpd
import unidecode

# Cargar el archivo Shapefile
data = gpd.read_file("files/mapa/muni_2018gw/muni_2018gw.shp", encoding="UTF-8")
data["NOM_MUN"] = data["NOM_MUN"].apply(lambda x: unidecode.unidecode(x.upper()))  # Convertir a mayúsculas y eliminar acentos
data = data[data["CVE_ENT"] == "13"]  # Filtrar solo los datos de Hidalgo
data = data[["NOM_MUN", "geometry"]]  # Nos quedamos solo con el nombre y la geometría

# Convertir el GeoDataFrame a GeoJSON
geojson_data = data.to_crs(epsg='4326').to_json()

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown-municipios',
        options=[{'label': row['NOM_MUN'], 'value': row['NOM_MUN']} for index, row in data.iterrows()],
        placeholder="Seleccione un municipio"
    ),
    dl.Map(
        center=[20.1, -98.75],  # Centro del mapa en Hidalgo
        zoom=8,  # Nivel de zoom inicial
        children=[
            dl.TileLayer(),  # Capa base del mapa
            dl.GeoJSON(data=geojson_data, id='municipios-geojson')  # Capa de municipios
        ],
        style={'width': '100%', 'height': '600px'},
        id='mapa'
    ),
    html.Div(id='municipio-info')  # Div para mostrar información del municipio
])

# Callback para manejar clics en los municipios
@app.callback(
    Output('municipio-info', 'children'),
    [Input('municipios-geojson', 'click_feature')]
)
def municipio_click(feature):
    if feature is not None:
        # Extraer información del municipio clickeado
        nombre_municipio = feature['properties']['NOM_MUN']
        return f'Municipio seleccionado: {nombre_municipio}'
    return 'Haz clic en un municipio para ver más información.'

# Callback para centrar el mapa en el municipio seleccionado desde el dropdown
@app.callback(
    Output('mapa', 'center'),
    [Input('dropdown-municipios', 'value')]
)
def centrar_mapa(municipio):
    if municipio is not None:
        # Obtener la geometría del municipio seleccionado
        geom = data[data['NOM_MUN'] == municipio].geometry.iloc[0]
        # Calcular el centroide de la geometría
        centroide = geom.centroid
        return [centroide.y, centroide.x]
    return [20.1, -98.75]  # Centro del mapa en Hidalgo

if __name__ == '__main__':
    app.run_server(debug=True)