# Configurări generale pentru joc
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Culori echipe
TEAM_COLORS = {
    0: (255, 50, 50),   # Roșu
    1: (50, 50, 255),   # Albastru
    2: (50, 255, 50),   # Verde
    3: (255, 255, 50)   # Galben
}

# Configurări hartă
TILE_SIZE = 32
MAP_WIDTH = 25
MAP_HEIGHT = 18

# Configurări agenți
AGENT_SIZE = 20
AGENT_SPEED = 2
AGENT_MAX_HEALTH = 100
AGENT_DAMAGE = 25
AGENT_ATTACK_RANGE = 250  # Raza de atac (pixels)
AGENT_ATTACK_COOLDOWN = 500  # milisecunde
AGENT_LOS_ANGLE = 90  # Unghiul conului de vedere (grade)
AGENT_LOS_RANGE = 250  # Distanța maximă de vedere
AGENT_SEPARATION_DISTANCE = 30  # Distanța minimă între agenți din aceeași echipă

# Configurări proiectile
PROJECTILE_SIZE = 5
PROJECTILE_SPEED = 8
PROJECTILE_DAMAGE = 25
PROJECTILE_LIFETIME = 2000  # milisecunde
PROJECTILE_COLOR = (255, 255, 0)  # Galben

# Configurări ziduri
WALL_HEALTH = 50  # Health pentru ziduri distructibile
WALL_DESTROYED_COLOR = (100, 100, 100)  # Gri pentru ziduri distruse
WALL_NORMAL_COLOR = (80, 80, 80)  # Gri închis pentru ziduri normale

# Configurări Survival
SURVIVAL_TIME_LIMIT = 180  # 3 minute în secunde

# Configurări King of the Hill
KOTH_TIME_LIMIT = 120  # 2 minute în secunde
KOTH_TIME_TO_WIN = 15  # Timp total în secunde petrecut în zonă pentru victorie
KOTH_AGENTS_PER_TEAM = 3  # 3 agenți per echipă
KOTH_ZONE_SIZE = 120  # Dimensiunea zonei centrale (pixels)
KOTH_RESPAWN_TIME = 2500  # Timp de respawn după moarte (2.5 secunde în milisecunde)
KOTH_NUM_OBSTACLES = 10  # Număr redus de obstacole pentru KOTH

# Roluri agenți
ROLE_ATTACKER = "attacker"
ROLE_DEFENDER = "defender"
ROLE_CARRIER = "carrier"  # Pentru CTF - poartă steagul
ROLE_CHASER = "chaser"    # Pentru CTF - urmărește carrier-ul inamic

# Configurări Capture the Flag
CTF_TIME_LIMIT = 60  # 2 minute în secunde
CTF_MAX_POINTS = 1  # Număr de steaguri necesare pentru victorie
CTF_AGENTS_PER_TEAM = 3  # 3 agenți per echipă
CTF_RESPAWN_TIME = 3000  # Timp de respawn după moarte (milisecunde)
CTF_FLAG_CAPTURE_RADIUS = 30  # Distanța pentru a captura un steag
CTF_FLAG_SIZE = 15  # Dimensiunea steagului
CTF_NUM_OBSTACLES = 5  # Număr redus de obstacole pentru CTF (mai puține decât KOTH)