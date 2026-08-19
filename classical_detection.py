import numpy as np

class ClassicalByzantineDetector:
    """
    Classical method: Voting
    If drone's reported position is far from
    what MOST others say → it's suspicious
    """

    def __init__(self, threshold=60):
        self.threshold = threshold
        self.suspected = set()

    def detect(self, drones):
        self.suspected = set()
        positions = {}

        # Collect all reported positions
        for drone in drones:
            positions[drone.id] = drone.get_reported_position()

        # For each drone, check if its report matches majority
        for drone in drones:
            rx, ry = drone.get_reported_position()

            # Compare with all others
            deviations = []
            for other in drones:
                if other.id == drone.id:
                    continue
                ox, oy = other.get_reported_position()
                dist = np.sqrt((rx - ox)**2 + (ry - oy)**2)
                deviations.append(dist)

            # If this drone is far from average cluster → suspect
            if len(deviations) > 0:
                avg_deviation = np.mean(deviations)
                # Real drones cluster together in reports
                # Malicious ones are outliers
                all_avg = []
                for d in drones:
                    px, py = d.get_reported_position()
                    ds = [np.sqrt((px-o.get_reported_position()[0])**2 +
                                  (py-o.get_reported_position()[1])**2)
                          for o in drones if o.id != d.id]
                    all_avg.append(np.mean(ds))

                global_avg = np.mean(all_avg)

                if avg_deviation > global_avg + self.threshold:
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

        precision = (true_positive / len(detected)
                     if len(detected) > 0 else 0)
        recall = true_positive / len(real_bad)

        return true_positive, false_positive, false_negative