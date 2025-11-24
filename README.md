# 2D Arena Micro-Battle

[![Stare Proiect](https://img.shields.io/badge/status-in%20development-yellow.svg)](https://shields.io/)
[![Licență](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)

Un joc 2D de tip arenă, cu acțiune rapidă, dezvoltat în cadrul materiei **Managementul Proiectelor Software**.

---

## Cuprins

*   [Despre Proiect](#despre-proiect)
*   [Tehnologii Folosite](#tehnologii-folosite)
*   [Cum se Rulează](#cum-se-ruleaz%C4%83)
*   [Structura Proiectului](#structura-proiectului)
*   [Flux de Dezvoltare (Workflow)](#flux-de-dezvoltare-workflow)
*   [Documentație](#documenta%C8%9Bie)
*   [Echipa](#echipa)

---

## Despre Proiect

**2D Arena Micro-Battle** este un prototip de joc în care agenți controlați de jucător și/sau de AI se luptă într-o arenă statică. Proiectul explorează conceptele de bază ale dezvoltării de jocuri, incluzând controlul personajului, mecanici de luptă, inteligență artificială simplă și managementul stării jocului.

### Funcționalități Principale
-   Controlul fluid al unui agent într-un mediu 2D.
-   Un sistem de luptă bazat pe proiectile.
-   Agenți inamici cu un comportament de bază (AI).
-   Sistem de viață și coliziuni.
-   O interfață de utilizator (UI) minimalistă pentru afișarea informațiilor esențiale.

---

## Tehnologii Folosite

*   **Motor de Joc:** ![Unity](https://img.shields.io/badge/Unity-202X.X-black?style=for-the-badge&logo=unity)
*   **Limbaj de Programare:** ![C#](https://img.shields.io/badge/C%23-239120?style=for-the-badge&logo=c-sharp&logoColor=white)*   **Versionare:** ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
*   **IDE:** Visual Studio / JetBrains Rider

---

## Cum se Rulează

Pentru a rula acest proiect local, urmați acești pași:

### Prerechizite
Asigurați-vă că aveți instalate următoarele:
*   [Git](https://git-scm.com/)
*   [Unity Hub](https://unity.com/download)
*   Unity Editor (versiunea **202x.x.x** - aceeași versiune folosită în proiect)

### Instalare și Rulare
1.  **Clonați repository-ul:**
    ```sh
    git clone [LINK-CATRE-REPOSITORY-UL-DVS.]
    ```
2.  **Deschideți proiectul în Unity Hub:**
    *   Lansați Unity Hub.
    *   Apăsați pe butonul `Open` sau `Add project from disk`.
    *   Navigați la folderul unde ați clonat repository-ul și selectați-l.
3.  **Deschideți scena principală:**
    *   În fereastra `Project` din Unity, navigați la `Assets/Scenes/`.
    *   Deschideți scena `MainArena.unity`.
4.  **Rulați jocul:**
    *   Apăsați butonul **Play** (▶) din partea de sus a editorului Unity.

---

## Structura Proiectului

Proiectul respectă o structură de foldere standard pentru a menține o bună organizare.

```
/
├── Assets/                 # Directorul principal pentru resursele Unity
│   ├── Scripts/            # Toate script-urile C#
│   │   ├── Player/
│   │   ├── Enemy/
│   │   └── Core/           # Script-uri de management (GameManager, etc.)
│   ├── Sprites/            # Toate resursele grafice 2D
│   ├── Prefabs/            # Obiecte pre-configurate (Player, Enemy, Projectile)
│   └── Scenes/             # Scenele jocului (MainArena, etc.)
│
├── Documentation/          # Documente de proiect (SRS, SDD, etc.)
│
├── .gitignore              # Fișier pentru a ignora fișierele temporare Unity
└── README.md               # Acest fișier
```

---

## Flux de Dezvoltare (Workflow)

Colaborarea în cadrul acestui proiect se bazează pe un flux de lucru **Gitflow simplificat**:
-   **`main`**: Conține doar versiuni stabile, corespunzătoare milestone-urilor.
-   **`develop`**: Este branch-ul principal de dezvoltare. Toate funcționalitățile noi sunt integrate aici.
-   **Branch-uri `feature/`**: Orice funcționalitate nouă se dezvoltă pe un branch dedicat (ex: `feature/player-shooting`).
-   **Pull Requests (PRs)**: Toate modificările trebuie să treacă printr-un Pull Request către `develop` și să fie aprobate de **cel puțin un alt membru al echipei** înainte de a fi integrate.

---

## Documentație

Pentru mai multe detalii despre planificarea, arhitectura și cerințele proiectului, consultați resursele de mai jos:

*   🌐 **[Pagina Wiki a Proiectului](https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm/-/wikis/homeLINK-CATRE-WIKI)**: Hub-ul central pentru documentația proiectului.
*   📄 **[Standarde de Codare (Coding Style)](https://gitlab.cs.pub.ro/mps-2025/track-1/lu-12-14-luckycharm/-/blob/main/CODING_STYLE.md?ref_type=heads)**: Regulile de codare pe care le respectăm.
*   📂 **[Director Google Drive](https://drive.google.com/drive/folders/1D7yvULvRNyAsXOY5aZUKo3iiGY99fhaN)**: Conține documentele detaliate (SRS, SDD, WBS, Gantt).

---

## Echipa

| Nume | Rol Principal |
| :--- | :--- |
| Samson Alexandru | **Project Manager** |
| [Nume Membru 2] | **Team Leader / Arhitect** |
| [Nume Membru 3] | **Dezvoltator Gameplay** |
| [Nume Membru 4] | **Dezvoltator / QA** |