from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_quarantine_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_quarantine_upgrade.py")
else:
    print("Backup already exists: main_before_quarantine_upgrade.py")


# ---------------------------------------------------------
# 1. Add QUARANTINE page
# ---------------------------------------------------------

try:
    start = text.index("self.panel_pages = [")
    end = text.index("        ]", start) + len("        ]")
    block = text[start:end]

    if '"QUARANTINE"' not in block:
        if '"HYBRID DEFENSE"' in block:
            block = block.replace(
                '"HYBRID DEFENSE"',
                '"HYBRID DEFENSE",\n            "QUARANTINE"',
                1
            )
        elif '"NETWORK"' in block:
            block = block.replace(
                '"NETWORK"',
                '"QUARANTINE",\n            "NETWORK"',
                1
            )
        else:
            block = block.replace(
                "        ]",
                '            "QUARANTINE"\n        ]',
                1
            )

        text = text[:start] + block + text[end:]
        print("Added QUARANTINE page.")
    else:
        print("QUARANTINE page already exists.")

except ValueError:
    print("ERROR: Could not find panel_pages block.")
    sys.exit(1)


# ---------------------------------------------------------
# 2. Add quarantine variables
# ---------------------------------------------------------

if "self.quarantined_drones" not in text:
    target = "self.hybrid_suspected = set()"

    replacement = """self.hybrid_suspected = set()
        self.quarantined_drones = set()
        self.quarantine_enabled = True
        self.quarantine_zone = (SIM_WIDTH - 90, HEIGHT - 90)"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added quarantine variables after hybrid_suspected.")
    else:
        target2 = "self.ml_suspected = set()"
        replacement2 = """self.ml_suspected = set()
        self.quarantined_drones = set()
        self.quarantine_enabled = True
        self.quarantine_zone = (SIM_WIDTH - 90, HEIGHT - 90)"""

        if target2 in text:
            text = text.replace(target2, replacement2, 1)
            print("Added quarantine variables after ml_suspected.")
        else:
            print("WARNING: Could not find detection variable block.")
else:
    print("Quarantine variables already exist.")


# ---------------------------------------------------------
# 3. Add Q key control
# ---------------------------------------------------------

if "pygame.K_q" not in text:
    target = '''if event.key == pygame.K_4:
                    self.detection_mode = "HYBRID"'''

    replacement = '''if event.key == pygame.K_4:
                    self.detection_mode = "HYBRID"

                # Q = Toggle quarantine system
                if event.key == pygame.K_q:
                    self.quarantine_enabled = not self.quarantine_enabled'''

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added Q key after key 4.")
    else:
        target2 = '''if event.key == pygame.K_c:
                    self.show_comm_links = not self.show_comm_links'''

        replacement2 = '''if event.key == pygame.K_c:
                    self.show_comm_links = not self.show_comm_links

                # Q = Toggle quarantine system
                if event.key == pygame.K_q:
                    self.quarantine_enabled = not self.quarantine_enabled'''

        if target2 in text:
            text = text.replace(target2, replacement2, 1)
            print("Added Q key after C key.")
        else:
            print("WARNING: Could not add Q key.")
else:
    print("Q key already exists.")


# ---------------------------------------------------------
# 4. Update control hints
# ---------------------------------------------------------

text = text.replace(
    "C Comms   N Next Drone   TAB Panel   G Graph",
    "C Comms   Q Quarantine   N Next Drone   TAB Panel   G Graph"
)

text = text.replace(
    "C=Comms  N=Next  TAB=Panel  G=Graph",
    "C=Comms  Q=Quarantine  N=Next  TAB=Panel  G=Graph"
)

text = text.replace(
    "Click Drone / N = Select   |   C = Comms   |   TAB = Page   |   G = Graph   |   ESC = Quit",
    "Click/N = Select | C = Comms | Q = Quarantine | TAB = Page | G = Graph | ESC = Quit"
)

print("Updated control hints.")


# ---------------------------------------------------------
# 5. Add quarantine update after hybrid calculation
# ---------------------------------------------------------

if "self.update_quarantine_status()" not in text:
    target = "self.hybrid_suspected = self.compute_hybrid_suspects()"

    replacement = """self.hybrid_suspected = self.compute_hybrid_suspects()

            # Update quarantine status
            self.update_quarantine_status()"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added update_quarantine_status() after hybrid update.")
    else:
        print("WARNING: Could not find hybrid update call.")
else:
    print("Quarantine status update already exists.")


