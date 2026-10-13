import pygame
import random
from config import *

class Wall:
    """Reprezintă un zid distructibil"""
    def __init__(self, x, y, tile_size, is_border=False):
        self.rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
        self.health = WALL_HEALTH if not is_border else 9999  # Zidurile de margine sunt indestructibile
        self.max_health = self.health
        self.alive = True
        self.is_border = is_border
        self.x = x
        self.y = y
    
    def take_damage(self, damage):
        """Primește damage"""
        if self.is_border:
            return  # Zidurile de margine nu pot fi distruse
        
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Desenează zidul"""
        if not self.alive:
            return
        
        rect = pygame.Rect(
            self.rect.x - camera_x,
            self.rect.y - camera_y,
            self.rect.width,
            self.rect.height
        )
        
        # Culoare bazată pe health
        if self.is_border:
            color = (50, 50, 50)  # Foarte închis pentru margini
        else:
            health_percent = self.health / self.max_health
            color_value = int(80 + (155 - 80) * (1 - health_percent))
            color = (color_value, color_value, color_value)
        
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (40, 40, 40), rect, 2)

class GameMap:
    def __init__(self, game_mode="Survival"):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.tile_size = TILE_SIZE
        self.game_mode = game_mode
        
        # 0 = gol, 1 = obstacol
        self.tiles = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Generează obstacole
        if game_mode == "King of the Hill":
            self.generate_koth_obstacles()
        elif game_mode == "Capture the Flag":
            self.generate_ctf_obstacles()
        else:
            self.generate_obstacles()
        
        # Lista de Wall objects pentru coliziuni și damage
        self.obstacles = []
        self.create_obstacle_walls()
    
    def generate_obstacles(self):
        """Generează obstacole random pe hartă"""
        # Ziduri pe margini
        for x in range(self.width):
            self.tiles[0][x] = 1
            self.tiles[self.height - 1][x] = 1
        
        for y in range(self.height):
            self.tiles[y][0] = 1
            self.tiles[y][self.width - 1] = 1
        
        # Definește zonele de spawn (să rămână libere)
        spawn_zones = [
            (2, 5, 2, 5),          # Stânga sus (x1, x2, y1, y2)
            (self.width - 5, self.width - 2, self.height - 5, self.height - 2),  # Dreapta jos
            (self.width - 5, self.width - 2, 2, 5),  # Dreapta sus
            (2, 5, self.height - 5, self.height - 2)  # Stânga jos
        ]
        
        # Zona centrală (să rămână relativ liberă pentru a permite acces)
        center_zone = (
            self.width // 2 - 3, self.width // 2 + 3,
            self.height // 2 - 3, self.height // 2 + 3
        )
        
        # Obstacole random în interior (redus și mai mici pentru a evita zone închise)
        num_obstacles = 25  # Redus de la 30
        attempts = 0
        max_attempts = 150
        
        while num_obstacles > 0 and attempts < max_attempts:
            attempts += 1
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            
            # Verifică dacă e în zona de spawn
            in_spawn_zone = False
            for x1, x2, y1, y2 in spawn_zones:
                if x1 <= x <= x2 and y1 <= y <= y2:
                    in_spawn_zone = True
                    break
            
            if in_spawn_zone:
                continue
            
            # Verifică dacă e în zona centrală (evită zona centrală)
            cx1, cx2, cy1, cy2 = center_zone
            if cx1 <= x <= cx2 and cy1 <= y <= cy2:
                continue  # Nu plasează obstacole în zona centrală
            
            # Creează grupuri de obstacole (redus dimensiunea maximă)
            size = random.randint(1, 2)  # Redus de la 3 la 2 (maxim 2x2)
            can_place = True
            
            # Verifică dacă poate plasa grupul întreg
            for dx in range(size):
                for dy in range(size):
                    check_x = x + dx
                    check_y = y + dy
                    
                    if check_x >= self.width - 1 or check_y >= self.height - 1:
                        can_place = False
                        break
                    
                    # Verifică zona de spawn
                    for x1, x2, y1, y2 in spawn_zones:
                        if x1 <= check_x <= x2 and y1 <= check_y <= y2:
                            can_place = False
                            break
                    
                    # Verifică zona centrală
                    if cx1 <= check_x <= cx2 and cy1 <= check_y <= cy2:
                        can_place = False
                        break
                    
                    if not can_place:
                        break
                
                if not can_place:
                    break
            
            if can_place:
                for dx in range(size):
                    for dy in range(size):
                        if x + dx < self.width - 1 and y + dy < self.height - 1:
                            self.tiles[y + dy][x + dx] = 1
                num_obstacles -= 1
    
    def generate_koth_obstacles(self):
        """Generează obstacole pentru modul King of the Hill (mai puține)"""
        # Ziduri pe margini
        for x in range(self.width):
            self.tiles[0][x] = 1
            self.tiles[self.height - 1][x] = 1
        
        for y in range(self.height):
            self.tiles[y][0] = 1
            self.tiles[y][self.width - 1] = 1
        
        # Zonele pentru fiecare echipă (să rămână libere)
        zone_margin = 3
        zone_size = KOTH_ZONE_SIZE // TILE_SIZE
        
        koth_zones = [
            (zone_margin, zone_margin + zone_size, 
             self.height // 2 - zone_size // 2, self.height // 2 + zone_size // 2),  # Zona stânga
            (self.width - zone_margin - zone_size, self.width - zone_margin,
             self.height // 2 - zone_size // 2, self.height // 2 + zone_size // 2)  # Zona dreapta
        ]
        
        # Obstacole random în interior (mult mai puține)
        num_obstacles = KOTH_NUM_OBSTACLES
        attempts = 0
        max_attempts = 100
        
        while num_obstacles > 0 and attempts < max_attempts:
            attempts += 1
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            
            # Verifică dacă e în zonele KOTH
            in_koth_zone = False
            for x1, x2, y1, y2 in koth_zones:
                if x1 <= x <= x2 and y1 <= y <= y2:
                    in_koth_zone = True
                    break
            
            if in_koth_zone:
                continue
            
            # Plasează un obstacol mai mic (1-2 tile-uri)
            size = random.randint(1, 2)
            can_place = True
            
            for dx in range(size):
                for dy in range(size):
                    check_x = x + dx
                    check_y = y + dy
                    
                    if check_x >= self.width - 1 or check_y >= self.height - 1:
                        can_place = False
                        break
                    
                    # Verifică zonele KOTH
                    for x1, x2, y1, y2 in koth_zones:
                        if x1 <= check_x <= x2 and y1 <= check_y <= y2:
                            can_place = False
                            break
                    
                    if not can_place:
                        break
                
                if not can_place:
                    break
            
            if can_place:
                for dx in range(size):
                    for dy in range(size):
                        if x + dx < self.width - 1 and y + dy < self.height - 1:
                            self.tiles[y + dy][x + dx] = 1
                num_obstacles -= 1
    
    def generate_ctf_obstacles(self):
        """Generează obstacole pentru modul Capture the Flag (foarte puține)"""
        # Ziduri pe margini
        for x in range(self.width):
            self.tiles[0][x] = 1
            self.tiles[self.height - 1][x] = 1
        
        for y in range(self.height):
            self.tiles[y][0] = 1
            self.tiles[y][self.width - 1] = 1
        
        # Zonele pentru baze și steaguri (să rămână libere)
        # Baza echipei 0 + steag în colțul stânga-sus
        # Baza echipei 1 + steag în colțul dreapta-jos
        ctf_zones = [
            (2, 7, 2, 7),  # Zona stânga sus (baza + steag echipa 0)
            (self.width - 7, self.width - 2, self.height - 7, self.height - 2)  # Zona dreapta jos (baza + steag echipa 1)
        ]
        
        # Obstacole random în interior (foarte puține pentru mișcare rapidă)
        num_obstacles = CTF_NUM_OBSTACLES
        attempts = 0
        max_attempts = 100
        
        while num_obstacles > 0 and attempts < max_attempts:
            attempts += 1
            x = random.randint(self.width // 3, 2 * self.width // 3)  # Doar în zona centrală
            y = random.randint(self.height // 3, 2 * self.height // 3)
            
            # Verifică dacă e în zonele CTF
            in_ctf_zone = False
            for x1, x2, y1, y2 in ctf_zones:
                if x1 <= x <= x2 and y1 <= y <= y2:
                    in_ctf_zone = True
                    break
            
            if in_ctf_zone:
                continue
            
            # Plasează un obstacol mic (doar 1 tile pentru CTF)
            size = 1
            can_place = True
            
            if x >= self.width - 1 or y >= self.height - 1:
                can_place = False
            else:
                # Verifică zonele CTF
                for x1, x2, y1, y2 in ctf_zones:
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        can_place = False
                        break
            
            if can_place:
                self.tiles[y][x] = 1
                num_obstacles -= 1
    
    def create_obstacle_walls(self):
        """Creează obiecte Wall pentru coliziuni și damage"""
        self.obstacles = []
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == 1:
                    # Verifică dacă e zid de margine
                    is_border = (x == 0 or x == self.width - 1 or 
                                y == 0 or y == self.height - 1)
                    wall = Wall(x, y, self.tile_size, is_border)
                    self.obstacles.append(wall)
    
    def update_obstacles(self):
        """Actualizează obstacole - elimină cele distruse din tiles"""
        for obstacle in self.obstacles:
            if not obstacle.alive and self.tiles[obstacle.y][obstacle.x] == 1:
                self.tiles[obstacle.y][obstacle.x] = 0
    
    def get_active_obstacles(self):
        """Returnează doar obstacole vii"""
        return [obs for obs in self.obstacles if obs.alive]
    
    def get_spawn_position(self, team_id, num_teams):
        """Returnează o poziție de spawn liberă pentru o echipă"""
        margin = 3 * TILE_SIZE
        max_attempts = 50
        
        for attempt in range(max_attempts):
            if team_id == 0:  # Stânga sus
                x = margin + random.randint(0, 2 * TILE_SIZE)
                y = margin + random.randint(0, 2 * TILE_SIZE)
            elif team_id == 1:  # Dreapta jos
                x = self.width * TILE_SIZE - margin - random.randint(0, 2 * TILE_SIZE)
                y = self.height * TILE_SIZE - margin - random.randint(0, 2 * TILE_SIZE)
            elif team_id == 2:  # Dreapta sus
                x = self.width * TILE_SIZE - margin - random.randint(0, 2 * TILE_SIZE)
                y = margin + random.randint(0, 2 * TILE_SIZE)
            else:  # Stânga jos
                x = margin + random.randint(0, 2 * TILE_SIZE)
                y = self.height * TILE_SIZE - margin - random.randint(0, 2 * TILE_SIZE)
            
            # Verifică dacă poziția e liberă (fără obstacole)
            # Folosește un rect mai mare pentru a se asigura că e suficient spațiu
            margin = AGENT_SIZE + 5  # Spațiu suplimentar pentru a evita coliziunile
            spawn_rect = pygame.Rect(x - margin, y - margin, 
                                     margin * 2, margin * 2)
            collision = False
            
            # Verifică coliziunea cu obstacolele
            for obstacle in self.obstacles:
                if obstacle.alive and spawn_rect.colliderect(obstacle.rect):
                    collision = True
                    break
            
            # Verifică și dacă poziția e în interiorul hărții (nu pe margini)
            if (x < AGENT_SIZE or x > self.width * TILE_SIZE - AGENT_SIZE or
                y < AGENT_SIZE or y > self.height * TILE_SIZE - AGENT_SIZE):
                collision = True
            
            if not collision:
                return x, y
        
        # Dacă nu găsește poziție liberă după multe încercări, încercă să găsească o poziție aproape de bază
        # dar cu verificări suplimentare
        safe_margin = margin + AGENT_SIZE
        for attempt in range(20):
            if team_id == 0:  # Stânga sus
                x = safe_margin + random.randint(0, 3 * TILE_SIZE)
                y = safe_margin + random.randint(0, 3 * TILE_SIZE)
            elif team_id == 1:  # Dreapta jos
                x = self.width * TILE_SIZE - safe_margin - random.randint(0, 3 * TILE_SIZE)
                y = self.height * TILE_SIZE - safe_margin - random.randint(0, 3 * TILE_SIZE)
            elif team_id == 2:  # Dreapta sus
                x = self.width * TILE_SIZE - safe_margin - random.randint(0, 3 * TILE_SIZE)
                y = safe_margin + random.randint(0, 3 * TILE_SIZE)
            else:  # Stânga jos
                x = safe_margin + random.randint(0, 3 * TILE_SIZE)
                y = self.height * TILE_SIZE - safe_margin - random.randint(0, 3 * TILE_SIZE)
            
            # Verifică coliziunea
            margin_check = AGENT_SIZE + 5
            spawn_rect = pygame.Rect(x - margin_check, y - margin_check, 
                                     margin_check * 2, margin_check * 2)
            collision = False
            
            for obstacle in self.obstacles:
                if obstacle.alive and spawn_rect.colliderect(obstacle.rect):
                    collision = True
                    break
            
            if not collision and (AGENT_SIZE <= x <= self.width * TILE_SIZE - AGENT_SIZE and
                                  AGENT_SIZE <= y <= self.height * TILE_SIZE - AGENT_SIZE):
                return x, y
        
        # Dacă tot nu găsește, returnează o poziție sigură în colț (fără obstacole)
        if team_id == 0:
            return safe_margin, safe_margin
        elif team_id == 1:
            return self.width * TILE_SIZE - safe_margin, self.height * TILE_SIZE - safe_margin
        elif team_id == 2:
            return self.width * TILE_SIZE - safe_margin, safe_margin
        else:
            return safe_margin, self.height * TILE_SIZE - safe_margin
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Desenează harta"""
        # Fundal
        screen.fill((34, 139, 34))  # Verde
        
        # Desenează obstacole (ziduri)
        for obstacle in self.obstacles:
            obstacle.draw(screen, camera_x, camera_y)