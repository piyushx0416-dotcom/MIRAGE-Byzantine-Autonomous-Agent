from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_hybrid_detector_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_hybrid_detector_upgrade.py")
else:
    print("Backup already exists: main_before_hybrid_detector_upgrade.py")


# ---------------------------------------------------------
# 1. Add HYBRID DEFENSE page
# ---------------------------------------------------------

try:
    start = text.index("self.panel_pages = [")
    end = text.index("        ]", start) + len("        ]")
    block = text[start:end]

    if '"HYBRID DEFENSE"' not in block:
        if '"RISK SIGNALS"' in block:
            block = block.replace(
                '"RISK SIGNALS"',
                '"RISK SIGNALS",\n            "HYBRID DEFENSE"',
                1
            )
        elif '"SIGNALS"' in block:
            block = block.replace(
                '"SIGNALS"',
                '"SIGNALS",\n            "HYBRID DEFENSE"',
                1
            )
        elif '"ML DETECTION"' in block:
            block = block.replace(
                '"ML DETECTION"',
                '"ML DETECTION",\n            "HYBRID DEFENSE"',
                1
            )
        else:
            block = block.replace(
                "        ]",
                '            "HYBRID DEFENSE"\n        ]',
                1
            )

        text = text[:start] + block + text[end:]
        print("Added HYBRID DEFENSE page.")
    else:
        print("HYBRID DEFENSE page already exists.")

except ValueError:
    print("ERROR: Could not find panel_pages block.")
    sys.exit(1)


# ---------------------------------------------------------
# 2. Add hybrid_suspected variable
# ---------------------------------------------------------

if "self.hybrid_suspected" not in text:
    target = "self.ml_suspected = set()"

    replacement = """self.ml_suspected = set()
        self.hybrid_suspected = set()"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added hybrid_suspected variable.")
    else:
        print("WARNING: Could not find self.ml_suspected initialization.")
else:
    print("hybrid_suspected already exists.")


# ---------------------------------------------------------
# 3. Add update call after trust update or ML detection
# ---------------------------------------------------------

if "self.hybrid_suspected = self.compute_hybrid_suspects()" not in text:
    if "self.update_trust_scores()" in text:
        text = text.replace(
            "self.update_trust_scores()",
            """self.update_trust_scores()

            # Update hybrid detector after trust/risk signals
            self.hybrid_suspected = self.compute_hybrid_suspects()""",
            1
        )
        print("Added hybrid detector update after trust update.")
    else:
        marker = """self.ml_suspected = self.ml_detector.detect(
                self.swarm.drones
            )"""

        replacement = """self.ml_suspected = self.ml_detector.detect(
                self.swarm.drones
            )

            # Update hybrid detector
            self.hybrid_suspected = self.compute_hybrid_suspects()"""

        if marker in text:
            text = text.replace(marker, replacement, 1)
            print("Added hybrid detector update after ML detection.")
        else:
            print("WARNING: Could not find detection update block.")
else:
    print("Hybrid detector update already exists.")


# ---------------------------------------------------------
# 4. Add key 4 for HYBRID mode
# ---------------------------------------------------------

if "pygame.K_4" not in text:
    target = """if event.key == pygame.K_3:
                    self.detection_mode = "BOTH\""""

    replacement = """if event.key == pygame.K_3:
                    self.detection_mode = "BOTH"

                # 4 = Hybrid defense mode
                if event.key == pygame.K_4:
                    self.detection_mode = "HYBRID\""""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added key 4 for HYBRID mode.")
    else:
        # safer alternative without escaped quote issue
        target2 = '''if event.key == pygame.K_3:
                    self.detection_mode = "BOTH"'''

        replacement2 = '''if event.key == pygame.K_3:
                    self.detection_mode = "BOTH"

                # 4 = Hybrid defense mode
                if event.key == pygame.K_4:
                    self.detection_mode = "HYBRID"'''

        if target2 in text:
            text = text.replace(target2, replacement2, 1)
            print("Added key 4 for HYBRID mode.")
        else:
            print("WARNING: Could not find key 3 block.")
else:
    print("Key 4 already exists.")


# ---------------------------------------------------------
# 5. Update controls text
# ---------------------------------------------------------

text = text.replace(
    "1 Classical   2 ML   3 Both   ESC Quit",
    "1 Classical   2 ML   3 Both   4 Hybrid   ESC Quit"
)

text = text.replace(
    "1 Classical   2 ML   3 Both",
    "1 Classical   2 ML   3 Both   4 Hybrid"
)

text = text.replace(
    "1=Classical  2=ML  3=Both  ESC=Quit",
    "1=Classical  2=ML  3=Both  4=Hybrid  ESC=Quit"
)

text = text.replace(
    "1=Classical  2=ML  3=Both",
    "1=Classical  2=ML  3=Both  4=Hybrid"
)

print("Updated control hints.")


# ---------------------------------------------------------
# 6. Add HYBRID page branch
# ---------------------------------------------------------

