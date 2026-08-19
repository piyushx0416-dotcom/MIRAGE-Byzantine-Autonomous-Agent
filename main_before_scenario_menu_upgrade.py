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
        self.show_comm_links = True
        self.selected_drone_id = 0
        self.panel_page = 0
        self.panel_pages = [
            "OVERVIEW",
            "CLASSICAL BFT",
            "ML DETECTION",
            "RISK SIGNALS",
            "HYBRID DEFENSE",
            "MISSION",
            "QUARANTINE",
            "DRONE DETAILS",
            "NETWORK",
            "GRAPH",
            "TRUST SYSTEM"
        ]

        # Trust score system
        self.trust_scores = {d.id: 100.0 for d in self.swarm.drones}
        self.suspicion_memory = {d.id: 0.0 for d in self.swarm.drones}
        self.clean_memory = {d.id: 0 for d in self.swarm.drones}
        self.trust_history = []


        # Stats tracking
        self.classical_tp_history = []
        self.ml_tp_history = []
        self.frame_history = []

        # Detection results
        self.classical_suspected = set()
        self.ml_suspected = set()
        self.hybrid_suspected = set()
        self.quarantined_drones = set()
        self.quarantine_enabled = True
        self.quarantine_zone = (SIM_WIDTH - 90, HEIGHT - 90)

        # Mission system: area coverage/scanning
        self.mission_enabled = True
        self.show_mission_overlay = True
        self.mission_cols = 16
        self.mission_rows = 12
        self.mission_target = 0.70
        self.verified_cells = set()
        self.claimed_cells = set()
        self.fake_claim_records = []

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

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.select_drone_at_position(event.pos)

            if event.type == pygame.KEYDOWN:
                # SPACE = pause
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                if event.key == pygame.K_TAB:
                    self.panel_page = (self.panel_page + 1) % len(self.panel_pages)

                if event.key == pygame.K_g:
                    self.show_large_graph = not self.show_large_graph

                if event.key == pygame.K_c:
                    self.show_comm_links = not self.show_comm_links

                if event.key == pygame.K_n:
                    self.selected_drone_id = (self.selected_drone_id + 1) % len(self.swarm.drones)
                    if "DRONE DETAILS" in self.panel_pages:
                        self.panel_page = self.panel_pages.index("DRONE DETAILS")

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

                # 4 = Hybrid defense mode
                if event.key == pygame.K_4:
                    self.detection_mode = "HYBRID"

                # Q = Toggle quarantine system
                if event.key == pygame.K_q:
                    self.quarantine_enabled = not self.quarantine_enabled

                # M = Toggle mission overlay
                if event.key == pygame.K_m:
                    self.show_mission_overlay = not self.show_mission_overlay

    def update(self):
        self.frame += 1
        self.swarm.update()

        # Update mission coverage/scanning
        if hasattr(self, "update_mission_system"):
            self.update_mission_system()

        # Move quarantined drones toward isolation zone
        if hasattr(self, "update_quarantine_motion"):
            self.update_quarantine_motion()

        # Run detection every 15 frames
        if self.frame % 15 == 0:
            self.classical_suspected = self.classical.detect(
                self.swarm.drones
            )
            self.ml_suspected = self.ml_detector.detect(
                self.swarm.drones
            )

            # Update trust scores after detectors run
            self.update_trust_scores()

            # Update hybrid detector after trust/risk signals
            self.hybrid_suspected = self.compute_hybrid_suspects()

            # Update quarantine status
            self.update_quarantine_status()

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

        # Draw mission overlay
        if hasattr(self, "draw_mission_overlay") and self.show_mission_overlay:
            self.draw_mission_overlay()

        # Draw quarantine isolation zone
        if hasattr(self, "draw_quarantine_zone"):
            self.draw_quarantine_zone()

        # Draw communication links before drones
        if self.show_comm_links:
            self.draw_communication_links()

        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)

        # Draw selected drone marker
        self.draw_selected_drone_marker()

        # Draw quarantine markers
        if hasattr(self, "draw_quarantine_markers"):
            self.draw_quarantine_markers()

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
            "SPACE Pause   R Reset   T Fake Position   C Comms   M Mission   Q Quarantine   N Next Drone   TAB Panel   G Graph",
            "1 Classical   2 ML   3 Both   4 Hybrid   4 Hybrid   ESC Quit"
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

        in_hybrid = (
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
            detected = in_classical or in_ml or in_hybrid

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
        page_name = self.panel_pages[self.panel_page]

        if page_name == "OVERVIEW":
            self.draw_overview_page(px, py)
        elif page_name == "CLASSICAL BFT":
            self.draw_classical_page(px, py)
        elif page_name == "ML DETECTION":
            self.draw_ml_page(px, py)
        elif page_name == "SIGNALS" or page_name == "RISK SIGNALS":
            self.draw_signals_page(px, py)
        elif page_name == "DRONE DETAILS":
            self.draw_drone_details_page(px, py)
        elif page_name == "HYBRID DEFENSE":
            self.draw_hybrid_page(px, py)
        elif page_name == "MISSION":
            self.draw_mission_page(px, py)
        elif page_name == "QUARANTINE":
            self.draw_quarantine_page(px, py)
        elif page_name == "NETWORK":
            self.draw_network_page(px, py)
        elif page_name == "GRAPH":
            self.draw_graph_page(px, py)
        elif page_name == "TRUST SYSTEM" and hasattr(self, "draw_trust_page"):
            self.draw_trust_page(px, py)
        else:
            msg = self.font_med.render(
                "Page not available.",
                True,
                RED
            )
            self.screen.blit(msg, (px + 20, py + 20))

        # Footer controls
        footer_text = self.font_small.render(
            "Click/N Select | C Comms | M Mission | Q Quarantine | TAB Page | G Graph | ESC Quit",
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
        """
        Futuristic graph with axes.

        X-axis = detection cycle/time
        Y-axis = number of correctly detected malicious drones
        """

        # Graph background glow
        glow = pygame.Surface((gw + 24, gh + 56), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (0, 255, 255, 22),
            (0, 0, gw + 24, gh + 56),
            border_radius=12
        )
        self.screen.blit(glow, (x - 12, y - 12))

        # Main graph card
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

        actual_bad = sum(1 for d in self.swarm.drones if d.is_malicious)
        max_val = max(1, actual_bad)

        n = len(self.classical_tp_history)

        # Internal plot margins for axes and labels
        left_margin = 42
        right_margin = 14
        top_margin = 24
        bottom_margin = 34

        plot_x = x + left_margin
        plot_y = y + top_margin
        plot_w = gw - left_margin - right_margin
        plot_h = gh - top_margin - bottom_margin

        # Plot background
        pygame.draw.rect(
            self.screen,
            (5, 8, 16),
            (plot_x, plot_y, plot_w, plot_h),
            border_radius=6
        )

        # Axis lines
        axis_color = (180, 230, 235)

        pygame.draw.line(
            self.screen,
            axis_color,
            (plot_x, plot_y),
            (plot_x, plot_y + plot_h),
            2
        )

        pygame.draw.line(
            self.screen,
            axis_color,
            (plot_x, plot_y + plot_h),
            (plot_x + plot_w, plot_y + plot_h),
            2
        )

        # Y-axis ticks and horizontal grid
        tick_count = max_val

        if tick_count > 5:
            tick_count = 5

        for i in range(0, tick_count + 1):
            value = int(round(i * max_val / tick_count)) if tick_count > 0 else 0
            tick_y = plot_y + plot_h - int((value / max_val) * plot_h)

            pygame.draw.line(
                self.screen,
                (25, 65, 75),
                (plot_x, tick_y),
                (plot_x + plot_w, tick_y),
                1
            )

            pygame.draw.line(
                self.screen,
                axis_color,
                (plot_x - 5, tick_y),
                (plot_x, tick_y),
                2
            )

            label = self.font_small.render(
                str(value),
                True,
                WHITE
            )
            self.screen.blit(label, (x + 16, tick_y - 7))

        # X-axis ticks and vertical grid
        x_tick_count = 4

        for i in range(0, x_tick_count + 1):
            tick_x = plot_x + int(i * plot_w / x_tick_count)

            pygame.draw.line(
                self.screen,
                (20, 45, 55),
                (tick_x, plot_y),
                (tick_x, plot_y + plot_h),
                1
            )

            pygame.draw.line(
                self.screen,
                axis_color,
                (tick_x, plot_y + plot_h),
                (tick_x, plot_y + plot_h + 5),
                2
            )

            if n > 1:
                cycle_label = int(i * (n - 1) / x_tick_count)
            else:
                cycle_label = 0

            label = self.font_small.render(
                str(cycle_label),
                True,
                WHITE
            )
            self.screen.blit(label, (tick_x - 6, plot_y + plot_h + 9))

        # Axis labels
        y_label = self.font_small.render(
            "Caught",
            True,
            CYAN
        )
        y_label_rotated = pygame.transform.rotate(y_label, 90)
        self.screen.blit(y_label_rotated, (x + 3, plot_y + plot_h // 2 - 25))

        x_label = self.font_small.render(
            "Detection Cycle / Time",
            True,
            CYAN
        )
        self.screen.blit(
            x_label,
            (plot_x + plot_w // 2 - 55, y + gh - 16)
        )

        # Small title inside graph
        graph_title = self.font_small.render(
            "Correct Malicious Detections Over Time",
            True,
            YELLOW
        )
        self.screen.blit(graph_title, (plot_x + 5, y + 6))

        # If no data yet
        if n <= 1:
            msg = self.font_small.render(
                "Collecting detection history...",
                True,
                WHITE
            )
            self.screen.blit(
                msg,
                (plot_x + 25, plot_y + plot_h // 2)
            )
            return

        classical_points = []
        ml_points = []

        for i in range(n):
            px = plot_x + int(i / (n - 1) * plot_w)

            classical_y = plot_y + plot_h - int(
                self.classical_tp_history[i] / max_val * plot_h
            )

            ml_y = plot_y + plot_h - int(
                self.ml_tp_history[i] / max_val * plot_h
            )

            classical_points.append((px, classical_y))
            ml_points.append((px, ml_y))

        # Moving graph scanline
        scan_x = plot_x + ((self.frame * 3) % max(1, plot_w))
        pygame.draw.line(
            self.screen,
            (0, 255, 255),
            (scan_x, plot_y),
            (scan_x, plot_y + plot_h),
            1
        )

        # Glow lines
        for i in range(1, n):
            pygame.draw.line(
                self.screen,
                (0, 100, 55),
                classical_points[i - 1],
                classical_points[i],
                5
            )

            pygame.draw.line(
                self.screen,
                (80, 35, 140),
                ml_points[i - 1],
                ml_points[i],
                5
            )

        # Main lines
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
        for px, point_y in classical_points[-8:]:
            pygame.draw.circle(
                self.screen,
                GREEN,
                (px, point_y),
                3
            )

        for px, point_y in ml_points[-8:]:
            pygame.draw.circle(
                self.screen,
                PURPLE,
                (px, point_y),
                3
            )

        # Latest value labels
        latest_c = self.classical_tp_history[-1]
        latest_m = self.ml_tp_history[-1]

        latest_c_pos = classical_points[-1]
        latest_m_pos = ml_points[-1]

        c_label = self.font_small.render(
            f"C:{latest_c}",
            True,
            GREEN
        )
        self.screen.blit(
            c_label,
            (latest_c_pos[0] - 18, latest_c_pos[1] - 18)
        )

        m_label = self.font_small.render(
            f"ML:{latest_m}",
            True,
            PURPLE
        )
        self.screen.blit(
            m_label,
            (latest_m_pos[0] - 20, latest_m_pos[1] + 6)
        )

        # Top-left max label
        max_label = self.font_small.render(
            f"Max malicious = {actual_bad}",
            True,
            WHITE
        )
        self.screen.blit(max_label, (plot_x + 8, plot_y + 8))

        # Legend below graph
        legend_y = y + gh + 8

        pygame.draw.line(
            self.screen,
            GREEN,
            (x + 10, legend_y + 8),
            (x + 35, legend_y + 8),
            3
        )

        self.screen.blit(
            self.font_small.render("Classical BFT", True, GREEN),
            (x + 42, legend_y)
        )

        pygame.draw.line(
            self.screen,
            PURPLE,
            (x + 155, legend_y + 8),
            (x + 180, legend_y + 8),
            3
        )

        self.screen.blit(
            self.font_small.render("ML Anomaly", True, PURPLE),
            (x + 187, legend_y)
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

    def update_trust_scores(self):
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
            "Trust uses suspicion memory over time.",
            "Trust no longer collapses to absolute zero.",
            "Weak one-method alerts cause tiny penalty.",
            "Repeated strong evidence causes quarantine.",
            "Clean behavior slowly restores trust."
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

    def get_drone_trust_value(self, drone_id):
        if hasattr(self, "trust_scores"):
            return self.trust_scores.get(drone_id, 100.0)
        return 100.0

    def get_communication_links(self):
        communication_range = 190
        links = []

        drones = self.swarm.drones

        for i in range(len(drones)):
            for j in range(i + 1, len(drones)):
                a = drones[i]
                b = drones[j]

                # Skip quarantined drones from normal communication
                if hasattr(self, "quarantined_drones"):
                    if a.id in self.quarantined_drones or b.id in self.quarantined_drones:
                        continue

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

    def get_network_metrics(self):
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

    def draw_dashed_line(self, surface, color, start_pos, end_pos, width=1, dash_length=10):
        x1, y1 = start_pos
        x2, y2 = end_pos

        total_dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if total_dist == 0:
            return

        dx = (x2 - x1) / total_dist
        dy = (y2 - y1) / total_dist

        current = 0

        while current < total_dist:
            sx = x1 + dx * current
            sy = y1 + dy * current

            ex = x1 + dx * min(current + dash_length, total_dist)
            ey = y1 + dy * min(current + dash_length, total_dist)

            pygame.draw.line(
                surface,
                color,
                (int(sx), int(sy)),
                (int(ex), int(ey)),
                width
            )

            current += dash_length * 2

    def draw_communication_links(self):
        links = self.get_communication_links()

        for link in links:
            a = link["a"]
            b = link["b"]
            color = link["color"]
            status = link["status"]

            ax = int(a.x)
            ay = int(a.y)
            bx = int(b.x)
            by = int(b.y)

            if status == "DROPPED":
                self.draw_dashed_line(
                    self.screen,
                    color,
                    (ax, ay),
                    (bx, by),
                    1,
                    8
                )
            else:
                width = 1

                if status == "SUSPICIOUS":
                    width = 2
                elif status == "LOW_TRUST":
                    width = 2

                # Glow line
                pygame.draw.line(
                    self.screen,
                    (color[0] // 3, color[1] // 3, color[2] // 3),
                    (ax, ay),
                    (bx, by),
                    width + 2
                )

                # Main line
                pygame.draw.line(
                    self.screen,
                    color,
                    (ax, ay),
                    (bx, by),
                    width
                )

                # Small moving pulse on active links
                if status != "DROPPED":
                    t = ((self.frame % 60) / 60)
                    pulse_x = int(ax + (bx - ax) * t)
                    pulse_y = int(ay + (by - ay) * t)

                    pygame.draw.circle(
                        self.screen,
                        color,
                        (pulse_x, pulse_y),
                        3
                    )

    def draw_network_page(self, px, py):
        metrics = self.get_network_metrics()
        health = metrics["health"]

        if health >= 80:
            health_color = GREEN
            health_label = "STRONG"
        elif health >= 55:
            health_color = YELLOW
            health_label = "MODERATE"
        else:
            health_color = RED
            health_label = "WEAK"

        # Card 1: Network health
        self.draw_panel_card(px, py, 360, 145, "COMMUNICATION NETWORK", CYAN)
        y = py + 42

        lines = [
            (f"Network Health: {health}% ({health_label})", health_color),
            (f"Communication Links: {metrics['total']}", WHITE),
            (f"Active Links: {metrics['active']}", GREEN),
            (f"Comms Visible: {'ON' if self.show_comm_links else 'OFF'}", YELLOW),
        ]

        for text, color in lines:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 23

        py += 160

        self.draw_bar(
            px + 15,
            py,
            330,
            22,
            health / 100,
            health_color,
            "Network Health"
        )

        py += 48

        # Card 2: Link breakdown
        self.draw_panel_card(px, py, 360, 165, "LINK BREAKDOWN", YELLOW)
        y = py + 42

        breakdown = [
            (f"Trusted Links: {metrics['trusted']}", CYAN),
            (f"Suspicious Links: {metrics['suspicious']}", RED),
            (f"Low Trust Links: {metrics['low_trust']}", PURPLE),
            (f"Dropped Messages: {metrics['dropped']}", GRAY),
            (f"Communication Range: 190 px", WHITE),
        ]

        for text, color in breakdown:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 22

        py += 180

        # Card 3: Legend
        self.draw_panel_card(px, py, 360, 140, "COMMUNICATION LEGEND", ORANGE)
        y = py + 42

        legend = [
            (CYAN, "Trusted communication"),
            (RED, "Suspicious communication"),
            (PURPLE, "Low-trust communication"),
            (GRAY, "Dropped/failed message"),
        ]

        for color, label in legend:
            pygame.draw.line(
                self.screen,
                color,
                (px + 18, y + 9),
                (px + 55, y + 9),
                3
            )

            s = self.font_small.render(label, True, WHITE)
            self.screen.blit(s, (px + 68, y + 2))
            y += 23

        py += 155

        # Card 4: Explanation
        self.draw_panel_card(px, py, 360, 120, "WHY THIS MATTERS", PURPLE)
        y = py + 42

        explanation = [
            "Byzantine attacks happen through messages.",
            "A swarm must know which links are trusted.",
            "Low-trust drones reduce network health.",
            "Press C to hide/show communication links."
        ]

        for line in explanation:
            s = self.font_small.render(line, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 19

    def get_selected_drone(self):
        if not self.swarm.drones:
            return None

        valid_ids = [d.id for d in self.swarm.drones]

        if self.selected_drone_id not in valid_ids:
            self.selected_drone_id = self.swarm.drones[0].id

        for drone in self.swarm.drones:
            if drone.id == self.selected_drone_id:
                return drone

        return self.swarm.drones[0]

    def select_drone_at_position(self, pos):
        mx, my = pos

        # Only select from simulation area, not right panel
        if mx >= SIM_WIDTH:
            return

        nearest = None
        nearest_dist = 999999

        for drone in self.swarm.drones:
            # Same pseudo altitude idea used by the 3D drone drawing
            altitude = 10 + (drone.id % 4) * 2 + int(
                3 * np.sin((self.frame + drone.id * 13) / 18)
            )

            body_x = int(drone.x)
            body_y = int(drone.y - altitude)

            d = np.sqrt((mx - body_x) ** 2 + (my - body_y) ** 2)

            if d < nearest_dist:
                nearest_dist = d
                nearest = drone

        if nearest is not None and nearest_dist <= 45:
            self.selected_drone_id = nearest.id

            if "DRONE DETAILS" in self.panel_pages:
                self.panel_page = self.panel_pages.index("DRONE DETAILS")

    def draw_selected_drone_marker(self):
        drone = self.get_selected_drone()

        if drone is None:
            return

        altitude = 10 + (drone.id % 4) * 2 + int(
            3 * np.sin((self.frame + drone.id * 13) / 18)
        )

        x = int(drone.x)
        y = int(drone.y - altitude)

        pulse = 28 + (self.frame % 15)

        pygame.draw.circle(
            self.screen,
            CYAN,
            (x, y),
            pulse,
            2
        )

        pygame.draw.circle(
            self.screen,
            WHITE,
            (x, y),
            pulse + 6,
            1
        )

        label = self.font_small.render(
            "SELECTED",
            True,
            CYAN
        )

        self.screen.blit(label, (x - 28, y - pulse - 18))

    def get_drone_comm_summary(self, drone_id):
        if not hasattr(self, "get_communication_links"):
            return {
                "total": 0,
                "trusted": 0,
                "suspicious": 0,
                "low_trust": 0,
                "dropped": 0
            }

        links = self.get_communication_links()

        relevant = [
            link for link in links
            if link["a"].id == drone_id or link["b"].id == drone_id
        ]

        return {
            "total": len(relevant),
            "trusted": sum(1 for l in relevant if l["status"] == "TRUSTED"),
            "suspicious": sum(1 for l in relevant if l["status"] == "SUSPICIOUS"),
            "low_trust": sum(1 for l in relevant if l["status"] == "LOW_TRUST"),
            "dropped": sum(1 for l in relevant if l["status"] == "DROPPED")
        }

    def draw_drone_details_page(self, px, py):
        drone = self.get_selected_drone()

        if drone is None:
            self.draw_panel_card(px, py, 360, 120, "DRONE DETAILS", RED)
            msg = self.font_small.render(
                "No drone selected.",
                True,
                WHITE
            )
            self.screen.blit(msg, (px + 15, py + 45))
            return

        # Get signal information
        if hasattr(self, "compute_detection_signals"):
            signal = self.compute_detection_signals(drone)
        else:
            signal = {
                "position_score": 0,
                "isolation_score": 0,
                "classical_score": 90 if drone.id in self.classical_suspected else 0,
                "ml_score": 90 if drone.id in self.ml_suspected else 0,
                "agreement_score": 100 if (
                    drone.id in self.classical_suspected and
                    drone.id in self.ml_suspected
                ) else 0,
                "final_risk": 0
            }

        trust = 100.0

        if hasattr(self, "trust_scores"):
            trust = self.trust_scores.get(drone.id, 100.0)

        comm = self.get_drone_comm_summary(drone.id)

        in_classical = drone.id in self.classical_suspected
        in_ml = drone.id in self.ml_suspected

        risk = signal["final_risk"]

        if trust < 30 or risk >= 75:
            decision = "QUARANTINE"
            decision_color = RED
        elif trust < 55 or risk >= 45:
            decision = "WATCHLIST"
            decision_color = YELLOW
        else:
            decision = "TRUSTED"
            decision_color = GREEN

        # Card 1: Identity
        self.draw_panel_card(px, py, 360, 145, f"DRONE {drone.id} DETAILS", CYAN)
        y = py + 42

        truth = "MALICIOUS" if drone.is_malicious else "HONEST"
        truth_color = RED if drone.is_malicious else GREEN

        lines = [
            (f"Ground Truth: {truth}", truth_color),
            (f"Classical Flagged: {'YES' if in_classical else 'NO'}", RED if in_classical else GREEN),
            (f"ML Flagged: {'YES' if in_ml else 'NO'}", RED if in_ml else GREEN),
            (f"Final Decision: {decision}", decision_color),
        ]

        for text, color in lines:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 23

        py += 160

        # Card 2: Trust and risk
        self.draw_panel_card(px, py, 360, 210, "TRUST + RISK BREAKDOWN", PURPLE)
        y = py + 42

        if hasattr(self, "draw_trust_bar"):
            self.draw_trust_bar(px + 15, y, 320, 19, trust, "Trust")
        else:
            self.draw_bar(px + 15, y, 320, 19, trust / 100, GREEN, "Trust")
        y += 28

        if hasattr(self, "draw_score_bar"):
            self.draw_score_bar(px + 15, y, 320, 18, signal["position_score"], "Position Lie")
            y += 26

            self.draw_score_bar(px + 15, y, 320, 18, signal["isolation_score"], "Isolation")
            y += 26

            self.draw_score_bar(px + 15, y, 320, 18, signal["classical_score"], "Classical")
            y += 26

            self.draw_score_bar(px + 15, y, 320, 18, signal["ml_score"], "ML")
            y += 26

            self.draw_score_bar(px + 15, y, 320, 18, signal["final_risk"], "Final Risk")
        else:
            self.draw_bar(px + 15, y, 320, 18, risk / 100, RED, "Final Risk")

        py += 225

        # Card 3: Communication details
        self.draw_panel_card(px, py, 360, 145, "COMMUNICATION PROFILE", YELLOW)
        y = py + 42

        comm_lines = [
            (f"Total Links: {comm['total']}", WHITE),
            (f"Trusted Links: {comm['trusted']}", CYAN),
            (f"Suspicious Links: {comm['suspicious']}", RED),
            (f"Low Trust Links: {comm['low_trust']}", PURPLE),
            (f"Dropped Links: {comm['dropped']}", GRAY),
        ]

        for text, color in comm_lines:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 20

        py += 160

        # Card 4: Explanation
        self.draw_panel_card(px, py, 360, 120, "INTERPRETATION", ORANGE)
        y = py + 42

        if decision == "QUARANTINE":
            explanation = [
                "This drone has high risk or very low trust.",
                "It should be isolated from decisions.",
                "Continue monitoring before removal."
            ]
        elif decision == "WATCHLIST":
            explanation = [
                "This drone has moderate suspicious signals.",
                "It should be monitored carefully.",
                "More evidence is needed."
            ]
        else:
            explanation = [
                "This drone currently behaves normally.",
                "It can participate in swarm decisions.",
                "Trust remains acceptable."
            ]

        for line in explanation:
            s = self.font_small.render(line, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 20

    def compute_hybrid_score(self, drone):
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

    def get_drone_by_id(self, drone_id):
        for drone in self.swarm.drones:
            if drone.id == drone_id:
                return drone
        return None

    def get_drone_trust_for_quarantine(self, drone_id):
        if hasattr(self, "trust_scores"):
            return self.trust_scores.get(drone_id, 100.0)
        return 100.0

    def get_drone_risk_for_quarantine(self, drone):
        if hasattr(self, "compute_hybrid_score"):
            return self.compute_hybrid_score(drone)["hybrid_score"]

        if hasattr(self, "compute_detection_signals"):
            return self.compute_detection_signals(drone)["final_risk"]

        return 0

    def update_quarantine_status(self):
        if not hasattr(self, "quarantined_drones"):
            self.quarantined_drones = set()

        if not hasattr(self, "quarantine_enabled"):
            self.quarantine_enabled = True

        if not self.quarantine_enabled:
            return

        for drone in self.swarm.drones:
            trust = self.get_drone_trust_for_quarantine(drone.id)
            risk = self.get_drone_risk_for_quarantine(drone)

            in_hybrid = (
                hasattr(self, "hybrid_suspected") and
                drone.id in self.hybrid_suspected
            )

            in_both = (
                drone.id in self.classical_suspected and
                drone.id in self.ml_suspected
            )

            # Quarantine rule:
            # Strong risk, very low trust, or detector agreement.
            if risk >= 78:
                self.quarantined_drones.add(drone.id)
            elif trust < 18 and risk >= 45:
                self.quarantined_drones.add(drone.id)
            elif in_hybrid and trust < 35:
                self.quarantined_drones.add(drone.id)
            elif in_both and risk >= 60:
                self.quarantined_drones.add(drone.id)

            # Release rule:
            # Only release if trust recovered and risk is low.
            if drone.id in self.quarantined_drones:
                if trust > 72 and risk < 30 and not drone.is_malicious:
                    self.quarantined_drones.discard(drone.id)

    def update_quarantine_motion(self):
        if not hasattr(self, "quarantined_drones"):
            return

        if not hasattr(self, "quarantine_enabled"):
            self.quarantine_enabled = True

        if not self.quarantine_enabled:
            return

        zone_x, zone_y = getattr(
            self,
            "quarantine_zone",
            (SIM_WIDTH - 90, HEIGHT - 90)
        )

        for drone_id in list(self.quarantined_drones):
            drone = self.get_drone_by_id(drone_id)

            if drone is None:
                continue

            # Pull drone toward isolation zone
            drone.x += (zone_x - drone.x) * 0.035
            drone.y += (zone_y - drone.y) * 0.035

            # Damp normal movement so it stays contained
            if hasattr(drone, "velocity_x"):
                drone.velocity_x *= 0.55
                drone.velocity_y *= 0.55

            if hasattr(drone, "vx"):
                drone.vx *= 0.55
                drone.vy *= 0.55

    def draw_quarantine_zone(self):
        zone_x, zone_y = getattr(
            self,
            "quarantine_zone",
            (SIM_WIDTH - 90, HEIGHT - 90)
        )

        zone_w = 150
        zone_h = 120

        x = int(zone_x - zone_w // 2)
        y = int(zone_y - zone_h // 2)

        # Transparent zone fill
        zone_surface = pygame.Surface((zone_w, zone_h), pygame.SRCALPHA)
        zone_surface.fill((255, 40, 40, 28))
        self.screen.blit(zone_surface, (x, y))

        # Border
        pygame.draw.rect(
            self.screen,
            RED,
            (x, y, zone_w, zone_h),
            2,
            border_radius=12
        )

        # Inner warning border
        pygame.draw.rect(
            self.screen,
            ORANGE,
            (x + 6, y + 6, zone_w - 12, zone_h - 12),
            1,
            border_radius=10
        )

        # Animated warning scan
        scan_y = y + ((self.frame * 2) % zone_h)

        pygame.draw.line(
            self.screen,
            RED,
            (x, scan_y),
            (x + zone_w, scan_y),
            1
        )

        label = self.font_small.render(
            "QUARANTINE ZONE",
            True,
            RED
        )
        self.screen.blit(label, (x + 20, y + 10))

        count = len(getattr(self, "quarantined_drones", set()))

        count_label = self.font_small.render(
            f"ISOLATED: {count}",
            True,
            YELLOW
        )
        self.screen.blit(count_label, (x + 36, y + 30))

    def draw_quarantine_markers(self):
        if not hasattr(self, "quarantined_drones"):
            return

        zone_x, zone_y = getattr(
            self,
            "quarantine_zone",
            (SIM_WIDTH - 90, HEIGHT - 90)
        )

        for drone_id in self.quarantined_drones:
            drone = self.get_drone_by_id(drone_id)

            if drone is None:
                continue

            altitude = 10 + (drone.id % 4) * 2 + int(
                3 * np.sin((self.frame + drone.id * 13) / 18)
            )

            x = int(drone.x)
            y = int(drone.y - altitude)

            # Tether line to quarantine zone
            pygame.draw.line(
                self.screen,
                RED,
                (x, y),
                (int(zone_x), int(zone_y)),
                1
            )

            pulse = 35 + (self.frame % 15)

            pygame.draw.circle(
                self.screen,
                RED,
                (x, y),
                pulse,
                2
            )

            pygame.draw.circle(
                self.screen,
                ORANGE,
                (x, y),
                pulse + 7,
                1
            )

            tag = self.font_small.render(
                "QUARANTINED",
                True,
                RED
            )
            self.screen.blit(tag, (x - 38, y - pulse - 18))

    def get_quarantine_candidate_info(self):
        infos = []

        for drone in self.swarm.drones:
            trust = self.get_drone_trust_for_quarantine(drone.id)
            risk = self.get_drone_risk_for_quarantine(drone)

            quarantined = (
                hasattr(self, "quarantined_drones") and
                drone.id in self.quarantined_drones
            )

            infos.append({
                "id": drone.id,
                "trust": trust,
                "risk": risk,
                "quarantined": quarantined,
                "is_malicious": drone.is_malicious
            })

        infos.sort(
            key=lambda item: (
                item["quarantined"],
                item["risk"],
                100 - item["trust"]
            ),
            reverse=True
        )

        return infos

    def draw_quarantine_row(self, x, y, info):
        drone_id = info["id"]
        risk = info["risk"]
        trust = info["trust"]
        quarantined = info["quarantined"]

        if quarantined:
            color = RED
            status = "LOCKED"
        elif risk >= 60 or trust < 40:
            color = YELLOW
            status = "WATCH"
        else:
            color = GREEN
            status = "CLEAR"

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

        risk_text = self.font_small.render(
            f"Risk {risk}",
            True,
            color
        )
        self.screen.blit(risk_text, (x + 58, y + 5))

        trust_text = self.font_small.render(
            f"Trust {trust:.0f}%",
            True,
            WHITE
        )
        self.screen.blit(trust_text, (x + 140, y + 5))

        status_text = self.font_small.render(
            status,
            True,
            color
        )
        self.screen.blit(status_text, (x + 250, y + 5))

    def draw_quarantine_page(self, px, py):
        if not hasattr(self, "quarantined_drones"):
            self.quarantined_drones = set()

        infos = self.get_quarantine_candidate_info()

        quarantined_count = len(self.quarantined_drones)
        watch_count = sum(
            1 for item in infos
            if not item["quarantined"] and
            (item["risk"] >= 60 or item["trust"] < 40)
        )

        # Card 1: Quarantine overview
        self.draw_panel_card(px, py, 360, 150, "QUARANTINE CONTROL", RED)
        y = py + 42

        status_text = "ENABLED" if self.quarantine_enabled else "DISABLED"
        status_color = GREEN if self.quarantine_enabled else YELLOW

        lines = [
            (f"System Status: {status_text}", status_color),
            (f"Quarantined Drones: {quarantined_count}", RED),
            (f"Watchlist Drones: {watch_count}", YELLOW),
            (f"Isolation Zone: ACTIVE", CYAN),
        ]

        for text, color in lines:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 23

        py += 165

        # Card 2: Top quarantine/watchlist
        self.draw_panel_card(px, py, 360, 190, "ISOLATION PRIORITY LIST", ORANGE)
        y = py + 42

        for info in infos[:5]:
            self.draw_quarantine_row(px + 15, y, info)
            y += 29

        py += 205

        # Card 3: Rules
        self.draw_panel_card(px, py, 360, 165, "QUARANTINE RULES", YELLOW)
        y = py + 42

        rules = [
            "Risk >= 78 triggers quarantine.",
            "Low trust + medium risk triggers quarantine.",
            "Hybrid suspicion + low trust triggers isolation.",
            "Quarantined drones stop normal communication.",
            "Press Q to enable/disable quarantine."
        ]

        for rule in rules:
            s = self.font_small.render(rule, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 22

        py += 180

        # Card 4: Why it matters
        self.draw_panel_card(px, py, 360, 120, "WHY THIS MATTERS", PURPLE)
        y = py + 42

        explanation = [
            "Detection alone is not enough.",
            "A secure swarm must contain risky agents.",
            "Quarantine prevents bad drones from",
            "influencing future swarm decisions."
        ]

        for line in explanation:
            s = self.font_small.render(line, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 20

    def get_mission_cell(self, x, y):
        if not hasattr(self, "mission_cols"):
            self.mission_cols = 16
            self.mission_rows = 12

        cell_w = SIM_WIDTH / self.mission_cols
        cell_h = HEIGHT / self.mission_rows

        col = int(max(0, min(self.mission_cols - 1, x // cell_w)))
        row = int(max(0, min(self.mission_rows - 1, y // cell_h)))

        return (col, row)

    def update_mission_system(self):
        if not hasattr(self, "mission_enabled"):
            self.mission_enabled = True

        if not self.mission_enabled:
            return

        if not hasattr(self, "verified_cells"):
            self.verified_cells = set()

        if not hasattr(self, "claimed_cells"):
            self.claimed_cells = set()

        if not hasattr(self, "fake_claim_records"):
            self.fake_claim_records = []

        for drone in self.swarm.drones:
            real_cell = self.get_mission_cell(drone.x, drone.y)

            # Honest drones verify the cell they really visit
            if not drone.is_malicious:
                self.verified_cells.add(real_cell)
                self.claimed_cells.add(real_cell)

            else:
                # Malicious drones sometimes claim fake mission completion
                # and only rarely verify real cells.
                if self.frame % 20 == 0:
                    fake_col = (real_cell[0] + drone.id + self.frame // 20) % self.mission_cols
                    fake_row = (real_cell[1] + drone.id * 2 + self.frame // 35) % self.mission_rows
                    fake_cell = (fake_col, fake_row)

                    self.claimed_cells.add(fake_cell)

                    if fake_cell not in self.verified_cells:
                        self.fake_claim_records.append({
                            "frame": self.frame,
                            "drone_id": drone.id,
                            "cell": fake_cell
                        })

                        if len(self.fake_claim_records) > 120:
                            self.fake_claim_records.pop(0)

                # Sometimes malicious drones do actually scan, to make behavior realistic
                if self.frame % 90 == 0:
                    self.verified_cells.add(real_cell)
                    self.claimed_cells.add(real_cell)

    def get_mission_metrics(self):
        total_cells = self.mission_cols * self.mission_rows

        verified = len(self.verified_cells)
        claimed = len(self.claimed_cells)

        fake_cells = self.claimed_cells - self.verified_cells
        fake_count = len(fake_cells)

        verified_progress = verified / total_cells if total_cells else 0
        claimed_progress = claimed / total_cells if total_cells else 0

        if claimed == 0:
            integrity = 100
        else:
            integrity = int(max(0, min(100, (verified / claimed) * 100)))

        target = getattr(self, "mission_target", 0.70)

        mission_success = (
            verified_progress >= target and
            integrity >= 75
        )

        return {
            "total_cells": total_cells,
            "verified": verified,
            "claimed": claimed,
            "fake_count": fake_count,
            "verified_progress": verified_progress,
            "claimed_progress": claimed_progress,
            "integrity": integrity,
            "target": target,
            "mission_success": mission_success
        }

    def draw_mission_overlay(self):
        if not hasattr(self, "mission_cols"):
            return

        cell_w = SIM_WIDTH / self.mission_cols
        cell_h = HEIGHT / self.mission_rows

        fake_cells = self.claimed_cells - self.verified_cells

        overlay = pygame.Surface((SIM_WIDTH, HEIGHT), pygame.SRCALPHA)

        # Verified cells
        for col, row in self.verified_cells:
            x = int(col * cell_w)
            y = int(row * cell_h)
            w = int(cell_w)
            h = int(cell_h)

            pygame.draw.rect(
                overlay,
                (0, 255, 180, 34),
                (x, y, w, h)
            )

            pygame.draw.rect(
                overlay,
                (0, 180, 150, 70),
                (x, y, w, h),
                1
            )

        # Claimed but unverified / fake cells
        for col, row in fake_cells:
            x = int(col * cell_w)
            y = int(row * cell_h)
            w = int(cell_w)
            h = int(cell_h)

            pygame.draw.rect(
                overlay,
                (255, 80, 40, 50),
                (x, y, w, h)
            )

            pygame.draw.rect(
                overlay,
                (255, 80, 40, 120),
                (x, y, w, h),
                1
            )

            # diagonal mark
            pygame.draw.line(
                overlay,
                (255, 90, 50, 150),
                (x + 3, y + h - 3),
                (x + w - 3, y + 3),
                1
            )

        self.screen.blit(overlay, (0, 0))

        # Mission HUD mini label
        metrics = self.get_mission_metrics()

        label_bg = pygame.Surface((270, 52), pygame.SRCALPHA)
        pygame.draw.rect(
            label_bg,
            (5, 10, 18, 190),
            (0, 0, 270, 52),
            border_radius=10
        )
        pygame.draw.rect(
            label_bg,
            CYAN,
            (0, 0, 270, 52),
            1,
            border_radius=10
        )

        self.screen.blit(label_bg, (20, 82))

        title = self.font_small.render(
            "MISSION: AREA COVERAGE",
            True,
            CYAN
        )
        self.screen.blit(title, (32, 91))

        prog = self.font_small.render(
            f"Verified {metrics['verified_progress'] * 100:.1f}% | Integrity {metrics['integrity']}%",
            True,
            WHITE
        )
        self.screen.blit(prog, (32, 112))

    def draw_mission_page(self, px, py):
        metrics = self.get_mission_metrics()

        verified_progress = metrics["verified_progress"]
        claimed_progress = metrics["claimed_progress"]
        integrity = metrics["integrity"]

        if metrics["mission_success"]:
            status = "SUCCESS"
            status_color = GREEN
        elif verified_progress >= metrics["target"]:
            status = "NEEDS VERIFICATION"
            status_color = YELLOW
        else:
            status = "IN PROGRESS"
            status_color = CYAN

        # Card 1: Mission overview
        self.draw_panel_card(px, py, 360, 160, "MISSION CONTROL", CYAN)
        y = py + 42

        lines = [
            (f"Mission Type: Area Coverage", WHITE),
            (f"Status: {status}", status_color),
            (f"Target Coverage: {metrics['target'] * 100:.0f}%", YELLOW),
            (f"Mission Overlay: {'ON' if self.show_mission_overlay else 'OFF'}", CYAN),
            (f"Total Cells: {metrics['total_cells']}", WHITE),
        ]

        for text, color in lines:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 22

        py += 175

        # Card 2: Coverage bars
        self.draw_panel_card(px, py, 360, 150, "COVERAGE METRICS", GREEN)
        y = py + 45

        self.draw_bar(
            px + 15,
            y,
            330,
            20,
            verified_progress,
            GREEN,
            "Verified Coverage"
        )

        y += 32

        self.draw_bar(
            px + 15,
            y,
            330,
            20,
            claimed_progress,
            ORANGE,
            "Claimed Coverage"
        )

        y += 32

        self.draw_bar(
            px + 15,
            y,
            330,
            20,
            integrity / 100,
            CYAN if integrity >= 75 else RED,
            "Mission Integrity"
        )

        py += 165

        # Card 3: Fake claims
        self.draw_panel_card(px, py, 360, 150, "BYZANTINE MISSION CLAIMS", RED)
        y = py + 42

        recent_fake = self.fake_claim_records[-5:] if hasattr(self, "fake_claim_records") else []

        fake_lines = [
            (f"Claimed Cells: {metrics['claimed']}", ORANGE),
            (f"Verified Cells: {metrics['verified']}", GREEN),
            (f"Unverified/Fake Cells: {metrics['fake_count']}", RED),
            (f"Recent Fake Claims: {len(recent_fake)}", YELLOW),
        ]

        for text, color in fake_lines:
            s = self.font_small.render(text, True, color)
            self.screen.blit(s, (px + 15, y))
            y += 22

        py += 165

        # Card 4: Mission explanation
        self.draw_panel_card(px, py, 360, 160, "MISSION LOGIC", YELLOW)
        y = py + 42

        explanation = [
            "Honest drones verify cells they really visit.",
            "Malicious drones may claim fake coverage.",
            "Verified coverage means physically scanned.",
            "Claimed coverage may include Byzantine lies.",
            "Press M to show/hide mission overlay."
        ]

        for line in explanation:
            s = self.font_small.render(line, True, WHITE)
            self.screen.blit(s, (px + 15, y))
            y += 22

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