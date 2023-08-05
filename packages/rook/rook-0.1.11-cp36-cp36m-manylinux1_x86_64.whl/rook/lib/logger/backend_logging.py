import os


def add_backend_specific_logs(logging_values):
    if os.environ.get('SYSTEM_APP') == "rookout_backend":
        import flask
        if flask.has_request_context():
            request_url, request_id = flask.request.url, flask.request.headers.get("RUID")
            logging_values["requestUrl"] = request_url
            logging_values["requestId"] = request_id
