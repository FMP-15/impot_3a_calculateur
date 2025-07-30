def get_commune_info(npa, communes_data):
    if str(npa) not in communes_data:
        raise ValueError(f"NPA {npa} non trouvé dans le fichier des communes.")
    entries = communes_data[str(npa)]
    # On prend la première occurrence en cas de doublon
    return entries[0]


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
    """
    Applique un système de tranches successives (sans impôt cumulé)
    """
    reste = revenu
    total = 0
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
    """
    Applique un système avec impôt cumulé (ex. Genève, Vaud)
    """
    for tranche in tranches:
        if revenu <= tranche["tranche"]:
            # S'il y a un impôt cumulé, on le retourne directement
            if "impot_cumule" in tranche:
                return tranche["impot_cumule"]
            else:
                return revenu * tranche["taux"] / 100
    # Si dépasse toutes les tranches
    return revenu * tranches[-1]["taux"] / 100


def calculer_impot(revenu, versement_3a, npa, situation_familiale, religion,
                   communes_data, cantonaux_data, confederation_data):
    # --- Revenu avant/après versement 3A ---
    revenu_apres_3a = max(0, revenu - versement_3a)

    # --- Infos commune ---
    commune = get_commune_info(npa, communes_data)
    canton_code = commune["canton"]
    taux_total = get_total_taux(commune, religion)

    # --- Barème cantonal ---
    barème_cantonal = cantonaux_data.get(canton_code)
    if not barème_cantonal:
        raise ValueError(f"Aucun barème pour le canton {canton_code}")

    # Gestion du barème applicable : situation ou "tous"
    if situation_familiale in barème_cantonal:
        tranches_canton = barème_cantonal[situation_familiale]
    elif "tous" in barème_cantonal:
        tranches_canton = barème_cantonal["tous"]
    else:
        raise ValueError(f"Aucun barème correspondant à la situation '{situation_familiale}' pour {canton_code}")

    # --- Barème fédéral ---
    tranches_conf = confederation_data["Confédération"].get(situation_familiale)
    if not tranches_conf:
        raise ValueError(f"Aucun barème fédéral pour la situation '{situation_familiale}'")

    # --- Calcul impôt sans 3A ---
    if "impot_cumule" in tranches_canton[0]:
        impot_cantonal_plein = appliquer_barème_cumulatif(revenu, tranches_canton)
        impot_cantonal_reduit = appliquer_barème_cumulatif(revenu_apres_3a, tranches_canton)
    else:
        impot_cantonal_plein = appliquer_barème_tranches(revenu, tranches_canton)
        impot_cantonal_reduit = appliquer_barème_tranches(revenu_apres_3a, tranches_canton)

    impot_federal_plein = appliquer_barème_tranches(revenu, tranches_conf)
    impot_federal_reduit = appliquer_barème_tranches(revenu_apres_3a, tranches_conf)

    # --- Total avec majoration communale/religieuse ---
    total_sans_3a = impot_federal_plein + impot_cantonal_plein * (1 + taux_total / 100)
    total_avec_3a = impot_federal_reduit + impot_cantonal_reduit * (1 + taux_total / 100)

    return {
        "impot_sans_3a": total_sans_3a,
        "impot_avec_3a": total_avec_3a,
        "economie_impot": total_sans_3a - total_avec_3a
    }
