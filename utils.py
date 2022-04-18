from flask import Response, make_response


def prepare_response(*args) -> Response:
    resp = make_response(*args)
    resp.headers["Content-Security-Policy"] = "default-srd 'none'; frame-ancestors 'none'"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


def sanitize(s: str) -> str:
    return s.replace("'", "''")
