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
            "RISK SIGNALS",
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
        # Futuristic dark gradient background
        for y in range(0, HEIGHT, 4):
            shade = 8 + int(14 * y / HEIGHT)
            pygame.draw.rect(
                self.screen,
                (shade, shade, shade + 18),
                (0, y, SIM_WIDTH, 4)
            )

        # Subtle animated star/particle field
        for i in range(55):
            px = int((i * 137 + self.frame * 0.35) % SIM_WIDTH)
            py = int((i * 83 + self.frame * 0.18) % HEIGHT)
            brightness = 45 + (i * 7) % 80
            pygame.draw.circle(
                self.screen,
                (brightness // 2, brightness // 2, brightness),
                (px, py),
                1
            )

        # Cyber grid
        grid_color = (24, 45, 58)
        grid_glow = (0, 95, 115)

        for x in range(0, SIM_WIDTH, 50):
            pygame.draw.line(
                self.screen,
                grid_color,
                (x, 0),
                (x, HEIGHT),
                1
            )

        for y in range(0, HEIGHT, 50):
            pygame.draw.line(
                self.screen,
                grid_color,
                (0, y),
                (SIM_WIDTH, y),
                1
            )

        # Stronger major grid lines
        for x in range(0, SIM_WIDTH, 200):
            pygame.draw.line(
                self.screen,
                grid_glow,
                (x, 0),
                (x, HEIGHT),
                1
            )

        for y in range(0, HEIGHT, 200):
            pygame.draw.line(
                self.screen,
                grid_glow,
                (0, y),
                (SIM_WIDTH, y),
                1
            )

        # Animated horizontal scanner line
        scanner_y = (self.frame * 3) % HEIGHT
        scan_surface = pygame.Surface((SIM_WIDTH, 22), pygame.SRCALPHA)
        scan_surface.fill((0, 255, 255, 28))
        self.screen.blit(scan_surface, (0, scanner_y - 11))

        pygame.draw.line(
            self.screen,
            (0, 255, 255),
            (0, scanner_y),
            (SIM_WIDTH, scanner_y),
            1
        )

        # HUD border around simulation area
        pygame.draw.rect(
            self.screen,
            (0, 180, 210),
            (6, 6, SIM_WIDTH - 12, HEIGHT - 12),
            1
        )

        # Corner brackets
        corner_len = 48
        corner_color = CYAN

        # Top-left
        pygame.draw.line(self.screen, corner_color, (12, 12), (12 + corner_len, 12), 3)
        pygame.draw.line(self.screen, corner_color, (12, 12), (12, 12 + corner_len), 3)

        # Top-right
        pygame.draw.line(self.screen, corner_color, (SIM_WIDTH - 12, 12), (SIM_WIDTH - 12 - corner_len, 12), 3)
        pygame.draw.line(self.screen, corner_color, (SIM_WIDTH - 12, 12), (SIM_WIDTH - 12, 12 + corner_len), 3)

        # Bottom-left
        pygame.draw.line(self.screen, corner_color, (12, HEIGHT - 12), (12 + corner_len, HEIGHT - 12), 3)
        pygame.draw.line(self.screen, corner_color, (12, HEIGHT - 12), (12, HEIGHT - 12 - corner_len), 3)

        # Bottom-right
        pygame.draw.line(self.screen, corner_color, (SIM_WIDTH - 12, HEIGHT - 12), (SIM_WIDTH - 12 - corner_len, HEIGHT - 12), 3)
        pygame.draw.line(self.screen, corner_color, (SIM_WIDTH - 12, HEIGHT - 12), (SIM_WIDTH - 12, HEIGHT - 12 - corner_len), 3)

        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)

        # Futuristic top title panel
        title_box = pygame.Surface((560, 58), pygame.SRCALPHA)
        title_box.fill((0, 0, 0, 0))

        pygame.draw.rect(
            title_box,
            (8, 15, 25, 205),
            (0, 0, 560, 58),
            border_radius=12
        )

        pygame.draw.rect(
            title_box,
            (0, 255, 255, 180),
            (0, 0, 560, 58),
            2,
            border_radius=12
        )

        self.screen.blit(title_box, (15, 15))

        # Neon title shadow
        title_shadow = self.font_large.render(
            "MIRAGE: BYZANTINE SIMULATION",
            True,
            (0, 90, 100)
        )
        self.screen.blit(title_shadow, (28, 29))

        title = self.font_large.render(
            "MIRAGE: BYZANTINE SIMULATION",
            True,
            CYAN
        )
        self.screen.blit(title, (26, 27))

        subtitle = self.font_small.render(
            "Autonomous swarm trust analysis under Byzantine adversaries",
            True,
            WHITE
        )
        self.screen.blit(subtitle, (28, 53))

        # Small live status chip
        live_text = self.font_small.render(
            f"FRAME {self.frame}  |  MODE {self.detection_mode}",
            True,
            YELLOW
        )
        self.screen.blit(live_text, (600, 28))

        # Bottom controls glass bar
        control_bar = pygame.Surface((SIM_WIDTH - 30, 48), pygame.SRCALPHA)
        pygame.draw.rect(
            control_bar,
            (6, 10, 18, 185),
            (0, 0, SIM_WIDTH - 30, 48),
            border_radius=12
        )
        pygame.draw.rect(
            control_bar,
            (0, 255, 255, 100),
            (0, 0, SIM_WIDTH - 30, 48),
            1,
            border_radius=12
        )
        self.screen.blit(control_bar, (15, HEIGHT - 62))

        hints = [
            "SPACE Pause   R Reset   T Fake Position   TAB Panel   G Graph",
            "1 Classical   2 ML   3 Both   ESC Quit"
        ]

        for i, hint in enumerate(hints):
            surf = self.font_small.render(hint, True, WHITE)
            self.screen.blit(surf, (30, HEIGHT - 52 + i * 18))

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
        chip_w = max(150, self.font_small.size(text)[0] + 30)
        chip_h = 26

        glow = pygame.Surface((chip_w + 12, chip_h + 12), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (color[0], color[1], color[2], 45),
            (0, 0, chip_w + 12, chip_h + 12),
            border_radius=14
        )
        self.screen.blit(glow, (x - 6, y - 6))

        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (x + 3, y + 3, chip_w, chip_h),
            border_radius=13
        )

        pygame.draw.rect(
            self.screen,
            (18, 21, 34),
            (x, y, chip_w, chip_h),
            border_radius=13
        )

        pygame.draw.rect(
            self.screen,
            color,
            (x, y, chip_w, chip_h),
            1,
            border_radius=13
        )

        pygame.draw.circle(
            self.screen,
            color,
            (x + 13, y + 13),
            5
        )

        pygame.draw.circle(
            self.screen,
            WHITE,
            (x + 13, y + 13),
            5,
            1
        )

        label = self.font_small.render(text, True, WHITE)
        self.screen.blit(label, (x + 27, y + 6))

    def draw_panel_card(self, x, y, w, h, title, color=CYAN):
        # Outer neon glow
        glow = pygame.Surface((w + 28, h + 28), pygame.SRCALPHA)

        pygame.draw.rect(
            glow,
            (color[0], color[1], color[2], 32),
            (0, 0, w + 28, h + 28),
            border_radius=18
        )

        pygame.draw.rect(
            glow,
            (color[0], color[1], color[2], 18),
            (6, 6, w + 16, h + 16),
            border_radius=16
        )

        self.screen.blit(glow, (x - 14, y - 14))

        # Deep shadow
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (x + 6, y + 7, w, h),
            border_radius=14
        )

        # Main glass body
        pygame.draw.rect(
            self.screen,
            (17, 20, 33),
            (x, y, w, h),
            border_radius=14
        )

        # Header strip
        pygame.draw.rect(
            self.screen,
            (28, 33, 52),
            (x + 2, y + 2, w - 4, 34),
            border_radius=12
        )

        # Subtle inner body
        pygame.draw.rect(
            self.screen,
            (22, 25, 40),
            (x + 4, y + 38, w - 8, h - 42),
            border_radius=10
        )

        # Border
        pygame.draw.rect(
            self.screen,
            color,
            (x, y, w, h),
            2,
            border_radius=14
        )

        # Thin lower border for 3D depth
        pygame.draw.line(
            self.screen,
            (5, 8, 14),
            (x + 12, y + h - 4),
            (x + w - 12, y + h - 4),
            2
        )

        # HUD corner brackets
        c = color
        l = 16

        pygame.draw.line(self.screen, c, (x + 8, y + 8), (x + 8 + l, y + 8), 2)
        pygame.draw.line(self.screen, c, (x + 8, y + 8), (x + 8, y + 8 + l), 2)

        pygame.draw.line(self.screen, c, (x + w - 8, y + 8), (x + w - 8 - l, y + 8), 2)
        pygame.draw.line(self.screen, c, (x + w - 8, y + 8), (x + w - 8, y + 8 + l), 2)

        pygame.draw.line(self.screen, c, (x + 8, y + h - 8), (x + 8 + l, y + h - 8), 2)
        pygame.draw.line(self.screen, c, (x + 8, y + h - 8), (x + 8, y + h - 8 - l), 2)

        pygame.draw.line(self.screen, c, (x + w - 8, y + h - 8), (x + w - 8 - l, y + h - 8), 2)
        pygame.draw.line(self.screen, c, (x + w - 8, y + h - 8), (x + w - 8, y + h - 8 - l), 2)

        # Neon title
        title_shadow = self.font_med.render(title, True, (0, 0, 0))
        self.screen.blit(title_shadow, (x + 13, y + 10))

        title_surf = self.font_med.render(title, True, color)
        self.screen.blit(title_surf, (x + 12, y + 9))

        # Animated small scan dot
        dot_x = x + 14 + ((self.frame * 2) % max(1, w - 28))
        pygame.draw.circle(
            self.screen,
            color,
            (dot_x, y + 35),
            2
        )

        pygame.draw.line(
            self.screen,
            color,
            (x + 14, y + 36),
            (x + w - 14, y + 36),
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

    def risk_color(self, score):
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
        # Graph background glow
        glow = pygame.Surface((gw + 20, gh + 50), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (0, 255, 255, 22),
            (0, 0, gw + 20, gh + 50),
            border_radius=12
        )
        self.screen.blit(glow, (x - 10, y - 10))

        pygame.draw.rect(
            self.screen,
            (8, 12, 20),
            (x, y, gw, gh),
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            CYAN,
            (x, y, gw, gh),
            1,
            border_radius=10
        )

        # Grid lines
        for i in range(1, 5):
            gy = y + int(i * gh / 5)
            pygame.draw.line(
                self.screen,
                (25, 65, 75),
                (x, gy),
                (x + gw, gy),
                1
            )

        for i in range(1, 6):
            gx = x + int(i * gw / 6)
            pygame.draw.line(
                self.screen,
                (20, 45, 55),
                (gx, y),
                (gx, y + gh),
                1
            )

        # Moving graph scanline
        scan_x = x + ((self.frame * 3) % max(1, gw))
        pygame.draw.line(
            self.screen,
            (0, 255, 255),
            (scan_x, y),
            (scan_x, y + gh),
            1
        )

        actual_bad = sum(1 for d in self.swarm.drones if d.is_malicious)
        max_val = max(1, actual_bad)

        n = len(self.classical_tp_history)

        if n <= 1:
            msg = self.font_small.render(
                "Collecting detection history...",
                True,
                WHITE
            )
            self.screen.blit(msg, (x + 25, y + gh // 2))
            return

        classical_points = []
        ml_points = []

        for i in range(n):
            px = x + int(i / (n - 1) * gw)

            cy = y + gh - int(
                self.classical_tp_history[i] / max_val * gh
            )

            my = y + gh - int(
                self.ml_tp_history[i] / max_val * gh
            )

            classical_points.append((px, cy))
            ml_points.append((px, my))

        # Draw glow lines first
        for i in range(1, n):
            pygame.draw.line(
                self.screen,
                (0, 120, 60),
                classical_points[i - 1],
                classical_points[i],
                5
            )

            pygame.draw.line(
                self.screen,
                (90, 40, 150),
                ml_points[i - 1],
                ml_points[i],
                5
            )

        # Draw main lines
        for i in range(1, n):
            pygame.draw.line(
                self.screen,
                GREEN,
                classical_points[i - 1],
                classical_points[i],
                2
            )

            pygame.draw.line(
                self.screen,
                PURPLE,
                ml_points[i - 1],
                ml_points[i],
                2
            )

        # Data points
        for px, py in classical_points[-8:]:
            pygame.draw.circle(self.screen, GREEN, (px, py), 3)

        for px, py in ml_points[-8:]:
            pygame.draw.circle(self.screen, PURPLE, (px, py), 3)

        # Labels
        label_top = self.font_small.render(
            f"Max malicious = {actual_bad}",
            True,
            WHITE
        )
        self.screen.blit(label_top, (x + 8, y + 8))

        pygame.draw.line(
            self.screen,
            GREEN,
            (x + 10, y + gh + 16),
            (x + 35, y + gh + 16),
            3
        )
        self.screen.blit(
            self.font_small.render("Classical BFT", True, GREEN),
            (x + 42, y + gh + 8)
        )

        pygame.draw.line(
            self.screen,
            PURPLE,
            (x + 155, y + gh + 16),
            (x + 180, y + gh + 16),
            3
        )
        self.screen.blit(
            self.font_small.render("ML Anomaly", True, PURPLE),
            (x + 187, y + gh + 8)
        )

    def draw_large_graph_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 205))
        self.screen.blit(overlay, (0, 0))

        box_x = 75
        box_y = 48
        box_w = WIDTH - 150
        box_h = HEIGHT - 96

        # Outer glow
        glow = pygame.Surface((box_w + 40, box_h + 40), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (0, 255, 255, 30),
            (0, 0, box_w + 40, box_h + 40),
            border_radius=20
        )
        self.screen.blit(glow, (box_x - 20, box_y - 20))

        pygame.draw.rect(
            self.screen,
            (8, 12, 22),
            (box_x, box_y, box_w, box_h),
            border_radius=16
        )

        pygame.draw.rect(
            self.screen,
            CYAN,
            (box_x, box_y, box_w, box_h),
            2,
            border_radius=16
        )

        # Header
        pygame.draw.rect(
            self.screen,
            (18, 23, 38),
            (box_x + 3, box_y + 3, box_w - 6, 60),
            border_radius=14
        )

        title = self.font_large.render(
            "MIRAGE FULL DETECTION HISTORY",
            True,
            CYAN
        )
        self.screen.blit(title, (box_x + 25, box_y + 18))

        subtitle = self.font_small.render(
            "Live comparison of Classical Byzantine detection vs ML anomaly detection",
            True,
            WHITE
        )
        self.screen.blit(subtitle, (box_x + 25, box_y + 45))

        # Graph
        self.draw_detection_graph(
            box_x + 45,
            box_y + 95,
            box_w - 90,
            box_h - 175
        )

        # Bottom info strip
        info_y = box_y + box_h - 55

        pygame.draw.rect(
            self.screen,
            (18, 23, 38),
            (box_x + 25, info_y, box_w - 50, 36),
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            YELLOW,
            (box_x + 25, info_y, box_w - 50, 36),
            1,
            border_radius=10
        )

        footer = self.font_med.render(
            "Press G to close graph view",
            True,
            YELLOW
        )
        self.screen.blit(footer, (box_x + 45, info_y + 8))

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