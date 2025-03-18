import dash
from dash import dcc, html, Input, Output
import geopandas as gpd
import unidecode
import folium
import dash_leaflet as dl

# Cargar los datos
df_mpios_shape = gpd.read_file("files/mapa/muni_2018gw/muni_2018gw.shp", encoding="UTF-8")
df_mpios_shape["NOM_MUN"] = df_mpios_shape["NOM_MUN"].apply(lambda x: unidecode.unidecode(x.upper()))

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    html.H1("Mapa Interactivo de Municipios"),
    html.Div([
        dcc.Input(
            id="input-municipio",
            type="text",
            placeholder="Escribe el nombre del municipio",
            style={"marginRight": "10px"}
        ),
        html.Button("Mostrar", id="btn-mostrar")
    ], style={"marginBottom": "20px"}),
    html.Div(id="mapa-container", children=[
        dl.Map(
            center=(20.12, -98.73),  # Coordenadas aproximadas de Hidalgo
            zoom=8,
            id="mapa",
            style={"height": "500px", "width": "100%"}
        )
    ])
])

# Callback para actualizar el mapa
@app.callback(
    Output("mapa", "children"),
    [Input("btn-mostrar", "n_clicks")],
    [Input("input-municipio", "value")]
)
def actualizar_mapa(n_clicks, municipio):
    if not municipio:
        return []

    # Filtrar por municipio
    municipio_upper = unidecode.unidecode(municipio.upper())
    municipio_shape = df_mpios_shape[df_mpios_shape["NOM_MUN"] == municipio_upper]

    if municipio_shape.empty:
        return []  # No hay coincidencias, devolver mapa vacío

    # Convertir la geometría en GeoJSON
    geojson = municipio_shape.__geo_interface__

    return [
        dl.TileLayer(),  # Fondo del mapa
        dl.GeoJSON(data=geojson, id="municipio", style={"color": "red", "weight": 2})
    ]

# Correr la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)