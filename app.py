import streamlit as st
import json
import os
from calculs import calculer_impot

# --- Chargement des fichiers JSON ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

with open(os.path.join(DATA_DIR, "baremes_communes.json"), "r", encoding="utf-8") as f:
    communes_data = json.load(f)

with open(os.path.join(DATA_DIR, "baremes_cantonaux.json"), "r", encoding="utf-8") as f:
    cantonaux_data = json.load(f)

with open(os.path.join(DATA_DIR, "bareme_confederation.json"), "r", encoding="utf-8") as f:
    confederation_data = json.load(f)

# --- Interface utilisateur ---
st.title("💼 Calculateur d’économie d’impôt 3ème pilier (3A)")

col1, col2 = st.columns(2)
with col1:
    npa = st.text_input("Code postal (NPA)", "1000")
    revenu = st.number_input("Revenu imposable net (CHF)", min_value=0, value=80000, step=1000)
with col2:
    versement_3a = st.number_input("Montant 3ème pilier (CHF)", min_value=0, value=7056, step=100)

etat_civil = st.selectbox("État civil", ["célibataire", "marié"])
avec_enfant = st.checkbox("Avec enfant(s)", value=False)

situation_familiale = f"{etat_civil}_{'avec_enfant' if avec_enfant else 'sans_enfant'}"

religion = st.radio("Appartenance religieuse", ["aucune", "catholique", "réformée", "chrétienne"], index=0)

# --- Lancement du calcul ---
if st.button("Calculer l’économie d’impôt"):
    try:
        resultat = calculer_impot(
            revenu=revenu,
            versement_3a=versement_3a,
            npa=int(npa),
            situation_familiale=situation_familiale,
            religion=religion,
            communes_data=communes_data,
            cantonaux_data=cantonaux_data,
            confederation_data=confederation_data
        )

        st.success("Résultats du calcul")
        st.markdown(f"- 💼 **Impôt sans 3A** : CHF **{resultat['impot_sans_3a']:.2f}**")
        st.markdown(f"- 🏦 **Impôt avec 3A** : CHF **{resultat['impot_avec_3a']:.2f}**")
        st.markdown(f"- 📉 **Économie d’impôt** : CHF **{resultat['economie_impot']:.2f}**")

    except Exception as e:
        st.error(f"Erreur : {e}")
