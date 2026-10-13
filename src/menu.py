import pygame
from config import *

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
    
    def draw(self, screen, font):
        # Desenează butonul
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)  # Border
        
        # Desenează textul
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def update(self, mouse_pos):
        # Verifică dacă mouse-ul e peste buton
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
    
    def is_clicked(self, event):
        # Verifică dacă butonul a fost apăsat
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

class Menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Synapse Strike - Game Mode Selection")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonturi
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 24)
        
        # Culori butoane
        button_color = (80, 80, 200)
        hover_color = (100, 100, 255)
        
        # Dimensiuni butoane
        button_width = 250
        button_height = 60
        button_spacing = 20
        start_y = SCREEN_HEIGHT // 2 - 100
        
        # Creează butoanele pentru modurile de joc
        self.buttons = []
        
        modes = [
            ("Survival", "Eliminate all enemy agents"),
            ("King of the Hill", "Control the central area"),
            ("Capture the Flag", "Capture enemy flags")
        ]
        
        for i, (mode_name, _) in enumerate(modes):
            y = start_y + i * (button_height + button_spacing)
            btn = Button(
                SCREEN_WIDTH // 2 - button_width // 2,
                y,
                button_width,
                button_height,
                mode_name,
                button_color,
                hover_color
            )
            self.buttons.append(btn)
        
        # Descrieri moduri
        self.mode_descriptions = {
            "Survival": "Eliminate all enemy agents or have the most agents alive when time runs out.",
            "King of the Hill": "Earn points by controlling the central area. No enemies must be in the area to score.",
            "Capture the Flag": "Capture the enemy flag and bring it back to your base."
        }
        
        self.selected_mode = None
        self.current_description = ""
    
    def run(self):
        """Rulează meniul și returnează modul selectat"""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Actualizează starea butoanelor
            for btn in self.buttons:
                btn.update(mouse_pos)
                if btn.is_hovered:
                    self.current_description = self.mode_descriptions[btn.text]
            
            # Procesează evenimentele
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    return None
                
                # Verifică click pe butoane
                for btn in self.buttons:
                    if btn.is_clicked(event):
                        self.selected_mode = btn.text
                        return self.selected_mode
            
            # Desenează
            self.draw()
            
            # Limitează FPS
            self.clock.tick(60)
        
        return None
    
    def draw(self):
        """Desenează meniul"""
        # Background
        self.screen.fill((30, 30, 60))
        
        # Titlu
        title_surf = self.title_font.render("SYNAPSE STRIKE", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)
        
        # Subtitlu
        subtitle_surf = self.button_font.render("Select Game Mode", True, (200, 200, 200))
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
        # Butoane
        for btn in self.buttons:
            btn.draw(self.screen, self.button_font)
        
        # Descriere mod selectat
        if self.current_description:
            desc_surf = self.info_font.render(self.current_description, True, (200, 200, 200))
            desc_rect = desc_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
            self.screen.blit(desc_surf, desc_rect)
        
        # Instrucțiuni
        instr_surf = self.info_font.render("Press ESC to quit", True, (150, 150, 150))
        instr_rect = instr_surf.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.screen.blit(instr_surf, instr_rect)
        
        pygame.display.flip()