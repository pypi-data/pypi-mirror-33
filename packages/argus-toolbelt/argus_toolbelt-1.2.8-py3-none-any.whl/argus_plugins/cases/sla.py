import time
from datetime import datetime

from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_api.api.cases.v2.case import advanced_case_search, list_case_comments, update_case
from argus_api.api.events.v1.aggregated import find_aggregated_events

from argus_plugins.cases import utils
from .utils import get_customer_id

# The plugin that has all sla commands
SLA_PLUGIN = ("cases", "sla")


def _to_csv(values: list):
    return ",".join(values)


def _date_time(input):
    """Parses a time argument in a ISO8601 format

    Can either be just date, or date + time
    """
    if len(input) is len("YYYY-mm-dd"):
        time_format = "%Y-%m-%d"
    elif len(input) is len("YYYY-mm-ddTHH-MM-SS"):
        time_format = "%Y-%m-%dT%H:%M:%S"
    elif input == "now":
        return int(time.mktime(datetime.now().timetuple()) * 1e3)  # Add milliseconds
    else:
        raise ValueError("Invalid time input-format. Use ISO8601 format")
    date = datetime.strptime(input, time_format)
    return int(time.mktime(date.timetuple()) * 1e3)


def _time_diff(input):
    """Converts the input from one unit to milliseconds"""
    units = {"s": 1, "m": 60, "h": 60 * 60, "d": 60 * 60 * 24, "w": 60 * 60 * 24 * 7}
    if input == "now":
        return 0
    else:
        return int(input[:-1]) * units[input[-1]] * 1000


def timestamp_to_period(timestamp: int):
    """Converts a timestamp to a ISO8601 style period with days"""
    return datetime.fromtimestamp(timestamp).strftime("P%jDT%H:%M:%S")


