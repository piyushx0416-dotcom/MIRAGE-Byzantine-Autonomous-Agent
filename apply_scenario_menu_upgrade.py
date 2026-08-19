from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_scenario_menu_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_scenario_menu_upgrade.py")
else:
    print("Backup already exists: main_before_scenario_menu_upgrade.py")


# ---------------------------------------------------------
# 1. Add scenario variables
# ---------------------------------------------------------

if "self.scenario_menu_active" not in text:
    target = "self.paused = False"

    replacement = """self.paused = False

        # Scenario selection system
        self.scenario_menu_active = True
        self.selected_scenario_index = 0
        self.current_scenario = "Basic Position Lie Attack"
        self.scenarios = self.get_scenario_list()"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added scenario variables.")
    else:
        print("WARNING: Could not find self.paused = False.")
else:
    print("Scenario variables already exist.")


# ---------------------------------------------------------
# 2. Stop update while scenario menu is active
# ---------------------------------------------------------

if "scenario_menu_active" in text and "return  # scenario menu pause" not in text:
    target = "self.frame += 1"

    replacement = """if getattr(self, "scenario_menu_active", False):
            return  # scenario menu pause

        self.frame += 1"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added update pause during scenario menu.")
    else:
        print("WARNING: Could not find self.frame += 1.")
else:
    print("Update pause already exists or scenario variable missing.")


# ---------------------------------------------------------
# 3. Add scenario menu key handling
# ---------------------------------------------------------

if "self.apply_selected_scenario()" not in text:
    target = "            if event.type == pygame.KEYDOWN:"

    replacement = """            if event.type == pygame.KEYDOWN:
                # Scenario menu controls
                if getattr(self, "scenario_menu_active", False):
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.selected_scenario_index = (
                            self.selected_scenario_index - 1
                        ) % len(self.scenarios)

                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.selected_scenario_index = (
                            self.selected_scenario_index + 1
                        ) % len(self.scenarios)

                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.apply_selected_scenario()
                        self.scenario_menu_active = False

                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    continue"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added scenario menu key controls.")
    else:
        print("WARNING: Could not find KEYDOWN block.")
else:
    print("Scenario menu key controls already exist.")


# ---------------------------------------------------------
# 4. Add S key to open scenario menu during simulation
# ---------------------------------------------------------

if "Open scenario menu" not in text:
    target = """if event.key == pygame.K_TAB:
                    self.panel_page = (self.panel_page + 1) % len(self.panel_pages)"""

    replacement = """if event.key == pygame.K_TAB:
                    self.panel_page = (self.panel_page + 1) % len(self.panel_pages)

                # S = Open scenario menu
                if event.key == pygame.K_s:
                    self.scenario_menu_active = True
                    self.paused = True"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added S key to open scenario menu.")
    else:
        print("WARNING: Could not add S key.")
else:
    print("S key scenario menu already exists.")


# ---------------------------------------------------------
# 5. Draw scenario menu before normal simulation
# ---------------------------------------------------------

