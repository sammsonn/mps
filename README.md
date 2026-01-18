# Synapse Strike

[![Pipeline Status](https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm/badges/main/pipeline.svg)](https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm/-/pipelines)
[![Stare Proiect](https://img.shields.io/badge/status-completed-green.svg)](https://shields.io/)
[![Licență](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)

Un joc 2D de tip arenă, cu acțiune rapidă și suport pentru Reinforcement Learning, dezvoltat în cadrul materiei **Managementul Proiectelor Software**.

---

## Cuprins

* [Despre Proiect](#despre-proiect)
* [Tehnologii Folosite](#tehnologii-folosite)
* [Moduri de Joc](#moduri-de-joc)
* [Cum se Rulează](#cum-se-rulează)
* [Structura Proiectului](#structura-proiectului)
* [Integrare AI & RL](#integrare-ai--rl)
* [Echipa](#echipa)

---

## Despre Proiect

**Synapse Strike** este un joc dezvoltat în Python folosind Pygame, în care agenți controlați de AI se luptă într-o arenă dinamică. Proiectul include mecanici complexe de luptă, pathfinding, comunicare între agenți și este proiectat să fie compatibil cu **PettingZoo** pentru antrenarea agenților folosind Reinforcement Learning (RL).

### Funcționalități Principale
-   **Engine propriu 2D:** Implementat de la zero folosind Pygame.
-   **AI Bazat pe Reguli:** Agenți inteligenți cu pathfinding (Dijkstra), Line of Sight (LoS), și comportamente specifice rolurilor (Attacker, Defender, Carrier, Chaser).
-   **Sistem de Comunicare Avansat:** Agenții colaborează folosind un "Message Bus" cu trei niveluri de comunicare:
    - **FULL:** Comunicare completă (implicit)
    - **LIMITED:** Comunicare limitată la distanță (max ~200px)
    - **NONE:** Fără comunicare între agenți
-   **Statistici Detaliate:** Tracking pentru KDA, DPS, controlul zonelor și obiective.
-   **Mediu RL Standardizat:** Wrapper compatibil cu **PettingZoo** și **Gymnasium** pentru experimente de Machine Learning.
-   **Sistem de Logging:** Logger custom integrat pentru debugging și monitoring.

---

## Tehnologii Folosite

* **Limbaj de Programare:** ![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
* **Bibliotecă Grafică:** ![Pygame](https://img.shields.io/badge/Pygame-2.x-green?style=for-the-badge&logo=python)
* **Reinforcement Learning:** ![PettingZoo](https://img.shields.io/badge/PettingZoo-API-orange?style=for-the-badge)
* **Altele:** NumPy, Gymnasium

---

## Moduri de Joc

Jocul include trei moduri distincte, accesibile din meniul principal:

1.  **Survival:**
    * **Obiectiv:** Elimină toți agenții echipei adverse.
    * **Mecanică:** Deathmatch clasic 5v5.
2.  **King of the Hill (KOTH):**
    * **Obiectiv:** Controlează zona centrală a hărții.
    * **Mecanică:** Echipele acumulează puncte doar când au agenți în zonă și inamicii sunt eliminați din perimetru. Include roluri dinamice de atacanți și apărători.
3.  **Capture the Flag (CTF):**
    * **Obiectiv:** Capturează steagul inamic și adu-l la bază.
    * **Mecanică:** Agenții primesc roluri specifice (Carrier, Chaser) și trebuie să colaboreze pentru a proteja purtătorul steagului.

---

## Cum se Rulează

Pentru a rula acest proiect local, urmați acești pași:

### Prerechizite
Asigurați-vă că aveți instalat **Python 3.8+**.

### Instalare și Rulare

1.  **Clonați repository-ul:**
    ```sh
    git clone [https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm.git](https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm.git)
    cd lu-12-14-luckycharm
    ```

2.  **Creați și activați environment-ul virtual:**
    ```sh
    # Linux/MacOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalați dependențele:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Rulați jocul (Modul Interactiv):**
    ```sh
    python src/main.py
    ```
    Jocul va deschide un meniu interactiv din care puteți selecta modul de joc dorit (Survival, King of the Hill, Capture the Flag).

5.  **Rulați testele:**
    Pentru a verifica integritatea codului (103 Unit Tests):
    ```sh
    python tests/run_tests.py -v
    ```
    Sau rulați teste pentru un modul specific:
    ```sh
    python tests/run_tests.py test_agent    # Doar teste Agent
    python tests/run_tests.py test_communication  # Doar teste Comunicare
    ```

6.  **Rulați exemplul PettingZoo (Modul RL):**
    Pentru a testa mediul de antrenament cu agenți AI:
    ```sh
    python src/pettingzoo_example.py
    ```
    Sau testați mediul RL rapid:
    ```sh
    python src/quick_test_pettingzoo.py
    ```

---

## Structura Proiectului

Proiectul este organizat modular, separând codul sursă de teste și documentație:

```text
/
├── src/
│   ├── main.py                 # Punctul de intrare (Meniu & Game Loop)
│   ├── menu.py                 # Interfața de meniu cu selectare mod joc
│   ├── config.py               # Constante și setări globale
│   ├── game_map.py             # Generare hărți și obstacole dinamice
│   ├── agent.py                # Logică agenți, AI, Pathfinding (Dijkstra)
│   ├── projectile.py           # Fizica proiectilelor și coliziuni
│   ├── communication.py        # MessageBus - Sistem de comunicare între agenți
│   ├── statistics.py           # Colectare metrici (DPS, KDA, zone control)
│   ├── logger.py               # Sistem de logging custom
│   ├── pettingzoo_env.py       # Wrapper standardizat pentru RL (PettingZoo/Gymnasium)
│   ├── pettingzoo_example.py   # Exemplu de antrenare cu agenți RL
│   ├── quick_test_pettingzoo.py # Test rapid al mediului RL
│   ├── test_pettingzoo.py      # Suite de teste RL
│   │
│   ├── survival_mode.py        # Logică mod Survival (Deathmatch 5v5)
│   ├── koth_mode.py            # Logică mod King of the Hill (control zonă)
│   └── ctf_mode.py             # Logică mod Capture the Flag (steag)
│
├── tests/                      # Suite Completa de Teste Unitare
│   ├── run_tests.py            # Runner principal - Execută 103 teste
│   ├── test_agent.py           # 20 teste Agent (inițializare, damage, roluri)
│   ├── test_projectile.py      # 13 teste Projectile (mișcare, coliziuni)
│   ├── test_communication.py   # 14 teste MessageBus (publish, filtering)
│   ├── test_game_map.py        # 19 teste GameMap (hărți, pereți, spawn)
│   ├── test_survival_mode.py   # 14 teste Survival (victoria, time limit)
│   ├── test_statistics.py      # 13 teste Statistics (tracking metrici)
│   ├── __init__.py
│   └── README.md               # Documentație testare detaliat
│
├── docs/
│   ├── CODING_STYLE.md         # Ghid de stil de codare al proiectului
│   ├── TESTING_SUMMARY.md      # Rezumatul suites de teste
│   └── UNIT_TESTS_COMPLETE.md  # Detalii complete despre 103 teste
│
├── requirements.txt            # Dependențele Python
├── README.md                   # Acest fișier
└── LICENSE.md                  # Licență MIT

```

---

## Teste Unitare

Proiectul include o suită **cuprinzătoare de 103 teste unitare** care validează integritatea componentelor principale:

### Acoperire Testare
- **20 teste Agent:** Inițializare, mecanica sănătății, calculare daune, roluri (Attacker, Defender, Carrier, Chaser)
- **13 teste Projectile:** Mișcare, coliziuni, friendly-fire prevention, expired projectiles
- **14 teste Communication:** MessageBus publish/collect, filtrare pe echipă, rază limitată
- **19 teste GameMap:** Creație pereți, spawn dinamice, mode-specific features (KOTH zone, CTF flags)
- **14 teste SurvivalMode:** Condiții de victorie, time limit, end game
- **13 teste Statistics:** Tracking DPS, KDA, zone control

### Rulare Teste
```bash
# Rulare completă
python tests/run_tests.py -v

# Teste specific modul
python -m unittest tests.test_agent
python -m unittest tests.test_communication

# Teste pentru o clasă specifică
python -m unittest tests.test_agent.TestAgentInitialization
```

---

## Integrare AI & RL

Proiectul expune un mediu standardizat pentru Reinforcement Learning prin clasa `MicroBattleEnv` din `src/pettingzoo_env.py`, implementat conform standardului **PettingZoo AECEnv**.

### Caracteristici RL
- **Spațiu de Observație:** 
  - Poziții și viață proprie
  - Inamici detectați în raza vizuală (LoS)
  - Mesaje de echipă (în funcție de nivel comunicare)
  - Stare hartă și obstacole
  
- **Spațiu de Acțiune:** 
  - Continuu (Box): X/Y velocitate + unghi tragere
  - Alternativ Discret: sus/jos/stânga/dreapta + foc
  
- **Recompense:**
  - Damage infligat
  - Kill-uri
  - Supraviețuire și control zone
  - Bonusuri pentru capturare obiective (CTF, KOTH)

### Exemple RL
```bash
# Exemplu cu agenți predefiniti
python src/pettingzoo_example.py

# Test rapid mediu RL
python src/quick_test_pettingzoo.py

# Suite completa teste RL
python src/test_pettingzoo.py
```

---

## Documentație

Pentru mai multe detalii despre planificarea, arhitectura și cerințele proiectului, consultați resursele de mai jos:

* 🌐 **[Pagina Wiki a Proiectului](https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm/-/wikis/home)**: Hub-ul central pentru documentația proiectului.
* 📄 **[Standarde de Codare (Coding Style)](https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm/-/blob/main/docs/CODING_STYLE.md?ref_type=heads)**: Regulile de codare pe care le respectăm.
* 📋 **[Raport Testare Complet](docs/UNIT_TESTS_COMPLETE.md)**: Detalii despre 103 teste unitare și acoperirea codului.
* 📂 **[Director Google Drive](https://drive.google.com/drive/folders/1D7yvULvRNyAsXOY5aZUKo3iiGY99fhaN)**: Conține documentele detaliate (SRS, SDD, WBS, Gantt).

---

## Echipa

| Nume | Rol Principal |
| --- | --- |
| Samson Alexandru | **Project Manager** |
| Carazeanu Antonio | **Team Leader** |
| Ilie Alexandru | **Dezvoltator** |
| Calu Andrei | **Dezvoltator** |
| Echim Andrei | **Dezvoltator** |
| Baston Jenică | **QA** |
| Trufelea Alexandru | **QA** |
| Petrea Octavian | **QA** |
| Logofătu Patricia | **QA** |