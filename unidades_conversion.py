import os
import pandas as pd
#Convertir archivo federal de CLUES a Parquet filtrando HGO e IMB
directorio = os.path.dirname(os.path.abspath(__file__))
excel_establecimientos = os.path.join(directorio, 'files', 'ESTABLECIMIENTO_SALUD_202501.xlsx')
if os.path.exists(excel_establecimientos):
    establecimientos = pd.read_excel(excel_establecimientos)
    establecimientos = establecimientos[(establecimientos['CLAVE DE LA ENTIDAD'] == 13) & (establecimientos['NOMBRE DE LA INSTITUCION'] == "SERVICIOS DE SALUD IMSS BIENESTAR ") & (establecimientos['NOMBRE TIPO ESTABLECIMIENTO'] == "DE CONSULTA EXTERNA")]
    ruta_parquet = os.path.join(directorio, 'files', 'ESTABLECIMIENTO_SALUD_202501.parquet')
    establecimientos.to_parquet(ruta_parquet)
    print(f"Archivo Parquet guardado en: {ruta_parquet}")
else:
    print(f"El archivo Excel no se encontró en: {excel_establecimientos}")


excel_establecimientos_ssh = os.path.join(directorio, 'files', 'ESTABLECIMIENTO_SALUD_202501.xlsx')
if os.path.exists(excel_establecimientos_ssh):
    establecimientos_ssh = pd.read_excel(excel_establecimientos_ssh)
    establecimientos_ssh = establecimientos_ssh[(establecimientos_ssh['CLAVE DE LA ENTIDAD'] == 13) & (establecimientos_ssh['NOMBRE DE LA INSTITUCION'] == "SECRETARIA DE SALUD") & 
                                                (establecimientos_ssh['NOMBRE TIPO ESTABLECIMIENTO'] == "DE CONSULTA EXTERNA") & (establecimientos_ssh['CLAVE MOTIVO BAJA'] == 9)]
    ruta_parquet_ssh = os.path.join(directorio, 'files', 'ESTABLECIMIENTO_SALUD_202501_SSH.parquet')
    establecimientos_ssh.to_parquet(ruta_parquet_ssh)
    print(f"Archivo Parquet guardado en: {ruta_parquet_ssh}")