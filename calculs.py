import json
import os

# ---------- Chargement des données ----------

def charger_bareme_federal():
    chemin = os.path.join("data", "bareme_confederation.json")
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)

def charger_communes():
    chemin = os.path.join("data", "baremes_communes.json")
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------- Détermination de la catégorie fiscale ----------

def determiner_categorie_fiscale(statut, enfants):
    if enfants >= 1 or statut.lower() == "marié":
        return "Personne mariée / vivant seule, avec enfant"
    else:
        return "Personne vivant seule, sans enfant"

# ---------- Calcul progressif de l'impôt fédéral ----------

def calculer_impot_federal(revenu_imposable, barème):
    impot = 0
    for tranche in barème:
        if revenu_imposable >= tranche["revenu_min"]:
            taux = tranche["taux"] / 100
            base = tranche["base"]
            impot = base + (revenu_imposable - tranche["revenu_min"]) * taux
        else:
            break
    return impot

# ---------- Fonction principale ----------

def calculer_economie(revenu, versement_3a, statut, enfants, npa, religion):
    plafond = 7056  # Plafond 3e pilier A pour salarié en 2025
    versement_utilisé = min(versement_3a, plafond)

    # 1. Chargement des données
    barèmes = charger_bareme_federal()
    communes = charger_communes()

    # 2. Sélection de la situation fiscale
    categorie = determiner_categorie_fiscale(statut, enfants)
    barème = barèmes.get(categorie, [])

    # 3. Recherche de la commune
    commune_data = communes.get(str(npa))
    if not commune_data:
        return 0  # NPA inconnu → pas d’économie

    taux_communal = commune_data.get("taux_communal", 0)
    taux_religieux = commune_data.get("religion", {}).get(religion.lower(), 0)

    # 4. Calcul de l'impôt fédéral
    revenu_avant = revenu
    revenu_apres = max(0, revenu - versement_utilisé)

    impot_avant = calculer_impot_federal(revenu_avant, barème)
    impot_apres = calculer_impot_federal(revenu_apres, barème)
    economie_federale = impot_avant - impot_apres

    # 5. Calcul communal et religieux (proportionnel au revenu imposable)
    impot_commun_religion_avant = revenu_avant * (taux_communal + taux_religieux)
    impot_commun_religion_apres = revenu_apres * (taux_communal + taux_religieux)
    economie_locale = impot_commun_religion_avant - impot_commun_religion_apres

    # 6. Total
    economie_totale = economie_federale + economie_locale
    return round(economie_totale, 2)
