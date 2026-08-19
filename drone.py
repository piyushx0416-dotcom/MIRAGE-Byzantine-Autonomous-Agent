import numpy as np
import random

class Drone:
    def __init__(self, drone_id, x, y, is_malicious=False):
        self.id = drone_id
        self.x = x                        # real x position
        self.y = y                        # real y position
        self.is_malicious = is_malicious  # secret - hidden from system
        self.reported_x = x              # what it tells others
        self.reported_y = y
        self.color = (0, 255, 0)         # green = good
        self.speed = 2
        self.task_completed = 0
        self.messages_sent = []
        self.velocity_x = random.uniform(-1, 1)
        self.velocity_y = random.uniform(-1, 1)

    def move(self, width, height):
        # Move drone
        self.x += self.velocity_x * self.speed
        self.y += self.velocity_y * self.speed

        # Bounce off walls
        if self.x <= 10 or self.x >= width - 10:
            self.velocity_x *= -1
        if self.y <= 10 or self.y >= height - 10:
            self.velocity_y *= -1

        # Keep inside screen
        self.x = max(10, min(width - 10, self.x))
        self.y = max(10, min(height - 10, self.y))

        # Update reported position
        if self.is_malicious:
            # LIE about position
            self.reported_x = self.x + random.uniform(50, 150)
            self.reported_y = self.y + random.uniform(50, 150)
        else:
            # Tell truth
            self.reported_x = self.x + random.uniform(-2, 2)
            self.reported_y = self.y + random.uniform(-2, 2)

    def get_reported_position(self):
        return (self.reported_x, self.reported_y)

    def get_real_position(self):
        return (self.x, self.y)

    def report_to_neighbors(self, neighbors):
        """What this drone tells its neighbors"""
        reports = []
        for neighbor in neighbors:
            if self.is_malicious:
                # Malicious: lie about neighbor positions too
                fake_x = neighbor.x + random.uniform(-100, 100)
                fake_y = neighbor.y + random.uniform(-100, 100)
                reports.append({
                    'reporter_id': self.id,
                    'target_id': neighbor.id,
                    'reported_x': fake_x,
                    'reported_y': fake_y,
                    'is_lie': True
                })
            else:
                # Honest: report correctly
                reports.append({
                    'reporter_id': self.id,
                    'target_id': neighbor.id,
                    'reported_x': neighbor.x + random.uniform(-3, 3),
                    'reported_y': neighbor.y + random.uniform(-3, 3),
                    'is_lie': False
                })
        return reports