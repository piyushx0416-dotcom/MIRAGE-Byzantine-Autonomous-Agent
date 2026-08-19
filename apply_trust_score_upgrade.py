from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_trust_score_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_trust_score_upgrade.py")
else:
    print("Backup already exists: main_before_trust_score_upgrade.py")


# ---------------------------------------------------------
# 1. Add TRUST SYSTEM page
# ---------------------------------------------------------

if '"TRUST SYSTEM"' not in text:
    if '"GRAPH"\n        ]' in text:
        text = text.replace(
            '"GRAPH"\n        ]',
            '"GRAPH",\n            "TRUST SYSTEM"\n        ]',
            1
        )
        print("Added TRUST SYSTEM page.")
    else:
        print("WARNING: Could not find GRAPH page list ending.")
else:
    print("TRUST SYSTEM page already exists.")


# ---------------------------------------------------------
# 2. Add trust score variables after panel_pages
# ---------------------------------------------------------

if "self.trust_scores" not in text:
    try:
        start = text.index("self.panel_pages = [")
        end = text.index("        ]", start) + len("        ]")

        insert_text = """

        # Trust score system
        self.trust_scores = {d.id: 100.0 for d in self.swarm.drones}
        self.trust_history = []
"""

        text = text[:end] + insert_text + text[end:]
        print("Added trust score variables.")
    except ValueError:
        print("ERROR: Could not find panel_pages block.")
        sys.exit(1)
else:
    print("Trust score variables already exist.")


# ---------------------------------------------------------
# 3. Call update_trust_scores() after detection
# ---------------------------------------------------------

if "self.update_trust_scores()" not in text:
    marker = """self.ml_suspected = self.ml_detector.detect(
                self.swarm.drones
            )

            # Track accuracy"""

    replacement = """self.ml_suspected = self.ml_detector.detect(
                self.swarm.drones
            )

            # Update trust scores after detectors run
            self.update_trust_scores()

            # Track accuracy"""

    if marker in text:
        text = text.replace(marker, replacement, 1)
        print("Added update_trust_scores() call.")
    else:
        print("WARNING: Could not find ML detection block. Trust may not update.")
else:
    print("update_trust_scores() call already exists.")


# ---------------------------------------------------------
# 4. Add TRUST SYSTEM branch to draw_info_panel()
# ---------------------------------------------------------

if "self.draw_trust_page(px, py)" not in text:
    marker = """elif self.panel_page == 4:
            self.draw_graph_page(px, py)"""

    replacement = """elif self.panel_page == 4:
            self.draw_graph_page(px, py)
        elif self.panel_page == 5:
            self.draw_trust_page(px, py)"""

    if marker in text:
        text = text.replace(marker, replacement, 1)
        print("Added draw_trust_page() branch.")
    else:
        print("WARNING: Could not add trust page branch.")
else:
    print("draw_trust_page() branch already exists.")


# ---------------------------------------------------------
# 5. Add trust score functions
# ---------------------------------------------------------

