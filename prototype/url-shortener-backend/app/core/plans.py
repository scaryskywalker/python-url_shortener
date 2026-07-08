from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    name: str
    token_limit: int | None
    url_validity_days: int | None


PLANS = {
    "Free": Plan("Free", 25, 30),
    "Growth": Plan("Growth", 250, 180),
    "Scale": Plan("Scale", 1000, 365),
    "Lifetime": Plan("Lifetime", None, None),
}


def get_plan(name: str) -> Plan:
    return PLANS.get(name, PLANS["Free"])


def plan_options() -> list[dict[str, int | str | None]]:
    return [
        {
            "name": plan.name,
            "token_limit": plan.token_limit,
            "url_validity_days": plan.url_validity_days,
        }
        for plan in PLANS.values()
    ]
