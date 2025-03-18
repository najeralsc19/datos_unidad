# funciones.py
import pandas as pd
from unidecode import unidecode

def procesar_datos():
    # Cargar los datos

    df_unidades = pd.read_parquet("files/ESTABLECIMIENTO_SALUD_202501.parquet")
    df_unidades_ssh = pd.read_parquet("files/ESTABLECIMIENTO_SALUD_202501_ssh.parquet")
    df_horarios = pd.read_parquet("files/ESTABLECIMIENTO_SALUD_202501_horarios.parquet")
    # Unir los datos
    df_unidades_merge = pd.merge(df_unidades, 
                             df_unidades_ssh[['NOMBRE DE LA UNIDAD', 'CLAVE DEL MUNICIPIO', 'CLAVE DE LA LOCALIDAD', 'CLUES']], 
                             on=['NOMBRE DE LA UNIDAD', 'CLAVE DEL MUNICIPIO', 'CLAVE DE LA LOCALIDAD'],  # Se usan varias columnas como clave
                             how='left', 
                             suffixes=('', '_SSH'))
    # Reorganizar columnas
    cols = list(df_unidades_merge.columns)
    clues_index = cols.index('CLUES')
    cols.insert(clues_index + 1, cols.pop(cols.index('CLUES_SSH')))
    df_unidades_merge = df_unidades_merge[cols]

    # Merge con horarios

    df_unidades_merge = pd.merge(
        df_unidades_merge,
        df_horarios,
        on='CLUES',
        how='left'
    )
    return df_unidades_merge


def municipios(df_unidades_merge):
    municipios = df_unidades_merge['MUNICIPIO'].unique()
    df_municipios = pd.DataFrame(municipios, columns=['nombre_municipio'])
    df_municipios['id_municipio'] = range(1, len(df_municipios) + 1)
    return df_municipios


def piramide_pob():
    df_poblacion_mpios_total = pd.read_excel('files/Reporte Población.xlsx', skiprows=1)
    columnas_borrar = ['Clave Jurisdicción Unidad', 'Nombre Jurisdicción Unidad', 'Clave Jurisdicción Loc.', 'ageb',
                   'Clave Municipio Unidad','CLUES','Clave Localidad Unidad','Nombre Localidad Unidad',
                   'Nombre Unidad','Nombre Jurisdicción Loc','Clave Municipio Loc','Nombre Municipio Loc','Clave Localidad','Nombre Localidad']
    df_poblacion_mpios_total.drop(columnas_borrar, axis=1, inplace=True)
    # Convertir la columna 'Nombre Municipio Unidad' a mayúsculas y eliminar acentos
    df_poblacion_mpios_total['Nombre Municipio Unidad'] = df_poblacion_mpios_total['Nombre Municipio Unidad'].apply(lambda x: unidecode(x).upper())
    df_poblacion_mpios_total = df_poblacion_mpios_total.groupby(['Nombre Municipio Unidad']).sum().reset_index()
    
    return df_poblacion_mpios_total


def totales_pob(df_poblacion_mpios_total):
    columnas_hombres = [col for col in df_poblacion_mpios_total.columns if col.startswith('h')]
    columnas_mujeres = [col for col in df_poblacion_mpios_total.columns if col.startswith('m')]
    # Calcular los totales de hombres y mujeres
    total_hombres = df_poblacion_mpios_total[columnas_hombres].sum().sum()  # Suma completa de todas las filas y columnas de hombres
    total_mujeres = df_poblacion_mpios_total[columnas_mujeres].sum().sum()  # Suma completa de todas las filas y columnas de mujeres
    poblacion_total = total_hombres + total_mujeres
    return total_hombres, total_mujeres, poblacion_total