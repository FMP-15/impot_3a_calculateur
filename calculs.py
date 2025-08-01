def get_commune_info(npa, communes_data):
    if str(npa) not in communes_data:
        raise ValueError(f"NPA {npa} non trouvé dans le fichier des communes.")
    return communes_data[str(npa)][0]


def get_total_taux(commune, religion):
    taux_communal = commune.get("taux_communal", 0)
    taux_religion = 0

    if religion == "catholique":
        taux_religion = commune.get("taux_catholique", 0)
    elif religion == "réformée":
        taux_religion = commune.get("taux_reforme", 0)
    elif religion == "chrétienne":
        taux_religion = commune.get("taux_chretienne", 0)

    return taux_communal + taux_religion


def appliquer_barème_tranches(revenu, tranches):
    total = 0
    reste = revenu
    for i, tranche in enumerate(tranches):
        if "tranche" not in tranche or "taux" not in tranche:
            raise ValueError(f"Tranche invalide à l'index {i} : {tranche}")
        montant = tranche["tranche"]
        taux = tranche["taux"] / 100
        applicable = min(reste, montant)
        total += applicable * taux
        reste -= applicable
        if reste <= 0:
            break
    return total


def appliquer_barème_cumulatif(revenu, tranches):
    for i, tranche in enumerate(tranches):
        if "tranche" not in tranche:
            raise ValueError(f"Tranche invalide à l'index {i} : {tranche}")
        if revenu <= tranche["tranche"]:
            if "impot_cumule" in tranche:
                return tranche["impot_cumule"]
            elif "taux" in tranche:
                return revenu * tranche["taux"] / 100
            else:
                raise ValueError(f"Tranche incomplète à l'index {i} : {tranche}")
    last = tranches[-1]
    return last.get("impot_cumule", revenu * last.get("taux", 0) / 100)


def get_cantonal_tranches(situation_familiale, barème_cantonal):
    # Cherche clé exacte, sinon fallback sur état civil seul ou "tous"
    if situation_familiale in barème_cantonal:
        return barème_cantonal[situation_familiale]
    elif situation_familiale.split("_")[0] in barème_cantonal:
        return barème_cantonal[situation_familiale.split("_")[0]]
    elif "tous" in barème_cantonal:
        return barème_cantonal["tous"]
    else:
        raise ValueError(f"Aucun barème cantonal trouvé pour la situation '{situation_familiale}'")


def get_federal_tranches(situation_familiale, confederation_data):
    # Traduction des situations
    if situation_familiale == "célibataire_sans_enfant":
        conf_key = "Personne vivant seule, sans enfant"
    elif situation_familiale in ["célibataire_avec_enfant", "marié_avec_enfant"]:
        conf_key = "Personne mariée / vivant seule, avec enfant"
    elif situation_familiale == "marié_sans_enfant":
        conf_key = "Personne vivant seule, sans enfant"
    else:
        raise ValueError(f"Situation fiscale non reconnue pour la Confédération : {situation_familiale}")

    tranches = confederation_data["Confédération"].get(conf_key)
    if not tranches:
        raise ValueError(f"Aucun barème fédéral pour la situation '{conf_key}'")
    return tranches


def calculer_impot(revenu, versement_3a, npa, situation_familiale, religion,
                   communes_data, cantonaux_data, confederation_data):
    revenu_reduit = max(0, revenu - versement_3a)

    # Commune & taux total
    commune = get_commune_info(npa, communes_data)
    canton_code = commune["canton"]
    taux_total = get_total_taux(commune, religion)

    # Barèmes cantonaux et fédéraux
    barème_cantonal = cantonaux_data.get(canton_code)
    if not barème_cantonal:
        raise ValueError(f"Aucun barème pour le canton {canton_code}")

    tranches_canton = get_cantonal_tranches(situation_familiale, barème_cantonal)
    tranches_conf = get_federal_tranches(situation_familiale, confederation_data)

    # Canton : détection auto du type de barème
    use_cumulatif = any("impot_cumule" in tranche for tranche in tranches_canton)
    if use_cumulatif:
        cantonal_sans = appliquer_barème_cumulatif(revenu, tranches_canton)
        cantonal_avec = appliquer_barème_cumulatif(revenu_reduit, tranches_canton)
    else:
        cantonal_sans = appliquer_barème_tranches(revenu, tranches_canton)
        cantonal_avec = appliquer_barème_tranches(revenu_reduit, tranches_canton)

    # Fédéral : toujours en barème par tranches simples
    federal_sans = appliquer_barème_tranches(revenu, tranches_conf)
    federal_avec = appliquer_barème_tranches(revenu_reduit, tranches_conf)

    # Total
    total_sans = federal_sans + cantonal_sans * (1 + taux_total / 100)
    total_avec = federal_avec + cantonal_avec * (1 + taux_total / 100)

    return {
        "impot_sans_3a": total_sans,
        "impot_avec_3a": total_avec,
        "economie_impot": total_sans - total_avec
    }
