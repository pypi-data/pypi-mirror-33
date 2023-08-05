from collections import defaultdict


NOT_AVAILABLE_TEXT = ""


def _dict_to_default_dict(d: dict) -> dict:
    """Converts a dict to a default dict.

    This is done to convert dicts to

    :param d: A dictionary with data
    :return: A dictionary that will return "not available" when accessing non-existing indices.
    """
    if isinstance(d, dict):
        for key, value in d.items():
            d[key] = _dict_to_default_dict(value)
        d = defaultdict(lambda: NOT_AVAILABLE_TEXT, **d)
    return d


def formatted(headers: list, data: list, formatter: callable, show_headers: bool = True) -> str:
    """Helper for creating formatted outputs
    
    :param headers: Headers of the data
    :param data: Data to output
    :param formatter: Function that turns a list of data into a string based on the headers
    :param show_header: Whether or not to display the headers
    :returns: A formatted string based on the input-data
    """
    printable_header = {header: header for header in headers}
    out = (formatter(printable_header, headers) + "\n") if show_headers else ""

    for row in data:
        row = _dict_to_default_dict(row)
        out += formatter(row, headers) + "\n"

    return out


def csv(headers: list, data: list,
        formatter: callable = lambda row, headers: [str(row[field]) for field in headers],
        show_headers: bool = True):
    """Standard CSV printer"""

    def csv_formatter(row, headers):
        return ",".join(formatter(row, headers))

    return formatted(headers, data, csv_formatter, show_headers)


def formatted_string(headers: list, data: list, format_string: str, show_headers=False) -> str:
    """Using format-strings for outputs.

    Simply calls .format(...) on the supplied string
    """

    def formatter(row: dict, headers: list):
        return format_string.format(**row)

    return formatted(headers, data, formatter, show_headers)
