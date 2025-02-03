import rdata
import os
import json
import pandas as pd


# Function to clean and convert unit_price
def clean_price(price):
    if isinstance(price, str):
        price = price.replace(".", "").replace(",", ".")
    try:
        return float(price)
    except ValueError:
        return None


# Read the dataframe from the RDA file
df_dict = rdata.read_rda("Mapeo_Sipsa_TCAC_GABAS_Grupos.rda")
df = df_dict["Mapeo_Sipsa_TCAC_GABAS_Grupos"]

df2 = rdata.read_rda("intercambio_gramos.rda")
df2 = df2["intercambio_gramos"]

# Print the column names of the dataframe

"""
['codigo', 'No.', 'Nombre del Alimento', 'Parte analizada', 'Columna1',
       'Humedad (g)', 'Energia (Kcal)', 'Energia (Kj)', 'Proteina (g)',
       'Lipidos (g)', 'Carbohidratos Totales (g)',
       'Carbohidratos disponibles (g)', 'Fibra Dietaria (g)', 'Cenizas (g)',
       'Calcio (mg)', 'Hierro (mg)', 'Sodio (mg)', 'Fosforo (mg)', 'Yodo (mg)',
       'Zinc (mg)', 'Magnesio (mg)', 'Potasio (mg)', 'Tiamina (mg)',
       'Riboflavina (mg)', 'Niacina (mg)', 'Folatos (mcg)',
       'Vitamina B12 (mcg)', 'Vitamina C (mg)', 'Vitamina A (ER)',
       'Grasa Saturada (g)', 'Grasa Monoinsaturada (g)',
       'Grasa Poliinsaturada (g)', 'Colesterol (mg)', 'Parte comestible (%)',
       'codigo2', 'Micr sin inf (por alimento)', 'Grupos  GABAS',
       'Subgrupos  GABAS', 'Grupo TCAC', 'Factor de conversión',
       '% de parte comestible']

"""

print(df.columns)

print(df)

# Initialize a set to store unique TCAC codes and a dictionary to store unit prices and names
tcac_set = set()
tcac_info = {}

# Iterate through all JSON files in the 'results' folder
for filename in os.listdir("."):
    if filename.endswith(".json"):
        with open(os.path.join(".", filename), "r", encoding="utf-8") as file:
            data = json.load(file)
            tcac = data.get("TCAC")
            if tcac:
                tcac_set.add(tcac)
                tcac_info[tcac] = {
                    "unit_price": clean_price(data.get("unit_price")),
                    "name": data.get("name"),
                }

# Filter the dataframe to include only rows with 'codigo' matching any TCAC code
filtered_df = df[df["codigo"].isin(tcac_set)]

# Drop unwanted columns
columns_to_drop = [
    "No.",
    "Parte analizada",
    "Columna1",
    "Humedad (g)",
    "Energia (Kj)",
    "Carbohidratos disponibles (g)",
    "Fibra Dietaria (g)",
    "Cenizas (g)",
    "Yodo (mg)",
    "Potasio (mg)",
    "Grasa Saturada (g)",
    "Grasa Monoinsaturada (g)",
    "Grasa Poliinsaturada (g)",
    "Colesterol (mg)",
    "codigo2",
    "Micr sin inf (por alimento)",
    "Factor de conversión",
    "% de parte comestible",
    "Grupo TCAC",
    "Parte comestible (%)",
]
filtered_df = filtered_df.drop(columns=columns_to_drop)

# Rename columns
columns_to_rename = {
    "codigo": "Cod_TCAC",
    "Nombre del Alimento": "Food",
    "Grupos  GABAS": "Group",
    "Subgrupos  GABAS": "Subgroup",
    "Energia (Kcal)": "Energy",
    "Proteina (g)": "Protein",
    "Carbohidratos Totales (g)": "Carbohydrates",
    "Lipidos (g)": "Lipids",
    "Calcio (mg)": "Calcium",
    "Zinc (mg)": "Zinc",
    "Hierro (mg)": "Iron",
    "Magnesio (mg)": "Magnesium",
    "Fosforo (mg)": "Phosphorus",
    "Vitamina C (mg)": "VitaminC",
    "Tiamina (mg)": "Thiamine",
    "Riboflavina (mg)": "Riboflavin",
    "Niacina (mg)": "Niacin",
    "Folatos (mcg)": "Folate",
    "Vitamina B12 (mcg)": "VitaminB12",
    "Vitamina A (ER)": "VitaminA",
    "Sodio (mg)": "Sodium",
}
filtered_df = filtered_df.rename(columns=columns_to_rename)

