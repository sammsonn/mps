import numpy as np
import pygame
import random
from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from gymnasium.spaces import Box, Discrete
from config import *
from agent import Agent
from communication import MessageBus
from game_map import GameMap
from projectile import Projectile

class MicroBattleEnv(AECEnv):
    """Environment PettingZoo pentru Micro Battle"""
    
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "micro_battle_v0",
        "is_parallelizable": False,
    }
    
    def __init__(self, game_mode="Survival", render_mode=None):
        super().__init__()
        
        self.game_mode = game_mode
        self.render_mode = render_mode
        
        # Creează harta
        self.game_map = GameMap(game_mode)
        
        # Creează bus de mesaje
        self.message_bus = MessageBus()

        # Creează agenții
        self.agents_list = []
        self._create_agents()
        
        # Definește action space și observation space
        self._setup_spaces()
        
        # Variabile de stare
        self.projectiles = []
        self.current_time = 0
        
        # Screen pentru rendering
        if render_mode == "human":
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.screen = None
    
    def _create_agents(self):
        """Creează agenții pentru joc"""
        num_teams = 2
        
        if self.game_mode == "King of the Hill":
            agents_per_team = KOTH_AGENTS_PER_TEAM
        elif self.game_mode == "Capture the Flag":
            agents_per_team = CTF_AGENTS_PER_TEAM
        else:
            agents_per_team = 5
        
        for team_id in range(num_teams):
            for i in range(agents_per_team):
                x, y = self.game_map.get_spawn_position(team_id, num_teams)
                agent = Agent(x, y, team_id)
                agent_id = f"agent_{team_id}_{i}"
                agent.agent_id = agent_id
                # Unii agenți au comunicare limitată (doar cu vecinii apropiați)
                agent.has_limited_communication = random.random() < 0.5
                agent.update_color()
                self.agents_list.append((agent_id, agent))
        
        # Creează lista de nume agenți pentru PettingZoo
        self.possible_agents = [agent_id for agent_id, _ in self.agents_list]
        # Index rapid agent_id -> Agent
        self.agent_index = {agent_id: agent for agent_id, agent in self.agents_list}
        # Actualizează bus-ul
        if hasattr(self, 'message_bus') and self.message_bus:
            self.message_bus.set_agents(self.agent_index)
    
    def _setup_spaces(self):
        """Configurează action space și observation space"""
        # Action space: [move_x, move_y, shoot, shoot_angle]
        # move_x, move_y: -1 to 1 (direcție normalizată)
        # shoot: 0 sau 1 (trage sau nu)
        # shoot_angle: 0 to 2π (unghi de tragere)
        self.action_spaces = {
            agent_id: Box(
                low=np.array([-1, -1, 0, 0], dtype=np.float32),
                high=np.array([1, 1, 1, 2*np.pi], dtype=np.float32),
                dtype=np.float32
            )
            for agent_id in self.possible_agents
        }
        
        # Observation space: [x, y, health, team_id, enemy_positions, ...]
        # Simplificat pentru început
        obs_size = 4 + 10 * 4  # Poziție, health, team, + 10 inamici (x, y, health, distance)
        self.observation_spaces = {
            agent_id: Box(
                low=-np.inf,
                high=np.inf,
                shape=(obs_size,),
                dtype=np.float32
            )
            for agent_id in self.possible_agents
        }
    
    def observation_space(self, agent):
        """Returnează observation space pentru un agent"""
        return self.observation_spaces[agent]
    
    def action_space(self, agent):
        """Returnează action space pentru un agent"""
        return self.action_spaces[agent]
    
    def reset(self, seed=None, options=None):
        """Resetează environment-ul"""
        if seed is not None:
            np.random.seed(seed)
        # Reinițializează bus (curăță mesaje vechi)
        self.message_bus = MessageBus()

        # Resetează agenții
        self._create_agents()
        
        # Resetează proiectile
        self.projectiles = []
        
        # Resetează timp
        self.current_time = pygame.time.get_ticks()
        
        # Setează agenții activi
        self.agents = self.possible_agents[:]
        # Creează un selector simplu pentru agenți (implementare manuală)
        self._agent_index = 0
        self.agent_selection = self.agents[0] if self.agents else None
        
        # Inițializează observații, recompense, terminații, truncări
        self.observations = {}
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}  # Necesar pentru PettingZoo API
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        
        # Calculează observațiile inițiale
        for agent_id in self.agents:
            self.observations[agent_id] = self._get_observation(agent_id)
        
        return self.observations
    
    def observe(self, agent):
        """Returnează observația pentru un agent specific"""
        if agent not in self.observations:
            # Dacă agentul nu are observație, calculează una
            self.observations[agent] = self._get_observation(agent)
        return self.observations[agent]
    
    def _get_agent_by_id(self, agent_id):
        """Găsește agentul după ID"""
        for aid, agent in self.agents_list:
            if aid == agent_id:
                return agent
        return None
    
    def _get_observation(self, agent_id):
        """Calculează observația pentru un agent"""
        agent = self._get_agent_by_id(agent_id)
        if not agent or not agent.alive:
            return np.zeros(self.observation_spaces[agent_id].shape, dtype=np.float32)
        
        # Observație de bază: [x, y, health, team_id]
        obs = [agent.x / (MAP_WIDTH * TILE_SIZE),  # Normalizat
               agent.y / (MAP_HEIGHT * TILE_SIZE),
               agent.health / AGENT_MAX_HEALTH,
               agent.team_id]
        
        # Adaugă informații despre inamici (max 10 cei mai apropiați)
        enemies = []
        for other_id, other_agent in self.agents_list:
            if other_agent.team_id != agent.team_id and other_agent.alive:
                distance = agent.distance_to(other_agent)
                enemies.append((distance, other_agent))
        
        enemies.sort(key=lambda x: x[0])  # Sortează după distanță
        enemies = enemies[:10]  # Primele 10
        
        for distance, enemy in enemies:
            obs.extend([
                enemy.x / (MAP_WIDTH * TILE_SIZE),
                enemy.y / (MAP_HEIGHT * TILE_SIZE),
                enemy.health / AGENT_MAX_HEALTH,
                distance / (MAP_WIDTH * TILE_SIZE)  # Normalizat
            ])
        
        # Completează până la dimensiunea fixă
        while len(obs) < self.observation_spaces[agent_id].shape[0]:
            obs.append(0.0)
        
        return np.array(obs[:self.observation_spaces[agent_id].shape[0]], dtype=np.float32)
    
    def step(self, action):
        """Efectuează un pas în environment"""
        if self.terminations[self.agent_selection] or self.truncations[self.agent_selection]:
            # Agentul este deja terminat, trece la următorul
            self._agent_index = (self._agent_index + 1) % len(self.agents)
            self.agent_selection = self.agents[self._agent_index]
            return
        
        agent = self._get_agent_by_id(self.agent_selection)
        
        if agent and agent.alive:
            # Aplică acțiunea
            move_x, move_y, shoot, shoot_angle = action
            
            # Convertim la float pentru a evita probleme cu numpy types
            move_x = float(move_x)
            move_y = float(move_y)
            shoot = float(shoot)
            shoot_angle = float(shoot_angle)
            
            # Mișcare
            agent.velocity_x = move_x * AGENT_SPEED
            agent.velocity_y = move_y * AGENT_SPEED
            agent.facing_angle = shoot_angle
            
            # Tragere
            if shoot > 0.5:
                current_time = pygame.time.get_ticks()
                if current_time - agent.last_attack_time >= AGENT_ATTACK_COOLDOWN:
                    projectile = Projectile(agent.x, agent.y, shoot_angle, agent.team_id, PROJECTILE_DAMAGE, owner=agent)
                    self.projectiles.append(projectile)
                    agent.last_attack_time = current_time
            
            current_time = pygame.time.get_ticks()
            # Livrează mesaje echipei și procesează inbox
            if self.message_bus:
                agent.inbox = self.message_bus.collect(agent.team_id, current_time, receiving_agent=agent)
                agent.process_inbox(self.message_bus)

            # Actualizează agentul (cu bus pentru broadcast targets)
            all_agents = [a for _, a in self.agents_list]
            agent.update(all_agents, self.game_map.obstacles, current_time, message_bus=self.message_bus)
            
            # Calculează recompensa
            reward = self._calculate_reward(agent)
            self.rewards[self.agent_selection] = reward
            # Actualizează recompensa cumulative
            self._cumulative_rewards[self.agent_selection] = reward
        
        # Actualizează observația
        self.observations[self.agent_selection] = self._get_observation(self.agent_selection)
        
        # Verifică terminarea
        self.terminations[self.agent_selection] = not (agent and agent.alive)
        
        # Dacă agentul este terminat, resetează recompensa cumulative
        if self.terminations[self.agent_selection] or self.truncations[self.agent_selection]:
            self._cumulative_rewards[self.agent_selection] = 0
        
        # Trece la următorul agent
        self._agent_index = (self._agent_index + 1) % len(self.agents)
        self.agent_selection = self.agents[self._agent_index]
        
        # Dacă toți agenții au făcut pas, actualizează proiectilele și curăță mesaje vechi
        if self.agent_selection == self.agents[0]:
            self._update_projectiles()
            if self.message_bus:
                self.message_bus.cleanup(pygame.time.get_ticks())
    
    def _calculate_reward(self, agent):
        """Calculează recompensa pentru un agent"""
        reward = 0.0
        
        # Recompensă pentru viață
        reward += agent.health / AGENT_MAX_HEALTH * 0.1
        
        # Recompensă pentru damage provocat (va fi actualizată când se lovește)
        # Recompensă pentru kill (va fi actualizată când moare un inamic)
        
        # Recompensă negativă pentru moarte
        if not agent.alive:
            reward -= 10.0
        
        return reward
    
    def _update_projectiles(self):
        """Actualizează toate proiectilele"""
        current_time = pygame.time.get_ticks()
        all_agents = [a for _, a in self.agents_list]
        
        for projectile in self.projectiles[:]:
            projectile.update(current_time)
            
            # Verifică coliziuni
            for agent in all_agents:
                if projectile.check_collision_with_agent(agent):
                    break
            
            # Verifică coliziuni cu obstacole
            projectile.check_collision_with_obstacles(self.game_map.obstacles)
            
            if not projectile.alive:
                self.projectiles.remove(projectile)
    
    def render(self):
        """Rendează environment-ul"""
        if self.render_mode == "human" and self.screen:
            self.screen.fill((34, 139, 34))
            
            # Desenează harta
            self.game_map.draw(self.screen)
            
            # Desenează proiectile
            for projectile in self.projectiles:
                projectile.draw(self.screen)
            
            # Desenează agenții
            for _, agent in self.agents_list:
                agent.draw(self.screen)
            
            pygame.display.flip()
    
    def close(self):
        """Închide environment-ul"""
        if self.screen:
            pygame.quit()

# Wrapper pentru a face environment-ul compatibil cu PettingZoo
def env(game_mode="Survival", render_mode=None):
    """Creează environment-ul PettingZoo"""
    env = MicroBattleEnv(game_mode, render_mode)
    
    # CaptureStdoutWrapper funcționează doar cu render_mode="human"
    if render_mode == "human":
        env = wrappers.CaptureStdoutWrapper(env)
    
    # TerminateIllegalWrapper nu este necesar pentru action spaces continue (Box)
    # și necesită action_mask care nu este relevant pentru acest environment
    # env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env