if "self.draw_hybrid_page(px, py)" not in text:
    target = '''elif page_name == "NETWORK":
            self.draw_network_page(px, py)'''

    replacement = '''elif page_name == "HYBRID DEFENSE":
            self.draw_hybrid_page(px, py)
        elif page_name == "NETWORK":
            self.draw_network_page(px, py)'''

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added HYBRID DEFENSE page branch before NETWORK.")
    else:
        target2 = '''elif page_name == "GRAPH":
            self.draw_graph_page(px, py)'''

        replacement2 = '''elif page_name == "HYBRID DEFENSE":
            self.draw_hybrid_page(px, py)
        elif page_name == "GRAPH":
            self.draw_graph_page(px, py)'''

        if target2 in text:
            text = text.replace(target2, replacement2, 1)
            print("Added HYBRID DEFENSE page branch before GRAPH.")
        else:
            print("WARNING: Could not add hybrid page branch.")
else:
    print("Hybrid page branch already exists.")


# ---------------------------------------------------------
# 7. Update draw_drone() detection mode logic
# ---------------------------------------------------------

old_detection_logic = '''        if self.detection_mode == "CLASSICAL":
            detected = in_classical
        elif self.detection_mode == "ML":
            detected = in_ml
        else:
            detected = in_classical or in_ml'''

new_detection_logic = '''        in_hybrid = (
            hasattr(self, "hybrid_suspected") and
            drone.id in self.hybrid_suspected
        )

        if self.detection_mode == "CLASSICAL":
            detected = in_classical
        elif self.detection_mode == "ML":
            detected = in_ml
        elif self.detection_mode == "HYBRID":
            detected = in_hybrid
        else:
            # BOTH mode shows all active detectors
            detected = in_classical or in_ml or in_hybrid'''

if old_detection_logic in text:
    text = text.replace(old_detection_logic, new_detection_logic, 1)
    print("Updated draw_drone() detection logic for HYBRID mode.")
else:
    print("WARNING: Could not update draw_drone detection logic. It may still work on pages only.")


# ---------------------------------------------------------
# 8. Add hybrid detector functions
# ---------------------------------------------------------

