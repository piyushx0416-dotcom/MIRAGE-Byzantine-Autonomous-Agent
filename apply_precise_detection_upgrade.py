from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_precise_detection_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_precise_detection_upgrade.py")
else:
    print("Backup already exists: main_before_precise_detection_upgrade.py")

# Rename SIGNALS page if possible
text = text.replace('"SIGNALS"', '"RISK SIGNALS"')

new_signals_code = '''    def risk_color(self, score):
        if score >= 75:
            return RED
        elif score >= 45:
            return YELLOW
        else:
            return GREEN

    def compute_detection_signals(self, drone):
        rx, ry = drone.get_reported_position()
        real_x, real_y = drone.get_real_position()

        # 1. Position lie score
        position_error = np.sqrt((rx - real_x) ** 2 + (ry - real_y) ** 2)
        position_score = int(max(0, min(100, position_error / 160 * 100)))

        # 2. Isolation score from reported swarm center
        all_rx = [d.get_reported_position()[0] for d in self.swarm.drones]
        all_ry = [d.get_reported_position()[1] for d in self.swarm.drones]

        center_x = np.mean(all_rx)
        center_y = np.mean(all_ry)

        center_dist = np.sqrt((rx - center_x) ** 2 + (ry - center_y) ** 2)
        isolation_score = int(max(0, min(100, center_dist / 360 * 100)))

        # 3. Classical confidence
        classical_score = 90 if drone.id in self.classical_suspected else 0

        # 4. ML confidence
        ml_score = 90 if drone.id in self.ml_suspected else 0

        # 5. Agreement score
        in_classical = drone.id in self.classical_suspected
        in_ml = drone.id in self.ml_suspected

        if in_classical and in_ml:
            agreement_score = 100
        elif in_classical or in_ml:
            agreement_score = 55
        else:
            agreement_score = 0

        # Final weighted risk score
        final_risk = int(
            0.30 * position_score +
            0.20 * isolation_score +
            0.20 * classical_score +
            0.20 * ml_score +
            0.10 * agreement_score
        )

        final_risk = max(0, min(100, final_risk))

        return {
            "id": drone.id,
            "position_error": position_error,
            "position_score": position_score,
            "isolation_score": isolation_score,
            "classical_score": classical_score,
            "ml_score": ml_score,
            "agreement_score": agreement_score,
            "final_risk": final_risk,
            "is_malicious": drone.is_malicious
        }

    def draw_score_bar(self, x, y, w, h, score, label):
        color = self.risk_color(score)
        ratio = max(0, min(1, score / 100))

        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (x + 2, y + 2, w, h),
            border_radius=6
        )

        pygame.draw.rect(
            self.screen,
            (42, 42, 50),
            (x, y, w, h),
            border_radius=6
        )

        pygame.draw.rect(
            self.screen,
            color,
            (x, y, int(w * ratio), h),
            border_radius=6
        )

        pygame.draw.rect(
            self.screen,
            WHITE,
            (x, y, w, h),
            1,
            border_radius=6
        )

        text = self.font_small.render(
            f"{label}: {score}",
            True,
            WHITE
        )
        self.screen.blit(text, (x + 6, y + 2))

    def draw_compact_risk_row(self, x, y, signal):
        drone_id = signal["id"]
        risk = signal["final_risk"]
        color = self.risk_color(risk)

        if signal["is_malicious"]:
            truth = "BAD"
            truth_color = RED
        else:
            truth = "OK"
            truth_color = GREEN

        # ID chip
        pygame.draw.rect(
            self.screen,
            (28, 30, 42),
            (x, y, 42, 22),
            border_radius=6
        )
        pygame.draw.rect(
            self.screen,
            color,
            (x, y, 42, 22),
            1,
            border_radius=6
        )

        id_text = self.font_small.render(
            f"D{drone_id}",
            True,
            WHITE
        )
        self.screen.blit(id_text, (x + 7, y + 4))

        # Risk bar
        bar_x = x + 50
        bar_w = 160

        pygame.draw.rect(
            self.screen,
            (40, 40, 48),
            (bar_x, y + 3, bar_w, 15),
            border_radius=5
        )

        pygame.draw.rect(
            self.screen,
            color,
            (bar_x, y + 3, int(bar_w * risk / 100), 15),
            border_radius=5
        )

        pygame.draw.rect(
            self.screen,
            WHITE,
            (bar_x, y + 3, bar_w, 15),
            1,
            border_radius=5
        )

        risk_text = self.font_small.render(
            f"Risk {risk}",
            True,
            WHITE
        )
        self.screen.blit(risk_text, (bar_x + bar_w + 8, y + 2))

        truth_text = self.font_small.render(
            truth,
            True,
            truth_color
        )
        self.screen.blit(truth_text, (x + 285, y + 2))

    def draw_signals_page(self, px, py):
        signals = []

        for drone in self.swarm.drones:
            signals.append(self.compute_detection_signals(drone))

        signals_sorted = sorted(
            signals,
            key=lambda s: s["final_risk"],
            reverse=True
        )

        high_position = [s for s in signals if s["position_score"] >= 70]
        high_isolation = [s for s in signals if s["isolation_score"] >= 70]
        high_risk = [s for s in signals if s["final_risk"] >= 70]

        both_methods = self.classical_suspected & self.ml_suspected
        classical_only = self.classical_suspected - self.ml_suspected
        ml_only = self.ml_suspected - self.classical_suspected

        # Card 1: Signal summary
        self.draw_panel_card(px, py, 360, 150, "PRECISION SIGNAL MODULES", CYAN)
        y = py + 42

        summary_lines = [
            (f"Position Lie Alerts: {len(high_position)}", ORANGE),
            (f"Isolation Alerts: {len(high_isolation)}", YELLOW),
            (f"Detected by Both Methods: {len(both_methods)}", GREEN),
            (f"High Final Risk Drones: {len(high_risk)}", RED),
        ]

        for text, color in summary_lines:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 23

        py += 165

        # Card 2: Top risky drones
        self.draw_panel_card(px, py, 360, 180, "TOP RISK DRONES", RED)
        y = py + 42

        for signal in signals_sorted[:5]:
            self.draw_compact_risk_row(px + 15, y, signal)
            y += 27

        py += 195

        # Card 3: Detailed highest risk breakdown
        top = signals_sorted[0]

        self.draw_panel_card(
            px,
            py,
            360,
            205,
            f"DRONE {top['id']} SIGNAL BREAKDOWN",
            PURPLE
        )

        y = py + 42

        self.draw_score_bar(
            px + 15,
            y,
            320,
            18,
            top["position_score"],
            "Position Lie"
        )
        y += 27

        self.draw_score_bar(
            px + 15,
            y,
            320,
            18,
            top["isolation_score"],
            "Isolation"
        )
        y += 27

        self.draw_score_bar(
            px + 15,
            y,
            320,
            18,
            top["classical_score"],
            "Classical"
        )
        y += 27

        self.draw_score_bar(
            px + 15,
            y,
            320,
            18,
            top["ml_score"],
            "ML"
        )
        y += 27

        self.draw_score_bar(
            px + 15,
            y,
            320,
            18,
            top["agreement_score"],
            "Agreement"
        )
        y += 27

        self.draw_score_bar(
            px + 15,
            y,
            320,
            18,
            top["final_risk"],
            "Final Risk"
        )

        py += 220

        # Card 4: Disagreement analysis
        self.draw_panel_card(px, py, 360, 110, "DETECTOR DISAGREEMENT", YELLOW)
        y = py + 42

        lines = [
            f"Classical only: {self.format_ids(classical_only)}",
            f"ML only: {self.format_ids(ml_only)}",
            "One-method alerts should be monitored first."
        ]

        for line in lines:
            s = self.font_small.render(line, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 20

'''

try:
    start = text.index("    def draw_signals_page")
    end = text.index("    def draw_graph_page", start)
    text = text[:start] + new_signals_code + text[end:]
    print("Replaced draw_signals_page() with precise risk scoring page.")
except ValueError:
    print("ERROR: Could not replace draw_signals_page().")
    print("Make sure your main.py has draw_signals_page() and draw_graph_page().")
    sys.exit(1)

MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("PRECISE DETECTION UPGRADE COMPLETE.")
print("Now run: python main.py")
print("Press TAB until you reach RISK SIGNALS page.")