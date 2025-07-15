import json

def charger_baremes():
    with open("data/bareme_confederation.json", encoding="utf-8") as f:
        conf = json.load(f)
    with open("data/baremes_cantonaux.json", encoding="utf-8") as f:
        cantons = json.load(f)
    with open("data/baremes_communes.json", encoding="utf-8") as f:
        communes = json.load(f)
    return conf, cantons, communes

def appliquer_bareme(bareme, revenu):
    impot = 0
    precedent = 0
    for tranche in bareme:
        seuil = tranche["seuil"]
        taux = tranche["taux"] / 100
        if revenu > seuil:
            impot += (seuil - precedent) * taux
            precedent = seuil
        else:
            impot += (revenu - precedent) * taux
            break
    return round(impot, 2)

def trouver_commune_et_canton(communes_data, npa, religion):
    commune_data = communes_data.get(str(npa))
    if not commune_data:
        return None, None, 0.0, 0.0
    canton = commune_data["canton"]
    taux_communal = commune_data.get("taux_communal", 0.0)
    taux_religion = commune_data.get("taux_religion", {}).get(religion.lower(), 0.0)
    return commune_data["commune"], canton, taux_communal, taux_religion

def calcul_economie(revenu_brut, versement_3a, statut, enfants, npa, religion):
    conf, cantons, communes = charger_baremes()

    situation = "Personne vivant seule, sans enfant"
    if statut == "marié" or enfants > 0:
        situation = "Personne mariée / vivant seule, avec enfant"

    revenu_imposable = max(0, revenu_brut - versement_3a)

    commune, canton, taux_communal, taux_religion = trouver_commune_et_canton(communes, npa, religion)
    if not canton:
        return None

    bareme_conf = conf.get(situation, [])
    impot_conf_avant = appliquer_bareme(bareme_conf, revenu_brut)
    impot_conf_apres = appliquer_bareme(bareme_conf, revenu_imposable)
    economie_conf = impot_conf_avant - impot_conf_apres

    bareme_canton = cantons.get(canton, {}).get(situation, [])
    impot_cantonal_avant = appliquer_bareme(bareme_canton, revenu_brut)
    impot_cantonal_apres = appliquer_bareme(bareme_canton, revenu_imposable)
    economie_canton = impot_cantonal_avant - impot_cantonal_apres

    economie_commune = economie_canton * (taux_communal / 100)
    economie_religion = economie_canton * (taux_religion / 100)

    total_economie = round(economie_conf + economie_canton + economie_commune + economie_religion, 2)
    return total_economie
