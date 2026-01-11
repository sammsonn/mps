import pygame
import math
import random
import heapq
from config import *
from projectile import Projectile

class Agent:
    def __init__(self, x, y, team_id, role=None):
        self.x = x
        self.y = y
        self.team_id = team_id
        self.health = AGENT_MAX_HEALTH
        self.alive = True
        self.speed = AGENT_SPEED
        self.color = TEAM_COLORS[team_id]
        self.last_attack_time = 0
        self.role = role  # ROLE_ATTACKER sau ROLE_DEFENDER
        
        # Pentru AI
        self.target = None
        self.velocity_x = 0
        self.velocity_y = 0
        self.stuck_counter = 0
        self.last_x = x
        self.last_y = y
        
        # Path finding
        self.path = []
        self.path_update_time = 0
        self.path_update_delay = 1000  # Recalculează calea la fiecare 1000ms
        
        # Line of Sight
        self.facing_angle = 0  # Unghiul în care se uită agentul (în radiani)
        
        # Pentru KOTH - ținta zonei
        self.target_zone = None
        
        # Pentru CTF - steagul purtat
        self.carrying_flag = None
        self.target_flag = None  # Steagul către care se îndreaptă
        self.enemy_base = None  # Baza inamică
        
        # Inbox pentru mesaje primite
        self.inbox = []  # List[Message]

        # Inițializează cu o direcție random
        angle = random.uniform(0, 2 * math.pi)
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed
        self.facing_angle = angle
        
        # Throttling pentru mesaje
        self.last_msg_times = {}
        # Căutare sistematică (Survival): tracking
        self.last_enemy_seen_time = 0
        self.search_mode = False
        self.search_waypoints = []
        self.search_index = 0
        self.search_reach_threshold = 40  # pixeli
        
        # Comunicare limitată - dacă True, agentul poate comunica doar cu vecinii apropiați
        self.has_limited_communication = False
    
    def get_color(self):
        """Returnează culoarea agentului în funcție de comunicare limitată"""
        if self.has_limited_communication:
            return TEAM_COLORS_LIMITED.get(self.team_id, TEAM_COLORS[self.team_id])
        return self.color
    
    def update_color(self):
        """Actualizează culoarea agentului în funcție de comunicare limitată"""
        if self.has_limited_communication:
            self.color = TEAM_COLORS_LIMITED.get(self.team_id, TEAM_COLORS[self.team_id])
        else:
            self.color = TEAM_COLORS[self.team_id]

    def _can_broadcast(self, msg_type, current_time, cooldown_ms):
        last = self.last_msg_times.get(msg_type, -1)
        if last == -1 or (current_time - last) >= cooldown_ms:
            self.last_msg_times[msg_type] = current_time
            return True
        return False
    
    def update(self, agents, obstacles, current_time, message_bus=None):
        """Actualizează starea agentului"""
        if not self.alive:
            return
        
        # Detectează dacă agentul e blocat
        distance_moved = math.sqrt((self.x - self.last_x)**2 + (self.y - self.last_y)**2)
        if distance_moved < 0.5:
            self.stuck_counter += 1
            if self.stuck_counter > 10:  # Blocat pentru 10 frame-uri - forțează scăpare
                self.escape_obstacle()
                self.stuck_counter = 0
                # Forțează recalcularea pathfinding-ului
                self.path = []
                self.path_update_time = 0
            elif self.stuck_counter > 5:
                # Dacă e blocat deja 5 frame-uri, forțează recalcularea pathfinding-ului
                # și încearcă o direcție nouă
                self.path = []
                self.path_update_time = 0
                
                # Verifică dacă e în centru sau aproape
                map_center_x = (MAP_WIDTH * TILE_SIZE) / 2
                map_center_y = (MAP_HEIGHT * TILE_SIZE) / 2
                dx_center = map_center_x - self.x
                dy_center = map_center_y - self.y
                dist_to_center = math.sqrt(dx_center*dx_center + dy_center*dy_center)
                
                # Schimbă direcția pentru a încerca să scape
                if abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
                    # Dacă nu se mișcă deloc, forțează o direcție
                    if dist_to_center < 80:
                        # E în centru, explorează perpendicular pe centru
                        center_angle = math.atan2(dy_center, dx_center) if dist_to_center > 0 else 0
                        perpendicular = random.choice([-1, 1])
                        angle = center_angle + (perpendicular * math.pi / 2) + random.uniform(-math.pi/3, math.pi/3)
                        self.velocity_x = math.cos(angle) * self.speed * 2
                        self.velocity_y = math.sin(angle) * self.speed * 2
                    else:
                        # E departe de centru, mergi către centru
                        if dist_to_center > 0:
                            self.velocity_x = (dx_center / dist_to_center) * self.speed * 2
                            self.velocity_y = (dy_center / dist_to_center) * self.speed * 2
                        else:
                            # Fallback: direcție random
                            angle = random.uniform(0, 2 * math.pi)
                            self.velocity_x = math.cos(angle) * self.speed * 2
                            self.velocity_y = math.sin(angle) * self.speed * 2
                else:
                    # Dacă se mișcă dar e blocat, schimbă direcția perpendicular
                    current_angle = math.atan2(self.velocity_y, self.velocity_x)
                    perpendicular = random.choice([-1, 1])
                    angle = current_angle + (perpendicular * math.pi / 2) + random.uniform(-math.pi/4, math.pi/4)
                    self.velocity_x = math.cos(angle) * self.speed * 2
                    self.velocity_y = math.sin(angle) * self.speed * 2
        else:
            self.stuck_counter = 0
        
        self.last_x = self.x
        self.last_y = self.y
        
        # Separare de ceilalți agenți din aceeași echipă
        self.apply_separation(agents)
        
        # Găsește cel mai apropiat inamic în LoS
        self.find_target(agents, obstacles, message_bus)
        # Reset/armare mod căutare în funcție de inamici văzuți
        if self.target and getattr(self.target, "alive", False):
            self.last_enemy_seen_time = current_time
            self.search_mode = False
        else:
            # Activează căutare dacă nu vede inamici de o perioadă
            SEARCH_TIMEOUT_MS = 4000
            if current_time - (self.last_enemy_seen_time or 0) > SEARCH_TIMEOUT_MS:
                self.search_mode = True
                if not self.search_waypoints:
                    self._build_search_waypoints()
        
        # Pentru CTF, dacă nu există inamic în LoS, asigură-te că continuă să caute steagul
        # (nu lasă explore() să facă mișcare random)
        
        # Comportament bazat pe rol
        if self.role == ROLE_ATTACKER:
            # Atacatorii prioritizează zona inamică (KOTH)
            self.update_attacker_behavior(current_time, obstacles, agents, message_bus)
        elif self.role == ROLE_DEFENDER:
            # Apărătorii protejează zona proprie (KOTH)
            self.update_defender_behavior(current_time, obstacles, agents, message_bus)
        elif self.role == ROLE_CARRIER:
            # Carrier - duce steagul la bază (CTF)
            self.update_carrier_behavior(current_time, obstacles, message_bus)
        elif self.role == ROLE_CHASER:
            # Chaser - urmărește carrier-ul inamic (CTF)
            self.update_chaser_behavior(current_time, obstacles, agents)
        else:
            # Comportament standard (Survival mode sau CTF fără rol specific)
            # Pentru CTF, dacă nu are rol, caută steagul inamic
            if self.target_flag and not self.carrying_flag:
                # CTF: Caută steagul inamic dacă nu poartă deja un steag
                flag_x = self.target_flag.x
                flag_y = self.target_flag.y
                
                dx = flag_x - self.x
                dy = flag_y - self.y
                distance = (dx*dx + dy*dy) ** 0.5
                
                # Dacă există inamic aproape, atacă-l, dar nu ignora complet steagul
                if self.target and getattr(self.target, "alive", False):
                    distance_to_enemy = self.distance_to(self.target)
                    # Atacă dacă inamicul e în raza de atac, dar dacă steagul e foarte aproape, prioritizează steagul
                    if distance_to_enemy < AGENT_ATTACK_RANGE * 1.2 and distance > 40:
                        # Inamic aproape și steagul nu e foarte aproape, atacă-l
                        if current_time - self.path_update_time > self.path_update_delay:
                            self.find_path_to_target(obstacles)
                            self.path_update_time = current_time
                        self.follow_path()
                    elif distance > 50:  # Steagul e departe, mergi către el
                        # Mergi către steagul inamic
                        if current_time - self.path_update_time > self.path_update_delay:
                            class TempTarget:
                                def __init__(self, x, y):
                                    self.x = x
                                    self.y = y
                            
                            old_target = self.target
                            self.target = TempTarget(flag_x, flag_y)
                            self.find_path_to_target(obstacles)
                            self.target = old_target
                            self.path_update_time = current_time
                        self.follow_path()
                    else:
                        # Aproape de steag, continuă să mergi direct
                        if distance > 0:
                            self.velocity_x = (dx / distance) * self.speed
                            self.velocity_y = (dy / distance) * self.speed
                elif distance > 30:  # Nu există inamic, mergi direct la steag
                    # Mergi către steagul inamic
                    if current_time - self.path_update_time > self.path_update_delay:
                        class TempTarget:
                            def __init__(self, x, y):
                                self.x = x
                                self.y = y
                        
                        old_target = self.target
                        self.target = TempTarget(flag_x, flag_y)
                        self.find_path_to_target(obstacles)
                        self.target = old_target
                        self.path_update_time = current_time
                    self.follow_path()
                else:
                    # Foarte aproape de steag, mergi direct
                    if distance > 0:
                        self.velocity_x = (dx / distance) * self.speed
                        self.velocity_y = (dy / distance) * self.speed
            elif self.target and getattr(self.target, "alive", False):
                # Actualizează calea doar periodic pentru performanță
                if current_time - self.path_update_time > self.path_update_delay:
                    self.find_path_to_target(obstacles)
                    self.path_update_time = current_time
                
                # Urmează calea sau atacă
                self.follow_path()
            else:
                # Dacă nu are țintă și nu e CTF, fie căutare sistematică, fie explorare
                if self.search_mode and self.search_waypoints:
                    wx, wy = self.search_waypoints[self.search_index % len(self.search_waypoints)]
                    dx = wx - self.x
                    dy = wy - self.y
                    dist = math.hypot(dx, dy)
                    if dist < self.search_reach_threshold:
                        self.search_index = (self.search_index + 1) % len(self.search_waypoints)
                    else:
                        # Navighează către waypoint folosind pathfinding cu update periodic
                        if current_time - self.path_update_time > self.path_update_delay:
                            class TempTarget:
                                def __init__(self, x, y):
                                    self.x = x
                                    self.y = y
                            old_target = self.target
                            self.target = TempTarget(wx, wy)
                            self.find_path_to_target(obstacles)
                            self.target = old_target
                            self.path_update_time = current_time
                        self.follow_path()
                else:
                    self.explore()
                    self.path = []  # Șterge calea când nu există țintă
        
        # Actualizează unghiul facing bazat pe velocity
        if abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1:
            self.facing_angle = math.atan2(self.velocity_y, self.velocity_x)
        
        # Broadcast LOW_HEALTH dacă e cazul
        if message_bus and self.health <= AGENT_MAX_HEALTH * 0.3:
            if hasattr(self, 'agent_id') and self._can_broadcast("LOW_HEALTH", current_time, 1500):
                self.send_team_broadcast(message_bus, "LOW_HEALTH", {"sender_id": self.agent_id, "x": self.x, "y": self.y, "health": self.health})

        # Aplică mișcarea
        self.apply_movement(obstacles)
    
    def shoot(self, projectiles_list):
        """Creează un proiectil în direcția în care se uită agentul"""
        projectile = Projectile(self.x, self.y, self.facing_angle, self.team_id)
        projectiles_list.append(projectile)
    
    def update_attacker_behavior(self, current_time, obstacles, agents=None, message_bus=None):
        """Comportament pentru atacatori - merg către zona centrală"""
        if not self.target_zone:
            self.explore()
            return
        
        # Verifică dacă agentul e în zona centrală
        in_zone = self.target_zone.collidepoint(self.x, self.y)
        
        # Dacă există inamic în LoS, atacă-l dacă e aproape sau blochează calea
        if self.target and self.target.alive:
            distance_to_enemy = self.distance_to(self.target)
            
            # Atacă dacă inamicul e în raza de atac
            if distance_to_enemy < AGENT_ATTACK_RANGE * 1.2:
                if current_time - self.path_update_time > self.path_update_delay:
                    self.find_path_to_target(obstacles)
                    self.path_update_time = current_time
                self.follow_path()
            elif not in_zone:
                # Inamicul nu e aproape, continuă către zona centrală
                zone_center_x = self.target_zone.centerx
                zone_center_y = self.target_zone.centery
                
                dx = zone_center_x - self.x
                dy = zone_center_y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 50:  # Dacă e departe, folosește pathfinding
                    if current_time - self.path_update_time > self.path_update_delay:
                        class TempTarget:
                            def __init__(self, x, y):
                                self.x = x
                                self.y = y
                        
                        old_target = self.target
                        self.target = TempTarget(zone_center_x, zone_center_y)
                        self.find_path_to_target(obstacles)
                        self.target = old_target
                        self.path_update_time = current_time
                    
                    self.follow_path()
                else:
                    # Aproape de zonă, mergi direct către centru
                    if distance > 0:
                        self.velocity_x = (dx / distance) * self.speed * 0.8
                        self.velocity_y = (dy / distance) * self.speed * 0.8
            else:
                # E în zonă și există inamic, dar nu e foarte aproape - rămâi în zonă
                self.patrol_central_zone(message_bus, current_time, contested=True)
        # Altfel, mergi către zona centrală sau patrulează dacă ești deja acolo
        elif in_zone:
            # E deja în zonă, patrulează în zonă (rămâi acolo)
            self.patrol_central_zone(message_bus, current_time, contested=False)
        else:
            # Nu e în zonă, mergi către ea
            zone_center_x = self.target_zone.centerx
            zone_center_y = self.target_zone.centery
            
            dx = zone_center_x - self.x
            dy = zone_center_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 50:  # Dacă e departe, folosește pathfinding
                if current_time - self.path_update_time > self.path_update_delay:
                    class TempTarget:
                        def __init__(self, x, y):
                            self.x = x
                            self.y = y
                    
                    old_target = self.target
                    self.target = TempTarget(zone_center_x, zone_center_y)
                    self.find_path_to_target(obstacles)
                    self.target = old_target
                    self.path_update_time = current_time
                
                self.follow_path()
            else:
                # Aproape de zonă, mergi direct către centru
                if distance > 0:
                    self.velocity_x = (dx / distance) * self.speed * 0.8
                    self.velocity_y = (dy / distance) * self.speed * 0.8
    
    def update_defender_behavior(self, current_time, obstacles, agents=None, message_bus=None):
        """Comportament pentru apărători - merg către zona centrală (același ca atacatorii)"""
        # Pentru KOTH cu zona centrală, apărătorii se comportă la fel ca atacatorii
        self.update_attacker_behavior(current_time, obstacles, agents, message_bus)
    
    def patrol_zone(self):
        """Patrulează în jurul zonei proprii (pentru apărători)"""
        if not self.target_zone:
            return
        
        # Verifică dacă e în zonă
        if self.target_zone.collidepoint(self.x, self.y):
            # E în zonă, mișcă-te lent în jurul zonei (patrulare)
            if random.random() < 0.03:  # 3% șansă să schimbe direcția
                # Alege o direcție către un punct random în zonă
                target_x = self.target_zone.x + random.randint(0, self.target_zone.width)
                target_y = self.target_zone.y + random.randint(0, self.target_zone.height)
                
                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    # Mișcare lentă în zonă pentru a rămâne acolo
                    self.velocity_x = (dx / distance) * self.speed * 0.4
                    self.velocity_y = (dy / distance) * self.speed * 0.4
            # Altfel, continuă în direcția curentă (dacă există) sau oprește-te
            elif abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
                # Dacă nu se mișcă, alege o direcție lentă în zonă
                target_x = self.target_zone.x + random.randint(0, self.target_zone.width)
                target_y = self.target_zone.y + random.randint(0, self.target_zone.height)
                
                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    self.velocity_x = (dx / distance) * self.speed * 0.3
                    self.velocity_y = (dy / distance) * self.speed * 0.3
        else:
            # Nu e în zonă, întoarce-te la centrul zonei
            zone_center_x = self.target_zone.centerx
            zone_center_y = self.target_zone.centery
            
            dx = zone_center_x - self.x
            dy = zone_center_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                self.velocity_x = (dx / distance) * self.speed * 0.8
                self.velocity_y = (dy / distance) * self.speed * 0.8
    
    def patrol_central_zone(self, message_bus=None, current_time=None, contested=None):
        """Patrulează în zona centrală - rămâne în zonă"""
        if not self.target_zone:
            return
        
        # Verifică dacă e în zonă
        if self.target_zone.collidepoint(self.x, self.y):
            # Trimite status zonă dacă e cazul (throttled)
            if message_bus and current_time is not None and hasattr(self, 'agent_id'):
                if contested is None:
                    # dacă nu e specificat, derivăm din existența unei ținte
                    contested = bool(self.target and self.target.alive)
                msg_type = "ZONE_CONTESTED" if contested else "ZONE_CLEAR"
                if self._can_broadcast(msg_type, current_time, 1200):
                    self.send_team_broadcast(message_bus, msg_type, {"x": self.target_zone.centerx, "y": self.target_zone.centery})
            # E în zonă, mișcă-te lent în jurul zonei pentru a rămâne acolo
            if random.random() < 0.04:  # 4% șansă să schimbe direcția
                # Alege o direcție către un punct random în zonă
                target_x = self.target_zone.x + random.randint(0, self.target_zone.width)
                target_y = self.target_zone.y + random.randint(0, self.target_zone.height)
                
                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    # Mișcare foarte lentă în zonă pentru a rămâne acolo și acumula timp
                    self.velocity_x = (dx / distance) * self.speed * 0.3
                    self.velocity_y = (dy / distance) * self.speed * 0.3
            # Altfel, continuă în direcția curentă (dacă există) sau oprește-te
            elif abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
                # Dacă nu se mișcă, alege o direcție lentă în zonă
                target_x = self.target_zone.x + random.randint(0, self.target_zone.width)
                target_y = self.target_zone.y + random.randint(0, self.target_zone.height)
                
                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    self.velocity_x = (dx / distance) * self.speed * 0.25
                    self.velocity_y = (dy / distance) * self.speed * 0.25
        else:
            # Nu e în zonă, mergi înapoi către centrul zonei
            zone_center_x = self.target_zone.centerx
            zone_center_y = self.target_zone.centery
            
            dx = zone_center_x - self.x
            dy = zone_center_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                self.velocity_x = (dx / distance) * self.speed * 0.8
                self.velocity_y = (dy / distance) * self.speed * 0.8
    
    def patrol_enemy_zone(self):
        """Patrulează în zona inamică (pentru atacatori) - rămâne în zonă"""
        # Folosește aceeași logică ca patrol_central_zone
        self.patrol_central_zone()
    
    def update_carrier_behavior(self, current_time, obstacles, message_bus=None):
        """Comportament pentru carrier - duce steagul la baza proprie"""
        # Prioritate 1: Dacă există inamic foarte aproape, încearcă să scapi
        if self.target and self.target.alive:
            distance_to_enemy = self.distance_to(self.target)
            if distance_to_enemy < AGENT_ATTACK_RANGE * 0.7:
                # Inamic prea aproape, încearcă să fugi
                dx = self.x - self.target.x
                dy = self.y - self.target.y
                distance = (dx*dx + dy*dy) ** 0.5
                if distance > 0:
                    self.velocity_x = (dx / distance) * self.speed * 1.5  # Fugă mai rapidă
                    self.velocity_y = (dy / distance) * self.speed * 1.5
                # Trimite un semnal de ajutor (DISTRESS_CALL)
                if message_bus and hasattr(self, 'agent_id'):
                    self.send_team_broadcast(
                        message_bus,
                        "DISTRESS_CALL",
                        {
                            "sender_id": self.agent_id,
                            "x": self.x,
                            "y": self.y,
                            "enemy_id": getattr(self.target, 'agent_id', None)
                        }
                    )
                return
        
        # Prioritate 2: Mergi către baza proprie
        if self.enemy_base:
            base_x = self.enemy_base.centerx
            base_y = self.enemy_base.centery
            
            dx = base_x - self.x
            dy = base_y - self.y
            distance = (dx*dx + dy*dy) ** 0.5
            
            if distance > 30:  # Nu e încă în bază
                if current_time - self.path_update_time > self.path_update_delay:
                    # Creează o țintă temporară pentru pathfinding
                    class TempTarget:
                        def __init__(self, x, y):
                            self.x = x
                            self.y = y
                    
                    old_target = self.target
                    self.target = TempTarget(base_x, base_y)
                    self.find_path_to_target(obstacles)
                    self.target = old_target
                    self.path_update_time = current_time
                
                self.follow_path()
            else:
                # E în bază, mergi către centru
                if distance > 0:
                    self.velocity_x = (dx / distance) * self.speed
                    self.velocity_y = (dy / distance) * self.speed
    
    def update_chaser_behavior(self, current_time, obstacles, agents):
        """Comportament pentru chaser - urmărește carrier-ul inamic"""
        # Caută carrier-ul inamic (agentul care poartă steagul echipei tale)
        enemy_carrier = None
        for agent in agents:
            if agent.team_id != self.team_id and agent.alive and agent.carrying_flag:
                # Verifică dacă poartă steagul echipei noastre
                if agent.carrying_flag.team_id == self.team_id:
                    enemy_carrier = agent
                    break
        
        if enemy_carrier:
            # Urmărește carrier-ul
            if current_time - self.path_update_time > self.path_update_delay:
                old_target = self.target
                self.target = enemy_carrier
                self.find_path_to_target(obstacles)
                self.path_update_time = current_time
                self.target = old_target
            
            self.follow_path()
        else:
            # Nu există carrier, comportament standard
            if self.target and self.target.alive:
                if current_time - self.path_update_time > self.path_update_delay:
                    self.find_path_to_target(obstacles)
                    self.path_update_time = current_time
                self.follow_path()
            elif self.target_flag:
                # Mergi către steagul propriu (pentru a-l apăra sau recupera)
                flag_x = self.target_flag.x
                flag_y = self.target_flag.y
                
                dx = flag_x - self.x
                dy = flag_y - self.y
                distance = (dx*dx + dy*dy) ** 0.5
                
                if distance > 30:
                    if current_time - self.path_update_time > self.path_update_delay:
                        class TempTarget:
                            def __init__(self, x, y):
                                self.x = x
                                self.y = y
                        
                        old_target = self.target
                        self.target = TempTarget(flag_x, flag_y)
                        self.find_path_to_target(obstacles)
                        self.target = old_target
                        self.path_update_time = current_time
                    
                    self.follow_path()
                else:
                    # Patrulează în jurul steagului
                    self.explore()
            else:
                self.explore()
    
    def escape_obstacle(self):
        """Scapă dintr-o situație de blocare"""
        # Calculează centrul hărții
        map_center_x = (MAP_WIDTH * TILE_SIZE) / 2
        map_center_y = (MAP_HEIGHT * TILE_SIZE) / 2
        
        # Calculează direcția către centru
        dx = map_center_x - self.x
        dy = map_center_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # 70% șansă să meargă către centru, 30% direcție random
            if random.random() < 0.7:
                self.velocity_x = (dx / distance) * self.speed * 1.5
                self.velocity_y = (dy / distance) * self.speed * 1.5
            else:
                # Direcție random dar perpendiculară pe direcția curentă pentru a evita blocarea
                current_angle = math.atan2(self.velocity_y, self.velocity_x) if (abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1) else 0
                perpendicular_angle = current_angle + math.pi / 2 + random.uniform(-math.pi/4, math.pi/4)
                self.velocity_x = math.cos(perpendicular_angle) * self.speed * 1.5
                self.velocity_y = math.sin(perpendicular_angle) * self.speed * 1.5
        else:
            # Fallback: direcție random
            angle = random.uniform(0, 2 * math.pi)
            self.velocity_x = math.cos(angle) * self.speed * 1.5
            self.velocity_y = math.sin(angle) * self.speed * 1.5
        
        self.path = []  # Resetează calea
        self.path_update_time = 0  # Forțează recalculare imediată
        self.explore_direction = None  # Resetează direcția de explorare
    
    def apply_separation(self, agents):
        """Aplică forță de repulsie față de alți agenți din aceeași echipă"""
        separation_force_x = 0
        separation_force_y = 0
        
        # Calculează centrul hărții pentru a detecta dacă suntem în bază
        map_center_x = (MAP_WIDTH * TILE_SIZE) / 2
        map_center_y = (MAP_HEIGHT * TILE_SIZE) / 2
        distance_to_center = math.sqrt((self.x - map_center_x)**2 + (self.y - map_center_y)**2)
        
        # Dacă suntem departe de centru (în bază), reducem separarea pentru a permite ieșirea
        in_base = distance_to_center < 150  # Considerăm că suntem în bază dacă suntem departe de centru
        
        for agent in agents:
            if agent == self or not agent.alive or agent.team_id != self.team_id:
                continue
            
            dx = self.x - agent.x
            dy = self.y - agent.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Dacă sunt prea aproape, aplică forță de repulsie
            if distance < AGENT_SEPARATION_DISTANCE and distance > 0:
                force = (AGENT_SEPARATION_DISTANCE - distance) / AGENT_SEPARATION_DISTANCE
                separation_force_x += (dx / distance) * force * self.speed
                separation_force_y += (dy / distance) * force * self.speed
        
        # Aplică forța de separare cu intensitate redusă când suntem în bază
        separation_multiplier = 0.15 if in_base else 0.3
        self.velocity_x += separation_force_x * separation_multiplier
        self.velocity_y += separation_force_y * separation_multiplier
    
    def is_in_line_of_sight(self, agent, obstacles):
        """
        Verifică dacă un agent este în linia de vedere (LoS)
        
        Args:
            agent: Agentul țintă
            obstacles: Lista de obstacole care pot bloca vederea
            
        Returns:
            True dacă agentul este în LoS, False altfel
        """
        if not agent.alive:
            return False
        
        # Calculează distanța
        dx = agent.x - self.x
        dy = agent.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Verifică dacă este în raza de vedere
        if distance > AGENT_LOS_RANGE:
            return False
        
        # Calculează unghiul către agent
        angle_to_agent = math.atan2(dy, dx)
        
        # Calculează diferența de unghi
        angle_diff = abs(angle_to_agent - self.facing_angle)
        # Normalizează unghiul la [-pi, pi]
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        angle_diff = abs(angle_diff)
        
        # Verifică dacă este în conul de vedere
        los_angle_rad = math.radians(AGENT_LOS_ANGLE / 2)
        if angle_diff > los_angle_rad:
            return False
        
        # Verifică dacă există obstacole între agenți
        # Simplificat: verificăm câteva puncte pe linia dintre agenți
        num_checks = int(distance / 10)  # Un check la fiecare 10 pixeli
        for i in range(1, num_checks):
            t = i / num_checks
            check_x = self.x + dx * t
            check_y = self.y + dy * t
            
            for obstacle in obstacles:
                if not obstacle.alive:
                    continue
                if obstacle.rect.collidepoint(check_x, check_y):
                    return False
        
        return True
    
    def find_target(self, agents, obstacles, message_bus=None):
        """Găsește cel mai apropiat agent inamic în LoS și broadcast dacă e nou."""
        min_distance = float('inf')
        closest_enemy = None
        
        for agent in agents:
            if agent.team_id != self.team_id and agent.alive:
                # Verifică dacă este în LoS
                if self.is_in_line_of_sight(agent, obstacles):
                    distance = self.distance_to(agent)
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = agent
        
        # Dacă ținta s-a schimbat, tratează update
        if self.target != closest_enemy:
            if closest_enemy is None and self.target_flag and not self.carrying_flag:
                # Nu reseta calea dacă mergem către steag
                pass
            else:
                self.path = []
            # Broadcast noul inamic spotat
            if closest_enemy and message_bus and hasattr(self, 'agent_id'):
                message_bus.broadcast_enemy_spotted(self, closest_enemy)

        self.target = closest_enemy

    def process_inbox(self, message_bus):
        """Procesează mesajele primite pentru actualizare ținte/decizii simple."""
        if not self.inbox:
            return
        # Strategii simple: adoptă primul ENEMY_SPOTTED dacă nu ai țintă sau ținta ta e moartă
        # Reacționează la DISTRESS_CALL: chaser/attacker sari pe inamicul indicat sau mergi spre coordonate
        for msg in self.inbox:
            if msg.type == "ENEMY_SPOTTED" and (self.target is None or not getattr(self.target, "alive", False)):
                enemy_id = msg.payload.get("enemy_id")
                if enemy_id and message_bus:
                    enemy = message_bus.resolve_agent(enemy_id)
                    if enemy and enemy.alive:
                        self.target = enemy
                        break  # Adoptă primul relevant
            elif msg.type == "DISTRESS_CALL":
                # Chasers răspund imediat; atacatorii fără target pot răspunde
                should_help = (self.role == ROLE_CHASER) or (self.role == ROLE_ATTACKER and (self.target is None or not getattr(self.target, "alive", False)))
                if should_help:
                    enemy_id = msg.payload.get("enemy_id")
                    enemy = message_bus.resolve_agent(enemy_id) if (enemy_id and message_bus) else None
                    if enemy and enemy.alive:
                        self.target = enemy
                        break
                    else:
                        # Mergi spre coordonatele apelului dacă nu poți rezolva inamicul
                        tx = msg.payload.get("x")
                        ty = msg.payload.get("y")
                        if tx is not None and ty is not None:
                            class TempTarget:
                                def __init__(self, x, y):
                                    self.x = x
                                    self.y = y
                            self.target = TempTarget(float(tx), float(ty))
                            break
            elif msg.type == "LOW_HEALTH":
                # Similar cu DISTRESS_CALL, dar fără enemy_id de obicei
                should_help = (self.role == ROLE_CHASER) or (self.role == ROLE_ATTACKER and (self.target is None or not getattr(self.target, "alive", False))) or (self.role == ROLE_DEFENDER and (self.target is None or not getattr(self.target, "alive", False)))
                if should_help:
                    tx = msg.payload.get("x")
                    ty = msg.payload.get("y")
                    if tx is not None and ty is not None:
                        class TempTarget:
                            def __init__(self, x, y):
                                self.x = x
                                self.y = y
                                self.alive = False
                        self.target = TempTarget(float(tx), float(ty))
                        break
            elif msg.type == "FLAG_TAKEN":
                # Urmărește carrier-ul care a luat steagul echipei noastre
                carrier_id = msg.payload.get("carrier_id")
                if carrier_id and (self.role == ROLE_CHASER or (self.role == ROLE_ATTACKER and (self.target is None or not getattr(self.target, "alive", False)))):
                    enemy = message_bus.resolve_agent(carrier_id) if message_bus else None
                    if enemy and enemy.alive:
                        self.target = enemy
                        break
            elif msg.type == "FLAG_TAKEN_FRIENDLY":
                # Însoțește carrier-ul propriei echipe (escortă) dacă nu ai target critic
                if self.team_id is not None and (self.target is None or not getattr(self.target, "alive", False)):
                    carrier_id = msg.payload.get("carrier_id")
                    ally = message_bus.resolve_agent(carrier_id) if message_bus else None
                    if ally and ally.alive and ally.team_id == self.team_id:
                        class TempTarget:
                            def __init__(self, x, y):
                                self.x = x
                                self.y = y
                                self.alive = False
                        self.target = TempTarget(float(ally.x), float(ally.y))
                        break
            elif msg.type in ("ZONE_CONTESTED", "ZONE_CLEAR"):
                # Reacție simplă: mergi către centru zonei dacă nu ai target sau ești defender/attacker în KOTH
                if self.target_zone and (self.role in (ROLE_ATTACKER, ROLE_DEFENDER)) and (self.target is None or not self.target.alive or msg.type == "ZONE_CONTESTED"):
                    class TempTarget:
                        def __init__(self, x, y):
                            self.x = x
                            self.y = y
                            self.alive = False
                    tx = msg.payload.get("x", self.target_zone.centerx)
                    ty = msg.payload.get("y", self.target_zone.centery)
                    self.target = TempTarget(float(tx), float(ty))
                    break
        # Golește inbox-ul după procesare (mesaje sunt temporare)
        self.inbox = []

    def send_team_broadcast(self, message_bus, msg_type, payload):
        """Trimite un mesaj de echipă generic.
        
        Coordonatele (x, y) din payload sunt rotunjite automat la 3 zecimale.
        """
        if not message_bus or not hasattr(self, 'agent_id'):
            return
        from communication import Message  # Import local pentru a evita cicluri
        ts = pygame.time.get_ticks()
        
        # Rotunjește coordonatele la 3 zecimale dacă există în payload
        processed_payload = payload.copy()
        if "x" in processed_payload and isinstance(processed_payload["x"], (int, float)):
            processed_payload["x"] = round(processed_payload["x"], 3)
        if "y" in processed_payload and isinstance(processed_payload["y"], (int, float)):
            processed_payload["y"] = round(processed_payload["y"], 3)
        
        # Obține poziția expeditorului și flag-ul de comunicare limitată
        sender_x = round(self.x, 3) if hasattr(self, 'x') else None
        sender_y = round(self.y, 3) if hasattr(self, 'y') else None
        is_limited = getattr(self, 'has_limited_communication', False)
        
        message_bus.publish(Message(
            self.agent_id, 
            self.team_id, 
            msg_type, 
            processed_payload, 
            ts,
            sender_x=sender_x,
            sender_y=sender_y,
            is_limited=is_limited
        ))
    
    def find_path_to_target(self, obstacles):
        """Găsește o cale către țintă folosind Dijkstra"""
        if not self.target:
            return
        
        # Convertește pozițiile în coordonate de grilă
        grid_size = TILE_SIZE
        start_x, start_y = int(self.x / grid_size), int(self.y / grid_size)
        target_x, target_y = int(self.target.x / grid_size), int(self.target.y / grid_size)
        
        # Creează harta de obstacole într-o grilă
        grid_obstacles = set()
        for obstacle in obstacles:
            if not obstacle.alive:
                continue
            obs_x1, obs_y1 = obstacle.rect.x // grid_size, obstacle.rect.y // grid_size
            obs_x2, obs_y2 = (obstacle.rect.x + obstacle.rect.width) // grid_size, (obstacle.rect.y + obstacle.rect.height) // grid_size
            
            for x in range(obs_x1, obs_x2 + 1):
                for y in range(obs_y1, obs_y2 + 1):
                    grid_obstacles.add((x, y))
        
        # Implementare Dijkstra (nu folosim heuristică)
        open_set = [(0, 0, (start_x, start_y))]  # (cost, counter, pos)
        came_from = {}
        cost = {(start_x, start_y): 0}
        open_set_hash = {(start_x, start_y)}
        counter = 1
        
        max_iterations = 500  # Limită pentru a preveni bucle infinite
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            current_cost, _, current = heapq.heappop(open_set)
            open_set_hash.remove(current)
            
            if current == (target_x, target_y):
                # Reconstruiește calea
                path = []
                while current in came_from:
                    path.append((current[0] * grid_size + grid_size // 2, 
                                current[1] * grid_size + grid_size // 2))
                    current = came_from[current]
                
                self.path = path[::-1]  # Inversează calea
                return
            
            # Verifică vecinii (8 direcții)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Verifică limitele hărții
                if (neighbor[0] < 0 or neighbor[0] >= MAP_WIDTH or 
                    neighbor[1] < 0 or neighbor[1] >= MAP_HEIGHT):
                    continue
                
                # Verifică obstacole
                if neighbor in grid_obstacles:
                    continue
                
                # Pentru diagonale, verifică și cele două căi directe
                if abs(dx) == 1 and abs(dy) == 1:
                    if (current[0] + dx, current[1]) in grid_obstacles or (current[0], current[1] + dy) in grid_obstacles:
                        continue
                
                # Cost suplimentar pentru diagonale
                move_cost = 1.4 if abs(dx) + abs(dy) == 2 else 1.0
                
                tentative_cost = cost[current] + move_cost
                
                if neighbor not in cost or tentative_cost < cost[neighbor]:
                    came_from[neighbor] = current
                    cost[neighbor] = tentative_cost
                    
                    if neighbor not in open_set_hash:
                        counter += 1
                        heapq.heappush(open_set, (tentative_cost, counter, neighbor))
                        open_set_hash.add(neighbor)
        
        # Dacă nu găsim o cale completă, încercăm să ne apropiem cât putem
        if not self.path and len(came_from) > 0:
            # Găsește cel mai apropiat punct explorat
            best_point = None
            best_dist = float('inf')
            
            for point in came_from.keys():
                dist = self.heuristic(point, (target_x, target_y))
                if dist < best_dist:
                    best_dist = dist
                    best_point = point
            
            if best_point:
                # Reconstruiește calea până la cel mai bun punct
                path = []
                current = best_point
                while current in came_from:
                    path.append((current[0] * grid_size + grid_size // 2, 
                                current[1] * grid_size + grid_size // 2))
                    current = came_from[current]
                
                self.path = path[::-1]  # Inversează calea
    
    def heuristic(self, a, b):
        """Calculează distanța Manhattan între două puncte"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def follow_path(self):
        """Urmează calea calculată"""
        if not self.path:
            # Dacă nu există cale, încearcă să te miști direct spre țintă
            self.move_direct_to_target()
            return
        
        # Verifică dacă am ajuns la primul punct din cale
        next_point = self.path[0]
        dx = next_point[0] - self.x
        dy = next_point[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Dacă suntem foarte aproape de punct, treci la următorul
        if distance < self.speed * 2:
            self.path.pop(0)
            if not self.path:
                # Dacă nu mai există puncte, mergi direct la țintă sau steag
                if self.target:
                    self.move_direct_to_target()
                elif self.target_flag and not self.carrying_flag:
                    flag_x = self.target_flag.x
                    flag_y = self.target_flag.y
                    dx = flag_x - self.x
                    dy = flag_y - self.y
                    distance = (dx*dx + dy*dy) ** 0.5
                    if distance > 0:
                        self.velocity_x = (dx / distance) * self.speed
                        self.velocity_y = (dy / distance) * self.speed
                return
            else:
                # Recalculează pentru următorul punct
                next_point = self.path[0]
                dx = next_point[0] - self.x
                dy = next_point[1] - self.y
                distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculează velocitățile pentru a te mișca spre următorul punct
        if distance > 0:
            self.velocity_x = (dx / distance) * self.speed
            self.velocity_y = (dy / distance) * self.speed
        else:
            # Dacă distanța e 0, elimină punctul și continuă
            self.path.pop(0) if self.path else None
    
    def move_direct_to_target(self):
        """Mișcare directă către țintă când suntem aproape sau nu avem cale"""
        if not self.target:
            return
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            if distance > AGENT_ATTACK_RANGE * 0.8:
                self.velocity_x = (dx / distance) * self.speed
                self.velocity_y = (dy / distance) * self.speed
            else:
                # Încetinește când e aproape
                self.velocity_x = (dx / distance) * self.speed * 0.4
                self.velocity_y = (dy / distance) * self.speed * 0.4
    
    def explore(self):
        """Mișcare de explorare când nu există țintă"""
        # Pentru CTF, dacă există target_flag, mergi către el
        if self.target_flag and not self.carrying_flag:
            flag_x = self.target_flag.x
            flag_y = self.target_flag.y
            
            dx = flag_x - self.x
            dy = flag_y - self.y
            distance = (dx*dx + dy*dy) ** 0.5
            
            if distance > 0:
                # Normalizează și aplică velocitatea
                self.velocity_x = (dx / distance) * self.speed
                self.velocity_y = (dy / distance) * self.speed
            return
        
        # Pentru Survival mode, explorare activă către centrul hărții sau zonele inamice
        # Calculează centrul hărții
        map_center_x = (MAP_WIDTH * TILE_SIZE) / 2
        map_center_y = (MAP_HEIGHT * TILE_SIZE) / 2
        
        # Calculează distanța până la centru
        dx = map_center_x - self.x
        dy = map_center_y - self.y
        distance_to_center = math.sqrt(dx*dx + dy*dy)
        
        # Dacă e departe de centru, mergi către centru (unde e mai probabil să fie acțiune)
        if distance_to_center > 150:
            # Foarte departe de centru, mergi direct către centru
            if distance_to_center > 0:
                self.velocity_x = (dx / distance_to_center) * self.speed
                self.velocity_y = (dy / distance_to_center) * self.speed
        elif distance_to_center > 80:
            # Aproape de centru, dar nu încă acolo - mergi către centru cu varietate
            if distance_to_center > 0:
                # 80% către centru, 20% direcție random pentru varietate
                if random.random() < 0.8:
                    self.velocity_x = (dx / distance_to_center) * self.speed
                    self.velocity_y = (dy / distance_to_center) * self.speed
                else:
                    # Schimbă direcția random pentru explorare
                    angle = random.uniform(0, 2 * math.pi)
                    self.velocity_x = math.cos(angle) * self.speed
                    self.velocity_y = math.sin(angle) * self.speed
        else:
            # E în centru sau foarte aproape, explorează activ și evită pereții
            # Nu mai merge către centru, explorează perpendicular sau opus
            center_angle = math.atan2(dy, dx) if distance_to_center > 0 else 0
            
            # Schimbă direcția periodic pentru a explora și a evita pereții
            if random.random() < 0.2:  # 20% șansă să schimbe direcția (explorare activă)
                # Alege o direcție care NU e către centru (pentru a explora)
                if random.random() < 0.5:
                    # Perpendicular la direcția către centru (stânga sau dreapta)
                    perpendicular = random.choice([-1, 1])  # -1 pentru stânga, 1 pentru dreapta
                    angle = center_angle + (perpendicular * math.pi / 2) + random.uniform(-math.pi/4, math.pi/4)
                else:
                    # Opus direcției către centru (departe de centru)
                    angle = center_angle + math.pi + random.uniform(-math.pi/3, math.pi/3)
                
                self.velocity_x = math.cos(angle) * self.speed
                self.velocity_y = math.sin(angle) * self.speed
            # Altfel, continuă în direcția curentă (dacă există)
            elif abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
                # Dacă nu se mișcă, forțează o direcție perpendiculară pe centru
                perpendicular = random.choice([-1, 1])
                angle = center_angle + (perpendicular * math.pi / 2) + random.uniform(-math.pi/4, math.pi/4)
                self.velocity_x = math.cos(angle) * self.speed
                self.velocity_y = math.sin(angle) * self.speed

    def _build_search_waypoints(self):
        """Construiește o listă de puncte de căutare care acoperă harta sistematic (colțuri, margini, centru)."""
        margin = TILE_SIZE * 2
        W = MAP_WIDTH * TILE_SIZE
        H = MAP_HEIGHT * TILE_SIZE
        points = []
        # Colțuri
        points.extend([
            (margin, margin),
            (W - margin, margin),
            (W - margin, H - margin),
            (margin, H - margin),
        ])
        # Mijloacele marginilor
        points.extend([
            (W // 2, margin),
            (W - margin, H // 2),
            (W // 2, H - margin),
            (margin, H // 2),
        ])
        # Puncte intermediare către centru (cvadrante)
        points.extend([
            (W // 4, H // 4),
            (3 * W // 4, H // 4),
            (3 * W // 4, 3 * H // 4),
            (W // 4, 3 * H // 4),
        ])
        # Center last
        points.append((W // 2, H // 2))
        self.search_waypoints = points
        # Pornim din cel mai apropiat waypoint pentru eficiență
        dists = [math.hypot(px - self.x, py - self.y) for (px, py) in points]
        self.search_index = dists.index(min(dists)) if points else 0
    
    def apply_movement(self, obstacles):
        """Aplică mișcarea și verifică coliziuni"""
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y
        
        # Verifică limitele hărții
        new_x = max(AGENT_SIZE//2, min(MAP_WIDTH * TILE_SIZE - AGENT_SIZE//2, new_x))
        new_y = max(AGENT_SIZE//2, min(MAP_HEIGHT * TILE_SIZE - AGENT_SIZE//2, new_y))
        
        # Verifică coliziuni cu obstacole
        if not self.check_collision(new_x, new_y, obstacles):
            self.x = new_x
            self.y = new_y
        else:
            # Încearcă să aluneci de-a lungul obstacolului (mișcare doar pe X sau doar pe Y)
            moved = False
            if not self.check_collision(new_x, self.y, obstacles):
                self.x = new_x
                moved = True
            elif not self.check_collision(self.x, new_y, obstacles):
                self.y = new_y
                moved = True
            
            if not moved:
                # Dacă nu s-a putut mișca deloc, încearcă să ocolești obstacolul
                # Verifică dacă există o cale liberă pe o distanță mai mare
                current_angle = math.atan2(self.velocity_y, self.velocity_x) if (abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1) else 0
                
                # Dacă nu avem direcție, folosim direcția către centru
                if abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
                    map_center_x = (MAP_WIDTH * TILE_SIZE) / 2
                    map_center_y = (MAP_HEIGHT * TILE_SIZE) / 2
                    dx = map_center_x - self.x
                    dy = map_center_y - self.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        current_angle = math.atan2(dy, dx)
                
                # Încearcă 16 direcții (toate direcțiile principale și intermediare)
                # Testează la distanțe mai mari pentru a ocoli pereții închisi
                test_directions = []
                for i in range(16):  # 16 direcții (22.5 grade între ele)
                    angle = (2 * math.pi * i) / 16
                    test_directions.append(angle)
                
                # Testează fiecare direcție verificând dacă există o cale liberă pe o distanță suficientă
                best_direction = None
                best_distance = 0
                
                for test_angle in test_directions:
                    # Testează dacă direcția e liberă pe o distanță mai mare (pentru a scăpa din colțuri)
                    test_distance = 0
                    step_size = self.speed * 2
                    max_test_distance = self.speed * 8  # Testează până la 8 pași înainte
                    
                    for distance in range(int(step_size), int(max_test_distance), int(step_size)):
                        test_x = self.x + math.cos(test_angle) * distance
                        test_y = self.y + math.sin(test_angle) * distance
                        
                        if self.check_collision(test_x, test_y, obstacles):
                            break  # Blocat, oprește testarea
                        
                        test_distance = distance
                    
                    # Dacă această direcție e mai bună (mai liberă), o salvează
                    if test_distance > best_distance:
                        best_distance = test_distance
                        best_direction = test_angle
                
                # Dacă am găsit o direcție bună, aplică-o
                if best_direction is not None and best_distance > 0:
                    # Aplică direcția cu o distanță suficientă pentru a scăpa
                    move_distance = min(best_distance, self.speed * 3)
                    self.velocity_x = math.cos(best_direction) * self.speed * 2
                    self.velocity_y = math.sin(best_direction) * self.speed * 2
                    
                    # Verifică dacă poate merge în direcția nouă
                    test_x = self.x + self.velocity_x
                    test_y = self.y + self.velocity_y
                    if not self.check_collision(test_x, test_y, obstacles):
                        self.x = test_x
                        self.y = test_y
                        moved = True
                
                if not moved:
                    # Dacă niciuna dintre direcții nu funcționează, încearcă să te îndepărtezi de obstacol
                    # Găsește cel mai apropiat obstacol
                    nearest_obstacle = None
                    min_dist = float('inf')
                    
                    for obstacle in obstacles:
                        if not obstacle.alive:
                            continue
                        dist = math.sqrt((self.x - obstacle.rect.centerx)**2 + (self.y - obstacle.rect.centery)**2)
                        if dist < min_dist:
                            min_dist = dist
                            nearest_obstacle = obstacle
                    
                    if nearest_obstacle and min_dist < AGENT_SIZE * 3:
                        # Calculează direcția opusă obstacolului
                        dx = self.x - nearest_obstacle.rect.centerx
                        dy = self.y - nearest_obstacle.rect.centery
                        dist = math.sqrt(dx*dx + dy*dy)
                        
                        if dist > 0:
                            # Normalizează și aplică velocitatea departe de obstacol
                            self.velocity_x = (dx / dist) * self.speed * 1.2
                            self.velocity_y = (dy / dist) * self.speed * 1.2
                            
                            # Verifică dacă poate merge în direcția nouă
                            test_x = self.x + self.velocity_x
                            test_y = self.y + self.velocity_y
                            if not self.check_collision(test_x, test_y, obstacles):
                                self.x = test_x
                                self.y = test_y
                                moved = True
                    
                    if not moved:
                        # Dacă încă nu s-a putut mișca, resetează calea și velocitatea
                        self.path = []
                        self.path_update_time = 0
                        # Redu velocitatea pentru a evita blocajele
                        self.velocity_x *= 0.3
                        self.velocity_y *= 0.3
    
    def check_collision(self, x, y, obstacles):
        """Verifică coliziune cu obstacole"""
        # Convertim la float pentru a evita probleme cu numpy types
        x = float(x)
        y = float(y)
        agent_rect = pygame.Rect(x - AGENT_SIZE//2, y - AGENT_SIZE//2, AGENT_SIZE, AGENT_SIZE)
        for obstacle in obstacles:
            if obstacle.alive and agent_rect.colliderect(obstacle.rect):
                return True
        return False
    
    def try_attack(self, current_time, projectiles):
        """Încearcă să atace ținta cu proiectile"""
        if not self.target or not self.target.alive:
            return
        
        distance = self.distance_to(self.target)
        if distance <= AGENT_ATTACK_RANGE:
            if current_time - self.last_attack_time >= AGENT_ATTACK_COOLDOWN:
                # Calculează unghiul către țintă
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                angle_to_target = math.atan2(dy, dx)
                
                # Creează proiectil cu owner pentru tracking statistici
                projectile = Projectile(self.x, self.y, angle_to_target, self.team_id, PROJECTILE_DAMAGE, owner=self)
                projectiles.append(projectile)
                
                self.last_attack_time = current_time
    
    def take_damage(self, damage):
        """Primește damage"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
    
    def distance_to(self, other):
        """Calculează distanța până la alt agent"""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx*dx + dy*dy)
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Desenează agentul"""
        if not self.alive:
            # Desenează mort (X roșu)
            x_pos = int(self.x - camera_x)
            y_pos = int(self.y - camera_y)
            pygame.draw.line(screen, (200, 0, 0), 
                           (x_pos - 10, y_pos - 10), 
                           (x_pos + 10, y_pos + 10), 3)
            pygame.draw.line(screen, (200, 0, 0), 
                           (x_pos + 10, y_pos - 10), 
                           (x_pos - 10, y_pos + 10), 3)
            return
        
        # Desenează calea (pentru debugging)
        if self.path:
            for i in range(len(self.path) - 1):
                p1 = (int(self.path[i][0] - camera_x), int(self.path[i][1] - camera_y))
                p2 = (int(self.path[i+1][0] - camera_x), int(self.path[i+1][1] - camera_y))
                pygame.draw.line(screen, (255, 255, 0), p1, p2, 1)
        
        # Obține culoarea corectă (deschisă pentru comunicare limitată)
        agent_color = self.get_color()
        
        # Desenează corpul agentului
        pygame.draw.circle(screen, agent_color, 
                         (int(self.x - camera_x), int(self.y - camera_y)), 
                         AGENT_SIZE // 2)
        
        # Desenează contur
        pygame.draw.circle(screen, (0, 0, 0), 
                         (int(self.x - camera_x), int(self.y - camera_y)), 
                         AGENT_SIZE // 2, 2)
        
        # Desenează direcția (o linie mică către direcția facing)
        end_x = self.x + math.cos(self.facing_angle) * (AGENT_SIZE // 2 + 10)
        end_y = self.y + math.sin(self.facing_angle) * (AGENT_SIZE // 2 + 10)
        pygame.draw.line(screen, (255, 255, 255),
                       (int(self.x - camera_x), int(self.y - camera_y)),
                       (int(end_x - camera_x), int(end_y - camera_y)), 3)
        
        # Desenează LoS (con semi-transparent)
        los_color = (*agent_color, 50)  # Semi-transparent
        los_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Calculează punctele pentru con
        los_angle_rad = math.radians(AGENT_LOS_ANGLE / 2)
        angle1 = self.facing_angle - los_angle_rad
        angle2 = self.facing_angle + los_angle_rad
        
        # Punctele conului
        point1 = (
            int(self.x + math.cos(angle1) * AGENT_LOS_RANGE - camera_x),
            int(self.y + math.sin(angle1) * AGENT_LOS_RANGE - camera_y)
        )
        point2 = (
            int(self.x + math.cos(angle2) * AGENT_LOS_RANGE - camera_x),
            int(self.y + math.sin(angle2) * AGENT_LOS_RANGE - camera_y)
        )
        center = (int(self.x - camera_x), int(self.y - camera_y))
        
        # Desenează conul LoS
        pygame.draw.polygon(los_surface, los_color, [center, point1, point2])
        screen.blit(los_surface, (0, 0))
        
        # Bara de viață
        health_bar_width = AGENT_SIZE
        health_bar_height = 4
        health_percentage = self.health / AGENT_MAX_HEALTH
        
        bar_x = self.x - camera_x - health_bar_width // 2
        bar_y = self.y - camera_y - AGENT_SIZE // 2 - 8
        
        # Fundal bara
        pygame.draw.rect(screen, (255, 0, 0), 
                        (bar_x, bar_y, health_bar_width, health_bar_height))
        # Viață curentă
        pygame.draw.rect(screen, (0, 255, 0), 
                        (bar_x, bar_y, health_bar_width * health_percentage, health_bar_height))