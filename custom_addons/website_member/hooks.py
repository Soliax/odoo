# -*- coding: utf-8 -*-
from datetime import date


DEMO_DIVERS = [
    {
        "login": "diver.1star",
        "plongeur": True,
        "hsa": False,
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
        "specs": {"dive_spec_cfps": date(2024, 6, 1)},
    },
    {
        "login": "diver.2star",
        "plongeur": True,
        "hsa": True,
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
        "other_brevets": "CFPS / Nitrox",
        "cfps_end": date(2028, 4, 15),
        "specs": {
            "dive_spec_cfps": date(2023, 4, 15),
            "dive_spec_pn": date(2023, 10, 5),
        },
    },
    {
        "login": "diver.3star",
        "plongeur": True,
        "hsa": False,
        "brevet": "3",
        "firstname": "Marc",
        "lastname": "ThreeStar",
        "function": "Membre",
        "profession": "Ingenieur",
        "street": "Avenue du Large 8",
        "zip": "1200",
        "city": "Woluwe",
        "phone": "0470 33 33 33",
        "email": "marc.threestar@example.com",
        "birthday": date(1988, 7, 3),
        "lifras_id": "30003",
        "specs": {
            "dive_spec_cfps": date(2022, 3, 10),
            "dive_spec_ve": date(2023, 5, 20),
            "dive_spec_pn": date(2022, 11, 8),
        },
    },
    {
        "login": "diver.4star",
        "plongeur": False,
        "hsa": True,
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
        "specs": {
            "dive_spec_cfps": date(2021, 2, 2),
            "dive_spec_ve": date(2022, 8, 14),
            "dive_spec_pn": date(2021, 9, 9),
            "dive_spec_pnc": date(2024, 1, 18),
        },
    },
    {
        "login": "diver.am",
        "plongeur": True,
        "hsa": True,
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
        "specs": {
            "dive_spec_cfps": date(2020, 4, 4),
            "dive_spec_ve": date(2021, 6, 6),
            "dive_spec_pn": date(2020, 10, 10),
            "dive_spec_pnc": date(2022, 12, 12),
            "dive_spec_in": date(2024, 3, 3),
        },
    },
    {
        "login": "diver.mc",
        "plongeur": True,
        "hsa": False,
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
        "specs": {
            "dive_spec_cfps": date(2019, 1, 15),
            "dive_spec_ve": date(2019, 7, 7),
            "dive_spec_pn": date(2018, 5, 5),
            "dive_spec_pnc": date(2020, 9, 9),
            "dive_spec_in": date(2021, 11, 11),
            "dive_spec_inc": date(2023, 4, 4),
        },
    },
    {
        "login": "diver.mf",
        "plongeur": False,
        "hsa": True,
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
        "specs": {
            "dive_spec_cfps": date(2017, 2, 2),
            "dive_spec_ve": date(2017, 8, 8),
            "dive_spec_pn": date(2016, 3, 3),
            "dive_spec_pnc": date(2018, 6, 6),
            "dive_spec_in": date(2019, 10, 10),
            "dive_spec_inc": date(2021, 1, 1),
            "dive_spec_fn": date(2024, 5, 5),
        },
    },
    {
        "login": "diver.mn",
        "plongeur": True,
        "hsa": True,
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
        "specs": {
            "dive_spec_cfps": date(2015, 1, 1),
            "dive_spec_ve": date(2015, 4, 4),
            "dive_spec_pn": date(2014, 2, 2),
            "dive_spec_pnc": date(2016, 7, 7),
            "dive_spec_in": date(2017, 9, 9),
            "dive_spec_inc": date(2019, 3, 3),
            "dive_spec_fn": date(2022, 8, 8),
        },
    },
    {
        "login": "diver.nb",
        "plongeur": True,
        "hsa": False,
        "brevet": False,
        "firstname": "Sam",
        "lastname": "NonBrevete",
        "function": "Membre",
        "profession": "Etudiant",
        "street": "Rue du Masque 2",
        "zip": "1000",
        "city": "Bruxelles",
        "phone": "0470 99 00 01",
        "email": "sam.nb@example.com",
        "birthday": date(2003, 3, 3),
        "lifras_id": "90009",
        "specs": {},
    },
    {
        "login": "diver.hsa",
        "plongeur": False,
        "hsa": True,
        "brevet": False,
        "firstname": "Lea",
        "lastname": "Hockey",
        "function": "Hockey subaquatique",
        "profession": "Sportive",
        "street": "Avenue du Palet 7",
        "zip": "1050",
        "city": "Ixelles",
        "phone": "0470 99 00 02",
        "email": "lea.hsa@example.com",
        "birthday": date(1995, 8, 8),
        "lifras_id": "90010",
        "specs": {},
    },
]