trust_code = '''    def update_trust_scores(self):
        """
        Updates trust score for every drone.
        Trust decreases when behavior looks suspicious.
        Trust increases slowly when behavior looks normal.
        """

        for drone in self.swarm.drones:
            rx, ry = drone.get_reported_position()
            real_x, real_y = drone.get_real_position()

            position_error = np.sqrt((rx - real_x) ** 2 + (ry - real_y) ** 2)

            penalty = 0
            reward = 0

            # Position lying penalty
            if position_error > 120:
                penalty += 4.0
            elif position_error > 70:
                penalty += 2.5
            elif position_error > 40:
                penalty += 1.2
            else:
                reward += 0.5

            in_classical = drone.id in self.classical_suspected
            in_ml = drone.id in self.ml_suspected

            # Detector-based penalty
            if in_classical:
                penalty += 2.0

            if in_ml:
                penalty += 2.5

            if in_classical and in_ml:
                penalty += 2.0

            # If no detector suspects it and it reports consistently
            if not in_classical and not in_ml and position_error < 25:
                reward += 0.8

            old_score = self.trust_scores.get(drone.id, 100.0)
            new_score = old_score - penalty + reward

            new_score = max(0, min(100, new_score))
            self.trust_scores[drone.id] = new_score

        avg_trust = sum(self.trust_scores.values()) / len(self.trust_scores)
        self.trust_history.append(avg_trust)

        if len(self.trust_history) > 80:
            self.trust_history.pop(0)

    def get_trust_color(self, score):
        if score >= 70:
            return GREEN
        elif score >= 40:
            return YELLOW
        else:
            return RED

    def get_trust_summary(self):
        scores = list(self.trust_scores.values())

        if not scores:
            return 0, 0, 0

        avg_trust = sum(scores) / len(scores)

        low_trust = [
            drone_id for drone_id, score in self.trust_scores.items()
            if score < 50
        ]

        quarantined = [
            drone_id for drone_id, score in self.trust_scores.items()
            if score < 30
        ]

        return avg_trust, low_trust, quarantined

    def draw_trust_bar(self, x, y, w, h, score, label):
        color = self.get_trust_color(score)
        ratio = max(0, min(1, score / 100))

        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (x + 3, y + 3, w, h),
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            (40, 42, 52),
            (x, y, w, h),
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            color,
            (x, y, int(w * ratio), h),
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            WHITE,
            (x, y, w, h),
            1,
            border_radius=7
        )

        txt = self.font_small.render(
            f"{label}: {score:.1f}%",
            True,
            WHITE
        )
        self.screen.blit(txt, (x + 8, y + 3))

    def draw_trust_row(self, x, y, drone_id, score):
        color = self.get_trust_color(score)

        pygame.draw.rect(
            self.screen,
            (24, 27, 40),
            (x, y, 330, 25),
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            color,
            (x, y, 330, 25),
            1,
            border_radius=7
        )

        id_text = self.font_small.render(
            f"Drone {drone_id}",
            True,
            WHITE
        )
        self.screen.blit(id_text, (x + 8, y + 5))

        bar_x = x + 75
        bar_w = 170

        pygame.draw.rect(
            self.screen,
            (45, 45, 55),
            (bar_x, y + 6, bar_w, 13),
            border_radius=5
        )

        pygame.draw.rect(
            self.screen,
            color,
            (bar_x, y + 6, int(bar_w * score / 100), 13),
            border_radius=5
        )

        pygame.draw.rect(
            self.screen,
            WHITE,
            (bar_x, y + 6, bar_w, 13),
            1,
            border_radius=5
        )

        score_text = self.font_small.render(
            f"{score:.1f}%",
            True,
            color
        )
        self.screen.blit(score_text, (x + 255, y + 5))

    def draw_trust_page(self, px, py):
        avg_trust, low_trust, quarantined = self.get_trust_summary()

        # Card 1: Trust overview
        self.draw_panel_card(px, py, 360, 150, "TRUST SYSTEM OVERVIEW", CYAN)
        y = py + 42

        overview_lines = [
            (f"Average Trust Score: {avg_trust:.1f}%", self.get_trust_color(avg_trust)),
            (f"Low Trust Drones (<50%): {len(low_trust)}", YELLOW),
            (f"Quarantined Drones (<30%): {len(quarantined)}", RED),
            (f"Trust Updates: Every detection cycle", WHITE),
        ]

        for text, color in overview_lines:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 23

        py += 165

        # Average trust bar
        self.draw_trust_bar(
            px + 15,
            py,
            330,
            22,
            avg_trust,
            "Average Swarm Trust"
        )
        py += 45

        # Card 2: Lowest trust drones
        self.draw_panel_card(px, py, 360, 190, "LOWEST TRUST DRONES", RED)
        y = py + 42

        sorted_trust = sorted(
            self.trust_scores.items(),
            key=lambda item: item[1]
        )

        for drone_id, score in sorted_trust[:5]:
            self.draw_trust_row(px + 15, y, drone_id, score)
            y += 29

        py += 205

        # Card 3: Trust rules
        self.draw_panel_card(px, py, 360, 170, "TRUST RULES", YELLOW)
        y = py + 42

        rules = [
            "Trust decreases if reported position is false.",
            "Trust decreases if Classical BFT flags drone.",
            "Trust decreases if ML flags drone.",
            "Trust decreases faster if both agree.",
            "Trust slowly recovers for stable behavior."
        ]

        for rule in rules:
            s = self.font_small.render(rule, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 22

        py += 185

        # Card 4: Quarantine suggestion
        self.draw_panel_card(px, py, 360, 95, "QUARANTINE DECISION", PURPLE)
        y = py + 42

        if quarantined:
            q_text = f"Isolate drones: {self.format_ids(set(quarantined))}"
            q_color = RED
        else:
            q_text = "No drones currently require isolation."
            q_color = GREEN

        s = self.font_small.render(q_text, True, q_color)
        self.screen.blit(s, (px + 15, y))

'''

if "def update_trust_scores" not in text:
    try:
        insert_before = text.index("    def draw_section_title")
        text = text[:insert_before] + trust_code + text[insert_before:]
        print("Added trust score functions.")
    except ValueError:
        print("ERROR: Could not find draw_section_title insertion point.")
        sys.exit(1)
else:
    print("Trust score functions already exist.")


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("TRUST SCORE UPGRADE COMPLETE.")
print("Now run: python main.py")
print("Press TAB until you reach TRUST SYSTEM page.")