if "self.draw_scenario_menu()" not in text:
    target = """        # Draw simulation panel
        self.draw_simulation_panel()"""

    replacement = """        # Scenario selection menu
        if getattr(self, "scenario_menu_active", False):
            self.draw_scenario_menu()
            pygame.display.flip()
            return

        # Draw simulation panel
        self.draw_simulation_panel()"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added scenario menu drawing.")
    else:
        print("WARNING: Could not add scenario menu drawing.")
else:
    print("Scenario menu drawing already exists.")


# ---------------------------------------------------------
# 6. Update control hints
# ---------------------------------------------------------

text = text.replace(
    "C Comms   M Mission   Q Quarantine   N Next Drone   TAB Panel   G Graph",
    "S Scenario   C Comms   M Mission   Q Quarantine   N Next Drone   TAB Panel   G Graph"
)

text = text.replace(
    "C=Comms  M=Mission  Q=Quarantine  N=Next  TAB=Panel  G=Graph",
    "S=Scenario  C=Comms  M=Mission  Q=Quarantine  N=Next  TAB=Panel  G=Graph"
)

text = text.replace(
    "Click/N Select | C Comms | M Mission | Q Quarantine | TAB Page | G Graph | ESC Quit",
    "S Scenario | Click/N Select | C Comms | M Mission | Q Quarantine | TAB Page | G Graph | ESC Quit"
)

print("Updated control hints.")


# ---------------------------------------------------------
# 7. Add scenario methods
# ---------------------------------------------------------

scenario_code = '''    def get_scenario_list(self):
        return [
            {
                "name": "Basic Position Lie Attack",
                "total": 20,
                "malicious": 5,
                "description": "Standard Byzantine scenario where malicious drones lie about their positions.",
                "difficulty": "NORMAL",
                "color": CYAN
            },
            {
                "name": "Communication Attack",
                "total": 24,
                "malicious": 6,
                "description": "More drones and more malicious agents. Best for showing suspicious network links.",
                "difficulty": "MEDIUM",
                "color": PURPLE
            },
            {
                "name": "Mission Sabotage Attack",
                "total": 22,
                "malicious": 7,
                "description": "Malicious drones create more fake mission claims and reduce mission integrity.",
                "difficulty": "HARD",
                "color": ORANGE
            },
            {
                "name": "Mixed Byzantine Attack",
                "total": 26,
                "malicious": 8,
                "description": "Position lies, communication risk, trust decay, mission sabotage, and hybrid detection.",
                "difficulty": "VERY HARD",
                "color": RED
            },
            {
                "name": "High Stress Test",
                "total": 35,
                "malicious": 10,
                "description": "Large swarm stress test with many drones and many malicious agents.",
                "difficulty": "EXTREME",
                "color": YELLOW
            }
        ]

    def apply_selected_scenario(self):
        scenario = self.scenarios[self.selected_scenario_index]

        self.current_scenario = scenario["name"]

        total = scenario["total"]
        bad = scenario["malicious"]

        # Recreate swarm for selected scenario
        self.swarm = Swarm(
            total_drones=total,
            malicious_count=bad,
            width=SIM_WIDTH,
            height=HEIGHT
        )

        # Reset detectors
        self.classical = ClassicalByzantineDetector(threshold=60)

        contamination = bad / total
        contamination = max(0.05, min(0.45, contamination))

        self.ml_detector = MLByzantineDetector(
            contamination=contamination
        )

        self.ml_detector.train(self.swarm.drones)

        # Reset detection results
        self.classical_suspected = set()
        self.ml_suspected = set()

        if hasattr(self, "hybrid_suspected"):
            self.hybrid_suspected = set()

        # Reset histories
        self.classical_tp_history = []
        self.ml_tp_history = []
        self.frame_history = []

        # Reset trust system
        if hasattr(self, "trust_scores"):
            self.trust_scores = {
                d.id: 100.0 for d in self.swarm.drones
            }

        if hasattr(self, "suspicion_memory"):
            self.suspicion_memory = {
                d.id: 0.0 for d in self.swarm.drones
            }

        if hasattr(self, "clean_memory"):
            self.clean_memory = {
                d.id: 0 for d in self.swarm.drones
            }

        if hasattr(self, "trust_history"):
            self.trust_history = []

        # Reset quarantine
        if hasattr(self, "quarantined_drones"):
            self.quarantined_drones = set()

        if hasattr(self, "quarantine_zone"):
            self.quarantine_zone = (SIM_WIDTH - 90, HEIGHT - 90)

        # Reset mission
        if hasattr(self, "verified_cells"):
            self.verified_cells = set()

        if hasattr(self, "claimed_cells"):
            self.claimed_cells = set()

        if hasattr(self, "fake_claim_records"):
            self.fake_claim_records = []

        # Scenario-specific tuning
        if hasattr(self, "mission_target"):
            if scenario["name"] == "High Stress Test":
                self.mission_target = 0.80
            elif scenario["name"] == "Mission Sabotage Attack":
                self.mission_target = 0.75
            else:
                self.mission_target = 0.70

        # Reset selected drone
        if hasattr(self, "selected_drone_id"):
            self.selected_drone_id = 0

        # Reset frame
        self.frame = 0
        self.paused = False

        # Default mode
        self.detection_mode = "BOTH"

    def draw_scenario_menu(self):
        self.screen.fill((4, 6, 14))

        # Animated background grid
        for x in range(0, WIDTH, 60):
            pygame.draw.line(
                self.screen,
                (0, 55, 70),
                (x, 0),
                (x, HEIGHT),
                1
            )

        for y in range(0, HEIGHT, 60):
            pygame.draw.line(
                self.screen,
                (0, 55, 70),
                (0, y),
                (WIDTH, y),
                1
            )

        scan_y = (self.frame * 2) % HEIGHT
        pygame.draw.line(
            self.screen,
            CYAN,
            (0, scan_y),
            (WIDTH, scan_y),
            1
        )

        # Main menu card
        box_x = 150
        box_y = 70
        box_w = WIDTH - 300
        box_h = HEIGHT - 140

        glow = pygame.Surface((box_w + 40, box_h + 40), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (0, 255, 255, 35),
            (0, 0, box_w + 40, box_h + 40),
            border_radius=22
        )
        self.screen.blit(glow, (box_x - 20, box_y - 20))

        pygame.draw.rect(
            self.screen,
            (12, 16, 28),
            (box_x, box_y, box_w, box_h),
            border_radius=18
        )

        pygame.draw.rect(
            self.screen,
            CYAN,
            (box_x, box_y, box_w, box_h),
            2,
            border_radius=18
        )

        # Title
        title = self.font_large.render(
            "MIRAGE SCENARIO SELECTION",
            True,
            CYAN
        )
        self.screen.blit(title, (box_x + 35, box_y + 25))

        subtitle = self.font_small.render(
            "Choose an adversarial drone-swarm environment to simulate.",
            True,
            WHITE
        )
        self.screen.blit(subtitle, (box_x + 35, box_y + 55))

        # Scenario options
        start_y = box_y + 105
        option_h = 78

        for i, scenario in enumerate(self.scenarios):
            y = start_y + i * option_h
            selected = i == self.selected_scenario_index
            color = scenario["color"]

            if selected:
                pygame.draw.rect(
                    self.screen,
                    (22, 32, 48),
                    (box_x + 35, y, box_w - 70, option_h - 12),
                    border_radius=12
                )

                pygame.draw.rect(
                    self.screen,
                    color,
                    (box_x + 35, y, box_w - 70, option_h - 12),
                    2,
                    border_radius=12
                )

                pointer = self.font_med.render(
                    "▶",
                    True,
                    color
                )
                self.screen.blit(pointer, (box_x + 48, y + 22))

            else:
                pygame.draw.rect(
                    self.screen,
                    (16, 20, 34),
                    (box_x + 35, y, box_w - 70, option_h - 12),
                    border_radius=12
                )

                pygame.draw.rect(
                    self.screen,
                    (45, 55, 75),
                    (box_x + 35, y, box_w - 70, option_h - 12),
                    1,
                    border_radius=12
                )

            name_text = self.font_med.render(
                scenario["name"],
                True,
                color if selected else WHITE
            )
            self.screen.blit(name_text, (box_x + 80, y + 10))

            desc_text = self.font_small.render(
                scenario["description"],
                True,
                WHITE
            )
            self.screen.blit(desc_text, (box_x + 80, y + 34))

            meta_text = self.font_small.render(
                f"Drones: {scenario['total']}   Malicious: {scenario['malicious']}   Difficulty: {scenario['difficulty']}",
                True,
                YELLOW
            )
            self.screen.blit(meta_text, (box_x + 80, y + 52))

        # Controls footer
        footer_y = box_y + box_h - 55

        pygame.draw.rect(
            self.screen,
            (18, 23, 38),
            (box_x + 35, footer_y, box_w - 70, 34),
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            YELLOW,
            (box_x + 35, footer_y, box_w - 70, 34),
            1,
            border_radius=10
        )

        controls = self.font_small.render(
            "UP/DOWN or W/S = Choose Scenario     ENTER/SPACE = Start     ESC = Quit",
            True,
            YELLOW
        )
        self.screen.blit(controls, (box_x + 55, footer_y + 9))

'''

if "def get_scenario_list" not in text:
    try:
        insert_before = text.index("    def draw_section_title")
        text = text[:insert_before] + scenario_code + text[insert_before:]
        print("Added scenario menu methods.")
    except ValueError:
        print("ERROR: Could not find insertion point before draw_section_title.")
        sys.exit(1)
else:
    print("Scenario methods already exist.")


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("SCENARIO MENU UPGRADE COMPLETE.")
print("Now run: python main.py")
print("Controls:")
print("UP/DOWN or W/S = choose scenario")
print("ENTER/SPACE = start scenario")
print("S = open scenario menu during simulation")