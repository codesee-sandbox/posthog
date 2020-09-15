from typing import Dict, List, Optional, Tuple

from ee.clickhouse.client import ch_client
from ee.clickhouse.models.cohort import format_cohort_table_name
from ee.clickhouse.sql.cohort import COHORT_DISTINCT_ID_FILTER_SQL
from ee.clickhouse.sql.events import EVENT_PROP_CLAUSE, SELECT_PROP_VALUES_SQL
from posthog.models.cohort import Cohort
from posthog.models.property import Property
from posthog.models.team import Team


def parse_filter(filters: List[Property]) -> Tuple[str, Dict]:
    result = ""
    params = {}
    for idx, prop in enumerate(filters):
        result += "{cond}(ep.key = %(k{idx})s) AND (ep.value = %(v{idx})s)".format(
            idx=idx, cond=" AND " if idx > 0 else ""
        )
        params.update({"k{}".format(idx): prop.key, "v{}".format(idx): prop.value})
    return result, params


def parse_prop_clauses(key: str, filters: List[Property], team: Team) -> Tuple[str, Dict]:
    final = ""
    params = {}

    for idx, prop in enumerate(filters):

        if prop.type == "cohort":
            cohort = Cohort.objects.get(pk=prop.value)
            clause = COHORT_DISTINCT_ID_FILTER_SQL.format(table_name=format_cohort_table_name(cohort))
            final += "{cond} ({clause}) ".format(cond="AND distinct_id IN", clause=clause)

        else:
            filter = "(ep.key = %(k{idx})s) AND (ep.value {operator} %(v{idx})s)".format(
                idx=idx, operator=get_operator(prop.operator)
            )
            clause = EVENT_PROP_CLAUSE.format(team_id=team.pk, filters=filter)
            final += "{cond} ({clause}) ".format(cond="AND {key} IN".format(key=key), clause=clause)
            params.update({"k{}".format(idx): prop.key, "v{}".format(idx): prop.value})
    return final, params


# TODO: handle all operators
def get_operator(operator: Optional[str]):
    if operator == "is_not":
        return "!="
    elif operator == "icontains":
        return "LIKE"
    elif operator == "not_icontains":
        return "NOT LIKE"
    elif operator == "regex":
        return "="
    elif operator == "not_regex":
        return "="
    elif operator == "gt":
        return ">"
    elif operator == "lt":
        return "<"
    else:
        return "="


def get_property_values_for_key(key: str, team: Team):
    result = ch_client.execute(SELECT_PROP_VALUES_SQL, {"team_id": team.pk, "key": key})
    return result
