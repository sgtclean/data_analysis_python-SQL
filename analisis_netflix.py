import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
#      ---------------------------LIMPIEZA---------------------------------------
data=pd.read_csv("netflix_titles.csv")
data.info() 
data.head() 
data.describe(include="all") 
# INSPECCIONAMOS DATA FRAME

data["director"]=data["director"].fillna("Unknown")
data["cast"]=data["cast"].fillna("Unknown")
data["country"]=data["country"].fillna("Unknown")
null=data.isnull().sum()
print(null)
# CAMBIAMOS VALORES NULOS POR UNO CONCRETO

data[data.duplicated(keep=False)]
data = data.drop_duplicates()

#VERIFICAMOS POR DUPLICADOS Y ELIMINAMOS

print(data['show_id'].dropna().unique())
print(data['type'].dropna().unique())
print(data['title'].dropna().unique())
print(data['director'].dropna().unique())
print(data['cast'].dropna().unique())
print(data['country'].dropna().unique())
print(data['date_added'].dropna().unique())
print(data['release_year'].dropna().unique())
print(data['rating'].dropna().unique())
print(data['duration'].dropna().unique())
print(data['listed_in'].dropna().unique())

#VERIFICAMOS SI EXISTE INFORMACION CRUZADA

valid_ratings = ['G', 'PG', 'PG-13', 'R', 'TV-MA', 'TV-PG', 'TV-14', 'NR', 'UR', 'TV-Y', 'TV-Y7', 'TV-G']
mask = ~data['rating'].isin(valid_ratings)
data.loc[mask, 'duration'] = data.loc[mask, 'rating']  # mover a duration
data.loc[mask, 'rating'] = pd.NA                      # limpiar la columna rating
data["rating"]=data["rating"].fillna("UR")

#CAMBIAMOS VALORES DE REGISTROS CRUZADOS Y LIMPIAMOS EL CAMPO RATING

data['date_added'] = pd.to_datetime(data['date_added'], errors='coerce') 
#CAMBIAMOS A FORMATO DE FECHA


#    -------------------------------SQL QUERY Y DATA BASE---------------------------

conn = sqlite3.connect("netflix.db")#creamos una base de datos vacia

data.to_sql("netflix", conn, if_exists="replace", index=False)#insertamos el dataframe limpio para poder trabajar con el.
cursor = conn.cursor()

#ejercicio 1: saber la tendencia de titulos por año y el tipo de titulo subido

query = """
SELECT release_year, type, COUNT(*) as cantidad
FROM netflix
GROUP BY release_year, type
ORDER BY release_year
"""
df = pd.read_sql_query(query, conn)

#usamos query para trabajar en la base de datos usando SQL 
sns.lineplot(data=df, x='release_year', y='cantidad', hue='type')
plt.title('Tendencia de títulos por año y tipo')
plt.show()

#usamos seaborn para graficar y matplotlib para desplegar las graficas

#ejercicio 2: saber los 10 paises que mas exportan contenido
query = """
SELECT country, COUNT(*) AS cantidad
FROM netflix
GROUP BY country
ORDER BY cantidad DESC
LIMIT 10
"""
country = pd.read_sql_query(query, conn)

# agrupamos los datos nuevamente con SQL y los nombramos con una variable nueva para poder utilizarla en python
sns.barplot(data=country, x="cantidad", y="country")
plt.title("Top 10 países con más títulos en Netflix")
plt.tight_layout()
plt.show()
#usamos seaborn y matplotlib nuevamente

#ejercicio 3: clasificaciones por rating, saber el tipo de publico mas atendido segun el rating.

query="""
SELECT type, rating , COUNT(*) as cantidad
FROM netflix
GROUP BY type, rating
ORDER BY type, cantidad DESC;
"""

types=pd.read_sql_query(query, conn)

# Filtramos solo las películas
movies = types[types['type'] == 'Movie']

# Pastel
plt.figure(figsize=(7,7))
plt.pie(movies['cantidad'], labels=movies['rating'], autopct='%1.1f%%', startangle=90)
plt.title("Distribución de ratings - Películas")
plt.show()


# Filtramos solo las series
series = types[types['type'] == 'TV Show']

# Pastel
plt.figure(figsize=(7,7))
plt.pie(series['cantidad'], labels=series['rating'], autopct='%1.1f%%', startangle=90)
plt.title("Distribución de ratings - Series")
plt.show()


#verificamos la duracion promedio de las peliculas por diferentes diferenciadores

query="""
SELECT 
    country,
    type,
    duration,
    CASE
        WHEN type='Movie' AND CAST(REPLACE(duration,' min','') AS INTEGER) <= 60 THEN 'Corta (<1h)'
        WHEN type='Movie' AND CAST(REPLACE(duration,' min','') AS INTEGER) <= 120 THEN 'Media (1-2h)'
        WHEN type='Movie' AND CAST(REPLACE(duration,' min','') AS INTEGER) <= 180 THEN 'Larga (2-3h)'
        ELSE 'Muy larga (>3h)'
    END AS duracion_categoria,
    COUNT(*) AS cantidad
FROM netflix
WHERE type='Movie'
GROUP BY country, duracion_categoria
ORDER BY country, cantidad DESC;
"""
region=pd.read_sql_query(query, conn)

top_countries = region.groupby('country')['cantidad'].sum().sort_values(ascending=False).head(10).index

# Filtrar solo esos países
region_top10 = region[region['country'].isin(top_countries)]

# Gráfico
plt.figure(figsize=(12,6))
sns.barplot(
    data=region_top10, 
    x='duracion_categoria', 
    y='cantidad', 
    hue='country'
)
plt.title("Distribución de películas por duración y top 10 países")
plt.xlabel("Categoría de duración")
plt.ylabel("Cantidad de películas")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
