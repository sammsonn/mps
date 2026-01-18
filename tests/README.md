# Teste Unitare pentru Synapse Strike

Acest director conține teste unitare cuprinzătoare pentru jocul Synapse Strike.

## Structura Teste

```
tests/
├── __init__.py              # Inițializare pachet teste
├── run_tests.py             # Runner principal teste
├── test_agent.py            # Teste clasa Agent
├── test_projectile.py       # Teste clasa Projectile
├── test_communication.py    # Teste Message & MessageBus
├── test_game_map.py         # Teste GameMap & Wall
├── test_survival_mode.py    # Teste mod Survival
├── test_statistics.py       # Teste tracking statistici
└── README.md                # Acest fișier
```

## Rulare Teste

### Rulare Toate Teste
```bash
# Asigurați-vă că venv este activat
source venv/bin/activate

# Rulați toate testele
python tests/run_tests.py

# Rulați cu output verbose
python tests/run_tests.py -v
```

### Rulare Modul Test Specific
```bash
# Rulați doar teste agent
python tests/run_tests.py test_agent

# Rulați doar teste projectile
python tests/run_tests.py test_projectile

# Rulați cu unittest direct
python -m unittest tests.test_agent
```

### Rulare Clasa Test Individual
```bash
# Rulați clasa test specifică
python -m unittest tests.test_agent.TestAgentInitialization

# Rulați metoda test specifică
python -m unittest tests.test_agent.TestAgentInitialization.test_agent_creation
```

## Acoperire Teste

### Teste Agent (`test_agent.py`)
- ✓ Inițializare și atribute agent
- ✓ Mecanica sănătății și daunelor
- ✓ Condiții moarte
- ✓ Funcții comunicare (limitată vs normală)
- ✓ Calculări distanță
- ✓ Atribuire roluri (Attacker, Defender, Carrier, Chaser)

### Teste Projectile (`test_projectile.py`)
- ✓ Inițializare proiectil
- ✓ Atribuire daune și proprietar personalizate
- ✓ Calculare viteză din unghi
- ✓ Mișcare și traiectorie
- ✓ Viață și expirare
- ✓ Coliziune cu agenți (prevenire friendly fire)
- ✓ Daune coliziune
- ✓ Verificare limite hartă

### Teste Communication (`test_communication.py`)
- ✓ Creare mesaje și atribute
- ✓ MessageBus publish/collect
- ✓ Filtrare mesaje team-specific
- ✓ Expirare și curățare mesaje
- ✓ Rezoluție agent după ID
- ✓ Rază comunicare limitată
- ✓ Filtrare mesaje bazată pe distanță

### Teste GameMap (`test_game_map.py`)
- ✓ Creare și distrugere pereți
- ✓ Pereți graniță (indestructibili)
- ✓ Mecanica daune pereți
- ✓ Inițializare hartă pentru moduri diferite
- ✓ Generare poziție spawn
- ✓ Utilitare pathfinding (dale plimbabile, vecini)
- ✓ Funcții mode-specifice (zone KOTH, steaguri CTF)

### Teste Mod Survival (`test_survival_mode.py`)
- ✓ Inițializare mod
- ✓ Condiții victorie (eliminare echipă)
- ✓ Mecanika limită timp
- ✓ Funcționalitate timer
- ✓ Condiții end game
- ✓ Determinare câștigător
- ✓ Configurări multiple echipe

### Teste Statistics (`test_statistics.py`)
- ✓ Inițializare și reset tracker
- ✓ Statistici agent (spawns, deaths, damage)
- ✓ Agregare statistici echipă
- ✓ Tracking shoturi (trase, lovituri)
- ✓ Tracking kill/death/assist
- ✓ Statistici KOTH-specific (timp zonă, daune)
- ✓ Statistici CTF-specific (capturi, livrări)
- ✓ Calculări acuratețe și KDA

## Scriere Teste Noi

### Template Test
```python
import unittest
import sys
import os

# Adaugă director src în path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from your_module import YourClass

class TestYourClass(unittest.TestCase):
    """Test funcționalitate YourClass"""
    
    def setUp(self):
        """Set up test fixtures - rulează înainte de fiecare test"""
        self.obj = YourClass()
    
    def tearDown(self):
        """Curățare după test - rulează după fiecare test"""
        pass
    
    def test_something(self):
        """Descriere test"""
        # Arrange
        expected = "valoare"
        
        # Act
        result = self.obj.method()
        
        # Assert
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
```

### Asertări Comune
```python
self.assertEqual(a, b)              # a == b
self.assertNotEqual(a, b)           # a != b
self.assertTrue(x)                  # bool(x) este True
self.assertFalse(x)                 # bool(x) este False
self.assertIs(a, b)                 # a is b
self.assertIsNone(x)                # x is None
self.assertIn(a, b)                 # a in b
self.assertIsInstance(a, b)         # isinstance(a, b)
self.assertAlmostEqual(a, b)        # round(a-b, 7) == 0
self.assertGreater(a, b)            # a > b
self.assertLess(a, b)               # a < b
self.assertRaises(SomeException)    # Verifică dacă excepție ridicată
```

## Practici Bune

1. **Un Test, O Asertare**: Fiecare test ar trebui să verifice un comportament specific
2. **Nume Descriptive**: Utilizați nume de metode test clare și descriptive
3. **Model AAA**: Structură Arrange, Act, Assert
4. **Teste Independente**: Testele nu ar trebui să depindă una de cealaltă
5. **Teste Rapide**: Teste unitare ar trebui să ruleze rapid
6. **Mock Dependențe Externe**: Mock pygame, I/O fișiere, etc. când necesar

## Integrare Continuă

Aceste teste sunt proiectate pentru a rula în pipelinuri CI/CD:

```bash
# În scriptul CI
source venv/bin/activate
pip install -r requirements.txt
python tests/run_tests.py -v
```

## Acoperire Teste Viitoare

Domenii care ar putea beneficia de teste suplimentare:
- [ ] Gameplay mod KOTH
- [ ] Gameplay mod CTF
- [ ] Mediu PettingZoo
- [ ] Sistem meniu
- [ ] Teste integrare
- [ ] Teste performanță
- [ ] Teste comportament AI

## Troubleshooting

### Probleme Comune

**ImportError: Nu se găsește modul 'pygame'**
```bash
# Activați venv și instalați dependențe
source venv/bin/activate
pip install -r requirements.txt
```

**Teste eșuează cu "No such file or directory"**
```bash
# Rulați teste din rădăcina proiectului
cd /path/to/lu-12-14-luckycharm
python tests/run_tests.py
```

**Sistem video Pygame nu inițializat**
- Unele teste pot necesita pygame.init() - deja gestionat în fișiere test
- Teste rulează în mod headless (niciun display necesar)

## Contribuire

Când adăugați funcții noi:
1. Scrieți teste mai întâi (abordare TDD)
2. Asigurați-vă că toate testele existente trec
3. Adăugați teste pentru cazuri limită
4. Documentați acoperire teste în acest README
