import pygame
from config import *


class SurvivalMode:
    def __init__(self, agents, statistics_tracker=None):
        self.agents = agents
        self.statistics_tracker = statistics_tracker
        self.time_limit = SURVIVAL_TIME_LIMIT
        self.start_time = pygame.time.get_ticks()
        self.end_time = None  # Timpul când jocul s-a terminat
        self.game_over = False
        self.winner = None
   
    def update(self):
        """Verifică condiția de victorie"""
        if self.game_over:
            return
       
        # Verifică timpul
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        if elapsed_time >= self.time_limit:
            self.end_game_by_time()
            return
       
        # Verifică dacă o echipă a fost eliminată
        teams_alive = {}
        for agent in self.agents:
            if agent.alive:
                if agent.team_id not in teams_alive:
                    teams_alive[agent.team_id] = 0
                teams_alive[agent.team_id] += 1
       
        if len(teams_alive) <= 1:
            if len(teams_alive) == 1:
                self.winner = list(teams_alive.keys())[0]
            self.game_over = True
            # Salvează momentul când jocul s-a terminat pentru timer
            if self.end_time is None:
                self.end_time = pygame.time.get_ticks()
            # Îngheață statisticile DPS
            if self.statistics_tracker:
                self.statistics_tracker.freeze_dps()
   
    def end_game_by_time(self):
        """Închide jocul bazat pe timp - câștigă echipa cu cei mai mulți agenți"""
        teams_count = {}
        for agent in self.agents:
            if agent.alive:
                if agent.team_id not in teams_count:
                    teams_count[agent.team_id] = 0
                teams_count[agent.team_id] += 1
       
        if teams_count:
            self.winner = max(teams_count, key=teams_count.get)
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
        """Desenează UI-ul modului Survival"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
       
        # Timp rămas (pe mijloc, ca la celelalte moduri)
        time_text = font.render(f"Time: {int(self.get_remaining_time())}s", True, (255, 255, 255))
        screen.blit(time_text, (SCREEN_WIDTH // 2 - 60, 10))
       
        # Statistici pentru fiecare echipă pe părțile laterale
        if self.statistics_tracker:
            y_offset = 50
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
       
        # Mesaj de victorie
        if self.game_over:
            game_over_text = font.render("GAME OVER!", True, (255, 255, 0))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
           
            if self.winner is not None:
                winner_text = font.render(f"Team {self.winner + 1} Wins!", True, TEAM_COLORS[self.winner])
                screen.blit(winner_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))



