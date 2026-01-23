"""Models model library"""

from lib.helpers import logit, get_all


def convert_family_id(model_family_id):
    logit(f"Converting family ID: {model_family_id}")

    model_families = get_all("model_families")
    logit(f"Retrieved model families", f"Got: {model_families}")

    if len(model_families) == 0:
        logit("No model families found")
        return None

    model_family = next(
        (mf for mf in model_families if mf["id"] == model_family_id), None
    )
    logit(f"Found model family: {model_family}")

    return model_family
