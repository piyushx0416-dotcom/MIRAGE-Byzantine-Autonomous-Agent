from pathlib import Path
import sys

MAIN_FILE = Path("main.py")

if not MAIN_FILE.exists():
    print("ERROR: main.py not found. Run this script in the same folder as main.py")
    sys.exit(1)

text = MAIN_FILE.read_text(encoding="utf-8")

backup_file = Path("main_before_communication_upgrade.py")
if not backup_file.exists():
    backup_file.write_text(text, encoding="utf-8")
    print("Backup created: main_before_communication_upgrade.py")
else:
    print("Backup already exists: main_before_communication_upgrade.py")


# ---------------------------------------------------------
# 1. Add NETWORK page into panel_pages
# ---------------------------------------------------------

try:
    start = text.index("self.panel_pages = [")
    end = text.index("        ]", start) + len("        ]")
    block = text[start:end]

    if '"NETWORK"' not in block:
        if '"GRAPH"' in block:
            block = block.replace(
                '"GRAPH"',
                '"NETWORK",\n            "GRAPH"',
                1
            )
        else:
            block = block.replace(
                "        ]",
                '            "NETWORK"\n        ]',
                1
            )

        text = text[:start] + block + text[end:]
        print("Added NETWORK page.")
    else:
        print("NETWORK page already exists.")

except ValueError:
    print("ERROR: Could not find panel_pages block.")
    sys.exit(1)


# ---------------------------------------------------------
# 2. Add show_comm_links variable
# ---------------------------------------------------------

if "self.show_comm_links" not in text:
    if "self.show_large_graph = False" in text:
        text = text.replace(
            "self.show_large_graph = False",
            "self.show_large_graph = False\n        self.show_comm_links = True",
            1
        )
        print("Added self.show_comm_links variable.")
    else:
        text = text.replace(
            "self.paused = False",
            "self.paused = False\n        self.show_comm_links = True",
            1
        )
        print("Added self.show_comm_links variable after paused.")
else:
    print("show_comm_links already exists.")


# ---------------------------------------------------------
# 3. Add keyboard control C
# ---------------------------------------------------------

if "pygame.K_c" not in text:
    target = """if event.key == pygame.K_g:
                    self.show_large_graph = not self.show_large_graph"""

    replacement = """if event.key == pygame.K_g:
                    self.show_large_graph = not self.show_large_graph

                if event.key == pygame.K_c:
                    self.show_comm_links = not self.show_comm_links"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added C key control for communication links.")
    else:
        print("WARNING: Could not find G key block. C control not added.")
else:
    print("C key control already exists.")


# ---------------------------------------------------------
# 4. Update simulation controls text
# ---------------------------------------------------------

text = text.replace(
    "SPACE Pause   R Reset   T Fake Position   TAB Panel   G Graph",
    "SPACE Pause   R Reset   T Fake Position   C Comms   TAB Panel   G Graph"
)

text = text.replace(
    "SPACE=Pause  R=Reset  T=Fake Pos  TAB=Panel  G=Graph",
    "SPACE=Pause  R=Reset  T=Fake Pos  C=Comms  TAB=Panel  G=Graph"
)

text = text.replace(
    "TAB = Switch Page   |   G = Full Graph   |   ESC = Quit",
    "C = Comms   |   TAB = Switch Page   |   G = Full Graph   |   ESC = Quit"
)

print("Updated control hints.")


# ---------------------------------------------------------
# 5. Add communication links before drones are drawn
# ---------------------------------------------------------

if "self.draw_communication_links()" not in text:
    target = """        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)"""

    replacement = """        # Draw communication links before drones
        if self.show_comm_links:
            self.draw_communication_links()

        # Draw drones
        for drone in self.swarm.drones:
            self.draw_drone(drone)"""

    if target in text:
        text = text.replace(target, replacement, 1)
        print("Added communication link drawing.")
    else:
        print("WARNING: Could not find drone drawing block.")
else:
    print("Communication link drawing already exists.")


# ---------------------------------------------------------
# 6. Replace draw_info_panel page selection with page-name system
# ---------------------------------------------------------

try:
    start = text.index("        # Page content")
    end = text.index("        # Footer controls", start)

    new_page_block = '''        # Page content
        page_name = self.panel_pages[self.panel_page]

        if page_name == "OVERVIEW":
            self.draw_overview_page(px, py)
        elif page_name == "CLASSICAL BFT":
            self.draw_classical_page(px, py)
        elif page_name == "ML DETECTION":
            self.draw_ml_page(px, py)
        elif page_name == "SIGNALS" or page_name == "RISK SIGNALS":
            self.draw_signals_page(px, py)
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

'''

    text = text[:start] + new_page_block + text[end:]
    print("Updated page switching logic.")

except ValueError:
    print("WARNING: Could not replace page switching logic.")


# ---------------------------------------------------------
# 7. Add communication/network methods
# ---------------------------------------------------------

network_code = '''    def get_drone_trust_value(self, drone_id):
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

                dist = np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

                if dist <= communication_range:
                    a_trust = self.get_drone_trust_value(a.id)
                    b_trust = self.get_drone_trust_value(b.id)
                    min_trust = min(a_trust, b_trust)

                    a_detected = (
                        a.id in self.classical_suspected or
                        a.id in self.ml_suspected
                    )

                    b_detected = (
                        b.id in self.classical_suspected or
                        b.id in self.ml_suspected
                    )

                    suspected_link = a_detected or b_detected
                    malicious_involved = a.is_malicious or b.is_malicious

                    # Deterministic dropped-link simulation.
                    # Malicious-involved links drop more often.
                    if malicious_involved:
                        dropped = ((self.frame + a.id * 7 + b.id * 13) % 31 == 0)
                    else:
                        dropped = ((self.frame + a.id * 11 + b.id * 17) % 67 == 0)

                    if dropped:
                        status = "DROPPED"
                        color = (110, 110, 120)
                    elif min_trust < 45:
                        status = "LOW_TRUST"
                        color = PURPLE
                    elif suspected_link:
                        status = "SUSPICIOUS"
                        color = RED
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

        penalty = (
            suspicious * 7 +
            low_trust * 6 +
            dropped * 4
        )

        health = 100 - penalty

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

'''

if "def get_communication_links" not in text:
    try:
        insert_before = text.index("    def draw_section_title")
        text = text[:insert_before] + network_code + text[insert_before:]
        print("Added communication/network methods.")
    except ValueError:
        print("ERROR: Could not find insertion point before draw_section_title.")
        sys.exit(1)
else:
    print("Communication/network methods already exist.")


MAIN_FILE.write_text(text, encoding="utf-8")

print()
print("COMMUNICATION NETWORK UPGRADE COMPLETE.")
print("Now run: python main.py")
print("Controls:")
print("C = show/hide communication links")
print("TAB = switch pages until NETWORK")
print("G = full graph")