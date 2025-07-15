import streamlit as st
from calculs import calcul_economie

st.set_page_config(page_title="Simulateur 3e pilier", page_icon=None)

st.title("Simulateur d'économie d'impôt - 3e pilier A")
st.markdown("Calcule ton économie fiscale selon ton revenu, ta commune et ton versement dans le 3e pilier.")

# Formulaire utilisateur
revenu = st.number_input("Revenu brut annuel (CHF)", min_value=0, step=1000)
versement = st.number_input("Montant versé au 3e pilier A (CHF)", min_value=0, step=500)

statut = st.selectbox("Statut civil", ["Célibataire", "Marié", "Partenaire enregistré"])
enfants = st.number_input("Nombre d’enfants à charge", min_value=0, step=1)

npa = st.text_input("Code postal (NPA)", max_chars=4)
religion = st.selectbox("Affiliation religieuse", ["Aucune", "Catholique", "Protestante"])

# Bouton d’action
if st.button("Calculer l’économie d’impôt"):
    if not npa.strip():
        st.warning("Veuillez entrer un code postal.")
    else:
        economie = calcul_economie(revenu, versement, statut.lower(), enfants, npa.strip(), religion)
        if economie is None:
            st.error("Impossible de trouver les données pour ce NPA.")
        else:
            st.success(f"Économie estimée : CHF {economie:,.2f}")
