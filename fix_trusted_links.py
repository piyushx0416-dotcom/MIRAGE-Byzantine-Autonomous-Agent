from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_trusted_links_fix.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_trusted_links_fix.py")
else:
    print("Backup already exists: main_before_trusted_links_fix.py")


# ---------------------------------------------------------
# 1. Replace update_trust_scores() with more stable version
# ---------------------------------------------------------

new_update_trust = '''    def update_trust_scores(self):
        """
        Updates trust score for every drone.
        This improved version avoids destroying honest drones' trust
        just because of temporary false alarms.
        """

        for drone in self.swarm.drones:
            rx, ry = drone.get_reported_position()
            real_x, real_y = drone.get_real_position()

            position_error = np.sqrt((rx - real_x) ** 2 + (ry - real_y) ** 2)

            penalty = 0.0
            reward = 0.0

            in_classical = drone.id in self.classical_suspected
            in_ml = drone.id in self.ml_suspected

            # Position lying penalty
            if position_error > 140:
                penalty += 3.5
            elif position_error > 90:
                penalty += 2.0
            elif position_error > 50:
                penalty += 0.9
            else:
                reward += 0.9

            # Detector penalty:
            # Strong penalty only if BOTH methods agree.
            if in_classical and in_ml:
                penalty += 2.4

            # If only one detector flags it, give smaller penalty.
            # This prevents ML false alarms from killing trust too fast.
            elif in_classical or in_ml:
                if position_error > 50:
                    penalty += 0.9
                else:
                    penalty += 0.2

            # Strong recovery for stable honest-looking behavior
            if not in_classical and not in_ml and position_error < 30:
                reward += 1.2

            old_score = self.trust_scores.get(drone.id, 100.0)
            new_score = old_score - penalty + reward

            # Keep score inside 0-100
            new_score = max(0, min(100, new_score))
            self.trust_scores[drone.id] = new_score

        avg_trust = sum(self.trust_scores.values()) / len(self.trust_scores)
        self.trust_history.append(avg_trust)

        if len(self.trust_history) > 80:
            self.trust_history.pop(0)

'''

if "    def update_trust_scores(self):" in text:
    try:
        start = text.index("    def update_trust_scores(self):")
        end = text.index("    def get_trust_color", start)
        text = text[:start] + new_update_trust + text[end:]
        print("Updated trust scoring logic.")
    except ValueError:
        print("WARNING: Could not fully replace update_trust_scores().")
else:
    print("WARNING: update_trust_scores() not found. Skipping trust update fix.")


# ---------------------------------------------------------
# 2. Replace get_communication_links() with stable version
# ---------------------------------------------------------

new_comm_links = '''    def get_communication_links(self):
        communication_range = 190
        links = []

        drones = self.swarm.drones

        for i in range(len(drones)):
            for j in range(i + 1, len(drones)):
                a = drones[i]
                b = drones[j]

                dist = np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

                if dist <= communication_range:
                    a_trust = self.get_drone_trust_value(a.id)
                    b_trust = self.get_drone_trust_value(b.id)
                    min_trust = min(a_trust, b_trust)

                    a_classical = a.id in self.classical_suspected
                    b_classical = b.id in self.classical_suspected
                    a_ml = a.id in self.ml_suspected
                    b_ml = b.id in self.ml_suspected

                    a_detected_by_both = a_classical and a_ml
                    b_detected_by_both = b_classical and b_ml

                    one_detector_alert = (
                        a_classical or a_ml or b_classical or b_ml
                    )

                    both_detector_alert = (
                        a_detected_by_both or b_detected_by_both
                    )

                    # Dropped link simulation:
                    # Dropped links should happen sometimes, not constantly.
                    if both_detector_alert or min_trust < 35:
                        dropped = ((self.frame + a.id * 7 + b.id * 13) % 73 == 0)
                    else:
                        dropped = ((self.frame + a.id * 11 + b.id * 17) % 139 == 0)

                    if dropped:
                        status = "DROPPED"
                        color = (110, 110, 120)

                    # Very low trust means low-trust communication
                    elif min_trust < 30:
                        status = "LOW_TRUST"
                        color = PURPLE

                    # Suspicious only when stronger evidence exists
                    elif both_detector_alert:
                        status = "SUSPICIOUS"
                        color = RED

                    # If one detector alerts but trust is still okay,
                    # do not immediately mark as suspicious.
                    elif one_detector_alert and min_trust < 55:
                        status = "SUSPICIOUS"
                        color = RED

                    # Otherwise, communication is trusted
                    else:
                        status = "TRUSTED"
                        color = CYAN

                    links.append({
                        "a": a,
                        "b": b,
                        "distance": dist,
                        "status": status,
                        "color": color,
                        "min_trust": min_trust
                    })

        return links

'''

if "    def get_communication_links(self):" in text:
    try:
        start = text.index("    def get_communication_links(self):")
        end = text.index("    def get_network_metrics", start)
        text = text[:start] + new_comm_links + text[end:]
        print("Updated communication link classification.")
    except ValueError:
        print("ERROR: Could not replace get_communication_links().")
        sys.exit(1)
else:
    print("ERROR: get_communication_links() not found.")
    sys.exit(1)


# ---------------------------------------------------------
# 3. Replace get_network_metrics() with ratio-based health
# ---------------------------------------------------------

new_network_metrics = '''    def get_network_metrics(self):
        links = self.get_communication_links()

        trusted = sum(1 for l in links if l["status"] == "TRUSTED")
        suspicious = sum(1 for l in links if l["status"] == "SUSPICIOUS")
        low_trust = sum(1 for l in links if l["status"] == "LOW_TRUST")
        dropped = sum(1 for l in links if l["status"] == "DROPPED")

        total = len(links)
        active = trusted + suspicious + low_trust

        if total == 0:
            return {
                "total": 0,
                "active": 0,
                "trusted": 0,
                "suspicious": 0,
                "low_trust": 0,
                "dropped": 0,
                "health": 0
            }

        suspicious_ratio = suspicious / total
        low_trust_ratio = low_trust / total
        dropped_ratio = dropped / total
        trusted_ratio = trusted / total

        health = 100

        health -= suspicious_ratio * 35
        health -= low_trust_ratio * 40
        health -= dropped_ratio * 25

        # Reward stable trusted communication
        health += trusted_ratio * 10

        # If network is too sparse, reduce health slightly
        if total < 8:
            health -= 10

        health = int(max(0, min(100, health)))

        return {
            "total": total,
            "active": active,
            "trusted": trusted,
            "suspicious": suspicious,
            "low_trust": low_trust,
            "dropped": dropped,
            "health": health
        }

'''

if "    def get_network_metrics(self):" in text:
    try:
        start = text.index("    def get_network_metrics(self):")
        end = text.index("    def draw_dashed_line", start)
        text = text[:start] + new_network_metrics + text[end:]
        print("Updated network health calculation.")
    except ValueError:
        print("ERROR: Could not replace get_network_metrics().")
        sys.exit(1)
else:
    print("ERROR: get_network_metrics() not found.")
    sys.exit(1)


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("TRUSTED LINKS FIX COMPLETE.")
print("Now run: python main.py")
print("Trusted links should no longer fall to 0 too quickly.")