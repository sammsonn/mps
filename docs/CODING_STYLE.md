# Coding Style Guide

## Introducere

Acest document definește stilul de codare și convențiile care trebuie urmate în cadrul proiectului **Synapse Strike**. Respectarea acestui ghid asigură un cod curat, lizibil și mentenabil, facilitând colaborarea în cadrul echipei.

## Principii Generale

- **Lizibilitate:** Codul trebuie să fie ușor de citit și de înțeles. Un cod clar este mai important decât un cod concis.
- **Consistență:** Urmați stilul de codare existent în proiect. Dacă adăugați cod nou, respectați convențiile deja stabilite.
- **Simplitate:** Păstrați codul cât mai simplu posibil. Evitați complexitatea inutilă.

## Convenții de Denumire

| Element | Convenție | Exemplu |
|---|---|---|
| **Variabile** | `camelCase` | `agentSpeed`, `remainingAmmo` |
| **Constante** | `UPPER_CASE_SNAKE_CASE` | `MAX_HEALTH`, `DEFAULT_SPEED` |
| **Funcții/Metode** | `camelCase` | `calculateDamage()`, `moveAgent()` |
| **Clase/Structuri** | `PascalCase` | `AgentController`, `GameMap` |
| **Fișiere** | `PascalCase` sau `kebab-case` | `AgentController.cs`, `game-map.js` |
| **Variabile Private** | Prefix `_` | `_agentHealth`, `_isReloading` |

## Formatare

- **Indentare:** Folosiți 4 spații pentru indentare, nu tab-uri.
- **Lungimea liniei:** Limitați lungimea liniilor de cod la 120 de caractere.
- **Spații:**
    - Folosiți un spațiu după virgule și în jurul operatorilor (`=`, `+`, `-`, `*`, `/`, etc.).
    - Nu folosiți spații în interiorul parantezelor.
- **Linii goale:** Folosiți linii goale pentru a separa blocurile logice de cod și pentru a îmbunătăți lizibilitatea.

## Comentarii

- **Comentarii de bloc:** Folosiți comentarii de bloc pentru a explica secțiuni complexe de cod.
- **Comentarii inline:** Folosiți comentarii inline pentru a clarifica linii specifice de cod.
- **Documentație:** Documentați funcțiile și clasele publice, explicând scopul lor, parametrii și valoarea de retur.

```javascript
/**
 * Calculează daunele pe care un agent le poate provoca.
 * @param {number} baseDamage - Daunele de bază ale agentului.
 * @param {number} damageMultiplier - Multiplicatorul de daune.
 * @returns {number} Daunele totale calculate.
 */
function calculateDamage(baseDamage, damageMultiplier) {
    // Calculează daunele totale
    return baseDamage * damageMultiplier; // Daunele finale
}