def _brevet_date_vals(brevet, birthday=None):
    """Fill obtention dates up to the given brevet level."""
    order = ["1", "2", "3", "4", "am", "mc", "mf", "mn"]
    if not brevet or brevet not in order:
        return {}
    start_year = (birthday.year + 18) if birthday else 2012
    idx = order.index(brevet)
    vals = {}
    for i, code in enumerate(order[: idx + 1]):
        vals["dive_brevet_date_%s" % code] = date(start_year + i, 6, 15)
    return vals


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
        "dive_brevet": data.get("brevet") or False,
        "dive_lifras_id": data.get("lifras_id"),
        "dive_contact_name": data.get("contact_name"),
        "dive_contact_phone": data.get("contact_phone"),
        "dive_last_medical": data.get("last_medical"),
        "dive_last_ecg": data.get("last_ecg"),
        "dive_other_brevets": data.get("other_brevets"),
        "dive_cfps_end": data.get("cfps_end"),
        "dive_is_plongeur": data.get("plongeur", True),
        "dive_is_hsa": data.get("hsa", False),
    }
    partner_vals.update(_brevet_date_vals(data.get("brevet"), data.get("birthday")))
    partner_vals.update(data.get("specs") or {})
    if user:
        user.partner_id.write(partner_vals)
        user.write({
            "name": name,
            "members_published": True,
            "members_subtitle": data.get("function"),
            "password": "diverdemo",
        })
        return user

    partner = Partners.create(partner_vals)
    return Users.create({
        "name": name,
        "login": data["login"],
        "password": "diverdemo",
        "partner_id": partner.id,
        "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        "members_published": True,
        "members_subtitle": data.get("function"),
    })


def _clean_legacy_member_markup(env):
    """Strip obsolete builder attrs from saved website pages (cannot delete pages)."""
    import re

    pattern = re.compile(
        r'\sdata-border-(?:card|oval|name|specs|stat|gem)="[^"]*"'
        r'|\sdata-frame-(?:fit|scale-x|scale-y|grow-x|grow-y)="[^"]*"'
        r'|\sdata-oval-scale="[^"]*"'
        r'|\sdata-card-special-corners="[^"]*"',
        re.I,
    )
    views = env["ir.ui.view"].sudo().search([
        "|", "|",
        ("arch_db", "ilike", "data-border-"),
        ("arch_db", "ilike", "data-frame-"),
        ("arch_db", "ilike", "s_md_members"),
    ])
    for view in views:
        arch = view.arch_db or ""
        cleaned = pattern.sub("", arch)
        if cleaned != arch:
            view.write({"arch_db": cleaned})


def _seed_demo_event_registrations(env):
    """Link a few demo divers to existing events so profile pages show history."""
    if "event.registration" not in env or "event.event" not in env:
        return
    Event = env["event.event"].sudo()
    Registration = env["event.registration"].sudo()
    Users = env["res.users"].sudo()
    events = Event.search([], order="date_begin desc", limit=5)
    if not events:
        return
    pairs = [
        ("diver.mc", 0, "open"),
        ("diver.mc", 1, "done"),
        ("diver.2star", 0, "open"),
        ("diver.am", 0, "open"),
        ("diver.mn", 1, "done"),
        ("diver.hsa", 0, "open"),
    ]
    for login, event_idx, state in pairs:
        if event_idx >= len(events):
            continue
        user = Users.search([("login", "=", login)], limit=1)
        if not user:
            continue
        event = events[event_idx]
        existing = Registration.search([
            ("event_id", "=", event.id),
            ("partner_id", "=", user.partner_id.id),
        ], limit=1)
        if existing:
            if existing.state != state:
                existing.write({"state": state})
            continue
        Registration.with_context(
            mail_create_nolog=True,
            mail_notrack=True,
            tracking_disable=True,
        ).create({
            "event_id": event.id,
            "partner_id": user.partner_id.id,
            "name": user.partner_id.name,
            "email": user.partner_id.email,
            "state": state,
        })


def post_init_hook(env):
    for data in DEMO_DIVERS:
        _upsert_demo_diver(env, data)
    other = env.ref("website_member.field_other_brevets", raise_if_not_found=False)
    if other:
        other.write({"section": "specialties", "sequence": 90})
    _clean_legacy_member_markup(env)
    _seed_demo_event_registrations(env)
