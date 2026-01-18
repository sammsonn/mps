import pygame
import random
from config import *


class KingOfTheHillMode:
    def __init__(self, agents, game_map, statistics_tracker=None):
        self.agents = agents
        self.game_map = game_map
        self.statistics_tracker = statistics_tracker
        self.time_limit = KOTH_TIME_LIMIT
        self.time_to_win = KOTH_TIME_TO_WIN
        self.start_time = pygame.time.get_ticks()
        self.end_time = None  # Timpul când jocul s-a terminat
        self.game_over = False
        self.winner = None
       
        # Timp acumulat în zonă pentru fiecare echipă (în secunde)
        self.team_zone_time = {0: 0.0, 1: 0.0}
        self.last_update_time = pygame.time.get_ticks()
       
        # O SINGURĂ ZONĂ CENTRALĂ pe care se luptă ambele echipe
        center_x = (MAP_WIDTH * TILE_SIZE) / 2
        center_y = (MAP_HEIGHT * TILE_SIZE) / 2
        self.central_zone = pygame.Rect(
            center_x - KOTH_ZONE_SIZE // 2,
            center_y - KOTH_ZONE_SIZE // 2,
            KOTH_ZONE_SIZE,
            KOTH_ZONE_SIZE
        )
       
        # Baze pentru respawn (colțuri opuse)
        spawn_margin = TILE_SIZE * 3
        self.bases = {
            0: (spawn_margin, spawn_margin),  # Stânga sus
            1: (MAP_WIDTH * TILE_SIZE - spawn_margin, MAP_HEIGHT * TILE_SIZE - spawn_margin)  # Dreapta jos
        }
       
        # Tracking pentru agenți morți
        self.respawn_queue = []  # (agent, death_time)
   
    def update(self):
        """Verifică condiția de victorie și acumulează timp în zonă"""
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
       
        # Actualizează DPS tracking
        if self.statistics_tracker:
            # Pentru DPS, folosim un dicționar cu zona centrală
            zones_dict = {0: self.central_zone, 1: self.central_zone}
            self.statistics_tracker.update_koth_dps(self.agents, zones_dict, current_time)
       
        # Acumulează timp în zonă pentru fiecare echipă
        # Actualizează la fiecare 100ms pentru precizie
        if current_time - self.last_update_time >= 100:
            self.accumulate_zone_time()
            self.last_update_time = current_time
       
        # Verifică dacă o echipă a atins timpul necesar pentru victorie
        for team_id, zone_time in self.team_zone_time.items():
            if zone_time >= self.time_to_win:
                self.winner = team_id
                self.game_over = True
                # Salvează momentul când jocul s-a terminat pentru timer
                if self.end_time is None:
                    self.end_time = current_time
                # Îngheață statisticile DPS
                if self.statistics_tracker:
                    self.statistics_tracker.freeze_dps()
                return
   
    def accumulate_zone_time(self):
        """Acumulează timp pentru echipele care controlează zona centrală"""
        # Verifică câți agenți din fiecare echipă sunt în zona centrală
        agents_in_zone = {0: 0, 1: 0}
       
        for agent in self.agents:
            if not agent.alive:
                continue
           
            if self.central_zone.collidepoint(agent.x, agent.y):
                agents_in_zone[agent.team_id] += 1
       
        # Timpul se acumulează doar dacă:
        # 1. Există agenți din echipă în zonă
        # 2. NU există agenți inamici în zonă (controlează zona)
        for team_id in [0, 1]:
            enemy_team = 1 - team_id
            if agents_in_zone[team_id] > 0 and agents_in_zone[enemy_team] == 0:
                # Controlează zona, acumulează timp (100ms = 0.1 secunde)
                self.team_zone_time[team_id] += 0.1
   
    def process_respawns(self, current_time):
        """Procesează respawn-ul agenților morți"""
        for agent, death_time in self.respawn_queue[:]:
            if current_time - death_time >= KOTH_RESPAWN_TIME:
                # Verifică dacă agentul e încă mort (nu a fost deja respawn-at)
                if not agent.alive:
                    # Folosește get_spawn_position pentru a găsi o poziție liberă (fără obstacole)
                    spawn_x, spawn_y = self.game_map.get_spawn_position(agent.team_id, 2)
                   
                    agent.x = spawn_x
                    agent.y = spawn_y
                    agent.health = AGENT_MAX_HEALTH
                    agent.alive = True
                    agent.path = []
                    agent.target = None
                    agent.velocity_x = 0
                    agent.velocity_y = 0
                    agent.stuck_counter = 0
                   
                    # Resetează tracking pentru statistici
                    if self.statistics_tracker:
                        self.statistics_tracker.on_agent_spawn(agent)
               
                # Elimină din coadă
                self.respawn_queue.remove((agent, death_time))
   
    def on_agent_death(self, agent):
        """Apelat când un agent moare"""
        current_time = pygame.time.get_ticks()
       
        # Verifică dacă agentul nu e deja în coadă (evită duplicate)
        already_in_queue = any(a == agent for a, _ in self.respawn_queue)
       
        if not already_in_queue:
            self.respawn_queue.append((agent, current_time))
   
    def end_game_by_time(self):
        """Închide jocul bazat pe timp - câștigă echipa cu cel mai mult timp în zonă"""
        if self.team_zone_time[0] > self.team_zone_time[1]:
            self.winner = 0
        elif self.team_zone_time[1] > self.team_zone_time[0]:
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
        """Desenează UI-ul modului King of the Hill"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
       
        # Timp rămas
        time_text = font.render(f"Time: {int(self.get_remaining_time())}s", True, (255, 255, 255))
        screen.blit(time_text, (SCREEN_WIDTH // 2 - 60, 10))
       
        # Timp în zonă pentru fiecare echipă
        y_offset = 50
        for team_id in [0, 1]:
            zone_time = self.team_zone_time[team_id]
            time_str = f"{zone_time:.1f}s"
            text = font.render(f"Team {team_id + 1}: {time_str}/{self.time_to_win}s", True, TEAM_COLORS[team_id])
            x_pos = 10 if team_id == 0 else SCREEN_WIDTH - 250
            screen.blit(text, (x_pos, y_offset))
       
        # Contorizare agenți vii
        y_offset = 100
        teams_alive = {}
        for agent in self.agents:
            if agent.alive:
                if agent.team_id not in teams_alive:
                    teams_alive[agent.team_id] = 0
                teams_alive[agent.team_id] += 1
       
        for team_id in [0, 1]:
            count = teams_alive.get(team_id, 0)
            text = small_font.render(f"Alive: {count}", True, TEAM_COLORS[team_id])
            x_pos = 10 if team_id == 0 else SCREEN_WIDTH - 150
            screen.blit(text, (x_pos, y_offset))
       
        # Desenează zona centrală
        # Zona semi-transparentă (galben pentru zona neutră)
        zone_surface = pygame.Surface((self.central_zone.width, self.central_zone.height), pygame.SRCALPHA)
        # Culoare bazată pe care echipă controlează zona
        controlling_team = None
        agents_in_zone = {0: 0, 1: 0}
        for agent in self.agents:
            if agent.alive and self.central_zone.collidepoint(agent.x, agent.y):
                agents_in_zone[agent.team_id] += 1
       
        if agents_in_zone[0] > 0 and agents_in_zone[1] == 0:
            controlling_team = 0
        elif agents_in_zone[1] > 0 and agents_in_zone[0] == 0:
            controlling_team = 1
       
        if controlling_team is not None:
            color = (*TEAM_COLORS[controlling_team], 80)  # Semi-transparent cu culoarea echipei
        else:
            color = (255, 255, 0, 50)  # Galben semi-transparent pentru zona neutră/contested
       
        zone_surface.fill(color)
        screen.blit(zone_surface, (self.central_zone.x, self.central_zone.y))
       
        # Contur zonă (galben pentru zona centrală)
        pygame.draw.rect(screen, (255, 255, 0), self.central_zone, 3)
       
        # Text în zonă
        zone_font = pygame.font.Font(None, 24)
        zone_text = zone_font.render("CENTRAL ZONE", True, (255, 255, 255))
        text_rect = zone_text.get_rect(center=(self.central_zone.centerx, self.central_zone.centery))
        screen.blit(zone_text, text_rect)
       
        # Afișează DPS
        if self.statistics_tracker:
            y_offset = 130
            small_font = pygame.font.Font(None, 20)
           
            for team_id in [0, 1]:
                dps_in = self.statistics_tracker.get_koth_dps(team_id, in_zone=True)
                dps_out = self.statistics_tracker.get_koth_dps(team_id, in_zone=False)
               
                text = small_font.render(f"DPS in zone: {dps_in:.1f}", True, TEAM_COLORS[team_id])
                x_pos = 10 if team_id == 0 else SCREEN_WIDTH - 200
                screen.blit(text, (x_pos, y_offset))
               
                text = small_font.render(f"DPS out zone: {dps_out:.1f}", True, TEAM_COLORS[team_id])
                screen.blit(text, (x_pos, y_offset + 20))
               
                # Statistici suplimentare
                avg_time_alive = self.statistics_tracker.get_team_avg_time_alive(team_id)
                text = small_font.render(f"Avg time alive: {avg_time_alive:.1f}s", True, TEAM_COLORS[team_id])
                screen.blit(text, (x_pos, y_offset + 40))
               
                avg_distance = self.statistics_tracker.get_team_avg_distance(team_id)
                text = small_font.render(f"Avg distance: {avg_distance:.0f}", True, TEAM_COLORS[team_id])
                screen.blit(text, (x_pos, y_offset + 60))
               
                #kills, deaths, assists = self.statistics_tracker.get_team_kda(team_id)
                #text = small_font.render(f"K/D/A: {kills}/{deaths}/{assists}", True, TEAM_COLORS[team_id])
                #screen.blit(text, (x_pos, y_offset + 80))
               
                # Total bullets fired
                total_shots = self.statistics_tracker.get_team_total_shots(team_id)
                text = small_font.render(f"Bullets fired: {total_shots}", True, TEAM_COLORS[team_id])
                screen.blit(text, (x_pos, y_offset + 100))
       
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





