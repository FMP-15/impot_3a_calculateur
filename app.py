import streamlit as st
import json
from calculs import calculer_impot

# Chargement des barèmes
with open("baremes_communes.json", "r", encoding="utf-8") as f:
    communes_data = json.load(f)

with open("baremes_cantonaux.json", "r", encoding="utf-8") as f:
    cantonaux_data = json.load(f)

with open("bareme_confederation.json", "r", encoding="utf-8") as f:
    confederation_data = json.load(f)

# --- UI ---
st.title("Calculateur d’économie d’impôt 3ème pilier (3A)")

col1, col2 = st.columns(2)
with col1:
    npa = st.text_input("Code postal (NPA)", "1000")
    revenu = st.number_input("Revenu imposable net (CHF)", min_value=0, value=80000, step=1000)
with col2:
    versement_3a = st.number_input("Montant 3ème pilier (CHF)", min_value=0, value=7056, step=100)
    situation = st.selectbox("Situation familiale", [
        "célibataire_sans_enfant", "célibataire_avec_enfant",
        "marié_sans_enfant", "marié_avec_enfant"
    ])
religion = st.radio("Appartenance religieuse", ["aucune", "catholique", "réformée", "chrétienne"], index=0)

if st.button("Calculer l’économie d’impôt"):
    try:
        resultat = calculer_impot(
            revenu=revenu,
            versement_3a=versement_3a,
            npa=int(npa),
            situation_familiale=situation,
            religion=religion,
            communes_data=communes_data,
            cantonaux_data=cantonaux_data,
            confederation_data=confederation_data
        )

        st.success("Résultats du calcul")
        st.write(f"💼 Impôt sans 3A : **CHF {resultat['impot_sans_3a']:.2f}**")
        st.write(f"🏦 Impôt avec 3A : **CHF {resultat['impot_avec_3a']:.2f}**")
        st.write(f"📉 Économie d’impôt : **CHF {resultat['economie_impot']:.2f}**")

    except Exception as e:
        st.error(f"Erreur : {e}")
