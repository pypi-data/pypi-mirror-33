"""
A configuration dict we pickle and depickle to store values so the user does not need to
enter them every single time
"""
import constants as c

CONFIG = {
    # false if the configs have been set
    "virgin": True,
    "ark": {
        # names used by arky to initialize
        "arky": "ark",
        "coin_in_sat": c.ARK,
        "epoch": 1490101200,
        "tip": 1 * c.ARK,
        "tipping_address": "AJwHyHAArNmzGfmDnsJenF857ATQevg8HY"
    },
    "dark": {
        # names used by arky to initialize
        "arky": "dark",
        "coin_in_sat": c.ARK,
        "testnet": True,
    },
    "test_persona": {
        # names used by arky to initialize
        "arky": "tprs",
        "coin_in_sat": c.ARK,
        "testnet": True,

    },
    # I do not acknowledge kapu as an actual network
    "kapu": {
        # names used by arky to initialize
        "arky": "kapu",
        "coin_in_sat": c.ARK,
        "testnet": True,
    },
    "persona": {
        # names used by arky to initialize
        "arky": "prs",
        "coin_in_sat": c.ARK,
        "testnet": True,
    }
}