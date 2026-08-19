from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_futuristic_visual_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_futuristic_visual_upgrade.py")
else:
    print("Backup already exists: main_before_futuristic_visual_upgrade.py")


# ---------------------------------------------------------
# 1. Replace simulation panel with futuristic cyber HUD
# ---------------------------------------------------------

new_simulation_panel = '''    def draw_simulation_panel(self):
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

'''


try:
    start = text.index("    def draw_simulation_panel(self):")
    end = text.index("    def draw_drone", start)
    text = text[:start] + new_simulation_panel + text[end:]
    print("Updated draw_simulation_panel() with futuristic HUD background.")
except ValueError:
    print("ERROR: Could not replace draw_simulation_panel().")
    sys.exit(1)


# ---------------------------------------------------------
# 2. Replace draw_status_chip with more futuristic version
# ---------------------------------------------------------

new_status_chip = '''    def draw_status_chip(self, x, y, text, color):
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

'''


try:
    start = text.index("    def draw_status_chip")
    end = text.index("    def draw_panel_card", start)
    text = text[:start] + new_status_chip + text[end:]
    print("Updated draw_status_chip().")
except ValueError:
    print("WARNING: Could not replace draw_status_chip(). Skipping.")


# ---------------------------------------------------------
# 3. Replace draw_panel_card with stronger futuristic cards
# ---------------------------------------------------------

new_panel_card = '''    def draw_panel_card(self, x, y, w, h, title, color=CYAN):
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

'''


try:
    start = text.index("    def draw_panel_card")
    end = text.index("    def draw_overview_page", start)
    text = text[:start] + new_panel_card + text[end:]
    print("Updated draw_panel_card() with futuristic card design.")
except ValueError:
    print("ERROR: Could not replace draw_panel_card().")
    sys.exit(1)


# ---------------------------------------------------------
# 4. Replace draw_detection_graph with futuristic graph
# ---------------------------------------------------------

new_detection_graph = '''    def draw_detection_graph(self, x, y, gw, gh):
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

'''


try:
    start = text.index("    def draw_detection_graph")
    end = text.index("    def draw_large_graph_overlay", start)
    text = text[:start] + new_detection_graph + text[end:]
    print("Updated draw_detection_graph() with futuristic graph style.")
except ValueError:
    print("ERROR: Could not replace draw_detection_graph().")
    sys.exit(1)


# ---------------------------------------------------------
# 5. Replace large graph overlay with command center style
# ---------------------------------------------------------

new_large_graph_overlay = '''    def draw_large_graph_overlay(self):
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

'''


try:
    start = text.index("    def draw_large_graph_overlay")
    end = text.index("    def draw_section_title", start)
    text = text[:start] + new_large_graph_overlay + text[end:]
    print("Updated draw_large_graph_overlay().")
except ValueError:
    print("WARNING: Could not replace draw_large_graph_overlay(). Skipping.")


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("FUTURISTIC VISUAL UPGRADE COMPLETE.")
print("Now run: python main.py")
print("Check: cyber grid, glowing cards, improved graph, and futuristic HUD.")