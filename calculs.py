import json
import os

# Charger les barèmes de la Confédération
def charger_bareme_federal():
    chemin = os.path.join("data", "bareme_confederation.json")
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)

# Déterminer la catégorie fiscale à utiliser
def determiner_categorie_fiscale(statut, enfants):
    if enfants >= 1 or statut.lower() == "marié":
        return "Personne mariée / vivant seule, avec enfant"
    else:
        return "Personne vivant seule, sans enfant"

# Calculer l'impôt fédéral sur le revenu (selon barème)
def calculer_impot_federal(revenu_imposable, barème):
    impot = 0
    for tranche in barème:
        if revenu_imposable >= tranche["revenu_min"]:
            taux = tranche["taux"] / 100  # % vers décimal
            base = tranche["base"]
            impot = base + (revenu_imposable - tranche["revenu_min"]) * taux
        else:
            break
    return impot

# Fonction principale appelée par le frontend
def calculer_economie(revenu, versement_3a, statut, enfants, npa, religion):
    plafond = 7056  # Plafond 3e pilier A salarié (2025)
    versement_utilisé = min(versement_3a, plafond)

    barèmes = charger_bareme_federal()
    categorie = determiner_categorie_fiscale(statut, enfants)
    barème = barèmes.get(categorie, [])

    revenu_avant = revenu
    revenu_apres = max(0, revenu - versement_utilisé)

    impot_avant = calculer_impot_federal(revenu_avant, barème)
    impot_apres = calculer_impot_federal(revenu_apres, barème)

    economie = impot_avant - impot_apres
    return round(economie, 2)
