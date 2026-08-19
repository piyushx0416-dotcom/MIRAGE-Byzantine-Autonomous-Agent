import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class MLByzantineDetector:
    """
    ML Method: Isolation Forest
    Learns what NORMAL behavior looks like
    Then flags anything unusual as malicious
    """

    def __init__(self, contamination=0.25):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.suspected = set()
        self.history = []  # store past behavior

    def extract_features(self, drone, all_drones):
        """
        Features we extract from each drone:
        - How far its report is from real position
        - How different its report is vs others
        - Consistency over time
        """
        rx, ry = drone.get_reported_position()
        real_x, real_y = drone.get_real_position()

        # Feature 1: Reporting error (lie distance)
        report_error = np.sqrt(
            (rx - real_x)**2 + (ry - real_y)**2
        )

        # Feature 2: Distance from swarm center
        all_rx = [d.get_reported_position()[0] for d in all_drones]
        all_ry = [d.get_reported_position()[1] for d in all_drones]
        center_x = np.mean(all_rx)
        center_y = np.mean(all_ry)
        dist_from_center = np.sqrt(
            (rx - center_x)**2 + (ry - center_y)**2
        )

        # Feature 3: How isolated is this drone's report
        distances = []
        for other in all_drones:
            if other.id == drone.id:
                continue
            ox, oy = other.get_reported_position()
            d = np.sqrt((rx-ox)**2 + (ry-oy)**2)
            distances.append(d)

        avg_neighbor_dist = np.mean(distances) if distances else 0
        min_neighbor_dist = np.min(distances) if distances else 0

        # Feature 4: Velocity consistency
        vel_magnitude = np.sqrt(
            drone.velocity_x**2 + drone.velocity_y**2
        )

        return [
            report_error,
            dist_from_center,
            avg_neighbor_dist,
            min_neighbor_dist,
            vel_magnitude,
            rx, ry  # raw position
        ]

    def train(self, drones):
        """Train on current swarm data"""
        features = []
        for drone in drones:
            f = self.extract_features(drone, drones)
            features.append(f)

        X = np.array(features)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True

    def detect(self, drones):
        """Detect malicious drones"""
        if not self.is_trained:
            self.train(drones)

        self.suspected = set()
        features = []

        for drone in drones:
            f = self.extract_features(drone, drones)
            features.append(f)

        X = np.array(features)
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        # -1 means anomaly (malicious), 1 means normal

        for i, drone in enumerate(drones):
            if predictions[i] == -1:
                self.suspected.add(drone.id)

        return self.suspected

    def get_accuracy(self, drones):
        real_bad = {d.id for d in drones if d.is_malicious}
        detected = self.suspected

        if len(real_bad) == 0:
            return 0, 0, 0

        true_positive = len(real_bad & detected)
        false_positive = len(detected - real_bad)
        false_negative = len(real_bad - detected)

        return true_positive, false_positive, false_negative