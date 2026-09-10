# -*- coding: utf-8 -*-
from datetime import date


DEMO_DIVERS = [
    {
        "login": "diver.1star",
        "brevet": "1",
        "firstname": "Nora",
        "lastname": "OneStar",
        "function": "Membre",
        "profession": "Etudiante",
        "street": "Rue des Algues 12",
        "zip": "1000",
        "city": "Bruxelles",
        "phone": "0470 11 11 11",
        "email": "nora.onestar@example.com",
        "birthday": date(2001, 5, 14),
        "lifras_id": "10001",
    },
    {
        "login": "diver.2star",
        "brevet": "2",
        "firstname": "Vinciane",
        "lastname": "Aubry",
        "function": "Membre",
        "profession": "Enseignante",
        "street": "Rue de l'Infante 184",
        "zip": "1410",
        "city": "Waterloo",
        "phone": "0473 74 75 20",
        "email": "vincianeaubry@example.com",
        "birthday": date(1976, 2, 11),
        "lifras_id": "54666",
        "contact_name": "Jacques Hanappe",
        "contact_phone": "0470 35 41 44",
        "last_medical": date(2025, 12, 17),
        "last_ecg": date(2025, 12, 17),
        "other_brevets": "CFPS / Nitrox Basic",
        "cfps": True,
        "nitrox": date(2023, 10, 5),
        "cfps_start": date(2023, 4, 15),
        "cfps_end": date(2028, 4, 15),
    },
    {
        "login": "diver.3star",
        "brevet": "3",
        "firstname": "Marc",
        "lastname": "ThreeStar",
        "function": "Membre",
        "profession": "Ingenieur",
        "street": "Avenue du Large 8",
        "zip": "1200",
        "city": "Woluw?",
        "phone": "0470 33 33 33",
        "email": "marc.threestar@example.com",
        "birthday": date(1988, 7, 3),
        "lifras_id": "30003",
    },
    {
        "login": "diver.4star",
        "brevet": "4",
        "firstname": "Ines",
        "lastname": "FourStar",
        "function": "Membre",
        "profession": "Infirmiere",
        "street": "Chemin des Recifs 3",
        "zip": "1050",
        "city": "Ixelles",
        "phone": "0470 44 44 44",
        "email": "ines.fourstar@example.com",
        "birthday": date(1984, 11, 21),
        "lifras_id": "40004",
    },
    {
        "login": "diver.am",
        "brevet": "am",
        "firstname": "Hugo",
        "lastname": "Assistant",
        "function": "Assistant Moniteur",
        "profession": "Coach",
        "street": "Quai des Palmes 19",
        "zip": "1180",
        "city": "Uccle",
        "phone": "0470 55 55 55",
        "email": "hugo.am@example.com",
        "birthday": date(1982, 1, 9),
        "lifras_id": "50005",
    },
    {
        "login": "diver.mc",
        "brevet": "mc",
        "firstname": "Claire",
        "lastname": "MoniteurClub",
        "function": "Moniteur Club",
        "profession": "Formatrice",
        "street": "Boulevard Ocean 45",
        "zip": "1030",
        "city": "Schaerbeek",
        "phone": "0470 66 66 66",
        "email": "claire.mc@example.com",
        "birthday": date(1979, 9, 18),
        "lifras_id": "60006",
    },
    {
        "login": "diver.mf",
        "brevet": "mf",
        "firstname": "Olivier",
        "lastname": "MoniteurFederal",
        "function": "Moniteur Federal",
        "profession": "Consultant",
        "street": "Place des Abysses 1",
        "zip": "1000",
        "city": "Bruxelles",
        "phone": "0470 77 77 77",
        "email": "olivier.mf@example.com",
        "birthday": date(1975, 4, 2),
        "lifras_id": "70007",
    },
    {
        "login": "diver.mn",
        "brevet": "mn",
        "firstname": "Amine",
        "lastname": "MoniteurNational",
        "function": "Moniteur National",
        "profession": "Instructeur",
        "street": "Route des Courants 99",
        "zip": "1160",
        "city": "Auderghem",
        "phone": "0470 88 88 88",
        "email": "amine.mn@example.com",
        "birthday": date(1971, 12, 28),
        "lifras_id": "80008",
    },
]


def _upsert_demo_diver(env, data):
    Users = env["res.users"].sudo()
    Partners = env["res.partner"].sudo()
    user = Users.search([("login", "=", data["login"])], limit=1)
    name = "%s %s" % (data["firstname"], data["lastname"])
    partner_vals = {
        "name": name,
        "street": data.get("street"),
        "zip": data.get("zip"),
        "city": data.get("city"),
        "phone": data.get("phone"),
        "email": data.get("email"),
        "function": data.get("function"),
        "dive_firstname": data["firstname"],
        "dive_lastname": data["lastname"],
        "dive_birthday": data.get("birthday"),
        "dive_profession": data.get("profession"),
        "dive_brevet": data["brevet"],
        "dive_lifras_id": data.get("lifras_id"),
        "dive_contact_name": data.get("contact_name"),
        "dive_contact_phone": data.get("contact_phone"),
        "dive_last_medical": data.get("last_medical"),
        "dive_last_ecg": data.get("last_ecg"),
        "dive_other_brevets": data.get("other_brevets"),
        "dive_cfps": data.get("cfps", False),
        "dive_nitrox_basic_date": data.get("nitrox"),
        "dive_cfps_start": data.get("cfps_start"),
        "dive_cfps_end": data.get("cfps_end"),
    }
    if user:
        user.partner_id.write(partner_vals)
        user.write({
            "name": name,
            "directory_published": True,
            "directory_subtitle": data.get("function"),
        })
        user.write({"password": "diverdemo"})
        return user

    partner = Partners.create(partner_vals)
    user = Users.create({
        "name": name,
        "login": data["login"],
        "password": "diverdemo",
        "partner_id": partner.id,
        "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        "directory_published": True,
        "directory_subtitle": data.get("function"),
    })
    return user


def post_init_hook(env):
    for data in DEMO_DIVERS:
        _upsert_demo_diver(env, data)


def post_load_hook():
    # unused placeholder kept for clarity
    return
