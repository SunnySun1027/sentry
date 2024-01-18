from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from snuba_sdk import Request as SnubaRequest
from snuba_sdk.column import Column
from snuba_sdk.conditions import Condition, Op
from snuba_sdk.entity import Entity
from snuba_sdk.expressions import Granularity
from snuba_sdk.function import Function
from snuba_sdk.orderby import Direction, OrderBy
from snuba_sdk.query import Query

from sentry.api.bases import FilterParams
from sentry.services.hybrid_cloud.organization.model import RpcOrganization
from sentry.snuba.dataset import Dataset
from sentry.utils import snuba


def get_errors_counts_timeseries_by_project_and_release(
    end: datetime,
    organization_id: int,
    project_id_list: List[int],
    release_value_list: List[str],
    start: datetime,
    environments_list: List[str] | None = None,
) -> List[Dict[str, Any]]:
    additional_conditions = []
    if environments_list:
        additional_conditions.append(Condition(Column("environment"), Op.IN, environments_list))
    query = Query(
        match=Entity("events"),  # synonymous w/ discover dataset
        select=[Function("count", [])],
        groupby=[
            Column("release"),
            Column("project_id"),
            Column("environment"),
            Column("time"),  # groupby 'time' gives us a timeseries
        ],
        orderby=[
            OrderBy(Column("time"), Direction.DESC),
        ],
        granularity=Granularity(60),
        where=[
            Condition(Column("type"), Op.EQ, "error"),
            Condition(Column("timestamp"), Op.GTE, start),
            Condition(Column("timestamp"), Op.LT, end),
            Condition(Column("project_id"), Op.IN, project_id_list),
            Condition(Column("release"), Op.IN, release_value_list),
            *additional_conditions,
        ],
    )
    request = SnubaRequest(
        dataset=Dataset.Events.value,
        app_id="default",
        query=query,
        tenant_ids={"organization_id": organization_id},
    )
    data = snuba.raw_snql_query(
        request=request, referrer="snuba.sessions.check_releases_have_health_data"
    )["data"]

    return data


from django.utils.datastructures import MultiValueDict
from rest_framework.request import Request

from sentry import release_health
from sentry.api.utils import handle_query_errors
from sentry.models.organization import Organization
from sentry.snuba.sessions_v2 import QueryDefinition

# In minutes
TWO_WEEKS = 20160
ONE_WEEK = 10080
TWENTY_FOUR_HOURS = 1440


def fetch_sessions_data(
    request: Request,
    organization: Organization | RpcOrganization,
    params: FilterParams,
    end: datetime,
    start: datetime,
    field: str | None = "sum(session)",  # alternatively count_unique(user)
):
    """
    This implementation was derived from organization_sessions GET endpoint
    NOTE: Params are derived from the request query and pulls the relevant project/environment objects
    TODO: make fetch generic for other session types
    TODO: capture potential issues with `interval` returning too many results
    """
    with handle_query_errors():
        request_get: dict[str, Any] = request.GET
        query_params: MultiValueDict[str, Any] = MultiValueDict(request_get)
        query_params.setlist("groupBy", ["project", "release", "session.status", "environment"])
        query_params.setlist("field", [field])
        query_params["query"] = " OR ".join(
            [f"release:{version}" for version in query_params.getlist("release")]
        )
        interval = "1hr"
        query_params["interval"] = interval
        query_params["start"] = start
        query_params["end"] = end

        # crash free rates are on a dynamic INTERVAL basis
        # TODO: determine how this affects results for new releases
        query_config = release_health.backend.sessions_query_config(organization)

        # NOTE: params start/end are overwritten by query start/end
        query = QueryDefinition(
            query=query_params,
            params=params,
            query_config=query_config,
        )

        return release_health.backend.run_sessions_query(
            organization.id, query, span_op="release_thresholds.endpoint"
        )