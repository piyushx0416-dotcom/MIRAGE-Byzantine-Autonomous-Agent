from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_3d_drone_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_3d_drone_upgrade.py")
else:
    print("Backup already exists: main_before_3d_drone_upgrade.py")

new_draw_drone = '''    def draw_drone(self, drone):
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

'''

try:
    start = text.index("    def draw_drone(self, drone):")
    end = text.index("    def draw_info_panel", start)
    text = text[:start] + new_draw_drone + "\\n" + text[end:]
    print("Replaced draw_drone() with 3D quadcopter-style drone drawing.")
except ValueError:
    print("ERROR: Could not find draw_drone() or draw_info_panel().")
    print("Make sure your main.py has both functions.")
    sys.exit(1)

MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("3D DRONE UPGRADE COMPLETE.")
print("Now run: python main.py")
print("You should see quadcopter-style drones with shadows, rotors, and detection glow.")