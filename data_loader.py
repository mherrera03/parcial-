import pandas as pd
import streamlit as st
import os

# Ruta base = carpeta donde está este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_pets():
    # Busca el CSV en la misma carpeta o en subcarpeta data/
    for path in [
        os.path.join(BASE_DIR, "pet_adoption_data.csv"),
        os.path.join(BASE_DIR, "data", "pet_adoption_data.csv"),
        os.path.join(BASE_DIR, "pet_adoption_data(in).csv"),
    ]:
        if os.path.exists(path):
            return pd.read_csv(path)
    raise FileNotFoundError("No se encontró pet_adoption_data.csv")

@st.cache_data
def load_books():
    for path in [
        os.path.join(BASE_DIR, "books.csv"),
        os.path.join(BASE_DIR, "data", "books.csv"),
    ]:
        if os.path.exists(path):
            return pd.read_csv(path)
    raise FileNotFoundError("No se encontró books.csv")

FIELD_DESCRIPTIONS = {
    "PetID": "Identificador único de cada mascota (ej. PET0001).",
    "PetType": "Tipo de animal: Dog (Perro), Cat (Gato), Rabbit (Conejo), Bird (Pájaro).",
    "Breed": "Raza específica del animal dentro de su especie.",
    "AgeMonths": "Edad del animal expresada en meses.",
    "Color": "Color del pelaje o plumaje del animal.",
    "Size": "Tamaño corporal del animal: Small (Pequeño), Medium (Mediano), Large (Grande).",
    "WeightKg": "Peso del animal en kilogramos.",
    "Vaccinated": "Indica si el animal está vacunado: 1 = Sí, 0 = No.",
    "HealthCondition": "Indica si el animal tiene alguna condición médica: 1 = Sí, 0 = No.",
    "TimeInShelterDays": "Número de días que el animal lleva en el refugio.",
    "AdoptionFee": "Tarifa de adopción en dólares estadounidenses.",
    "PreviousOwner": "Indica si el animal tuvo dueño anterior: 1 = Sí, 0 = No.",
    "AdoptionLikelihood": "Variable objetivo: probabilidad de adopción. 1 = Adoptado, 0 = No adoptado.",
}