filtered_df.insert(loc=2, column="Price_serving", value=None)
filtered_df.insert(loc=2, column="Serving_g", value=None)
filtered_df.insert(loc=2, column="Serving", value=None)
filtered_df.insert(loc=2, column="Price_100g", value=None)

filtered_df["Serving"] = 100

price_mapping = {tcac: info["unit_price"] for tcac, info in tcac_info.items()}
filtered_df["Price_100g"] = filtered_df["Cod_TCAC"].map(price_mapping)

food_mapping = {tcac: info["name"] for tcac, info in tcac_info.items()}
filtered_df["Food"] = filtered_df["Cod_TCAC"].map(food_mapping)

cols = list(filtered_df.columns)
# Remove 'Group' and 'Subgroup' from their current positions
cols.remove("Group")
cols.remove("Subgroup")
# Find the index to insert 'Group' and 'Subgroup'
insert_index = cols.index("Price_serving") + 1
# Insert 'Group' and 'Subgroup' after 'Price_serving'
cols.insert(insert_index, "Group")
cols.insert(insert_index + 1, "Subgroup")
# Reorder the DataFrame columns
filtered_df = filtered_df[cols]

filtered_df["Food"] = filtered_df["Food"].str.capitalize()
filtered_df["Group"] = filtered_df["Group"].str.capitalize()
filtered_df["Subgroup"] = filtered_df["Subgroup"].str.capitalize()
filtered_df["Price_100g"] = filtered_df["Price_100g"].round(2)
filtered_df["Energy"] = filtered_df["Energy"].round(2)


filtered_df = filtered_df.merge(
    df2[["Cod_TCAC", "Intercambio_g"]], on="Cod_TCAC", how="left"
)
filtered_df["Price_serving"] = (filtered_df["Price_100g"] / 100) * filtered_df[
    "Intercambio_g"
]
filtered_df["Serving_g"] = filtered_df["Price_serving"] / (
    filtered_df["Price_100g"] / 100
)
filtered_df = filtered_df.drop(columns=["Intercambio_g"])

desired_order = [
    "Cod_TCAC",
    "Food",
    "Price_100g",
    "Serving",
    "Serving_g",
    "Price_serving",
    "Group",
    "Subgroup",
    "Energy",
    "Protein",
    "Carbohydrates",
    "Lipids",
    "Calcium",
    "Zinc",
    "Iron",
    "Magnesium",
    "Phosphorus",
    "VitaminC",
    "Thiamine",
    "Riboflavin",
    "Niacin",
    "Folate",
    "VitaminB12",
    "VitaminA",
    "Sodium",
]
filtered_df = filtered_df[desired_order]

filtered_df = filtered_df.drop_duplicates(subset="Cod_TCAC")

subgroup_mapping = {
    "Leguminosas cocidas y mezclas vegetales cocidas": "Leguminosas",
    "Raíces": "Raices",
    "Tubérculos": "Tuberculos",
    "Plátanos": "Cereales",
    "Grasas monoinsaturadas": "Grasas",
    "Grasas saturadas": "Grasas",
    "Grasas poliinsaturadas": "Grasas",
    "Carnes magras crudas": "Carnes",
    "Productos altos en grasas saturadas y colesterol": "Grasas",
    "Azucares simples": "Azucares",
    "Dulces y postres": "Azucares",
    "Huevos": "Grasas",
    "Leche entera": "Lácteos",
}

filtered_df["Subgroup"] = filtered_df["Subgroup"].replace(subgroup_mapping)

filtered_df.to_csv("scraped_dataframe.csv", index=False, encoding="utf-8-sig")

for filename in os.listdir("."):
    if filename.endswith(".json"):
        with open(os.path.join(".", filename), "r", encoding="utf-8") as file:
            data = json.load(file)

        tcac = data.get("TCAC")
        if tcac in filtered_df["Cod_TCAC"].values:
            subgroup = filtered_df.loc[
                filtered_df["Cod_TCAC"] == tcac, "Subgroup"
            ].values
            if len(subgroup) > 0:
                data["subgroup"] = subgroup[0]

        with open(os.path.join(".", filename), "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