hybrid_code = '''    def compute_hybrid_score(self, drone):
        """
        Hybrid score combines:
        - Risk signal score
        - Trust risk
        - Classical detector
        - ML detector
        - Communication risk
        """

        drone_id = drone.id

        # Risk signal score
        if hasattr(self, "compute_detection_signals"):
            signal = self.compute_detection_signals(drone)
            signal_risk = signal.get("final_risk", 0)
        else:
            rx, ry = drone.get_reported_position()
            real_x, real_y = drone.get_real_position()
            position_error = np.sqrt((rx - real_x) ** 2 + (ry - real_y) ** 2)
            signal_risk = int(max(0, min(100, position_error / 160 * 100)))

        # Trust risk
        if hasattr(self, "trust_scores"):
            trust = self.trust_scores.get(drone_id, 100.0)
        else:
            trust = 100.0

        trust_risk = 100 - trust

        # Detector risks
        classical_risk = 100 if drone_id in self.classical_suspected else 0
        ml_risk = 100 if drone_id in self.ml_suspected else 0

        # Communication risk
        comm_risk = 0

        if hasattr(self, "get_drone_comm_summary"):
            comm = self.get_drone_comm_summary(drone_id)

            total = max(1, comm["total"])
            suspicious_ratio = comm["suspicious"] / total
            low_trust_ratio = comm["low_trust"] / total
            dropped_ratio = comm["dropped"] / total

            comm_risk = int(
                suspicious_ratio * 45 +
                low_trust_ratio * 35 +
                dropped_ratio * 20
            )

            comm_risk = max(0, min(100, comm_risk))

        # Agreement bonus
        agreement_bonus = 0

        if drone_id in self.classical_suspected and drone_id in self.ml_suspected:
            agreement_bonus += 10

        if trust < 35 and signal_risk > 55:
            agreement_bonus += 8

        # Final hybrid score
        hybrid_score = int(
            0.25 * signal_risk +
            0.25 * trust_risk +
            0.20 * ml_risk +
            0.15 * classical_risk +
            0.15 * comm_risk +
            agreement_bonus
        )

        hybrid_score = max(0, min(100, hybrid_score))

        return {
            "id": drone_id,
            "hybrid_score": hybrid_score,
            "signal_risk": int(signal_risk),
            "trust": trust,
            "trust_risk": int(trust_risk),
            "classical_risk": int(classical_risk),
            "ml_risk": int(ml_risk),
            "comm_risk": int(comm_risk),
            "agreement_bonus": int(agreement_bonus),
            "is_malicious": drone.is_malicious
        }

    def compute_hybrid_suspects(self):
        suspected = set()

        for drone in self.swarm.drones:
            info = self.compute_hybrid_score(drone)
            score = info["hybrid_score"]

            trust = info["trust"]

            # Hybrid decision rule
            if score >= 62:
                suspected.add(drone.id)

            # Very low trust also triggers hybrid suspicion
            elif trust < 25 and score >= 45:
                suspected.add(drone.id)

        return suspected

    def get_hybrid_stats(self):
        suspected = self.compute_hybrid_suspects()
        self.hybrid_suspected = suspected

        actual_bad = {
            d.id for d in self.swarm.drones
            if d.is_malicious
        }

        tp = len(actual_bad & suspected)
        fp = len(suspected - actual_bad)
        fn = len(actual_bad - suspected)

        precision = tp / len(suspected) if suspected else 0
        recall = tp / len(actual_bad) if actual_bad else 0

        if precision + recall > 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0

        return {
            "suspected": suspected,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "actual_bad": len(actual_bad)
        }

    def get_hybrid_color(self, score):
        if score >= 75:
            return RED
        elif score >= 50:
            return YELLOW
        else:
            return GREEN

    def draw_hybrid_row(self, x, y, info):
        drone_id = info["id"]
        score = info["hybrid_score"]
        color = self.get_hybrid_color(score)

        truth = "BAD" if info["is_malicious"] else "OK"
        truth_color = RED if info["is_malicious"] else GREEN

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
            f"D{drone_id}",
            True,
            WHITE
        )
        self.screen.blit(id_text, (x + 8, y + 5))

        bar_x = x + 45
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
            f"{score}",
            True,
            color
        )
        self.screen.blit(score_text, (x + 225, y + 5))

        truth_text = self.font_small.render(
            truth,
            True,
            truth_color
        )
        self.screen.blit(truth_text, (x + 285, y + 5))

    def draw_hybrid_page(self, px, py):
        stats = self.get_hybrid_stats()

        actual_bad = stats["actual_bad"]

        # Card 1: Hybrid summary
        self.draw_panel_card(px, py, 360, 165, "HYBRID DEFENSE SYSTEM", CYAN)
        y = py + 42

        summary = [
            (f"Hybrid Suspected: {len(stats['suspected'])}", ORANGE),
            (f"Correct Catches: {stats['tp']}/{actual_bad}", GREEN),
            (f"False Alarms: {stats['fp']}", RED),
            (f"Missed Malicious: {stats['fn']}", YELLOW),
            (f"F1 Score: {stats['f1'] * 100:.1f}%", CYAN),
        ]

        for text, color in summary:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 23

        py += 180

        self.draw_bar(
            px + 15,
            py,
            330,
            22,
            stats["recall"],
            GREEN,
            "Hybrid Recall"
        )

        py += 35

        self.draw_bar(
            px + 15,
            py,
            330,
            22,
            stats["precision"],
            PURPLE,
            "Hybrid Precision"
        )

        py += 48

        # Card 2: Top hybrid risks
        self.draw_panel_card(px, py, 360, 180, "TOP HYBRID RISK DRONES", RED)
        y = py + 42

        infos = [
            self.compute_hybrid_score(d)
            for d in self.swarm.drones
        ]

        infos = sorted(
            infos,
            key=lambda item: item["hybrid_score"],
            reverse=True
        )

        for info in infos[:5]:
            self.draw_hybrid_row(px + 15, y, info)
            y += 28

        py += 195

        # Card 3: Highest risk breakdown
        top = infos[0]

        self.draw_panel_card(
            px,
            py,
            360,
            205,
            f"DRONE {top['id']} HYBRID BREAKDOWN",
            PURPLE
        )

        y = py + 42

        if hasattr(self, "draw_score_bar"):
            self.draw_score_bar(px + 15, y, 320, 18, top["signal_risk"], "Risk Signal")
            y += 27
            self.draw_score_bar(px + 15, y, 320, 18, top["trust_risk"], "Trust Risk")
            y += 27
            self.draw_score_bar(px + 15, y, 320, 18, top["classical_risk"], "Classical")
            y += 27
            self.draw_score_bar(px + 15, y, 320, 18, top["ml_risk"], "ML")
            y += 27
            self.draw_score_bar(px + 15, y, 320, 18, top["comm_risk"], "Comm Risk")
            y += 27
            self.draw_score_bar(px + 15, y, 320, 18, top["hybrid_score"], "Hybrid Score")
        else:
            self.draw_bar(px + 15, y, 320, 20, top["hybrid_score"] / 100, RED, "Hybrid Score")

        py += 220

        # Card 4: Hybrid logic
        self.draw_panel_card(px, py, 360, 125, "HYBRID DECISION LOGIC", YELLOW)
        y = py + 42

        explanation = [
            "Combines BFT + ML + Trust + Risk Signals.",
            "Communication behavior affects final risk.",
            "Hybrid mode reduces single-detector mistakes.",
            "Press 4 to visualize Hybrid decisions."
        ]

        for line in explanation:
            s = self.font_small.render(line, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 20

'''

if "def compute_hybrid_score" not in text:
    try:
        insert_before = text.index("    def draw_section_title")
        text = text[:insert_before] + hybrid_code + text[insert_before:]
        print("Added hybrid detector methods.")
    except ValueError:
        print("ERROR: Could not find insertion point before draw_section_title.")
        sys.exit(1)
else:
    print("Hybrid methods already exist.")


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("HYBRID DETECTOR UPGRADE COMPLETE.")
print("Now run: python main.py")
print("Controls:")
print("4 = Hybrid mode")
print("TAB = switch pages until HYBRID DEFENSE")