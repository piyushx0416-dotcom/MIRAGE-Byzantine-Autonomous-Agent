from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_auto_ui_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_auto_ui_upgrade.py")
else:
    print("Backup already exists: main_before_auto_ui_upgrade.py")

# ---------------------------------------------------------
# 1. Add new variables after self.paused = False
# ---------------------------------------------------------
if "self.show_large_graph" not in text:
    text = text.replace(
        "self.paused = False",
        """self.paused = False
        self.show_large_graph = False
        self.panel_page = 0
        self.panel_pages = [
            "OVERVIEW",
            "CLASSICAL BFT",
            "ML DETECTION",
            "SIGNALS",
            "GRAPH"
        ]""",
        1
    )
    print("Added panel page variables.")
else:
    print("Panel page variables already exist.")

# ---------------------------------------------------------
# 2. Add keyboard controls for TAB, G, ESC
# ---------------------------------------------------------
if "pygame.K_TAB" not in text:
    space_block = """if event.key == pygame.K_SPACE:
                    self.paused = not self.paused"""

    insert_block = """if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                if event.key == pygame.K_TAB:
                    self.panel_page = (self.panel_page + 1) % len(self.panel_pages)

                if event.key == pygame.K_g:
                    self.show_large_graph = not self.show_large_graph

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()"""

    if space_block not in text:
        print("ERROR: Could not find SPACE key block.")
        sys.exit(1)

    text = text.replace(space_block, insert_block, 1)
    print("Added TAB, G, ESC keyboard controls.")
else:
    print("TAB/G/ESC controls already exist.")

# ---------------------------------------------------------
# 3. Update bottom hint text
# ---------------------------------------------------------
old_hints = '''hints = [
            "SPACE=Pause  R=Reset  T=Toggle Real Pos",
            "1=Classical  2=ML  3=Both"
        ]'''

new_hints = '''hints = [
            "SPACE=Pause  R=Reset  T=Fake Pos  TAB=Panel  G=Graph",
            "1=Classical  2=ML  3=Both  ESC=Quit"
        ]'''

if old_hints in text:
    text = text.replace(old_hints, new_hints, 1)
    print("Updated bottom control hints.")
else:
    print("Hint text already changed or not found. Skipping.")

# ---------------------------------------------------------
# 4. Replace draw() function
# ---------------------------------------------------------
new_draw = '''    def draw(self):
        self.screen.fill(DARK)

        # Draw simulation panel
        self.draw_simulation_panel()

        # Draw info panel
        self.draw_info_panel()

        # Draw divider
        pygame.draw.line(
            self.screen, GRAY,
            (SIM_WIDTH, 0), (SIM_WIDTH, HEIGHT), 2
        )

        # Large graph overlay
        if self.show_large_graph:
            self.draw_large_graph_overlay()

        pygame.display.flip()

'''

try:
    start = text.index("    def draw(self):")
    end = text.index("    def draw_simulation_panel", start)
    text = text[:start] + new_draw + text[end:]
    print("Replaced draw() function.")
except ValueError:
    print("ERROR: Could not replace draw() function.")
    sys.exit(1)

