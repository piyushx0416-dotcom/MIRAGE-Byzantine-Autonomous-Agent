from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_mission_system_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_mission_system_upgrade.py")
else:
    print("Backup already exists: main_before_mission_system_upgrade.py")


# ---------------------------------------------------------
# 1. Add MISSION page
# ---------------------------------------------------------

try:
    start = text.index("self.panel_pages = [")
    end = text.index("        ]", start) + len("        ]")
    block = text[start:end]

    if '"MISSION"' not in block:
        if '"HYBRID DEFENSE"' in block:
            block = block.replace(
                '"HYBRID DEFENSE"',
                '"HYBRID DEFENSE",\n            "MISSION"',
                1
            )
        elif '"QUARANTINE"' in block:
            block = block.replace(
                '"QUARANTINE"',
                '"MISSION",\n            "QUARANTINE"',
                1
            )
        elif '"NETWORK"' in block:
            block = block.replace(
                '"NETWORK"',
                '"MISSION",\n            "NETWORK"',
                1
            )
        else:
            block = block.replace(
                "        ]",
                '            "MISSION"\n        ]',
                1
            )

        text = text[:start] + block + text[end:]
        print("Added MISSION page.")
    else:
        print("MISSION page already exists.")

except ValueError:
    print("ERROR: Could not find panel_pages block.")
    sys.exit(1)


# ---------------------------------------------------------
# 2. Add mission variables
# ---------------------------------------------------------

if "self.mission_cols" not in text:
    # Add after quarantine variables if possible
    target = "self.quarantine_zone = (SIM_WIDTH - 90, HEIGHT - 90)"

    mission_vars = """self.quarantine_zone = (SIM_WIDTH - 90, HEIGHT - 90)

        # Mission system: area coverage/scanning
        self.mission_enabled = True
        self.show_mission_overlay = True
        self.mission_cols = 16
        self.mission_rows = 12
        self.mission_target = 0.70
        self.verified_cells = set()
        self.claimed_cells = set()
        self.fake_claim_records = []"""

    if target in text:
        text = text.replace(target, mission_vars, 1)
        print("Added mission variables after quarantine variables.")
    else:
        # fallback after selected drone variable
        target2 = "self.selected_drone_id = 0"

        mission_vars2 = """self.selected_drone_id = 0

        # Mission system: area coverage/scanning
        self.mission_enabled = True
        self.show_mission_overlay = True
        self.mission_cols = 16
        self.mission_rows = 12
        self.mission_target = 0.70
        self.verified_cells = set()
        self.claimed_cells = set()
        self.fake_claim_records = []"""

        if target2 in text:
            text = text.replace(target2, mission_vars2, 1)
            print("Added mission variables after selected_drone_id.")
        else:
            target3 = "self.paused = False"

            mission_vars3 = """self.paused = False

        # Mission system: area coverage/scanning
        self.mission_enabled = True
        self.show_mission_overlay = True
        self.mission_cols = 16
        self.mission_rows = 12
        self.mission_target = 0.70
        self.verified_cells = set()
        self.claimed_cells = set()
        self.fake_claim_records = []"""

            if target3 in text:
                text = text.replace(target3, mission_vars3, 1)
                print("Added mission variables after paused.")
            else:
                print("WARNING: Could not add mission variables.")
else:
    print("Mission variables already exist.")


# ---------------------------------------------------------
# 3. Add M key control
# ---------------------------------------------------------

if "pygame.K_m" not in text:
    target = '''if event.key == pygame.K_q:
                    self.quarantine_enabled = not self.quarantine_enabled'''

    replacement = '''if event.key == pygame.K_q:
                    self.quarantine_enabled = not self.quarantine_enabled

                # M = Toggle mission overlay
                if event.key == pygame.K_m:
                    self.show_mission_overlay = not self.show_mission_overlay'''

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added M key after Q key.")
    else:
        target2 = '''if event.key == pygame.K_c:
                    self.show_comm_links = not self.show_comm_links'''

        replacement2 = '''if event.key == pygame.K_c:
                    self.show_comm_links = not self.show_comm_links

                # M = Toggle mission overlay
                if event.key == pygame.K_m:
                    self.show_mission_overlay = not self.show_mission_overlay'''

        if target2 in text:
            text = text.replace(target2, replacement2, 1)
            print("Added M key after C key.")
        else:
            print("WARNING: Could not add M key.")
else:
    print("M key already exists.")


# ---------------------------------------------------------
# 4. Update control hints
# ---------------------------------------------------------

text = text.replace(
    "C Comms   Q Quarantine   N Next Drone   TAB Panel   G Graph",
    "C Comms   M Mission   Q Quarantine   N Next Drone   TAB Panel   G Graph"
)

