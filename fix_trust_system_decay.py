from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_trust_decay_fix.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_trust_decay_fix.py")
else:
    print("Backup already exists: main_before_trust_decay_fix.py")


# ---------------------------------------------------------
# 1. Add suspicion memory variables if missing
# ---------------------------------------------------------

if "self.suspicion_memory" not in text:
    target = "self.trust_scores = {d.id: 100.0 for d in self.swarm.drones}"

    replacement = """self.trust_scores = {d.id: 100.0 for d in self.swarm.drones}
        self.suspicion_memory = {d.id: 0.0 for d in self.swarm.drones}
        self.clean_memory = {d.id: 0 for d in self.swarm.drones}"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added suspicion_memory and clean_memory variables.")
    else:
        print("WARNING: Could not find trust_scores initialization.")
else:
    print("Suspicion memory variables already exist.")


# ---------------------------------------------------------
# 2. Replace update_trust_scores() with stable version
# ---------------------------------------------------------

new_update_trust = '''    def update_trust_scores(self):
        """
        Stable Trust Score System.

        Trust no longer drops to 0 just because of repeated weak alerts.
        It uses suspicion memory:
        - Strong repeated evidence increases suspicion.
        - Clean behavior decreases suspicion.
        - Trust is calculated smoothly from suspicion.
        """

        # If older save does not have these variables, create them safely
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
            # Evidence scoring
            # -----------------------------
            evidence = 0.0

            # Position lie evidence
            if position_error > 150:
                evidence += 45
            elif position_error > 100:
                evidence += 30
            elif position_error > 60:
                evidence += 15
            elif position_error > 35:
                evidence += 6

            # Detector evidence
            # Strong evidence only when both methods agree
            if in_classical and in_ml:
                evidence += 35

            # One detector alone gives weak evidence only
            elif in_classical or in_ml:
                if position_error > 60:
                    evidence += 15
                else:
                    evidence += 4

            # Agreement bonus for serious suspicious behavior
            if (in_classical and in_ml) and position_error > 80:
                evidence += 15

            evidence = max(0, min(100, evidence))

            # -----------------------------
            # Suspicion memory update
            # -----------------------------
            old_suspicion = self.suspicion_memory.get(drone.id, 0.0)

            # If evidence is strong, suspicion rises
            if evidence >= 45:
                new_suspicion = old_suspicion + evidence * 0.10
                self.clean_memory[drone.id] = 0

            # Medium evidence rises slowly
            elif evidence >= 20:
                new_suspicion = old_suspicion + evidence * 0.04
                self.clean_memory[drone.id] = 0

            # Weak evidence should not destroy trust
            elif evidence > 0:
                new_suspicion = old_suspicion + evidence * 0.01

            # Clean behavior reduces suspicion
            else:
                self.clean_memory[drone.id] = self.clean_memory.get(drone.id, 0) + 1

                clean_bonus = 2.5

                # If it has been clean for many cycles, recover faster
                if self.clean_memory[drone.id] > 5:
                    clean_bonus = 4.0

                new_suspicion = old_suspicion - clean_bonus

            # Extra recovery for stable drones
            if not in_classical and not in_ml and position_error < 30:
                new_suspicion -= 2.0

            # Keep suspicion bounded
            new_suspicion = max(0, min(100, new_suspicion))
            self.suspicion_memory[drone.id] = new_suspicion

            # -----------------------------
            # Convert suspicion to trust
            # -----------------------------
            target_trust = 100 - new_suspicion

            old_trust = self.trust_scores.get(drone.id, 100.0)

            # Smooth trust change so it does not crash suddenly
            new_trust = old_trust * 0.88 + target_trust * 0.12

            # If drone is clean, allow extra recovery
            if evidence == 0 and position_error < 30:
                new_trust += 1.0

            # Keep inside range
            new_trust = max(0, min(100, new_trust))

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
        print("Updated update_trust_scores() with stable trust decay logic.")
    except ValueError:
        print("ERROR: Could not replace update_trust_scores().")
        sys.exit(1)
else:
    print("ERROR: update_trust_scores() not found.")
    sys.exit(1)


# ---------------------------------------------------------
# 3. Update trust rules text if present
# ---------------------------------------------------------

old_rules = '''        rules = [
            "Trust decreases if reported position is false.",
            "Trust decreases if Classical BFT flags drone.",
            "Trust decreases if ML flags drone.",
            "Trust decreases faster if both agree.",
            "Trust slowly recovers for stable behavior."
        ]'''

new_rules = '''        rules = [
            "Trust uses suspicion memory over time.",
            "Weak one-method alerts cause only small penalty.",
            "Strong repeated evidence lowers trust.",
            "Clean behavior reduces suspicion.",
            "Stable drones recover trust gradually."
        ]'''

if old_rules in text:
    text = text.replace(old_rules, new_rules, 1)
    print("Updated trust rules text.")
else:
    print("Trust rules text not found or already changed. Skipping.")


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("TRUST DECAY FIX COMPLETE.")
print("Now run: python main.py")
print("Important: press R or restart simulation so trust starts fresh.")