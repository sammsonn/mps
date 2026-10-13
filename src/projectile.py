import pygame
import math
from config import *

class Projectile:
    def __init__(self, x, y, angle, team_id, damage=PROJECTILE_DAMAGE, owner=None):
        """
        Inițializează un proiectil
        
        Args:
            x, y: Poziția inițială
            angle: Unghiul de deplasare (în radiani)
            team_id: Echipa din care face parte proiectilul
            damage: Damage-ul pe care îl provoacă
            owner: Agentul care a tras proiectilul (pentru tracking statistici)
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.team_id = team_id
        self.damage = damage
        self.owner = owner  # Agentul care a tras proiectilul
        self.speed = PROJECTILE_SPEED
        self.size = PROJECTILE_SIZE
        self.alive = True
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = PROJECTILE_LIFETIME
        
        # Calculează velocity-ul bazat pe unghi
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed
    
    def update(self, current_time):
        """Actualizează poziția proiectilului"""
        if not self.alive:
            return
        
        # Verifică dacă proiectilul a expirat
        if current_time - self.creation_time > self.lifetime:
            self.alive = False
            return
        
        # Actualizează poziția
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Verifică dacă a ieșit din hartă
        if (self.x < 0 or self.x > MAP_WIDTH * TILE_SIZE or
            self.y < 0 or self.y > MAP_HEIGHT * TILE_SIZE):
            self.alive = False
    
    def check_collision_with_agent(self, agent):
        """
        Verifică coliziunea cu un agent
        
        Args:
            agent: Agentul cu care se verifică coliziunea
            
        Returns:
            True dacă există coliziune, False altfel
        """
        if not self.alive or not agent.alive:
            return False
        
        # Nu poate lovi agenți din aceeași echipă
        if self.team_id == agent.team_id:
            return False
        
        # Calculează distanța
        dx = self.x - agent.x
        dy = self.y - agent.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Verifică coliziunea
        if distance < (self.size + AGENT_SIZE // 2):
            agent.take_damage(self.damage)
            self.alive = False
            return True
        
        return False
    
    def check_collision_with_obstacles(self, obstacles):
        """
        Verifică coliziunea cu obstacole
        
        Args:
            obstacles: Lista de obstacole (Wall objects)
            
        Returns:
            Obstacle lovit sau None
        """
        if not self.alive:
            return None
        
        projectile_rect = pygame.Rect(
            self.x - self.size,
            self.y - self.size,
            self.size * 2,
            self.size * 2
        )
        
        for obstacle in obstacles:
            if obstacle.alive and projectile_rect.colliderect(obstacle.rect):
                self.alive = False
                return obstacle
        
        return None
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Desenează proiectilul"""
        if not self.alive:
            return
        
        pygame.draw.circle(
            screen,
            PROJECTILE_COLOR,
            (int(self.x - camera_x), int(self.y - camera_y)),
            self.size
        )
        
        # Desenează un contur negru
        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (int(self.x - camera_x), int(self.y - camera_y)),
            self.size,
            1
        )
