import threading
import time

from database.db import get_services, save_monitoring_result
from monitoring.monitor import check_service


class MonitoringScheduler:

    def __init__(self, interval=60):
        self.interval = interval
        self.running = False
        self.thread = None

    def check_all_services(self):
        services = get_services()

        if not services:
            print("No services found.")
            return

        for service in services:
            service_id = service[0]
            service_name = service[1]
            url = service[2]

            print(f"Checking {service_name}...")

            result = check_service(url)

            save_monitoring_result(
                service_id=service_id,
                status=result["status"],
                status_code=result["status_code"],
                response_time=result["response_time"]
            )

            print(
                f"{service_name}: "
                f"{result['status']} "
                f"({result['response_time']} ms)"
            )

    def _run(self):
        while self.running:
            try:
                self.check_all_services()
            except Exception as error:
                print(f"Automation error: {error}")

            time.sleep(self.interval)

    def start(self):
        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()

        print(
            f"Automatic monitoring started "
            f"(every {self.interval} seconds)"
        )

    def stop(self):
        self.running = False
        print("Automatic monitoring stopped.")
