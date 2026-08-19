from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_selectable_drone_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_selectable_drone_upgrade.py")
else:
    print("Backup already exists: main_before_selectable_drone_upgrade.py")


# ---------------------------------------------------------
# 1. Add DRONE DETAILS page into panel_pages
# ---------------------------------------------------------

try:
    start = text.index("self.panel_pages = [")
    end = text.index("        ]", start) + len("        ]")
    block = text[start:end]

    if '"DRONE DETAILS"' not in block:
        if '"NETWORK"' in block:
            block = block.replace(
                '"NETWORK"',
                '"DRONE DETAILS",\n            "NETWORK"',
                1
            )
        elif '"GRAPH"' in block:
            block = block.replace(
                '"GRAPH"',
                '"DRONE DETAILS",\n            "GRAPH"',
                1
            )
        else:
            block = block.replace(
                "        ]",
                '            "DRONE DETAILS"\n        ]',
                1
            )

        text = text[:start] + block + text[end:]
        print("Added DRONE DETAILS page.")
    else:
        print("DRONE DETAILS page already exists.")

except ValueError:
    print("ERROR: Could not find panel_pages block.")
    sys.exit(1)


# ---------------------------------------------------------
# 2. Add selected_drone_id variable
# ---------------------------------------------------------

if "self.selected_drone_id" not in text:
    if "self.show_comm_links = True" in text:
        text = text.replace(
            "self.show_comm_links = True",
            "self.show_comm_links = True\n        self.selected_drone_id = 0",
            1
        )
    elif "self.show_large_graph = False" in text:
        text = text.replace(
            "self.show_large_graph = False",
            "self.show_large_graph = False\n        self.selected_drone_id = 0",
            1
        )
    else:
        text = text.replace(
            "self.paused = False",
            "self.paused = False\n        self.selected_drone_id = 0",
            1
        )

    print("Added selected_drone_id variable.")
else:
    print("selected_drone_id already exists.")


# ---------------------------------------------------------
# 3. Add mouse click handling
# ---------------------------------------------------------

if "self.select_drone_at_position" not in text:
    target = "            if event.type == pygame.KEYDOWN:"
    replacement = """            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.select_drone_at_position(event.pos)

            if event.type == pygame.KEYDOWN:"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added mouse click drone selection.")
    else:
        print("WARNING: Could not find KEYDOWN block.")
else:
    print("Mouse click selection already exists.")


# ---------------------------------------------------------
# 4. Add N key for next drone
# ---------------------------------------------------------

if "pygame.K_n" not in text:
    target = """if event.key == pygame.K_c:
                    self.show_comm_links = not self.show_comm_links"""

    replacement = """if event.key == pygame.K_c:
                    self.show_comm_links = not self.show_comm_links

                if event.key == pygame.K_n:
                    self.selected_drone_id = (self.selected_drone_id + 1) % len(self.swarm.drones)
                    if "DRONE DETAILS" in self.panel_pages:
                        self.panel_page = self.panel_pages.index("DRONE DETAILS")"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added N key for next drone.")
    else:
        print("WARNING: Could not find C key block. Trying TAB block.")

        target2 = """if event.key == pygame.K_TAB:
                    self.panel_page = (self.panel_page + 1) % len(self.panel_pages)"""

        replacement2 = """if event.key == pygame.K_TAB:
                    self.panel_page = (self.panel_page + 1) % len(self.panel_pages)

                if event.key == pygame.K_n:
                    self.selected_drone_id = (self.selected_drone_id + 1) % len(self.swarm.drones)
                    if "DRONE DETAILS" in self.panel_pages:
                        self.panel_page = self.panel_pages.index("DRONE DETAILS")"""

        if target2 in text:
            text = text.replace(target2, replacement2, 1)
            print("Added N key after TAB block.")
        else:
            print("WARNING: Could not add N key.")
else:
    print("N key already exists.")


# ---------------------------------------------------------
# 5. Update control hints
# ---------------------------------------------------------

text = text.replace(
    "SPACE Pause   R Reset   T Fake Position   C Comms   TAB Panel   G Graph",
    "SPACE Pause   R Reset   T Fake Position   C Comms   N Next Drone   TAB Panel   G Graph"
)

text = text.replace(
    "SPACE=Pause  R=Reset  T=Fake Pos  C=Comms  TAB=Panel  G=Graph",
    "SPACE=Pause  R=Reset  T=Fake Pos  C=Comms  N=Next  TAB=Panel  G=Graph"
)

text = text.replace(
    "C = Comms   |   TAB = Switch Page   |   G = Full Graph   |   ESC = Quit",
    "Click Drone / N = Select   |   C = Comms   |   TAB = Page   |   G = Graph   |   ESC = Quit"
)

print("Updated control hints.")


# ---------------------------------------------------------
# 6. Draw selected drone marker after drones
# ---------------------------------------------------------

if "self.draw_selected_drone_marker()" not in text:
    target = """        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)"""

    replacement = """        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)

        # Draw selected drone marker
        self.draw_selected_drone_marker()"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added selected drone marker drawing.")
    else:
        print("WARNING: Could not find drone drawing block.")
else:
    print("Selected marker drawing already exists.")


# ---------------------------------------------------------
# 7. Add DRONE DETAILS branch in page switching logic
# ---------------------------------------------------------

if "self.draw_drone_details_page(px, py)" not in text:
    target = """elif page_name == "NETWORK":
            self.draw_network_page(px, py)"""

    replacement = """elif page_name == "DRONE DETAILS":
            self.draw_drone_details_page(px, py)
        elif page_name == "NETWORK":
            self.draw_network_page(px, py)"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added DRONE DETAILS page branch.")
    else:
        print("WARNING: Could not find NETWORK branch.")
else:
    print("Drone details page branch already exists.")


# ---------------------------------------------------------
# 8. Add selectable drone helper methods
# ---------------------------------------------------------

details_code = '''    def get_selected_drone(self):
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

'''

if "def draw_drone_details_page" not in text:
    try:
        insert_before = text.index("    def draw_section_title")
        text = text[:insert_before] + details_code + text[insert_before:]
        print("Added selectable drone details methods.")
    except ValueError:
        print("ERROR: Could not find insertion point before draw_section_title.")
        sys.exit(1)
else:
    print("Drone details methods already exist.")


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("SELECTABLE DRONE DETAILS UPGRADE COMPLETE.")
print("Now run: python main.py")
print("Controls:")
print("Click a drone = select it")
print("N = next drone")
print("TAB = switch pages")