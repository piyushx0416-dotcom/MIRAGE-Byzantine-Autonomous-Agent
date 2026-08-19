from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_3d_panel_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_3d_panel_upgrade.py")
else:
    print("Backup already exists: main_before_3d_panel_upgrade.py")

# ---------------------------------------------------------
# New futuristic draw_info_panel()
# ---------------------------------------------------------

new_info_panel = '''    def draw_info_panel(self):
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

'''

try:
    start = text.index("    def draw_info_panel(self):")
    end = text.index("    def draw_panel_card", start)
    text = text[:start] + new_info_panel + text[end:]
    print("Updated draw_info_panel() with futuristic header.")
except ValueError:
    print("ERROR: Could not replace draw_info_panel().")
    sys.exit(1)

# ---------------------------------------------------------
# Replace draw_panel_card and add helper methods before overview page
# ---------------------------------------------------------

new_card_helpers = '''    def get_system_health_score(self):
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

'''

try:
    start = text.index("    def draw_panel_card")
    end = text.index("    def draw_overview_page", start)
    text = text[:start] + new_card_helpers + text[end:]
    print("Updated panel cards and added system health helpers.")
except ValueError:
    print("ERROR: Could not replace draw_panel_card().")
    sys.exit(1)

# ---------------------------------------------------------
# Replace draw_bar() with 3D-style progress bars
# ---------------------------------------------------------

new_draw_bar = '''    def draw_bar(self, x, y, w, h, ratio, color, label):
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

'''

try:
    start = text.index("    def draw_bar")
    end = text.index("    def draw_mini_graph", start)
    text = text[:start] + new_draw_bar + text[end:]
    print("Updated draw_bar() with 3D-style progress bars.")
except ValueError:
    print("WARNING: Could not replace draw_bar(). Skipping bar upgrade.")

MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("3D PANEL UPGRADE COMPLETE.")
print("Now run: python main.py")
print("You should see a more futuristic detection panel.")