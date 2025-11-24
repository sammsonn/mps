import pygame
from config import *

class SurvivalMode:
    def __init__(self, agents):
        self.agents = agents
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
        
        # Contorizare echipe
        y_offset = 50
        teams_alive = {}
        for agent in self.agents:
            if agent.alive:
                if agent.team_id not in teams_alive:
                    teams_alive[agent.team_id] = 0
                teams_alive[agent.team_id] += 1
        
        for team_id, count in sorted(teams_alive.items()):
            text = small_font.render(f"Team {team_id + 1}: {count}", True, TEAM_COLORS[team_id])
            screen.blit(text, (10, y_offset))
            y_offset += 30
        
        # Mesaj de victorie
        if self.game_over:
            game_over_text = font.render("GAME OVER!", True, (255, 255, 0))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            
            if self.winner is not None:
                winner_text = font.render(f"Team {self.winner + 1} Wins!", True, TEAM_COLORS[self.winner])
                screen.blit(winner_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))