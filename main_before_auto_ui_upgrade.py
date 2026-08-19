import pygame
import sys
import numpy as np
import random
from swarm import Swarm
from classical_detection import ClassicalByzantineDetector
from ml_detection import MLByzantineDetector

# ─── SETTINGS ───────────────────────────────────────────
WIDTH = 1200
HEIGHT = 700
SIM_WIDTH = 800   # left panel for simulation
PANEL_WIDTH = 400  # right panel for stats
FPS = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
RED = (255, 60, 60)
YELLOW = (255, 220, 0)
BLUE = (100, 180, 255)
GRAY = (50, 50, 50)
DARK = (20, 20, 30)
ORANGE = (255, 140, 0)
PURPLE = (180, 100, 255)
CYAN = (0, 255, 255)

class MirageSimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(
            "MIRAGE: Byzantine Autonomous Agents"
        )
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_large = pygame.font.SysFont('Arial', 22, bold=True)
        self.font_med = pygame.font.SysFont('Arial', 16)
        self.font_small = pygame.font.SysFont('Arial', 13)

        # Simulation
        self.swarm = Swarm(
            total_drones=20,
            malicious_count=5,
            width=SIM_WIDTH,
            height=HEIGHT
        )

        # Detectors
        self.classical = ClassicalByzantineDetector(threshold=60)
        self.ml_detector = MLByzantineDetector(contamination=0.25)

        # Train ML on initial data
        self.ml_detector.train(self.swarm.drones)

        # State
        self.frame = 0
        self.show_real_positions = False
        self.show_reported_positions = True
        self.detection_mode = "BOTH"  # CLASSICAL, ML, BOTH
        self.paused = False

        # Stats tracking
        self.classical_tp_history = []
        self.ml_tp_history = []
        self.frame_history = []

        # Detection results
        self.classical_suspected = set()
        self.ml_suspected = set()

    def run(self):
        while True:
            self.handle_events()

            if not self.paused:
                self.update()

            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # SPACE = pause
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                # R = reset
                if event.key == pygame.K_r:
                    self.__init__()

                # T = toggle real positions
                if event.key == pygame.K_t:
                    self.show_real_positions = (
                        not self.show_real_positions
                    )

                # 1 = Classical only
                if event.key == pygame.K_1:
                    self.detection_mode = "CLASSICAL"

                # 2 = ML only
                if event.key == pygame.K_2:
                    self.detection_mode = "ML"

                # 3 = Both
                if event.key == pygame.K_3:
                    self.detection_mode = "BOTH"

    def update(self):
        self.frame += 1
        self.swarm.update()

        # Run detection every 15 frames
        if self.frame % 15 == 0:
            self.classical_suspected = self.classical.detect(
                self.swarm.drones
            )
            self.ml_suspected = self.ml_detector.detect(
                self.swarm.drones
            )

            # Track accuracy
            c_tp, c_fp, c_fn = self.classical.get_accuracy(
                self.swarm.drones
            )
            m_tp, m_fp, m_fn = self.ml_detector.get_accuracy(
                self.swarm.drones
            )

            self.classical_tp_history.append(c_tp)
            self.ml_tp_history.append(m_tp)
            self.frame_history.append(self.frame)

            # Keep history short
            if len(self.classical_tp_history) > 30:
                self.classical_tp_history.pop(0)
                self.ml_tp_history.pop(0)
                self.frame_history.pop(0)

    def draw(self):
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

        pygame.display.flip()

    def draw_simulation_panel(self):
        # Background grid
        for x in range(0, SIM_WIDTH, 50):
            pygame.draw.line(
                self.screen, (30, 30, 45),
                (x, 0), (x, HEIGHT)
            )
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(
                self.screen, (30, 30, 45),
                (0, y), (SIM_WIDTH, y)
            )

        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)

        # Title
        title = self.font_large.render(
            "MIRAGE: Byzantine Simulation Agent", True, CYAN
        )
        self.screen.blit(title, (10, 10))

        # Controls hint
        hints = [
            "SPACE=Pause  R=Reset  T=Toggle Real Pos",
            "1=Classical  2=ML  3=Both"
        ]
        for i, hint in enumerate(hints):
            surf = self.font_small.render(hint, True, GRAY)
            self.screen.blit(surf, (10, HEIGHT - 35 + i*15))

    def draw_drone(self, drone):
        real_x = int(drone.x)
        real_y = int(drone.y)
        rep_x = int(min(SIM_WIDTH-10, max(10, drone.reported_x)))
        rep_y = int(min(HEIGHT-10, max(10, drone.reported_y)))

        # Determine drone color based on detection
        in_classical = drone.id in self.classical_suspected
        in_ml = drone.id in self.ml_suspected

        if self.detection_mode == "CLASSICAL":
            detected = in_classical
        elif self.detection_mode == "ML":
            detected = in_ml
        else:
            detected = in_classical or in_ml

        # Color logic
        if detected and drone.is_malicious:
            color = RED       # correctly caught
        elif detected and not drone.is_malicious:
            color = ORANGE    # false alarm
        elif not detected and drone.is_malicious:
            color = YELLOW    # missed bad drone
        else:
            color = GREEN     # good drone, correctly cleared

        # Draw real position
        pygame.draw.circle(
            self.screen, color,
            (real_x, real_y), 10
        )
        # White border
        pygame.draw.circle(
            self.screen, WHITE,
            (real_x, real_y), 10, 2
        )

        # Drone ID
        id_text = self.font_small.render(
            str(drone.id), True, BLACK
        )
        self.screen.blit(
            id_text, (real_x - 5, real_y - 7)
        )

        # Show reported position (where drone CLAIMS to be)
        if self.show_reported_positions and drone.is_malicious:
            # Draw ghost position with X
            pygame.draw.line(
                self.screen, (255, 100, 100),
                (rep_x - 8, rep_y - 8),
                (rep_x + 8, rep_y + 8), 2
            )
            pygame.draw.line(
                self.screen, (255, 100, 100),
                (rep_x + 8, rep_y - 8),
                (rep_x - 8, rep_y + 8), 2
            )
            # Line from real to fake
            pygame.draw.line(
                self.screen, (100, 100, 100),
                (real_x, real_y),
                (rep_x, rep_y), 1
            )

        # Detection ring animation
        if detected:
            ring_radius = 15 + (self.frame % 10)
            pygame.draw.circle(
                self.screen, RED,
                (real_x, real_y),
                ring_radius, 1
            )

    def draw_info_panel(self):
        px = SIM_WIDTH + 10
        py = 10

        # Panel background
        pygame.draw.rect(
            self.screen, (15, 15, 25),
            (SIM_WIDTH, 0, PANEL_WIDTH, HEIGHT)
        )

        # Title
        t = self.font_large.render(
            "DETECTION PANEL", True, CYAN
        )
        self.screen.blit(t, (px, py))
        py += 35

        # Mode
        mode_text = self.font_med.render(
            f"Mode: {self.detection_mode}", True, YELLOW
        )
        self.screen.blit(mode_text, (px, py))
        py += 25

        # Frame counter
        frame_text = self.font_med.render(
            f"Frame: {self.frame}", True, WHITE
        )
        self.screen.blit(frame_text, (px, py))
        py += 30

        # ── SWARM INFO ──────────────────────────────
        self.draw_section_title("SWARM STATUS", px, py)
        py += 25

        total = len(self.swarm.drones)
        actual_bad = sum(
            1 for d in self.swarm.drones if d.is_malicious
        )

        info_lines = [
            (f"Total Drones: {total}", WHITE),
            (f"Actual Malicious: {actual_bad}", RED),
            (f"Honest Drones: {total - actual_bad}", GREEN),
        ]
        for text, color in info_lines:
            s = self.font_med.render(text, True, color)
            self.screen.blit(s, (px, py))
            py += 20
        py += 10

        # ── CLASSICAL RESULTS ───────────────────────
        self.draw_section_title("CLASSICAL METHOD", px, py)
        py += 25

        c_tp, c_fp, c_fn = self.classical.get_accuracy(
            self.swarm.drones
        )
        c_detected = len(self.classical_suspected)
        actual_bad_set = {
            d.id for d in self.swarm.drones if d.is_malicious
        }
        c_recall = (c_tp / actual_bad * 100
                    if actual_bad > 0 else 0)

        c_lines = [
            (f"Suspected: {c_detected}", ORANGE),
            (f"Correct Catches: {c_tp}", GREEN),
            (f"False Alarms: {c_fp}", RED),
            (f"Missed: {c_fn}", YELLOW),
            (f"Detection Rate: {c_recall:.1f}%", CYAN),
        ]
        for text, color in c_lines:
            s = self.font_med.render(text, True, color)
            self.screen.blit(s, (px, py))
            py += 20
        py += 10

        # Classical accuracy bar
        self.draw_bar(
            px, py, 350, 20,
            c_recall / 100, GREEN, "Classical Accuracy"
        )
        py += 35

        # ── ML RESULTS ──────────────────────────────
        self.draw_section_title("ML METHOD (Isolation Forest)", px, py)
        py += 25

        m_tp, m_fp, m_fn = self.ml_detector.get_accuracy(
            self.swarm.drones
        )
        m_detected = len(self.ml_suspected)
        m_recall = (m_tp / actual_bad * 100
                    if actual_bad > 0 else 0)

        m_lines = [
            (f"Suspected: {m_detected}", ORANGE),
            (f"Correct Catches: {m_tp}", GREEN),
            (f"False Alarms: {m_fp}", RED),
            (f"Missed: {m_fn}", YELLOW),
            (f"Detection Rate: {m_recall:.1f}%", CYAN),
        ]
        for text, color in m_lines:
            s = self.font_med.render(text, True, color)
            self.screen.blit(s, (px, py))
            py += 20
        py += 10

        # ML accuracy bar
        self.draw_bar(
            px, py, 350, 20,
            m_recall / 100, PURPLE, "ML Accuracy"
        )
        py += 35

        # ── LEGEND ──────────────────────────────────
        self.draw_section_title("LEGEND", px, py)
        py += 25

        legend = [
            (GREEN, "Honest - Not Detected (Correct)"),
            (RED, "Malicious - Detected (Correct)"),
            (YELLOW, "Malicious - MISSED (Bad!)"),
            (ORANGE, "Honest - False Alarm"),
        ]
        for color, label in legend:
            pygame.draw.circle(
                self.screen, color, (px + 8, py + 8), 8
            )
            s = self.font_small.render(label, True, WHITE)
            self.screen.blit(s, (px + 22, py + 2))
            py += 22
        py += 10

        # ── MINI GRAPH ──────────────────────────────
        if len(self.classical_tp_history) > 1:
            self.draw_mini_graph(px, py)

        # Paused indicator
        if self.paused:
            pause_surf = self.font_large.render(
                "⏸ PAUSED", True, YELLOW
            )
            self.screen.blit(pause_surf, (px + 100, HEIGHT - 50))

    def draw_section_title(self, text, x, y):
        surf = self.font_med.render(text, True, YELLOW)
        self.screen.blit(surf, (x, y))
        pygame.draw.line(
            self.screen, YELLOW,
            (x, y + 20), (x + 370, y + 20), 1
        )

    def draw_bar(self, x, y, w, h, ratio, color, label):
        ratio = max(0, min(1, ratio))
        # Background
        pygame.draw.rect(self.screen, GRAY, (x, y, w, h))
        # Fill
        pygame.draw.rect(
            self.screen, color,
            (x, y, int(w * ratio), h)
        )
        # Border
        pygame.draw.rect(self.screen, WHITE, (x, y, w, h), 1)
        # Label
        pct = self.font_small.render(
            f"{label}: {ratio*100:.1f}%", True, WHITE
        )
        self.screen.blit(pct, (x + 5, y + 3))

    def draw_mini_graph(self, x, y):
        title = self.font_small.render(
            "Detection History", True, YELLOW
        )
        self.screen.blit(title, (x, y))
        y += 18

        gw, gh = 370, 80
        pygame.draw.rect(self.screen, GRAY, (x, y, gw, gh))

        max_val = 5  # max possible true positives

        # Draw classical line
        if len(self.classical_tp_history) > 1:
            for i in range(1, len(self.classical_tp_history)):
                x1 = x + int((i-1) / 30 * gw)
                x2 = x + int(i / 30 * gw)
                y1 = y + gh - int(
                    self.classical_tp_history[i-1] / max_val * gh
                )
                y2 = y + gh - int(
                    self.classical_tp_history[i] / max_val * gh
                )
                pygame.draw.line(
                    self.screen, GREEN, (x1, y1), (x2, y2), 2
                )

        # Draw ML line
        if len(self.ml_tp_history) > 1:
            for i in range(1, len(self.ml_tp_history)):
                x1 = x + int((i-1) / 30 * gw)
                x2 = x + int(i / 30 * gw)
                y1 = y + gh - int(
                    self.ml_tp_history[i-1] / max_val * gh
                )
                y2 = y + gh - int(
                    self.ml_tp_history[i] / max_val * gh
                )
                pygame.draw.line(
                    self.screen, PURPLE, (x1, y1), (x2, y2), 2
                )

        pygame.draw.rect(self.screen, WHITE, (x, y, gw, gh), 1)

        # Legend for graph
        pygame.draw.line(
            self.screen, GREEN, (x+5, y+gh+12), (x+25, y+gh+12), 2
        )
        self.screen.blit(
            self.font_small.render("Classical", True, GREEN),
            (x+28, y+gh+5)
        )
        pygame.draw.line(
            self.screen, PURPLE,
            (x+110, y+gh+12), (x+130, y+gh+12), 2
        )
        self.screen.blit(
            self.font_small.render("ML", True, PURPLE),
            (x+133, y+gh+5)
        )


# ─── RUN ────────────────────────────────────────────────
if __name__ == "__main__":
    sim = MirageSimulation()
    sim.run()