def timestamp_to_date(timestamp: int):
    """Converts a timestamp to a ISO8601 style date and time"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S")


@register_command(extending=SLA_PLUGIN)
def escalate(before: _date_time, customer: get_customer_id, dry: bool = False,
             case_type: utils.CASE_TYPES = None, status: utils.STATUSES = None,
             priority: utils.PRIORITIES = None):
    """Escalates a case if it hasn't been resolved within a given timeframe

    :param before: Only get cases before this time
    :param customer: The customer short-name
    :param list case_type: Service types to include
    :param list status: Case statuses to include
    :param list priority: Priorities to include
    :param dry: Dry run - don't push changes upstream
    """
    cases = advanced_case_search(
        limit=0,
        customerID=customer,
        type=case_type, status=status, priority=priority,
        endTimestamp=before, timeFieldStrategy=["createdTimestamp"],
        subCriteria=[{"exclude": True, "status": "closed"}]
    )["data"]

    for case in cases:
        log.info("Escalating #%s" % case["id"])
        if dry:
            log.info("Dry run - skipping update")
        else:
            update_case(
                id=case["id"],
                priority="high",
                status="pendingSoc",
                comment="Escalated support case as it has been open for more than %s days" % before
            )


def get_case_statistics(case: dict) -> dict:
    """Gets SLA related statistics for a case"""
    times_closed = 0
    created_by_custumer = "SUBMITTED_BY_TECH" in case["flags"]
    first_response_time = None
    time_to_respond = None
    closed_at = None
    response_to_close_time = None

    comments = list_case_comments(limit=0, caseID=case["id"])["data"]
    last_status = None
    for comment in comments:
        if not first_response_time and "SUBMITTED_BY_TECH" in comment["flags"]:
            first_response_time = comment["addedTimestamp"]
            time_to_respond = first_response_time - case["createdTimestamp"]
        if comment["status"] == "closed" and last_status not in ("closed", "pendingClose"):
            times_closed += 1
        if not closed_at and comment["status"] in ("closed", "pendingClose"):
            # Get the first time we closed the case
            times_closed = 1
            closed_at = comment["addedTimestamp"]
            response_to_close_time = closed_at - first_response_time if first_response_time else None
        last_status = comment["status"]

    return {
        "created_by_customer": created_by_custumer,
        "created_at": case["createdTimestamp"],
        "last_update": case["lastUpdatedTimestamp"],
        "times_closed": times_closed,
        "closed_at": closed_at or "Not closed",
        "first_response_time": first_response_time or "No response",
        "time_to_respond": time_to_respond or "No response",
        "response_to_close_time": response_to_close_time or "N/A",
    }


def print_statistics(statistics: dict) -> None:
    """Prints the statistics for each case"""
    headers = [
        "case_id", "created_by_customer", "created_at", "last_update", "closed_at", "times_closed",
        "first_response_time", "time_to_respond", "response_to_close_time"
    ]
    print(",".join(headers))

    for case_id, data in statistics.items():
        # We want to give the user a better timestamp than milliseconds since epoch
        data["created_at"] = timestamp_to_date(data["created_at"] / 1000.0)
        data["last_update"] = timestamp_to_date(data["created_at"] / 1000.0)

        if isinstance(data["closed_at"], int):
            data["closed_at"] = timestamp_to_date(data["closed_at"] / 1000.0)
        if isinstance(data["first_response_time"], int):
            data["first_response_time"] = timestamp_to_date(data["closed_at"] / 1000.0)
            data["time_to_respond"] = timestamp_to_period(data["time_to_respond"] / 1000.0)
        if isinstance(data["response_to_close_time"], int):
            data["response_to_close_time"] = timestamp_to_period(data["response_to_close_time"] / 1000.0)

        body = "#%s," % case_id
        body += ",".join([str(data[header]) for header in headers[1:]])  # Ignore case_id
        print(body)


@register_command(extending=SLA_PLUGIN, alias="incident")
def case_times(start: _date_time, end: _date_time, customer: get_customer_id,
               case_type: utils.CASE_TYPES = None, status: utils.STATUSES = None,
               priority: utils.PRIORITIES = None, category: str = None):
    """Gets SLA related statistics for cases

    These statistics are the likes of:
        time to respond,
        time to close,
        etc

    :param start: Earliest time to search for in ISO 8601 format
    :param end: Latest time to search for in ISO 8601 format
    :param customer: The customer short-name
    :param list case_type: Service types to include
    :param list status: Case statuses to include
    :param list priority: Priorities to include
    :param list category: Categories to include
    """
    log.debug("Getting related cases...")
    cases = advanced_case_search(
        limit=10000,
        customerID=[customer],
        type=case_type, status=status, priority=priority, category=category,
        startTimestamp=start, endTimestamp=end, timeFieldStrategy=["createdTimestamp"]
    )["data"]

    log.debug("Got %d cases" % len(cases))

    log.info("Getting case statistics...")
    statistics = {}
    for case in cases:
        log.debug("Querying case #%s" % case["id"])
        statistics[case["id"]] = get_case_statistics(case)

    log.info("Printing statistics...")
    print_statistics(statistics)


def parse_case_info(cases: list) -> dict:
    """Gets cases within the given timeframe"""
    info = {}
    for case in cases:
        info[case["id"]] = {
            "user": case["createdByUser"]["userName"],
            "case_subject": case["subject"],
            "case_priority": case["priority"],
            "case_created_time": case["createdTimestamp"],
        }

    return info


def get_earliest_event(events: list, cases: dict) -> dict:
    """Gets the earliest event for each case"""
    for event in events:
        case_id = event["associatedCase"]["id"]

        if "event_time" not in cases[case_id] and event["startTimestamp"] > cases[case_id]["case_created_time"]:
            # We only want the earliest event associated with the case
            continue
        elif "event_time" in cases[case_id] and event["startTimestamp"] > cases[case_id]["event_time"]:
            # We only want the earliest event associated with the case
            continue
        elif "argus.assessed.by.userid" not in event["properties"]:
            # If it isn't assessed by a user, that means that it's handled by a filter
            continue

        log.debug("Updating case #%s with event with time %s" % (case_id, event["startTimestamp"]))

        event_info = {
            "event_time": event["startTimestamp"],
            "event_ack_time": int(event["properties"]["argus.assessed.timestamp"]),
            "event_alarm": event["attackInfo"]["alarmDescription"],
        }
        cases[case_id].update(event_info)

    return cases


def calculate_lag(cases: dict, threshold: int) -> dict:
    """Calculates the lag for each case

    This will also remover cases without events or events that are under the threshold.
    """
    for case_id, case in cases.copy().items():
        if "event_time" not in case:
            log.debug("Deleting case #%s as it doesn't have any events" % case_id)
            del cases[case_id]
            continue

        case["lag"] = case["case_created_time"] - case["event_time"]
        if case["lag"] < threshold:
            log.debug(
                "Removing case #%s as it's below the lag threshold (%d < %d)."
                % (case_id, case["lag"], threshold)
            )
            del cases[case_id]
        else:
            log.debug("CASE: %d, EVENT: %d, LAG: %d" % (case["case_created_time"], case["event_time"], case["lag"]))
    return cases


def print_incident_statistics(cases: dict) -> None:
    """Prints the statistics as in a CSV format"""
    headers = [
        "case_id", "case_subject", "case_priority", "event_alarm",
        "case_created_time", "event_ack_time", "user", "lag"
    ]
    print(",".join(headers))

    for case_id, data in cases.items():
        # We want to give the user a better timestamp than seconds since epoch.
        data["case_created_time"] = timestamp_to_date(data["case_created_time"] / 1000.0)
        data["event_ack_time"] = timestamp_to_date(data["event_ack_time"] / 1000.0)
        data["lag"] = timestamp_to_period(data["lag"] / 1000.0)

        body = "#%s," % case_id
        body += ",".join([str(data[header]) for header in headers[1:]])  # Ignore case_id
        print(body)


@register_command(extending=SLA_PLUGIN, alias="soc")
def time_to_case(start: _date_time, end: _date_time, threshold: _time_diff):
    """Gives the lag between an event and the creation of an incident.

    :param start: The start time of the search
    :param end: The end time of the search
    :param threshold: SLA threshold
    :return:
    """
    log.info("Getting info about cases...")
    cases = advanced_case_search(
        limit=10000,
        startTimestamp=start, endTimestamp=end, timeFieldStrategy=["createdTimestamp"],
        type=["securityIncident"],  # Event's only create security incidents
    )["data"]

    log.info("Parsing each case...")
    cases = parse_case_info(cases)

    log.info("Getting events that created the case...")

    log.debug("Getting events...")
    events = find_aggregated_events(
        limit=100000,
        # An event can be from before the start-time
        startTimestamp=start - _time_diff("10w"), endTimestamp=end,
        associatedCaseID=[case_id for case_id in cases.keys()],
        minSeverity="high",
        includeFlags=["NOTIFIED"],
    )["data"]

    log.debug("Parsing events...")
    cases = get_earliest_event(events, cases)

    log.info("Calculating lag time...")
    cases = calculate_lag(cases, threshold)

    log.info("Printing statistics")
    print_incident_statistics(cases)
