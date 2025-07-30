def get_commune_info(npa, communes_data):
    if str(npa) not in communes_data:
        raise ValueError(f"NPA {npa} non trouvé dans le fichier des communes.")
    entries = communes_data[str(npa)]
    return entries[0]  # On prend la première commune liée au NPA


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
    for tranche in tranches:
        montant = tranche["tranche"]
        taux = tranche["taux"] / 100
        applicable = min(reste, montant)
        total += applicable * taux
        reste -= applicable
        if reste <= 0:
            break
    return total


def appliquer_barème_cumulatif(revenu, tranches):
    for tranche in tranches:
        if revenu <= tranche["tranche"]:
            if "impot_cumule" in tranche:
                return tranche["impot_cumule"]
            else:
                return revenu * tranche["taux"] / 100
    return revenu * tranches[-1]["taux"] / 100


def calculer_impot(revenu, versement_3a, npa, situation_familiale, religion,
                   communes_data, cantonaux_data, confederation_data):
    revenu_reduit = max(0, revenu - versement_3a)

    # --- Infos sur la commune et canton ---
    commune = get_commune_info(npa, communes_data)
    canton_code = commune["canton"]
    taux_total = get_total_taux(commune, religion)

    # --- Barème cantonal ---
    barème_cantonal = cantonaux_data.get(canton_code)
    if not barème_cantonal:
        raise ValueError(f"Aucun barème pour le canton {canton_code}")

    if situation_familiale in barème_cantonal:
        tranches_canton = barème_cantonal[situation_familiale]
    elif situation_familiale.split("_")[0] in barème_cantonal:
        tranches_canton = barème_cantonal[situation_familiale.split("_")[0]]
    elif "tous" in barème_cantonal:
        tranches_canton = barème_cantonal["tous"]
    else:
        raise ValueError(f"Aucun barème correspondant à la situation '{situation_familiale}' pour {canton_code}")

    # --- Barème fédéral ---
    tranches_conf = confederation_data["Confédération"].get(situation_familiale)
    if not tranches_conf:
        raise ValueError(f"Aucun barème fédéral pour la situation '{situation_familiale}'")

    # --- Impôt cantonal ---
    is_cumulatif = "impot_cumule" in tranches_canton[0]
    if is_cumulatif:
        cantonal_sans = appliquer_barème_cumulatif(revenu, tranches_canton)
        cantonal_avec = appliquer_barème_cumulatif(revenu_reduit, tranches_canton)
    else:
        cantonal_sans = appliquer_barème_tranches(revenu, tranches_canton)
        cantonal_avec = appliquer_barème_tranches(revenu_reduit, tranches_canton)

    # --- Impôt fédéral (toujours successif) ---
    federal_sans = appliquer_barème_tranches(revenu, tranches_conf)
    federal_avec = appliquer_barème_tranches(revenu_reduit, tranches_conf)

    total_sans = federal_sans + cantonal_sans * (1 + taux_total / 100)
    total_avec = federal_avec + cantonal_avec * (1 + taux_total / 100)

    return {
        "impot_sans_3a": total_sans,
        "impot_avec_3a": total_avec,
        "economie_impot": total_sans - total_avec
    }
