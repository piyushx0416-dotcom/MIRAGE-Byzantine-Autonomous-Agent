import random
from drone import Drone

class Swarm:
    def __init__(self, total_drones=20, malicious_count=5,
                 width=800, height=600):
        self.width = width
        self.height = height
        self.drones = []
        self.total = total_drones
        self.malicious_count = malicious_count
        self.create_swarm()

    def create_swarm(self):
        malicious_ids = random.sample(
            range(self.total), self.malicious_count
        )

        for i in range(self.total):
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            is_bad = i in malicious_ids

            drone = Drone(
                drone_id=i,
                x=x, y=y,
                is_malicious=is_bad
            )
            if is_bad:
                drone.color = (255, 0, 0)  # red internally
            self.drones.append(drone)

    def update(self):
        for drone in self.drones:
            drone.move(self.width, self.height)

    def get_all_reports(self):
        """Collect what every drone reports"""
        all_reports = []
        for drone in self.drones:
            neighbors = [d for d in self.drones if d.id != drone.id]
            reports = drone.report_to_neighbors(neighbors[:5])
            all_reports.extend(reports)
        return all_reports