text = text.replace(
    "C=Comms  Q=Quarantine  N=Next  TAB=Panel  G=Graph",
    "C=Comms  M=Mission  Q=Quarantine  N=Next  TAB=Panel  G=Graph"
)

text = text.replace(
    "Click/N = Select | C = Comms | Q = Quarantine | TAB = Page | G = Graph | ESC = Quit",
    "Click/N Select | C Comms | M Mission | Q Quarantine | TAB Page | G Graph | ESC Quit"
)

print("Updated control hints.")


# ---------------------------------------------------------
# 5. Update mission system every frame
# ---------------------------------------------------------

if "self.update_mission_system()" not in text:
    # Insert after swarm.update() block
    target = "self.swarm.update()"

    replacement = """self.swarm.update()

        # Update mission coverage/scanning
        if hasattr(self, "update_mission_system"):
            self.update_mission_system()"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added mission update after swarm.update().")
    else:
        print("WARNING: Could not find self.swarm.update().")
else:
    print("Mission update already exists.")


# ---------------------------------------------------------
# 6. Draw mission overlay in simulation area
# ---------------------------------------------------------

if "self.draw_mission_overlay()" not in text:
    target = """        # Draw quarantine isolation zone
        if hasattr(self, "draw_quarantine_zone"):
            self.draw_quarantine_zone()"""

    replacement = """        # Draw mission overlay
        if hasattr(self, "draw_mission_overlay") and self.show_mission_overlay:
            self.draw_mission_overlay()

        # Draw quarantine isolation zone
        if hasattr(self, "draw_quarantine_zone"):
            self.draw_quarantine_zone()"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added mission overlay before quarantine zone.")
    else:
        target2 = """        # Draw communication links before drones
        if self.show_comm_links:
            self.draw_communication_links()"""

        replacement2 = """        # Draw mission overlay
        if hasattr(self, "draw_mission_overlay") and self.show_mission_overlay:
            self.draw_mission_overlay()

        # Draw communication links before drones
        if self.show_comm_links:
            self.draw_communication_links()"""

        if target2 in text:
            text = text.replace(target2, replacement2, 1)
            print("Added mission overlay before communication links.")
        else:
            target3 = """        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)"""

            replacement3 = """        # Draw mission overlay
        if hasattr(self, "draw_mission_overlay") and self.show_mission_overlay:
            self.draw_mission_overlay()

        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)"""

            if target3 in text:
                text = text.replace(target3, replacement3, 1)
                print("Added mission overlay before drones.")
            else:
                print("WARNING: Could not add mission overlay drawing.")
else:
    print("Mission overlay already exists.")


# ---------------------------------------------------------
# 7. Add MISSION page branch
# ---------------------------------------------------------

if "self.draw_mission_page(px, py)" not in text:
    target = '''elif page_name == "QUARANTINE":
            self.draw_quarantine_page(px, py)'''

    replacement = '''elif page_name == "MISSION":
            self.draw_mission_page(px, py)
        elif page_name == "QUARANTINE":
            self.draw_quarantine_page(px, py)'''

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added MISSION page branch before QUARANTINE.")
    else:
        target2 = '''elif page_name == "NETWORK":
            self.draw_network_page(px, py)'''

        replacement2 = '''elif page_name == "MISSION":
            self.draw_mission_page(px, py)
        elif page_name == "NETWORK":
            self.draw_network_page(px, py)'''

        if target2 in text:
            text = text.replace(target2, replacement2, 1)
            print("Added MISSION page branch before NETWORK.")
        else:
            target3 = '''elif page_name == "GRAPH":
            self.draw_graph_page(px, py)'''

            replacement3 = '''elif page_name == "MISSION":
            self.draw_mission_page(px, py)
        elif page_name == "GRAPH":
            self.draw_graph_page(px, py)'''

            if target3 in text:
                text = text.replace(target3, replacement3, 1)
                print("Added MISSION page branch before GRAPH.")
            else:
                print("WARNING: Could not add mission page branch.")
else:
    print("Mission page branch already exists.")


# ---------------------------------------------------------
# 8. Add mission methods
# ---------------------------------------------------------

mission_code = '''    def get_mission_cell(self, x, y):
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

'''

if "def update_mission_system" not in text:
    try:
        insert_before = text.index("    def draw_section_title")
        text = text[:insert_before] + mission_code + text[insert_before:]
        print("Added mission system methods.")
    except ValueError:
        print("ERROR: Could not find insertion point before draw_section_title.")
        sys.exit(1)
else:
    print("Mission methods already exist.")


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("MISSION SYSTEM UPGRADE COMPLETE.")
print("Now run: python main.py")
print("Controls:")
print("M = show/hide mission overlay")
print("TAB = switch pages until MISSION")