import pygame
import math
from config import COMMUNICATION_RANGE
from logger import logger

class Message:
    """Mesaj simplu pentru comunicare între agenți din aceeași echipă.

    type exemple:
      ENEMY_SPOTTED: payload {enemy_id, x, y}
      DISTRESS_CALL: payload {sender_id, x, y, enemy_id}
      FLAG_TAKEN: payload {carrier_id, x, y}
      FLAG_DROPPED: payload {x, y}
      ZONE_CLEAR / ZONE_CONTESTED: payload {x, y}
    """
    def __init__(self, sender_id, team_id, msg_type, payload, timestamp, sender_x=None, sender_y=None, is_limited=False):
        self.sender_id = sender_id
        self.team_id = team_id
        self.type = msg_type
        self.payload = payload
        self.timestamp = timestamp
        self.sender_x = sender_x  # Poziția expeditorului (pentru comunicare limitată)
        self.sender_y = sender_y
        self.is_limited = is_limited  # Dacă True, mesajul poate fi primit doar de vecinii apropiați


class MessageBus:
    """Bus de mesaje cu retenție scurtă și rezolvare de agenți.

    Mesajele sunt păstrate doar câteva milisecunde pentru a preveni acumularea.
    """
    def __init__(self, max_age_ms=2000):
        self.max_age_ms = max_age_ms
        self.messages = []
        self._agent_index = {}  # agent_id -> Agent
        self._team_communication_modes = {}  # team_id -> "FULL" | "LIMITED" | "NONE"

    def set_agents(self, agent_index):
        """Actualizează indexul de agenți (apelat după spawn/reset)."""
        self._agent_index = agent_index

    def set_team_communication_modes(self, team_modes):
        """Setează modurile de comunicare pentru fiecare echipă."""
        self._team_communication_modes = team_modes

    def publish(self, message):
        self.messages.append(message)
        # Console logging for each message sent by an agent
        try:
            ts = message.timestamp
            logger.info(f"[MSG][{ts}ms] {message.sender_id} (team {message.team_id}) -> {message.type} {message.payload}")
        except Exception:
            # Avoid breaking the game if printing fails
            pass

    def collect(self, team_id, current_time, receiving_agent=None):
        """Returnează mesaje recente pentru echipă (nu le elimină).
        
        Dacă receiving_agent este furnizat și mesajul este de la un agent cu comunicare limitată,
        verifică dacă receptorul este suficient de aproape pentru a primi mesajul.
        
        Respectă modul de comunicare al echipei: NONE blochează toate mesajele, 
        LIMITED permite doar mesajele de la vecinii apropiați, FULL permite toate mesajele.
        """
        # Dacă echipa nu are comunicare (NONE), returnează lista goală
        team_mode = self._team_communication_modes.get(team_id, "FULL")
        if team_mode == "NONE":
            return []
        
        filtered_messages = []
        for m in self.messages:
            # Verifică dacă mesajul este pentru echipa corectă și nu a expirat
            if m.team_id != team_id or (current_time - m.timestamp) > self.max_age_ms:
                continue
            
            # Pentru modul LIMITED, verifică distanța
            if team_mode == "LIMITED" and receiving_agent is not None:
                # Verifică dacă receptorul este suficient de aproape
                if m.sender_x is not None and m.sender_y is not None:
                    dx = receiving_agent.x - m.sender_x
                    dy = receiving_agent.y - m.sender_y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Dacă distanța este mai mare decât raza de comunicare, ignoră mesajul
                    if distance > COMMUNICATION_RANGE:
                        continue
            # Pentru modul FULL, toate mesajele sunt permise (dar verificăm și flag-ul legacy is_limited)
            elif m.is_limited and receiving_agent is not None:
                # Verifică dacă receptorul este suficient de aproape pentru mesajele cu is_limited=True
                if m.sender_x is not None and m.sender_y is not None:
                    dx = receiving_agent.x - m.sender_x
                    dy = receiving_agent.y - m.sender_y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Dacă distanța este mai mare decât raza de comunicare, ignoră mesajul
                    if distance > COMMUNICATION_RANGE:
                        continue
            
            filtered_messages.append(m)
        
        return filtered_messages

    def cleanup(self, current_time):
        """Elimină mesajele expirate."""
        self.messages = [m for m in self.messages if current_time - m.timestamp <= self.max_age_ms]

    def resolve_agent(self, agent_id):
        return self._agent_index.get(agent_id)

    def broadcast_enemy_spotted(self, spotter_agent, enemy_agent):
        """Conveniență pentru a trimite un mesaj ENEMY_SPOTTED.
        
        Dacă agentul are comunicare limitată, mesajul va fi primit doar de vecinii apropiați.
        Coordonatele sunt rotunjite la 3 zecimale.
        """
        # Dacă comunicarea este dezactivată pentru agent, nu trimite mesaje
        if getattr(spotter_agent, 'communication_disabled', False):
            return
        if not enemy_agent:
            return
        ts = pygame.time.get_ticks()
        is_limited = getattr(spotter_agent, 'has_limited_communication', False)
        msg = Message(
            sender_id=spotter_agent.agent_id,
            team_id=spotter_agent.team_id,
            msg_type="ENEMY_SPOTTED",
            payload={
                "enemy_id": getattr(enemy_agent, "agent_id", None),
                "x": round(enemy_agent.x, 3),
                "y": round(enemy_agent.y, 3)
            },
            timestamp=ts,
            sender_x=round(spotter_agent.x, 3),
            sender_y=round(spotter_agent.y, 3),
            is_limited=is_limited
        )
        self.publish(msg)
