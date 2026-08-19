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
        self.show_large_graph = False
        self.panel_page = 0
        self.panel_pages = [
            "OVERVIEW",
            "CLASSICAL BFT",
            "ML DETECTION",
            "SIGNALS",
            "GRAPH"
        ]

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

                if event.key == pygame.K_TAB:
                    self.panel_page = (self.panel_page + 1) % len(self.panel_pages)

                if event.key == pygame.K_g:
                    self.show_large_graph = not self.show_large_graph

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

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

        # Large graph overlay
        if self.show_large_graph:
            self.draw_large_graph_overlay()

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
            "SPACE=Pause  R=Reset  T=Fake Pos  TAB=Panel  G=Graph",
            "1=Classical  2=ML  3=Both  ESC=Quit"
        ]
        for i, hint in enumerate(hints):
            surf = self.font_small.render(hint, True, GRAY)
            self.screen.blit(surf, (10, HEIGHT - 35 + i*15))

    def draw_drone(self, drone):
        real_x = int(drone.x)
        real_y = int(drone.y)

        rep_x = int(min(SIM_WIDTH - 10, max(10, drone.reported_x)))
        rep_y = int(min(HEIGHT - 10, max(10, drone.reported_y)))

        # Determine detection status
        in_classical = drone.id in self.classical_suspected
        in_ml = drone.id in self.ml_suspected

        if self.detection_mode == "CLASSICAL":
            detected = in_classical
        elif self.detection_mode == "ML":
            detected = in_ml
        else:
            detected = in_classical or in_ml

        # Color meaning
        if detected and drone.is_malicious:
            color = RED       # correctly caught malicious drone
            glow_color = (255, 40, 40)
        elif detected and not drone.is_malicious:
            color = ORANGE    # false alarm
            glow_color = (255, 150, 30)
        elif not detected and drone.is_malicious:
            color = YELLOW    # missed malicious drone
            glow_color = (255, 220, 0)
        else:
            color = GREEN     # honest trusted drone
            glow_color = (0, 255, 120)

        # Pseudo-3D floating effect
        altitude = 10 + (drone.id % 4) * 2 + int(3 * np.sin((self.frame + drone.id * 13) / 18))
        body_x = real_x
        body_y = real_y - altitude

        # Shadow on ground
        shadow_w = 38 + altitude
        shadow_h = 14
        pygame.draw.ellipse(
            self.screen,
            (5, 5, 8),
            (real_x - shadow_w // 2, real_y + 12, shadow_w, shadow_h)
        )

        pygame.draw.ellipse(
            self.screen,
            (28, 28, 35),
            (real_x - shadow_w // 2 + 3, real_y + 14, shadow_w - 6, shadow_h - 4)
        )

        # Fake reported position for malicious drones
        if self.show_reported_positions and drone.is_malicious:
            pygame.draw.line(
                self.screen,
                (95, 95, 105),
                (body_x, body_y),
                (rep_x, rep_y),
                1
            )

            # Red X at fake position
            pygame.draw.line(
                self.screen,
                (255, 80, 80),
                (rep_x - 9, rep_y - 9),
                (rep_x + 9, rep_y + 9),
                2
            )
            pygame.draw.line(
                self.screen,
                (255, 80, 80),
                (rep_x + 9, rep_y - 9),
                (rep_x - 9, rep_y + 9),
                2
            )

        # Detection glow ring
        if detected:
            ring_radius = 22 + (self.frame % 12)
            pygame.draw.circle(
                self.screen,
                glow_color,
                (body_x, body_y),
                ring_radius,
                2
            )
            pygame.draw.circle(
                self.screen,
                glow_color,
                (body_x, body_y),
                ring_radius + 5,
                1
            )

        # Rotor positions
        rotor_offsets = [
            (-22, -16),
            (22, -16),
            (-22, 16),
            (22, 16)
        ]

        rotor_points = []

        for ox, oy in rotor_offsets:
            rx = body_x + ox
            ry = body_y + oy
            rotor_points.append((rx, ry))

        # Drone arms
        for rx, ry in rotor_points:
            pygame.draw.line(
                self.screen,
                (120, 125, 135),
                (body_x, body_y),
                (rx, ry),
                4
            )
            pygame.draw.line(
                self.screen,
                (40, 45, 55),
                (body_x, body_y + 2),
                (rx, ry + 2),
                2
            )

        # Rotors
        spin = self.frame % 12

        for rx, ry in rotor_points:
            # outer rotor ring
            pygame.draw.circle(
                self.screen,
                (18, 20, 28),
                (rx, ry),
                10
            )

            pygame.draw.circle(
                self.screen,
                WHITE,
                (rx, ry),
                10,
                1
            )

            # rotor blades animation
            if spin < 6:
                pygame.draw.line(
                    self.screen,
                    (170, 175, 185),
                    (rx - 12, ry),
                    (rx + 12, ry),
                    2
                )
                pygame.draw.line(
                    self.screen,
                    (170, 175, 185),
                    (rx, ry - 12),
                    (rx, ry + 12),
                    2
                )
            else:
                pygame.draw.line(
                    self.screen,
                    (170, 175, 185),
                    (rx - 9, ry - 9),
                    (rx + 9, ry + 9),
                    2
                )
                pygame.draw.line(
                    self.screen,
                    (170, 175, 185),
                    (rx + 9, ry - 9),
                    (rx - 9, ry + 9),
                    2
                )

            # rotor center
            pygame.draw.circle(
                self.screen,
                color,
                (rx, ry),
                4
            )

        # Main 3D drone body - diamond shape
        body_points = [
            (body_x, body_y - 13),
            (body_x + 15, body_y),
            (body_x, body_y + 13),
            (body_x - 15, body_y)
        ]

        # body shadow/depth
        body_shadow = [
            (body_x, body_y - 10 + 4),
            (body_x + 13, body_y + 4),
            (body_x, body_y + 10 + 4),
            (body_x - 13, body_y + 4)
        ]

        pygame.draw.polygon(
            self.screen,
            (35, 35, 45),
            body_shadow
        )

        pygame.draw.polygon(
            self.screen,
            color,
            body_points
        )

        pygame.draw.polygon(
            self.screen,
            WHITE,
            body_points,
            2
        )

        # Highlight to make body look 3D
        highlight_points = [
            (body_x, body_y - 10),
            (body_x + 8, body_y),
            (body_x, body_y + 4),
            (body_x - 8, body_y)
        ]

        pygame.draw.polygon(
            self.screen,
            (255, 255, 255),
            highlight_points,
            1
        )

        # Small central sensor/camera
        pygame.draw.circle(
            self.screen,
            (20, 20, 25),
            (body_x, body_y),
            5
        )

        pygame.draw.circle(
            self.screen,
            CYAN,
            (body_x, body_y),
            3
        )

        # Drone ID label
        if color in [GREEN, YELLOW]:
            text_color = BLACK
        else:
            text_color = WHITE

        id_text = self.font_small.render(
            str(drone.id),
            True,
            text_color
        )

        self.screen.blit(
            id_text,
            (body_x - 5, body_y - 8)
        )


    def draw_info_panel(self):
        px = SIM_WIDTH + 10
        py = 10

        # Futuristic gradient background
        for gy in range(0, HEIGHT, 4):
            shade = 10 + int(18 * gy / HEIGHT)
            pygame.draw.rect(
                self.screen,
                (shade, shade, shade + 14),
                (SIM_WIDTH, gy, PANEL_WIDTH, 4)
            )

        # Left neon edge
        pygame.draw.line(
            self.screen,
            CYAN,
            (SIM_WIDTH + 1, 0),
            (SIM_WIDTH + 1, HEIGHT),
            2
        )

        pygame.draw.line(
            self.screen,
            (0, 80, 90),
            (SIM_WIDTH + 4, 0),
            (SIM_WIDTH + 4, HEIGHT),
            1
        )

        # Header card
        header_h = 100

        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (px + 5, py + 5, PANEL_WIDTH - 25, header_h),
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            (18, 20, 34),
            (px, py, PANEL_WIDTH - 25, header_h),
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            CYAN,
            (px, py, PANEL_WIDTH - 25, header_h),
            2,
            border_radius=12
        )

        title = self.font_large.render(
            "MIRAGE CONTROL DECK",
            True,
            CYAN
        )
        self.screen.blit(title, (px + 12, py + 10))

        page_name = self.panel_pages[self.panel_page]

        page_text = self.font_small.render(
            f"PAGE {self.panel_page + 1}/{len(self.panel_pages)}  |  {page_name}",
            True,
            YELLOW
        )
        self.screen.blit(page_text, (px + 14, py + 42))

        health = self.get_system_health_score()

        if health >= 80:
            health_color = GREEN
            health_label = "STRONG"
        elif health >= 55:
            health_color = YELLOW
            health_label = "MODERATE"
        else:
            health_color = RED
            health_label = "WEAK"

        self.draw_status_chip(
            px + 14,
            py + 65,
            f"HEALTH {health}% - {health_label}",
            health_color
        )

        self.draw_status_chip(
            px + 190,
            py + 65,
            f"MODE {self.detection_mode}",
            PURPLE
        )

        py += header_h + 18

        # Page content
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

        # Footer controls
        footer_text = self.font_small.render(
            "TAB = Switch Page   |   G = Full Graph   |   ESC = Quit",
            True,
            CYAN
        )
        self.screen.blit(footer_text, (px + 8, HEIGHT - 24))

        if self.paused:
            pause_surf = self.font_large.render(
                "PAUSED",
                True,
                YELLOW
            )
            self.screen.blit(pause_surf, (px + 120, HEIGHT - 55))

    def get_system_health_score(self):
        actual_bad = sum(
            1 for d in self.swarm.drones if d.is_malicious
        )

        c_tp, c_fp, c_fn = self.classical.get_accuracy(
            self.swarm.drones
        )

        m_tp, m_fp, m_fn = self.ml_detector.get_accuracy(
            self.swarm.drones
        )

        c_recall = c_tp / actual_bad if actual_bad > 0 else 0
        m_recall = m_tp / actual_bad if actual_bad > 0 else 0

        false_alarm_penalty = min((c_fp + m_fp) * 4, 30)
        missed_penalty = min((c_fn + m_fn) * 3, 30)

        score = (0.35 * c_recall + 0.50 * m_recall) * 100
        score = score + 15 - false_alarm_penalty - missed_penalty

        return int(max(0, min(100, score)))

    def draw_status_chip(self, x, y, text, color):
        chip_w = max(150, self.font_small.size(text)[0] + 24)
        chip_h = 24

        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (x + 3, y + 3, chip_w, chip_h),
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            (24, 26, 40),
            (x, y, chip_w, chip_h),
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            color,
            (x, y, chip_w, chip_h),
            1,
            border_radius=12
        )

        pygame.draw.circle(
            self.screen,
            color,
            (x + 12, y + 12),
            5
        )

        label = self.font_small.render(text, True, WHITE)
        self.screen.blit(label, (x + 24, y + 5))

    def draw_panel_card(self, x, y, w, h, title, color=CYAN):
        # Outer glow shadow
        glow = pygame.Surface((w + 16, h + 16), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (color[0], color[1], color[2], 35),
            (0, 0, w + 16, h + 16),
            border_radius=14
        )
        self.screen.blit(glow, (x - 8, y - 8))

        # Dark shadow
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (x + 5, y + 5, w, h),
            border_radius=12
        )

        # Main body
        pygame.draw.rect(
            self.screen,
            (20, 22, 34),
            (x, y, w, h),
            border_radius=12
        )

        # Inner highlight
        pygame.draw.rect(
            self.screen,
            (32, 35, 52),
            (x + 2, y + 2, w - 4, 28),
            border_radius=10
        )

        # Border
        pygame.draw.rect(
            self.screen,
            color,
            (x, y, w, h),
            2,
            border_radius=12
        )

        # Top neon line
        pygame.draw.line(
            self.screen,
            color,
            (x + 14, y + 34),
            (x + w - 14, y + 34),
            1
        )

        # Title
        title_surf = self.font_med.render(title, True, color)
        self.screen.blit(title_surf, (x + 12, y + 8))

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

    def draw_section_title(self, text, x, y):
        surf = self.font_med.render(text, True, YELLOW)
        self.screen.blit(surf, (x, y))
        pygame.draw.line(
            self.screen, YELLOW,
            (x, y + 20), (x + 370, y + 20), 1
        )

    def draw_bar(self, x, y, w, h, ratio, color, label):
        ratio = max(0, min(1, ratio))

        # Shadow
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (x + 3, y + 3, w, h),
            border_radius=8
        )

        # Background
        pygame.draw.rect(
            self.screen,
            (42, 42, 50),
            (x, y, w, h),
            border_radius=8
        )

        # Fill
        fill_w = int(w * ratio)

        if fill_w > 0:
            pygame.draw.rect(
                self.screen,
                color,
                (x, y, fill_w, h),
                border_radius=8
            )

            # Highlight strip
            pygame.draw.rect(
                self.screen,
                (255, 255, 255),
                (x + 2, y + 2, max(0, fill_w - 4), max(1, h // 4)),
                border_radius=5
            )

        # Border
        pygame.draw.rect(
            self.screen,
            WHITE,
            (x, y, w, h),
            1,
            border_radius=8
        )

        text = self.font_small.render(
            f"{label}: {ratio * 100:.1f}%",
            True,
            WHITE
        )

        self.screen.blit(text, (x + 8, y + 3))

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