# ---------------------------------------------------------
# 6. Apply quarantine movement every frame
# ---------------------------------------------------------

if "self.update_quarantine_motion()" not in text:
    target = "self.swarm.update()"

    replacement = """self.swarm.update()

        # Move quarantined drones toward isolation zone
        if hasattr(self, "update_quarantine_motion"):
            self.update_quarantine_motion()"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added quarantine motion update.")
    else:
        print("WARNING: Could not find swarm.update().")
else:
    print("Quarantine motion update already exists.")


# ---------------------------------------------------------
# 7. Draw quarantine zone before drones
# ---------------------------------------------------------

if "self.draw_quarantine_zone()" not in text:
    target = """        # Draw communication links before drones
        if self.show_comm_links:
            self.draw_communication_links()"""

    replacement = """        # Draw quarantine isolation zone
        if hasattr(self, "draw_quarantine_zone"):
            self.draw_quarantine_zone()

        # Draw communication links before drones
        if self.show_comm_links:
            self.draw_communication_links()"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added quarantine zone drawing.")
    else:
        target2 = """        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)"""

        replacement2 = """        # Draw quarantine isolation zone
        if hasattr(self, "draw_quarantine_zone"):
            self.draw_quarantine_zone()

        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)"""

        if target2 in text:
            text = text.replace(target2, replacement2, 1)
            print("Added quarantine zone before drones.")
        else:
            print("WARNING: Could not add quarantine zone drawing.")
else:
    print("Quarantine zone drawing already exists.")


# ---------------------------------------------------------
# 8. Draw quarantine markers after selected marker
# ---------------------------------------------------------

if "self.draw_quarantine_markers()" not in text:
    target = "self.draw_selected_drone_marker()"

    replacement = """self.draw_selected_drone_marker()

        # Draw quarantine markers
        if hasattr(self, "draw_quarantine_markers"):
            self.draw_quarantine_markers()"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added quarantine markers drawing.")
    else:
        print("WARNING: Could not find selected marker drawing.")
else:
    print("Quarantine markers already exist.")


# ---------------------------------------------------------
# 9. Add QUARANTINE page branch
# ---------------------------------------------------------

if "self.draw_quarantine_page(px, py)" not in text:
    target = '''elif page_name == "NETWORK":
            self.draw_network_page(px, py)'''

    replacement = '''elif page_name == "QUARANTINE":
            self.draw_quarantine_page(px, py)
        elif page_name == "NETWORK":
            self.draw_network_page(px, py)'''

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added QUARANTINE page branch.")
    else:
        target2 = '''elif page_name == "GRAPH":
            self.draw_graph_page(px, py)'''

        replacement2 = '''elif page_name == "QUARANTINE":
            self.draw_quarantine_page(px, py)
        elif page_name == "GRAPH":
            self.draw_graph_page(px, py)'''

        if target2 in text:
            text = text.replace(target2, replacement2, 1)
            print("Added QUARANTINE page branch before GRAPH.")
        else:
            print("WARNING: Could not add quarantine page branch.")
else:
    print("Quarantine page branch already exists.")


# ---------------------------------------------------------
# 10. Skip quarantined drones in communication network
# ---------------------------------------------------------

if "Skip quarantined drones from normal communication" not in text:
    target = """                a = drones[i]
                b = drones[j]

                dist = np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)"""

    replacement = """                a = drones[i]
                b = drones[j]

                # Skip quarantined drones from normal communication
                if hasattr(self, "quarantined_drones"):
                    if a.id in self.quarantined_drones or b.id in self.quarantined_drones:
                        continue

                dist = np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Quarantined drones removed from communication links.")
    else:
        print("WARNING: Could not modify get_communication_links().")
else:
    print("Communication quarantine skip already exists.")


# ---------------------------------------------------------
# 11. Add quarantine methods
# ---------------------------------------------------------

quarantine_code = '''    def get_drone_by_id(self, drone_id):
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

'''

if "def update_quarantine_status" not in text:
    try:
        insert_before = text.index("    def draw_section_title")
        text = text[:insert_before] + quarantine_code + text[insert_before:]
        print("Added quarantine methods.")
    except ValueError:
        print("ERROR: Could not find insertion point before draw_section_title.")
        sys.exit(1)
else:
    print("Quarantine methods already exist.")


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("QUARANTINE UPGRADE COMPLETE.")
print("Now run: python main.py")
print("Controls:")
print("Q = enable/disable quarantine")
print("TAB = switch pages until QUARANTINE")