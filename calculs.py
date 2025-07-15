import json

def charger_baremes():
    with open("data/bareme_confederation.json", encoding="utf-8") as f:
        conf = json.load(f)
    with open("data/baremes_cantonaux.json", encoding="utf-8") as f:
        cantons = json.load(f)
    with open("data/baremes_communes.json", encoding="utf-8") as f:
        communes = json.load(f)
    return conf, cantons, communes

def appliquer_bareme(bareme, revenu_imposable):
    impot = 0
    precedent = 0
    for tranche in bareme:
        seuil = tranche["seuil"]
        taux = tranche["taux"] / 100
        if revenu_imposable > seuil:
            impot += (seuil - precedent) * taux
            precedent = seuil
        else:
            impot += (revenu_imposable - precedent) * taux
            break
    return round(impot, 2)

def trouver_canton_et_taux(communes_data, npa, religion):
    entree = communes_data.get(str(npa))
    if not entree:
        return None, 0.0, 0.0
    canton = entree["canton"]
    communal = entree.get("taux_communal", 0.0)
    religieux = entree.get("taux_religion", {}).get(religion, 0.0)
    return canton, communal, religieux

def calcul_economie(revenu_brut, versement_3a, statut, enfants, npa, religion):
    conf, cantons, communes = charger_baremes()

    situation = "Personne vivant seule, sans enfant"
    if statut == "marie" or enfants > 0:
        situation = "Personne mariée / vivant seule, avec enfant"

    revenu_imposable = revenu_brut - versement_3a

    # Barème confédération
    bareme_conf = conf.get(situation, [])
    impot_conf = appliquer_bareme(bareme_conf, revenu_brut) - appliquer_bareme(bareme_conf, revenu_imposable)

    # Trouver canton via commune
    canton, taux_communal, taux_religieux = trouver_canton_et_taux(communes, npa, religion)
    if not canton:
        return None

    bareme_canton = cantons.get(canton, {}).get(situation, [])
    impot_canton = appliquer_bareme(bareme_canton, revenu_brut) - appliquer_bareme(bareme_canton, revenu_imposable)

    # Impôt communal et religieux (calculés proportionnellement à la base cantonale)
    base_apres_3a = appliquer_bareme(bareme_canton, revenu_imposable)
    base_avant_3a = appliquer_bareme(bareme_canton, revenu_brut)
    eco_commune = (base_avant_3a - base_apres_3a) * (taux_communal / 100)
    eco_religion = (base_avant_3a - base_apres_3a) * (taux_religieux / 100)

    total_economie = round(impot_conf + impot_canton + eco_commune + eco_religion, 2)
    return total_economie
