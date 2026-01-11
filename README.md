# Synapse Strike

[![Stare Proiect](https://img.shields.io/badge/status-in%20development-yellow.svg)](https://shields.io/)
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
-   **Sistem de Comunicare:** Agenții colaborează folosind un "Message Bus" (ex: semnalizează inamici văzuți, cer ajutor, anunță capturarea steagului).
-   **Statistici Detaliate:** Tracking pentru KDA, DPS, controlul zonelor și obiective.
-   **Mediu RL:** Wrapper compatibil cu standardul PettingZoo/Gymnasium pentru experimente de Machine Learning.

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
    git clone https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm.git
    cd lu-12-14-luckycharm
    ```

2.  **Creați și activați environment-ul virtual:**
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # Pentru Linux/Mac
    # Pentru Windows: venv\Scripts\activate
    ```

3.  **Instalați dependențele:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Rulați jocul (Modul Interactiv):**
    ```sh
    python src/main.py
    ```

5.  **Rulați exemplul PettingZoo (Modul RL):**
    Pentru a testa mediul de antrenament:
    ```sh
    python src/pettingzoo_example.py
    ```

6.  **Rulați testele:**
    Pentru a verifica că totul funcționează corect:
    ```sh
    python tests/run_tests.py -v
    ```

---

## Structura Proiectului

Proiectul este organizat modular în directorul `src/`:

````
/
├── src/
│   ├── main.py                 \# Punctul de intrare (Meniu & Game Loop)
│   ├── menu.py                 \# Interfața de meniu
│   ├── config.py               \# Constante și setări globale
│   ├── game_map.py             \# Generare hărți și obstacole
│   ├── agent.py                \# Logică agenți, AI, Pathfinding
│   ├── projectile.py           \# Fizica proiectilelor
│   ├── communication.py        \# Sistemul de mesaje între agenți
│   ├── statistics.py           \# Colectare metrici (DPS, KDA)
│   ├── pettingzoo_env.py       \# Wrapper pentru mediul RL
│   │
│   ├── survival_mode.py        \# Logică mod Survival
│   ├── koth_mode.py            \# Logică mod King of the Hill
│   └── ctf_mode.py             \# Logică mod Capture the Flag
│
├── docs/
│    └── CODING_STYLE.md        \# Coding Style
└── README.md                   \# Acest fișier
````

---

## Integrare AI & RL

Proiectul expune un mediu standardizat pentru Reinforcement Learning prin clasa `MicroBattleEnv` din `src/pettingzoo_env.py`.

* **Spațiu de Observație:** Poziții, viață, inamici în raza vizuală, mesaje de echipă.
* **Spațiu de Acțiune:** Continuu (Box) pentru mișcare și unghi tragere, sau Discret (în funcție de configurare).
* **Recompense:** Bazate pe damage dat, kill-uri, capturare obiective și supraviețuire.

---

## Documentație

Pentru mai multe detalii despre planificarea, arhitectura și cerințele proiectului, consultați resursele de mai jos:

*   🌐 **[Pagina Wiki a Proiectului](https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm/-/wikis/home)**: Hub-ul central pentru documentația proiectului.
*   📄 **[Standarde de Codare (Coding Style)](https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm/-/blob/main/docs/CODING_STYLE.md?ref_type=heads)**: Regulile de codare pe care le respectăm.
*   📂 **[Director Google Drive](https://drive.google.com/drive/folders/1D7yvULvRNyAsXOY5aZUKo3iiGY99fhaN)**: Conține documentele detaliate (SRS, SDD, WBS, Gantt).

---

## Echipa

| Nume | Rol Principal |
| :--- | :--- |
| Samson Alexandru | **Project Manager** |
| Carazeanu Antonio | **Team Leader** |
| Ilie Alexandru | **Dezvoltator** |
| Calu Andrei | **Dezvoltator** |
| Echim Andrei | **Dezvoltator** |
| Baston Jenică | **QA** |
| Trufelea Alexandru | **QA** |
| Petrea Octavian | **QA** |
| Logofătu Patricia | **QA** |
