import pygame
import sys
import random
from config import *
from game_map import GameMap
from agent import Agent
from survival_mode import SurvivalMode
from koth_mode import KingOfTheHillMode
from ctf_mode import CaptureTheFlagMode
from menu import Menu
from projectile import Projectile
from communication import MessageBus
from statistics import StatisticsTracker

class Game:
    def __init__(self, game_mode="Survival"):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Micro Battle - {game_mode} Mode")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_mode_name = game_mode
        # Bus de mesaje pentru comunicare între agenți
        self.message_bus = MessageBus()
        
        # Creează harta (cu parametri specifici pentru game mode)
        self.game_map = GameMap(game_mode)
        
        # Creează agenții bazat pe modul de joc
        self.agents = []
        
        if game_mode == "King of the Hill":
            num_teams = 2
            agents_per_team = KOTH_AGENTS_PER_TEAM
            
            for team_id in range(num_teams):
                for i in range(agents_per_team):
                    x, y = self.game_map.get_spawn_position(team_id, num_teams)
                    
                    # Alocă roluri: unii atacatori, alții apărători (random)
                    role = ROLE_ATTACKER #if random.random() < 0.5 else ROLE_DEFENDER
                    agent = Agent(x, y, team_id, role)
                    agent.agent_id = f"agent_{team_id}_{i}"
                    self.agents.append(agent)
        elif game_mode == "Capture the Flag":
            num_teams = 2
            agents_per_team = CTF_AGENTS_PER_TEAM
            for team_id in range(num_teams):
                for i in range(agents_per_team):
                    x, y = self.game_map.get_spawn_position(team_id, num_teams)
                    # Toți agenții sunt atacatori
                    agent = Agent(x, y, team_id, ROLE_ATTACKER)
                    agent.agent_id = f"agent_{team_id}_{i}"
                    self.agents.append(agent)
        else:
            # Survival mode - 5 agenți per echipă, fără roluri
            num_teams = 2
            agents_per_team = 5
            
            for team_id in range(num_teams):
                for i in range(agents_per_team):
                    x, y = self.game_map.get_spawn_position(team_id, num_teams)
                    agent = Agent(x, y, team_id)
                    agent.agent_id = f"agent_{team_id}_{i}"
                    self.agents.append(agent)
        
        # Lista de proiectile
        self.projectiles = []
        
        # Creează tracker-ul de statistici
        self.statistics_tracker = StatisticsTracker()
        
        # Inițializează statistici pentru agenți
        for agent in self.agents:
            self.statistics_tracker.on_agent_spawn(agent)
        
        # Index agenți pentru bus
        self.agent_index = {getattr(a, 'agent_id', f'id_{idx}'): a for idx, a in enumerate(self.agents)}
        self.message_bus.set_agents(self.agent_index)

        # Inițializează modul de joc ales
        if game_mode == "Survival":
            self.game_mode = SurvivalMode(self.agents)
        elif game_mode == "King of the Hill":
            self.game_mode = KingOfTheHillMode(self.agents, self.game_map, self.statistics_tracker)
            # Setează zona centrală ca țintă pentru toți agenții
            for agent in self.agents:
                agent.target_zone = self.game_mode.central_zone
        elif game_mode == "Capture the Flag":
            self.game_mode = CaptureTheFlagMode(self.agents, self.game_map, self.statistics_tracker, message_bus=self.message_bus)
            # Setează referințe pentru fiecare agent
            for agent in self.agents:
                # Baza proprie (unde să aducă steagul)
                agent.enemy_base = self.game_mode.bases[agent.team_id]
                # Steagul echipei adverse (să-l captureze)
                enemy_team = 1 - agent.team_id
                agent.target_flag = self.game_mode.flags[enemy_team]  # Steagul INAMIC (să-l captureze)
                agent.own_flag = self.game_mode.flags[agent.team_id]  # Steagul propriu (pentru apărare)
        else:
            # Default la Survival dacă nu recunoaște modul
            self.game_mode = SurvivalMode(self.agents)
    
    def run(self):
        """Bucla principală a jocului"""
        while self.running:
            result = self.handle_events()
            if result == "MENU":
                return "MENU"
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        return None
    
    def handle_events(self):
        """Gestionează evenimente"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.game_mode.game_over:
                    # Reporni jocul cu același mod
                    self.__init__(self.game_mode_name)
                elif event.key == pygame.K_m and self.game_mode.game_over:
                    # Înapoi la meniu
                    self.running = False
                    return "MENU"
        return None
    
    def update(self):
        """Actualizează starea jocului"""
        if not self.game_mode.game_over:
            current_time = pygame.time.get_ticks()
            
            # Actualizează agenții
            for agent in self.agents:
                was_alive = agent.alive
                
                # Actualizează tracking mișcare
                if agent.alive:
                    self.statistics_tracker.update_agent_movement(agent)
                # Livrează mesaje și procesează inbox
                agent.inbox = self.message_bus.collect(agent.team_id, current_time)
                agent.process_inbox(self.message_bus)
                # Update cu bus pentru broadcast
                agent.update(self.agents, self.game_map.obstacles, current_time, message_bus=self.message_bus)
                
                # Verifică dacă agentul tocmai a murit și notifică game mode-ul (pentru respawn)
                if was_alive and not agent.alive:
                    self.statistics_tracker.on_agent_death(agent)
                    if self.game_mode_name in ["King of the Hill", "Capture the Flag"]:
                        self.game_mode.on_agent_death(agent)
                
                # Verifică dacă agentul trebuie să tragă
                if agent.alive and agent.target and getattr(agent.target, "alive", False):
                    self.statistics_tracker.on_shot_fired(agent)
                    agent.try_attack(current_time, self.projectiles)
            
            # Actualizează proiectilele
            for projectile in self.projectiles[:]:
                projectile.update(current_time)
                
                # Verifică coliziuni cu agenți
                for agent in self.agents:
                    was_alive_before = agent.alive
                    if projectile.check_collision_with_agent(agent):
                        # Track damage și hit
                        if projectile.owner and projectile.team_id != agent.team_id:
                            self.statistics_tracker.on_damage_dealt(
                                projectile.owner,
                                projectile.damage,
                                agent
                            )
                            self.statistics_tracker.on_shot_hit(projectile.owner)
                            
                            # Pentru KOTH, verifică dacă damage-ul a fost provocat în zonă sau în afara zonei
                            # Verificăm poziția agentului care a tras (owner), nu a celui lovit
                            if self.game_mode_name == "King of the Hill" and self.statistics_tracker and projectile.owner:
                                in_zone = False
                                if hasattr(self.game_mode, 'central_zone'):
                                    # Zona centrală unică
                                    if self.game_mode.central_zone.collidepoint(projectile.owner.x, projectile.owner.y):
                                        in_zone = True
                                else:
                                    # Fallback pentru vechea versiune cu multiple zone
                                    for zone in self.game_mode.zones.values():
                                        if zone.collidepoint(projectile.owner.x, projectile.owner.y):
                                            in_zone = True
                                            break
                                self.statistics_tracker.on_koth_damage(projectile.owner, projectile.damage, in_zone)
                        
                        # Verifică dacă agentul tocmai a murit (din cauza proiectilului)
                        if was_alive_before and not agent.alive:
                            self.statistics_tracker.on_agent_death(agent)
                            if self.game_mode_name in ["King of the Hill", "Capture the Flag"]:
                                self.game_mode.on_agent_death(agent)
                        break
                
                # Verifică coliziuni cu obstacole
                hit_obstacle = projectile.check_collision_with_obstacles(self.game_map.obstacles)
                if hit_obstacle:
                    hit_obstacle.take_damage(PROJECTILE_DAMAGE)
                
                # Elimină proiectile moarte
                if not projectile.alive:
                    self.projectiles.remove(projectile)
            
            # Actualizează obstacole (elimină cele distruse)
            self.game_map.update_obstacles()
            # Curăță mesaje expirate
            self.message_bus.cleanup(current_time)
        
        self.game_mode.update()
    
    def draw(self):
        """Desenează totul"""
        self.game_map.draw(self.screen)
        
        # Desenează proiectilele
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Desenează agenții
        for agent in self.agents:
            agent.draw(self.screen)
        
        # Desenează proiectilele
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        self.game_mode.draw_ui(self.screen)
        
        # Instrucțiuni
        if self.game_mode.game_over:
            font = pygame.font.Font(None, 24)
            restart_text = font.render("Press R to restart, M for menu, ESC to quit", True, (255, 255, 255))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()

def main():
    while True:
        # Afișează meniul
        menu = Menu()
        selected_mode = menu.run()
        
        # Verifică dacă utilizatorul a ieșit
        if selected_mode is None:
            break
        
        # Pornește jocul cu modul selectat
        game = Game(selected_mode)
        result = game.run()
        
        # Verifică dacă utilizatorul vrea să se întoarcă la meniu
        if result != "MENU":
            break

if __name__ == "__main__":
    main()