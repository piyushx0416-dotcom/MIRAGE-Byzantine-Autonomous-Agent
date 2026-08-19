from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_trust_never_zero_fix.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_trust_never_zero_fix.py")
else:
    print("Backup already exists: main_before_trust_never_zero_fix.py")


new_update_trust = '''    def update_trust_scores(self):
        """
        Stable Trust Score System v2.

        Main fix:
        Trust will no longer collapse to 0.
        Highly suspicious drones are pushed toward a low quarantine range,
        but not absolute zero.

        Trust meaning:
        80-100 = highly trusted
        55-80  = normal
        35-55  = suspicious
        15-35  = quarantine watch
        8-15   = critical but not zero
        """

        if not hasattr(self, "suspicion_memory"):
            self.suspicion_memory = {
                d.id: 0.0 for d in self.swarm.drones
            }

        if not hasattr(self, "clean_memory"):
            self.clean_memory = {
                d.id: 0 for d in self.swarm.drones
            }

        for drone in self.swarm.drones:
            rx, ry = drone.get_reported_position()
            real_x, real_y = drone.get_real_position()

            position_error = np.sqrt((rx - real_x) ** 2 + (ry - real_y) ** 2)

            in_classical = drone.id in self.classical_suspected
            in_ml = drone.id in self.ml_suspected

            # -----------------------------
            # Evidence calculation
            # -----------------------------
            evidence = 0.0

            # Position lying evidence
            if position_error > 170:
                evidence += 40
            elif position_error > 125:
                evidence += 28
            elif position_error > 80:
                evidence += 16
            elif position_error > 45:
                evidence += 7

            # Detector evidence
            # Strong only when both agree
            if in_classical and in_ml:
                evidence += 30

            # One method alone gives weak evidence
            elif in_classical or in_ml:
                if position_error > 70:
                    evidence += 10
                else:
                    evidence += 3

            # Strong combined evidence
            if in_classical and in_ml and position_error > 100:
                evidence += 12

            evidence = max(0, min(90, evidence))

            # -----------------------------
            # Suspicion memory update
            # -----------------------------
            old_suspicion = self.suspicion_memory.get(drone.id, 0.0)

            if evidence >= 45:
                # Strong repeated malicious behavior
                new_suspicion = old_suspicion + evidence * 0.075
                self.clean_memory[drone.id] = 0

            elif evidence >= 20:
                # Medium suspicious behavior
                new_suspicion = old_suspicion + evidence * 0.035
                self.clean_memory[drone.id] = 0

            elif evidence > 0:
                # Weak alert only slightly increases suspicion
                new_suspicion = old_suspicion + evidence * 0.006

            else:
                # Clean behavior decreases suspicion
                self.clean_memory[drone.id] = self.clean_memory.get(drone.id, 0) + 1

                clean_bonus = 3.0

                if self.clean_memory[drone.id] > 5:
                    clean_bonus = 4.5

                if self.clean_memory[drone.id] > 12:
                    clean_bonus = 6.0

                new_suspicion = old_suspicion - clean_bonus

            # Extra recovery for very stable clean behavior
            if not in_classical and not in_ml and position_error < 28:
                new_suspicion -= 2.5

            # Suspicion should not lock permanently at 100
            new_suspicion = max(0, min(92, new_suspicion))
            self.suspicion_memory[drone.id] = new_suspicion

            # -----------------------------
            # Convert suspicion to trust
            # -----------------------------
            # Minimum trust floor prevents ugly 0.0%
            # Serious malicious drones still go into quarantine range.
            if new_suspicion >= 85:
                trust_floor = 8
            elif new_suspicion >= 70:
                trust_floor = 12
            elif new_suspicion >= 55:
                trust_floor = 18
            else:
                trust_floor = 25

            target_trust = max(trust_floor, 100 - new_suspicion)

            old_trust = self.trust_scores.get(drone.id, 100.0)

            # Smooth transition:
            # trust moves toward target instead of crashing instantly.
            new_trust = old_trust * 0.90 + target_trust * 0.10

            # Clean drones recover gradually
            if evidence == 0 and position_error < 28:
                new_trust += 1.5

            # If trust is already extremely low, allow tiny recovery
            # so it does not visually stick at zero.
            if new_trust < trust_floor:
                new_trust = trust_floor

            new_trust = max(trust_floor, min(100, new_trust))

            self.trust_scores[drone.id] = new_trust

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
        print("Updated update_trust_scores(): trust will no longer collapse to 0.")
    except ValueError:
        print("ERROR: Could not replace update_trust_scores().")
        sys.exit(1)
else:
    print("ERROR: update_trust_scores() not found.")
    sys.exit(1)


# Update trust rules text if possible
old_rules_1 = '''        rules = [
            "Trust uses suspicion memory over time.",
            "Weak one-method alerts cause only small penalty.",
            "Strong repeated evidence lowers trust.",
            "Clean behavior reduces suspicion.",
            "Stable drones recover trust gradually."
        ]'''

new_rules = '''        rules = [
            "Trust uses suspicion memory over time.",
            "Trust no longer collapses to absolute zero.",
            "Weak one-method alerts cause tiny penalty.",
            "Repeated strong evidence causes quarantine.",
            "Clean behavior slowly restores trust."
        ]'''

if old_rules_1 in text:
    text = text.replace(old_rules_1, new_rules, 1)
    print("Updated trust rules text.")
else:
    print("Trust rules text not found or already changed. Skipping.")


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("TRUST NEVER-ZERO FIX COMPLETE.")
print("Now run: python main.py")
print("Important: press R after opening the simulation to start fresh.")