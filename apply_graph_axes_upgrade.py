from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_graph_axes_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_graph_axes_upgrade.py")
else:
    print("Backup already exists: main_before_graph_axes_upgrade.py")


new_detection_graph = '''    def draw_detection_graph(self, x, y, gw, gh):
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

'''


try:
    start = text.index("    def draw_detection_graph")
    end = text.index("    def draw_large_graph_overlay", start)
    text = text[:start] + new_detection_graph + text[end:]
    print("Updated draw_detection_graph() with axes and improved labels.")
except ValueError:
    print("ERROR: Could not replace draw_detection_graph().")
    sys.exit(1)


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("GRAPH AXES UPGRADE COMPLETE.")
print("Now run: python main.py")
print("Check the GRAPH page and press G for the large graph.")