# ---------------------------------------------------------
# 5. Replace draw_info_panel() section
# ---------------------------------------------------------
new_panel_code = '''    def draw_info_panel(self):
        px = SIM_WIDTH + 10
        py = 10

        pygame.draw.rect(
            self.screen,
            (12, 12, 22),
            (SIM_WIDTH, 0, PANEL_WIDTH, HEIGHT)
        )

        title = self.font_large.render(
            "3D DETECTION PANEL", True, CYAN
        )
        self.screen.blit(title, (px, py))
        py += 34

        page_name = self.panel_pages[self.panel_page]
        page_text = self.font_med.render(
            f"Page {self.panel_page + 1}/{len(self.panel_pages)}: {page_name}",
            True,
            YELLOW
        )
        self.screen.blit(page_text, (px, py))
        py += 23

        mode_text = self.font_small.render(
            f"Mode: {self.detection_mode}   Frame: {self.frame}",
            True,
            WHITE
        )
        self.screen.blit(mode_text, (px, py))
        py += 22

        control_text = self.font_small.render(
            "TAB=Next Page   G=Large Graph",
            True,
            CYAN
        )
        self.screen.blit(control_text, (px, py))
        py += 28

        pygame.draw.line(
            self.screen,
            GRAY,
            (px, py),
            (WIDTH - 20, py),
            1
        )
        py += 15

        if self.panel_page == 0:
            self.draw_overview_page(px, py)
        elif self.panel_page == 1:
            self.draw_classical_page(px, py)
        elif self.panel_page == 2:
            self.draw_ml_page(px, py)
        elif self.panel_page == 3:
            self.draw_signals_page(px, py)
        elif self.panel_page == 4:
            self.draw_graph_page(px, py)

        if self.paused:
            pause_surf = self.font_large.render(
                "PAUSED", True, YELLOW
            )
            self.screen.blit(pause_surf, (px + 120, HEIGHT - 42))

    def draw_panel_card(self, x, y, w, h, title, color=CYAN):
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (x + 4, y + 4, w, h)
        )

        pygame.draw.rect(
            self.screen,
            (22, 23, 36),
            (x, y, w, h)
        )

        pygame.draw.rect(
            self.screen,
            color,
            (x, y, w, h),
            1
        )

        title_surf = self.font_med.render(title, True, color)
        self.screen.blit(title_surf, (x + 10, y + 8))

        pygame.draw.line(
            self.screen,
            color,
            (x + 10, y + 32),
            (x + w - 10, y + 32),
            1
        )

    def draw_overview_page(self, px, py):
        total = len(self.swarm.drones)
        actual_bad = sum(1 for d in self.swarm.drones if d.is_malicious)

        c_tp, c_fp, c_fn = self.classical.get_accuracy(
            self.swarm.drones
        )
        m_tp, m_fp, m_fn = self.ml_detector.get_accuracy(
            self.swarm.drones
        )

        c_recall = c_tp / actual_bad if actual_bad > 0 else 0
        m_recall = m_tp / actual_bad if actual_bad > 0 else 0

        self.draw_panel_card(px, py, 360, 125, "SWARM STATUS", CYAN)
        y = py + 42

        lines = [
            (f"Total Drones: {total}", WHITE),
            (f"Honest Drones: {total - actual_bad}", GREEN),
            (f"Actual Malicious: {actual_bad}", RED),
            (f"Current Mode: {self.detection_mode}", YELLOW),
        ]

        for text, color in lines:
            s = self.font_med.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 20

        py += 140

        self.draw_panel_card(px, py, 360, 145, "QUICK COMPARISON", YELLOW)
        y = py + 42

        quick_lines = [
            (f"Classical Correct: {c_tp}/{actual_bad}", GREEN),
            (f"Classical False Alarms: {c_fp}", RED),
            (f"ML Correct: {m_tp}/{actual_bad}", GREEN),
            (f"ML False Alarms: {m_fp}", RED),
        ]

        for text, color in quick_lines:
            s = self.font_med.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 20

        py += 160

        self.draw_bar(
            px + 10, py, 340, 22,
            c_recall, GREEN, "Classical Detection"
        )
        py += 35

        self.draw_bar(
            px + 10, py, 340, 22,
            m_recall, PURPLE, "ML Detection"
        )
        py += 45

        self.draw_panel_card(px, py, 360, 125, "LEGEND", ORANGE)
        y = py + 42

        legend = [
            (GREEN, "Honest - Trusted"),
            (RED, "Malicious - Detected"),
            (YELLOW, "Malicious - Missed"),
            (ORANGE, "Honest - False Alarm"),
        ]

        for color, label in legend:
            pygame.draw.circle(
                self.screen,
                color,
                (px + 22, y + 8),
                8
            )
            s = self.font_small.render(label, True, WHITE)
            self.screen.blit(s, (px + 40, y + 1))
            y += 21

    def draw_classical_page(self, px, py):
        actual_bad = sum(1 for d in self.swarm.drones if d.is_malicious)

        c_tp, c_fp, c_fn = self.classical.get_accuracy(
            self.swarm.drones
        )

        c_recall = c_tp / actual_bad if actual_bad > 0 else 0

        self.draw_panel_card(px, py, 360, 190, "CLASSICAL BFT METHOD", GREEN)
        y = py + 42

        lines = [
            (f"Suspected Drones: {len(self.classical_suspected)}", ORANGE),
            (f"Correct Catches: {c_tp}", GREEN),
            (f"False Alarms: {c_fp}", RED),
            (f"Missed Malicious: {c_fn}", YELLOW),
            (f"Detection Rate: {c_recall * 100:.1f}%", CYAN),
        ]

        for text, color in lines:
            s = self.font_med.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 22

        py += 205

        self.draw_bar(
            px + 10, py, 340, 22,
            c_recall, GREEN, "Classical Accuracy"
        )
        py += 45

        self.draw_panel_card(px, py, 360, 150, "CLASSICAL LOGIC", YELLOW)
        y = py + 42

        explanation = [
            "Uses fixed rules and voting-style checks.",
            "Flags drones that report positions far",
            "from expected behavior or majority pattern.",
            "Simple and explainable, but weaker",
            "against colluding attackers."
        ]

        for line in explanation:
            s = self.font_small.render(line, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 18

        py += 165

        self.draw_panel_card(px, py, 360, 90, "SUSPECTED IDS", RED)
        ids = self.format_ids(self.classical_suspected)
        s = self.font_small.render(ids, True, WHITE)
        self.screen.blit(s, (px + 15, py + 45))

    def draw_ml_page(self, px, py):
        actual_bad = sum(1 for d in self.swarm.drones if d.is_malicious)

        m_tp, m_fp, m_fn = self.ml_detector.get_accuracy(
            self.swarm.drones
        )

        m_recall = m_tp / actual_bad if actual_bad > 0 else 0

        self.draw_panel_card(px, py, 360, 190, "ML ANOMALY METHOD", PURPLE)
        y = py + 42

        lines = [
            (f"Suspected Drones: {len(self.ml_suspected)}", ORANGE),
            (f"Correct Catches: {m_tp}", GREEN),
            (f"False Alarms: {m_fp}", RED),
            (f"Missed Malicious: {m_fn}", YELLOW),
            (f"Detection Rate: {m_recall * 100:.1f}%", CYAN),
        ]

        for text, color in lines:
            s = self.font_med.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 22

        py += 205

        self.draw_bar(
            px + 10, py, 340, 22,
            m_recall, PURPLE, "ML Accuracy"
        )
        py += 45

        self.draw_panel_card(px, py, 360, 165, "ML FEATURE LOGIC", YELLOW)
        y = py + 42

        explanation = [
            "ML detector finds abnormal behavior.",
            "It checks position error, distance from",
            "swarm center, neighbor isolation, and",
            "movement consistency.",
            "Better for unknown attack patterns."
        ]

        for line in explanation:
            s = self.font_small.render(line, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 18

        py += 180

        self.draw_panel_card(px, py, 360, 90, "SUSPECTED IDS", RED)
        ids = self.format_ids(self.ml_suspected)
        s = self.font_small.render(ids, True, WHITE)
        self.screen.blit(s, (px + 15, py + 45))

    def draw_signals_page(self, px, py):
        position_suspects = set()

        for drone in self.swarm.drones:
            rx, ry = drone.get_reported_position()
            x, y = drone.get_real_position()

            error = np.sqrt((rx - x) ** 2 + (ry - y) ** 2)

            if error > 50:
                position_suspects.add(drone.id)

        both_methods = self.classical_suspected & self.ml_suspected
        classical_only = self.classical_suspected - self.ml_suspected
        ml_only = self.ml_suspected - self.classical_suspected

        self.draw_panel_card(px, py, 360, 130, "POSITION LIE SIGNAL", CYAN)
        y = py + 42

        lines = [
            (f"Position Lie Suspects: {len(position_suspects)}", ORANGE),
            (f"IDs: {self.format_ids(position_suspects)}", WHITE),
        ]

        for text, color in lines:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 22

        py += 145

        self.draw_panel_card(px, py, 360, 130, "CONSENSUS SIGNAL", GREEN)
        y = py + 42

        lines = [
            (f"Detected by BOTH methods: {len(both_methods)}", GREEN),
            (f"IDs: {self.format_ids(both_methods)}", WHITE),
        ]

        for text, color in lines:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 22

        py += 145

        self.draw_panel_card(px, py, 360, 155, "DISAGREEMENT SIGNAL", YELLOW)
        y = py + 42

        lines = [
            (f"Classical only: {self.format_ids(classical_only)}", WHITE),
            (f"ML only: {self.format_ids(ml_only)}", WHITE),
            "If only one method detects a drone,",
            "it should be watched instead of removed."
        ]

        for line in lines:
            if isinstance(line, tuple):
                text, color = line
            else:
                text, color = line, WHITE

            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 20

        py += 170

        self.draw_panel_card(px, py, 360, 115, "FINAL RISK IDEA", RED)
        y = py + 42

        explanation = [
            "High Risk = Classical + ML + Position Lie",
            "Medium Risk = Only one detector flags it",
            "Low Risk = No suspicious signal"
        ]

        for line in explanation:
            s = self.font_small.render(line, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 20

    def draw_graph_page(self, px, py):
        self.draw_panel_card(px, py, 360, 330, "DETECTION HISTORY", CYAN)

        self.draw_detection_graph(
            px + 15,
            py + 50,
            330,
            220
        )

        y = py + 285

        msg = self.font_small.render(
            "Press G to open full graph view.",
            True,
            YELLOW
        )
        self.screen.blit(msg, (px + 15, y))

        py += 350

        self.draw_panel_card(px, py, 360, 130, "GRAPH MEANING", YELLOW)
        y = py + 42

        explanation = [
            "Green line = Classical correct catches",
            "Purple line = ML correct catches",
            "Higher line means better detection."
        ]

        for line in explanation:
            s = self.font_small.render(line, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 20

    def format_ids(self, ids):
        if not ids:
            return "None"

        ids = sorted(list(ids))
        text = ", ".join(str(i) for i in ids)

        if len(text) > 42:
            text = text[:42] + "..."

        return text

    def draw_detection_graph(self, x, y, gw, gh):
        pygame.draw.rect(
            self.screen,
            (35, 35, 35),
            (x, y, gw, gh)
        )

        pygame.draw.rect(
            self.screen,
            WHITE,
            (x, y, gw, gh),
            1
        )

        for i in range(1, 5):
            gy = y + int(i * gh / 5)
            pygame.draw.line(
                self.screen,
                (60, 60, 70),
                (x, gy),
                (x + gw, gy),
                1
            )

        actual_bad = sum(1 for d in self.swarm.drones if d.is_malicious)
        max_val = max(1, actual_bad)

        n = len(self.classical_tp_history)

        if n <= 1:
            msg = self.font_small.render(
                "Waiting for detection data...",
                True,
                WHITE
            )
            self.screen.blit(msg, (x + 20, y + gh // 2))
            return

        for i in range(1, n):
            x1 = x + int((i - 1) / (n - 1) * gw)
            x2 = x + int(i / (n - 1) * gw)

            y1 = y + gh - int(
                self.classical_tp_history[i - 1] / max_val * gh
            )
            y2 = y + gh - int(
                self.classical_tp_history[i] / max_val * gh
            )

            pygame.draw.line(
                self.screen,
                GREEN,
                (x1, y1),
                (x2, y2),
                2
            )

        for i in range(1, n):
            x1 = x + int((i - 1) / (n - 1) * gw)
            x2 = x + int(i / (n - 1) * gw)

            y1 = y + gh - int(
                self.ml_tp_history[i - 1] / max_val * gh
            )
            y2 = y + gh - int(
                self.ml_tp_history[i] / max_val * gh
            )

            pygame.draw.line(
                self.screen,
                PURPLE,
                (x1, y1),
                (x2, y2),
                2
            )

        pygame.draw.line(
            self.screen,
            GREEN,
            (x + 10, y + gh + 12),
            (x + 35, y + gh + 12),
            2
        )
        self.screen.blit(
            self.font_small.render("Classical", True, GREEN),
            (x + 40, y + gh + 5)
        )

        pygame.draw.line(
            self.screen,
            PURPLE,
            (x + 130, y + gh + 12),
            (x + 155, y + gh + 12),
            2
        )
        self.screen.blit(
            self.font_small.render("ML", True, PURPLE),
            (x + 160, y + gh + 5)
        )

    def draw_large_graph_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        box_x = 90
        box_y = 60
        box_w = WIDTH - 180
        box_h = HEIGHT - 120

        pygame.draw.rect(
            self.screen,
            (18, 20, 32),
            (box_x, box_y, box_w, box_h)
        )

        pygame.draw.rect(
            self.screen,
            CYAN,
            (box_x, box_y, box_w, box_h),
            2
        )

        title = self.font_large.render(
            "FULL DETECTION HISTORY GRAPH",
            True,
            CYAN
        )
        self.screen.blit(title, (box_x + 25, box_y + 20))

        subtitle = self.font_small.render(
            "Green = Classical BFT correct catches    Purple = ML correct catches",
            True,
            WHITE
        )
        self.screen.blit(subtitle, (box_x + 25, box_y + 52))

        self.draw_detection_graph(
            box_x + 45,
            box_y + 95,
            box_w - 90,
            box_h - 170
        )

        footer = self.font_med.render(
            "Press G to close graph view",
            True,
            YELLOW
        )
        self.screen.blit(
            footer,
            (box_x + 25, box_y + box_h - 42)
        )

'''

try:
    start = text.index("    def draw_info_panel(self):")
    end = text.index("    def draw_section_title", start)
    text = text[:start] + new_panel_code + text[end:]
    print("Replaced draw_info_panel() with paged panel.")
except ValueError:
    print("ERROR: Could not replace draw_info_panel() section.")
    sys.exit(1)

MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("PATCH COMPLETE.")
print("Now run: python main.py")
print("Controls:")
print("TAB = change panel page")
print("G = open/close large graph")
print("ESC = quit")