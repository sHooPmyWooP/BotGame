class mission_type_ids(object):
    """
    OGame internal IDs for Mission types
    """
    attack = 1
    transport = 3
    park = 4
    park_ally = 5
    spy = 6
    colonize = 7
    recycle = 8
    destroy = 9
    expedition = 15
    trade = 16


class messages:
    """
    OGame internal IDs for Inboxes
    """
    spy_reports = 20
    fight = 21
    expedition = 22
    transport = 23
    other = 24


class expo_messages:
    """
    Keywords to classify Expo Messages
    """
    keywords = {
        "pirats": ["piraten", "weltraumpiraten", "primitive barbaren", "sternen-freibeuter"],
        "aliens": ["fremdartige rasse", "alienrasse", "unbekannten spezies", "fremdartig anmutenden schiffe",
                   "unbekannter schiffe", "fremdartig anmutende schiffe"],
        "resources": ["erbeutet"],
        "nothing": ["roten riesen", "bestes-bild-des-universums", "kurioser", "das führungsschiff", "leere des alls",
                    "gravitationsfeld",
                    "reaktorfehler", "computervirus", "hypnotischen muster", "leeren Händen", "Dschungelfieber",
                    "bugs zu kämpfen", "rote Anomalien", "wunderschöne bilder", "fremde Spezies zu begrüßen",
                    "uraltes Strategiespiel"],
        "delayed_return": ["verzögerte", "verspätung", "patzer des navigators",
                           "länger dauern als ursprünglich gedacht"],
        "faster_return": ["rückkopplung in den energiespulen", "deine expedition kehrt nun etwas früher"],
        "fleet_loss": ["flotte endgültig verloren"],
        "ships": ["schlossen sich der flotte an"],
        "item": ["unbemannten flieger", "wertvolles Artefakt", "gegenstand hinterlassen"],
        "dark_matter": ["dunkle materie"]
    }


class resources:
    metall = "Metall"
    kristall = "Kristall"
    deuterium = "Deuterium"
