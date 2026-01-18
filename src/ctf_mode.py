import pygame
import random
from config import *


class Flag:
    """Reprezintă un steag care poate fi capturat"""
    def __init__(self, x, y, team_id):
        self.x = x
        self.y = y
        self.home_x = x  # Poziția inițială
        self.home_y = y
        self.team_id = team_id  # Echipa căreia îi aparține
        self.carrier = None  # Agentul care îl poartă
        self.at_base = True  # Dacă e la baza proprie
        self.color = TEAM_COLORS[team_id]
   
    def is_carried(self):
        """Verifică dacă steagul este purtat de cineva"""
        return self.carrier is not None and self.carrier.alive
   
    def reset(self):
        """Resetează steagul la baza proprie"""
        self.x = self.home_x
        self.y = self.home_y
        self.carrier = None
        self.at_base = True
   
    def update(self):
        """Actualizează poziția steagului"""
        if self.is_carried():
            # Steagul urmează carrier-ul
            self.x = self.carrier.x
            self.y = self.carrier.y
            self.at_base = False
        elif not self.at_base and self.carrier is None:
            # Steagul a fost scăpat, rămâne pe loc pentru a fi recuperat
            pass
   
    def draw(self, screen, camera_x=0, camera_y=0):
        """Desenează steagul"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
       
        # Desenează baza steagului (baza de respawn)
        base_color = (*self.color, 100)  # Semi-transparent
        base_surface = pygame.Surface((CTF_FLAG_CAPTURE_RADIUS * 2, CTF_FLAG_CAPTURE_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(base_surface, base_color, (CTF_FLAG_CAPTURE_RADIUS, CTF_FLAG_CAPTURE_RADIUS), CTF_FLAG_CAPTURE_RADIUS)
        screen.blit(base_surface, (int(self.home_x - camera_x - CTF_FLAG_CAPTURE_RADIUS),
                                    int(self.home_y - camera_y - CTF_FLAG_CAPTURE_RADIUS)))
       
        # Desenează steagul propriu-zis
        if self.is_carried():
            # Steag purtat - deasupra carrier-ului
            flag_points = [
                (screen_x, screen_y - 20),
                (screen_x, screen_y - 5),
                (screen_x + 15, screen_y - 12)
            ]
            pygame.draw.polygon(screen, self.color, flag_points)
            pygame.draw.line(screen, (50, 50, 50), (screen_x, screen_y - 20), (screen_x, screen_y), 2)
        else:
            # Steag la bază sau scăpat
            flag_height = 25
            flag_width = 20
            # Catarg
            pygame.draw.line(screen, (50, 50, 50),
                           (screen_x, screen_y - flag_height),
                           (screen_x, screen_y), 3)
            # Steag
            flag_points = [
                (screen_x, screen_y - flag_height),
                (screen_x, screen_y - flag_height + 15),
                (screen_x + flag_width, screen_y - flag_height + 7)
            ]
            pygame.draw.polygon(screen, self.color, flag_points)
            pygame.draw.polygon(screen, (0, 0, 0), flag_points, 2)




class CaptureTheFlagMode:
    def __init__(self, agents, game_map, statistics_tracker=None, message_bus=None):
        self.agents = agents
        self.game_map = game_map
        self.statistics_tracker = statistics_tracker
        self.message_bus = message_bus
        self.time_limit = CTF_TIME_LIMIT
        self.max_points = CTF_MAX_POINTS
        self.start_time = pygame.time.get_ticks()
        self.end_time = None  # Timpul când jocul s-a terminat
        self.game_over = False
        self.winner = None
       
        # Puncte pentru fiecare echipă (steaguri capturate)
        self.team_scores = {0: 0, 1: 0}
       
        # Baze pentru fiecare echipă (unde se aduc steagurile)
        margin = TILE_SIZE * 2
        self.bases = {
            0: pygame.Rect(
                margin,
                margin,
                TILE_SIZE * 3,
                TILE_SIZE * 3
            ),
            1: pygame.Rect(
                MAP_WIDTH * TILE_SIZE - margin - TILE_SIZE * 3,
                MAP_HEIGHT * TILE_SIZE - margin - TILE_SIZE * 3,
                TILE_SIZE * 3,
                TILE_SIZE * 3
            )
        }
       
        # Creează steaguri pentru fiecare echipă
        # Steagul echipei 0 e în colțul stânga-sus (unde spawn-uiește echipa 0)
        # Steagul echipei 1 e în colțul dreapta-jos (unde spawn-uiește echipa 1)
        # Fiecare echipă trebuie să meargă la baza adversă să captureze steagul
        self.flags = {
            0: Flag(
                margin + TILE_SIZE * 1.5,
                margin + TILE_SIZE * 1.5,
                0
            ),
            1: Flag(
                MAP_WIDTH * TILE_SIZE - margin - TILE_SIZE * 1.5,
                MAP_HEIGHT * TILE_SIZE - margin - TILE_SIZE * 1.5,
                1
            )
        }
       
        # Tracking pentru agenți morți
        self.respawn_queue = []  # (agent, death_time)
   
    def update(self):
        """Verifică condiția de victorie și gestionează capturarea steagurilor"""
        if self.game_over:
            return
       
        current_time = pygame.time.get_ticks()
       
        # Verifică timpul
        elapsed_time = (current_time - self.start_time) / 1000
        if elapsed_time >= self.time_limit:
            self.end_game_by_time()
            return
       
        # Procesează respawn-uri
        self.process_respawns(current_time)
       
        # Actualizează steaguri
        for flag in self.flags.values():
            flag.update()
       
        # Verifică capturarea steagurilor
        self.check_flag_captures()
       
        # Verifică livrarea steagurilor
        self.check_flag_deliveries()
       
        # Verifică dacă o echipă a atins numărul maxim de puncte
        for team_id, score in self.team_scores.items():
            if score >= self.max_points:
                self.winner = team_id
                self.game_over = True
                # Salvează momentul când jocul s-a terminat pentru timer
                if self.end_time is None:
                    self.end_time = current_time
                # Îngheață statisticile DPS
                if self.statistics_tracker:
                    self.statistics_tracker.freeze_dps()
                return
   
    def check_flag_captures(self):
        """Verifică dacă agenții captează steaguri"""
        current_time = pygame.time.get_ticks()
       
        for agent in self.agents:
            if not agent.alive:
                continue
           
            # Un agent poate captura doar steagul echipei adverse
            enemy_team = 1 - agent.team_id
            enemy_flag = self.flags[enemy_team]
           
            # Verifică dacă agentul nu poartă deja un steag
            if agent.carrying_flag:
                continue
           
            # Verifică distanța până la steagul inamic
            dx = agent.x - enemy_flag.x
            dy = agent.y - enemy_flag.y
            distance = (dx*dx + dy*dy) ** 0.5
           
            # Poate captura steagul dacă:
            # 1. Steagul nu e purtat de altcineva
            # 2. Agentul e suficient de aproape
            if not enemy_flag.is_carried() and distance < CTF_FLAG_CAPTURE_RADIUS:
                # Captează steagul
                enemy_flag.carrier = agent
                enemy_flag.at_base = False
                agent.carrying_flag = enemy_flag
                agent.role = ROLE_CARRIER
                # Broadcast pentru ambele echipe
                if self.message_bus and hasattr(agent, 'agent_id'):
                    # Echipa victimă: FLAG_TAKEN -> urmărește carrier-ul inamic
                    from communication import Message
                    is_limited = getattr(agent, 'has_limited_communication', False)
                    msg_enemy = Message(
                        sender_id=agent.agent_id,
                        team_id=enemy_team,
                        msg_type="FLAG_TAKEN",
                        payload={"carrier_id": agent.agent_id, "x": round(agent.x, 3), "y": round(agent.y, 3)},
                        timestamp=current_time,
                        sender_x=round(agent.x, 3),
                        sender_y=round(agent.y, 3),
                        is_limited=is_limited
                    )
                    self.message_bus.publish(msg_enemy)
                    # Echipa carrier-ului: pentru escortă (opțional)
                    msg_friendly = Message(
                        sender_id=agent.agent_id,
                        team_id=agent.team_id,
                        msg_type="FLAG_TAKEN_FRIENDLY",
                        payload={"carrier_id": agent.agent_id, "x": round(agent.x, 3), "y": round(agent.y, 3)},
                        timestamp=current_time,
                        sender_x=round(agent.x, 3),
                        sender_y=round(agent.y, 3),
                        is_limited=is_limited
                    )
                    self.message_bus.publish(msg_friendly)
               
                # Track statistici
                if self.statistics_tracker:
                    self.statistics_tracker.on_flag_captured(agent, current_time)
   
    def check_flag_deliveries(self):
        """Verifică dacă agenții livrează steaguri la baza proprie"""
        current_time = pygame.time.get_ticks()
       
        for agent in self.agents:
            if not agent.alive or not agent.carrying_flag:
                continue
           
            # Verifică dacă agentul e în baza proprie
            own_base = self.bases[agent.team_id]
            if own_base.collidepoint(agent.x, agent.y):
                # Livrează steagul - punctaj!
                self.team_scores[agent.team_id] += 1
               
                # Track statistici
                if self.statistics_tracker:
                    self.statistics_tracker.on_flag_delivered(agent, current_time)
               
                # Resetează steagul la baza adversă
                agent.carrying_flag.reset()
                agent.carrying_flag = None
               
                # Agentul devine din nou doar atacator
                agent.role = ROLE_ATTACKER
                # Broadcast livrare
                if self.message_bus and hasattr(agent, 'agent_id'):
                    from communication import Message
                    for team in [0,1]:
                        self.message_bus.publish(Message(
                            sender_id=agent.agent_id,
                            team_id=team,
                            msg_type="FLAG_DELIVERED",
                            payload={"scoring_team": agent.team_id},
                            timestamp=current_time
                        ))
   
    def process_respawns(self, current_time):
        """Procesează respawn-ul agenților morți"""
        for agent, death_time in self.respawn_queue[:]:
            if current_time - death_time >= CTF_RESPAWN_TIME:
                # Respawn agentul în baza echipei
                base = self.bases[agent.team_id]
                agent.x = base.centerx + random.randint(-20, 20)
                agent.y = base.centery + random.randint(-20, 20)
                agent.health = AGENT_MAX_HEALTH
                agent.alive = True
                agent.path = []
                agent.target = None
                agent.carrying_flag = None
                agent.role = ROLE_ATTACKER  # Toți devin atacatori după respawn
                # Elimină din coadă
                self.respawn_queue.remove((agent, death_time))
   
    def on_agent_death(self, agent):
        """Apelat când un agent moare"""
        current_time = pygame.time.get_ticks()
       
        # Dacă purta un steag, îl scapă la poziția curentă
        if agent.carrying_flag:
            # Track statistici pentru steag scăpat
            if self.statistics_tracker:
                self.statistics_tracker.on_flag_dropped(agent, current_time)
           
            agent.carrying_flag.carrier = None
            # Steagul rămâne pe hartă la poziția unde a murit
            agent.carrying_flag = None
            # Broadcast FLAG_DROPPED
            if self.message_bus and hasattr(agent, 'agent_id'):
                from communication import Message
                is_limited = getattr(agent, 'has_limited_communication', False)
                for team in [0,1]:
                    self.message_bus.publish(Message(
                        sender_id=agent.agent_id,
                        team_id=team,
                        msg_type="FLAG_DROPPED",
                        payload={"x": round(agent.x, 3), "y": round(agent.y, 3)},
                        timestamp=current_time,
                        sender_x=round(agent.x, 3),
                        sender_y=round(agent.y, 3),
                        is_limited=is_limited
                    ))
       
        self.respawn_queue.append((agent, current_time))
   
    def end_game_by_time(self):
        """Închide jocul bazat pe timp - câștigă echipa cu cele mai multe puncte"""
        if self.team_scores[0] > self.team_scores[1]:
            self.winner = 0
        elif self.team_scores[1] > self.team_scores[0]:
            self.winner = 1
        else:
            self.winner = None  # Egalitate
        self.game_over = True
        # Salvează momentul când jocul s-a terminat pentru timer
        if self.end_time is None:
            self.end_time = pygame.time.get_ticks()
        # Îngheață statisticile DPS
        if self.statistics_tracker:
            self.statistics_tracker.freeze_dps()
   
    def get_remaining_time(self):
        """Returnează timpul rămas"""
        # Dacă jocul s-a terminat, returnează timpul rămas la momentul terminării
        if self.game_over and self.end_time is not None:
            elapsed = (self.end_time - self.start_time) / 1000
        else:
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        return max(0, self.time_limit - elapsed)
   
    def draw_ui(self, screen):
        """Desenează UI-ul modului Capture the Flag"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
       
        # Timp rămas
        time_text = font.render(f"Time: {int(self.get_remaining_time())}s", True, (255, 255, 255))
        screen.blit(time_text, (SCREEN_WIDTH // 2 - 60, 10))
       
        # Scoruri echipe
        y_offset = 50
        for team_id in [0, 1]:
            score = self.team_scores[team_id]
            text = font.render(f"Team {team_id + 1}: {score}/{self.max_points}", True, TEAM_COLORS[team_id])
            x_pos = 10 if team_id == 0 else SCREEN_WIDTH - 200
            screen.blit(text, (x_pos, y_offset))
       
        # Statistici pentru fiecare echipă pe părțile laterale
        if self.statistics_tracker:
            y_offset = 100
            small_font_stats = pygame.font.Font(None, 20)
           
            for team_id in [0, 1]:
                # Număr de jucători în viață
                teams_alive = {}
                for agent in self.agents:
                    if agent.alive:
                        if agent.team_id not in teams_alive:
                            teams_alive[agent.team_id] = 0
                        teams_alive[agent.team_id] += 1
               
                players_alive = teams_alive.get(team_id, 0)
                text = small_font_stats.render(f"Players alive: {players_alive}", True, TEAM_COLORS[team_id])
                x_pos = 10 if team_id == 0 else SCREEN_WIDTH - 200
                screen.blit(text, (x_pos, y_offset))
               
                # DPS
                dps = self.statistics_tracker.get_team_dps(team_id)
                text = small_font_stats.render(f"DPS: {dps:.1f}", True, TEAM_COLORS[team_id])
                screen.blit(text, (x_pos, y_offset + 20))
               
                # Avg time alive
                avg_time_alive = self.statistics_tracker.get_team_avg_time_alive(team_id)
                text = small_font_stats.render(f"Avg time alive: {avg_time_alive:.1f}s", True, TEAM_COLORS[team_id])
                screen.blit(text, (x_pos, y_offset + 40))
               
                # Avg distance traveled
                avg_distance = self.statistics_tracker.get_team_avg_distance(team_id)
                text = small_font_stats.render(f"Avg distance: {avg_distance:.0f}", True, TEAM_COLORS[team_id])
                screen.blit(text, (x_pos, y_offset + 60))
               
                # Total bullets fired
                total_shots = self.statistics_tracker.get_team_total_shots(team_id)
                text = small_font_stats.render(f"Bullets fired: {total_shots}", True, TEAM_COLORS[team_id])
                screen.blit(text, (x_pos, y_offset + 80))
       
        # Desenează bazele
        for team_id, base in self.bases.items():
            # Baza semi-transparentă
            base_surface = pygame.Surface((base.width, base.height), pygame.SRCALPHA)
            color = (*TEAM_COLORS[team_id], 30)  # Semi-transparent
            base_surface.fill(color)
            screen.blit(base_surface, (base.x, base.y))
           
            # Contur bază
            pygame.draw.rect(screen, TEAM_COLORS[team_id], base, 2)
       
        # Desenează steaguri
        for flag in self.flags.values():
            flag.draw(screen)
       
        # Afișează statistici CTF
        if self.statistics_tracker:
            y_offset = 200  # Mutat mai jos pentru a nu se suprapune cu statisticile echipelor
            small_font = pygame.font.Font(None, 20)
           
            avg_delivery = self.statistics_tracker.get_avg_delivery_time()
            avg_carry = self.statistics_tracker.get_avg_flag_carry_time()
           
            text = small_font.render(f"Avg delivery: {avg_delivery:.1f}s", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - 100, y_offset))
           
            text = small_font.render(f"Avg carry time: {avg_carry:.1f}s", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - 100, y_offset + 20))
       
        # Mesaj de victorie
        if self.game_over:
            game_over_text = font.render("GAME OVER!", True, (255, 255, 0))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
           
            if self.winner is not None:
                winner_text = font.render(f"Team {self.winner + 1} Wins!", True, TEAM_COLORS[self.winner])
                screen.blit(winner_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
            else:
                draw_text = font.render("Draw!", True, (255, 255, 255))
                screen.blit(draw_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))





