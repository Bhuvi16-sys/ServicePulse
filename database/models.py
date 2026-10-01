class User:
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password


class Service:
    def __init__(self, service_id, service_name, url, created_at=None):
        self.service_id = service_id
        self.service_name = service_name
        self.url = url
        self.created_at = created_at


class MonitoringLog:
    def __init__(self, log_id, service_id, checked_at, status, status_code, response_time):
        self.log_id = log_id
        self.service_id = service_id
        self.checked_at = checked_at
        self.status = status
        self.status_code = status_code
        self.response_time = response_time
