COMPOUNDS = {
    "sodium_chloride": {
        "display_name": "Sodium Chloride",
        "formula": "NaCl",
        "category": "inorganic_salt",
        "kappa": 1.28,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Petters & Kreidenweis (2007), ACP 7:1961, Table 1",
        "notes": "CCN-derived value; sigma assumed = water at T=298.15K in source.",
    },
    "ammonium_sulfate": {
        "display_name": "Ammonium Sulfate",
        "formula": "(NH4)2SO4",
        "category": "inorganic_salt",
        "kappa": 0.61,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Petters & Kreidenweis (2007), ACP 7:1961, Table 1",
        "notes": "Based on Clegg et al. (1998) AIM model calculations.",
    },
    "ammonium_nitrate": {
        "display_name": "Ammonium Nitrate",
        "formula": "NH4NO3",
        "category": "inorganic_salt",
        "kappa": 0.67,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Petters & Kreidenweis (2007), ACP 7:1961, Table 1",
        "notes": "Based on Svenningsson et al. (2006) measurements.",
    },
    "sulfuric_acid": {
        "display_name": "Sulfuric Acid",
        "formula": "H2SO4",
        "category": "inorganic_salt",
        "kappa": 0.90,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Petters & Kreidenweis (2007), ACP 7:1961, Table 1",
        "notes": "",
    },
    "sodium_nitrate": {
        "display_name": "Sodium Nitrate",
        "formula": "NaNO3",
        "category": "inorganic_salt",
        "kappa": 0.88,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Petters & Kreidenweis (2007), ACP 7:1961, Table 1",
        "notes": "CCN-derived (gf-derived alternative: 0.80). Often shows continuous water uptake, no sharp deliquescence point.",
    },
    "sodium_bisulfate": {
        "display_name": "Sodium Bisulfate",
        "formula": "NaHSO4",
        "category": "inorganic_salt",
        "kappa": 0.91,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Petters & Kreidenweis (2007), ACP 7:1961, Table 1",
        "notes": "CCN-derived (gf-derived alternative: 1.01).",
    },
    "sodium_sulfate": {
        "display_name": "Sodium Sulfate",
        "formula": "Na2SO4",
        "category": "inorganic_salt",
        "kappa": 0.80,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Petters & Kreidenweis (2007), ACP 7:1961, Table 1",
        "notes": "CCN-derived (gf-derived alternative: 0.68).",
    },
    "letovicite": {
        "display_name": "Letovicite",
        "formula": "(NH4)3H(SO4)2",
        "category": "inorganic_salt",
        "kappa": 0.65,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Petters & Kreidenweis (2007), ACP 7:1961, Table 1",
        "notes": "'Acidic ammonium sulfate' -- not the same as sodium bisulfate. CCN-derived (gf-derived alternative: 0.51).",
    },
    "potassium_chloride": {
        "display_name": "Potassium Chloride",
        "formula": "KCl",
        "category": "inorganic_salt",
        "kappa": 1.2,  # approximated as similar to NaCl per source
        "kappa_type": "measured",
        "sigma": None,
        "source": "Carrico et al. (2010), cited in Petters & Kreidenweis (2013), ACP 13:1081",
        "notes": "Source states 'KCl has kappa similar to NaCl' without a single precise value -- treat as approximate.",
    },
    "calcium_chloride": {
        "display_name": "Calcium Chloride",
        "formula": "CaCl2",
        "category": "inorganic_salt",
        "kappa": 0.525,  # midpoint of 0.49-0.56
        "kappa_type": "measured",
        "sigma": None,
        "source": "Sullivan et al. (2009), ACP 9:3303; range confirmed by Tang et al. (2019), ACP 19:2115",
        "notes": "Reported range 0.49-0.56. Proxy for processed/saline mineral dust and sea salt.",
    },
    "sucrose": {
        "display_name": "Sucrose",
        "formula": "C12H22O11",
        "category": "organic",
        "kappa": 0.084,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Gohil & Asa-Awuku (2022), AMT 15:1007 (theoretical value; measured range 0.036-0.10)",
        "notes": "Measured value depends on technique; theoretical value used here.",
    },
    "glycerol": {
        "display_name": "Glycerol",
        "formula": "C3H8O3",
        "category": "organic",
        "kappa": 0.28,
        "kappa_type": "derived",  # FLAGGED -- not a confirmed measured value
        "sigma": None,
        "source": "Derived via Petters & Kreidenweis (2007) molecular-property formula -- no confirmed primary measured source located",
        "notes": "FLAG: this is an ESTIMATE, not a directly measured literature value. Treat with lower confidence than other entries.",
    },
    "silver_iodide": {
        "display_name": "Silver Iodide",
        "formula": "AgI",
        "category": "ice_nucleus",
        "kappa": 0.0,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Solubility Ksp = 8.3e-17, Utah Div. of Water Resources (2011) report",
        "notes": "FLAG: functions as an ice nucleus, not a CCN, due to near-zero solubility. Real seeding solutions add NaCl to make particles CCN-active -- model that added NaCl fraction separately via the volume-mixing rule, don't assign CCN activity to AgI itself.",
    },
    "sea_salt": {
        "display_name": "Sea Salt (mixed inorganic)",
        "formula": None,
        "category": "inorganic_salt",
        "kappa": 1.1,
        "kappa_type": "measured",
        "sigma": None,
        "source": "Zieger et al. (2017), Nat. Commun. 8:15883 (recommended value at RH=90%; range 0.91-1.33 per Petters & Kreidenweis 2007)",
        "notes": "8-15% lower growth than pure NaCl, likely due to hydrates.",
    },
    # Surfactants (DERIVED kappa, measured sigma)
    "ctab": {
        "display_name": "CTAB (Cetyltrimethylammonium Bromide)",
        "formula": "C19H42BrN",
        "category": "surfactant",
        "kappa": 0.30,  # from earlier project research
        "kappa_type": "derived",
        "sigma": 0.036,
        "sigma_type": "measured",
        "cmc_mM": 0.93,
        "measurement_temp_K": 298.0,
        "source": "Project's earlier surfactant chemistry research (CMC/surface tension literature)",
        "notes": "sigma measured at ~25C -- warmer than cloud-base temperature.",
    },
    "sls_sds": {
        "display_name": "SLS / SDS (Sodium Dodecyl Sulfate)",
        "formula": "C12H25NaO4S",
        "category": "surfactant",
        "kappa": 0.134,  # CCN-chamber measured, overriding pure derivation
        "kappa_type": "measured",
        "sigma": 0.037,
        "sigma_type": "measured",
        "cmc_mM": 8.1,
        "measurement_temp_K": 298.0,
        "source": "kappa: Ruehl et al. (2010) via Petters & Kreidenweis (2013), ACP 13:1081 (kappa_chem,SDS=0.134); CMC/sigma: Mukerjee & Mysels (1971), NSRDS-NBS 36, confirmed arXiv:1909.01085",
        "notes": "kappa here is a real CCN-chamber measurement, NOT derived -- stronger confidence than most surfactant entries. CCN-apparent kappa reported elsewhere as 0.15-0.18.",
    },
    "capb": {
        "display_name": "CAPB (Cocamidopropyl Betaine)",
        "formula": "C19H38N2O3",
        "category": "surfactant",
        "kappa": 0.20,  # from earlier project research
        "kappa_type": "derived",
        "sigma": 0.033,
        "sigma_type": "measured",
        "cmc_mM": 0.90,
        "measurement_temp_K": 298.0,
        "source": "Project's earlier surfactant chemistry research (CMC/surface tension literature)",
        "notes": "Zwitterionic -- van't Hoff factor assumption in kappa derivation is less certain than for ionic surfactants.",
    },
    "sdbs": {
        "display_name": "SDBS (Sodium Dodecylbenzenesulfonate)",
        "formula": "C18H29NaO3S",
        "category": "surfactant",
        "kappa": 0.12,  # placeholder derived value
        "kappa_type": "derived",
        "sigma": 0.030,  #midpoint of 28-33 mN/m range
        "sigma_type": "measured",
        "cmc_mM": 1.5,
        "measurement_temp_K": 298.0,
        "source": "CMC/sigma: Zhu (EIU thesis); Tyowua et al. (2012), Chem. Sci. J. CSJ-79",
        "notes": "FLAG: CMC has wide reported spread (0.4-2 mM) since commercial SDBS is often a branched-isomer mixture. kappa is a rough placeholder -- recompute via the P&K formula with real MW/density before relying on this.",
    },
    "triton_x100": {
        "display_name": "Triton X-100",
        "formula": None,  #average formula, n~9.5 EO units
        "category": "surfactant",
        "kappa": 0.05,  #placeholder -- nonionic, low kappa expected
        "kappa_type": "derived",
        "sigma": 0.0306,
        "sigma_type": "measured",
        "cmc_mM": 0.23,
        "measurement_temp_K": 298.0,
        "source": "CMC: Sigma/ChemicalBook product data; sigma: arXiv:2111.07021 (Wilhelmy plate)",
        "notes": "Nonionic (van't Hoff factor ~1) -- kappa placeholder needs proper recomputation with real MW (~625 average).",
    },
    "tween_20": {
        "display_name": "Tween 20 (Polysorbate 20)",
        "formula": None,
        "category": "surfactant",
        "kappa": 0.03,  #placeholder, very low expected for large nonionic MW
        "kappa_type": "derived",
        "sigma": 0.0385,  #midpoint of 37-40
        "sigma_type": "measured",
        "cmc_mM": 0.06,
        "measurement_temp_K": 298.0,
        "source": "Mittal (1972), J. Pharm. Sci. 61:1334; Sidim (2013), J. Surf. Deterg. 16:601",
        "notes": "Very large MW (~1228) -- kappa placeholder needs recomputation.",
    },
    "cpc": {
        "display_name": "Cetylpyridinium Chloride (CPC)",
        "formula": "C21H38ClN",
        "category": "surfactant",
        "kappa": 0.28,  #placeholder, cationic similar order to CTAB
        "kappa_type": "derived",
        "sigma": 0.039,  #midpoint of 38-40
        "sigma_type": "measured",
        "cmc_mM": 0.9,
        "measurement_temp_K": 298.0,
        "source": "Mukhim & Ismail (2012), J. Surf. Deterg. 15:47",
        "notes": "Cationic, complementary to CTAB -- kappa placeholder needs proper recomputation.",
    },
    "aot": {
        "display_name": "AOT / Docusate Sodium (Dioctyl Sulfosuccinate)",
        "formula": "C20H37NaO7S",
        "category": "surfactant",
        "kappa": 0.18,  #placeholder, twin-tail anionic
        "kappa_type": "derived",
        "sigma": 0.028,  #midpoint of 26-30
        "sigma_type": "measured",
        "cmc_mM": 2.5,
        "measurement_temp_K": 298.0,
        "source": "Colloids Surf. A S092777572301854X",
        "notes": "Twin-tail anionic -- kappa placeholder needs proper recomputation.",
    },
    "sodium_oleate": {
        "display_name": "Sodium Oleate",
        "formula": "C18H33NaO2",
        "category": "surfactant",
        "kappa": 0.20,  #placeholder
        "kappa_type": "derived",
        "sigma": 0.0275,  #midpoint of 25-30
        "sigma_type": "measured",
        "cmc_mM": 0.1,
        "measurement_temp_K": 298.0,
        "source": "Theander & Pugh (2001), J. Colloid Interface Sci. 239:209",
        "notes": "FLAG: strongly pH- and temperature-dependent, measured at pH 12. Precipitation near CMC complicates measurement. kappa placeholder needs recomputation.",
    },
}


def get_compound(key):
    """Look up a compound by its dict key. Raises KeyError with a helpful
    message listing available keys if not found."""
    if key not in COMPOUNDS:
        raise KeyError(f"'{key}' not in database. Available: {sorted(COMPOUNDS.keys())}")
    return COMPOUNDS[key]


def list_by_category(category):
    """Return all compound keys matching a category (inorganic_salt, organic,
    surfactant, ice_nucleus)."""
    return [k for k, v in COMPOUNDS.items() if v["category"] == category]


def list_derived_kappa():
    """Return compound keys where kappa is DERIVED/ESTIMATED rather than
    directly measured -- useful for a confidence-flagging UI element."""
    return [k for k, v in COMPOUNDS.items() if v.get("kappa_type") == "derived"]