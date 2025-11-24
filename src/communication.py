import pygame

class Message:
    """Mesaj simplu pentru comunicare între agenți din aceeași echipă.

    type exemple:
      ENEMY_SPOTTED: payload {enemy_id, x, y}
      DISTRESS_CALL: payload {sender_id, x, y, enemy_id}
      FLAG_TAKEN: payload {carrier_id, x, y}
      FLAG_DROPPED: payload {x, y}
      ZONE_CLEAR / ZONE_CONTESTED: payload {x, y}
    """
    def __init__(self, sender_id, team_id, msg_type, payload, timestamp):
        self.sender_id = sender_id
        self.team_id = team_id
        self.type = msg_type
        self.payload = payload
        self.timestamp = timestamp


class MessageBus:
    """Bus de mesaje cu retenție scurtă și rezolvare de agenți.

    Mesajele sunt păstrate doar câteva milisecunde pentru a preveni acumularea.
    """
    def __init__(self, max_age_ms=2000):
        self.max_age_ms = max_age_ms
        self.messages = []
        self._agent_index = {}  # agent_id -> Agent

    def set_agents(self, agent_index):
        """Actualizează indexul de agenți (apelat după spawn/reset)."""
        self._agent_index = agent_index

    def publish(self, message):
        self.messages.append(message)
        # Console logging for each message sent by an agent
        try:
            ts = message.timestamp
            print(f"[MSG][{ts}ms] {message.sender_id} (team {message.team_id}) -> {message.type} {message.payload}")
        except Exception:
            # Avoid breaking the game if printing fails
            pass

    def collect(self, team_id, current_time):
        """Returnează mesaje recente pentru echipă (nu le elimină)."""
        return [m for m in self.messages if m.team_id == team_id and current_time - m.timestamp <= self.max_age_ms]

    def cleanup(self, current_time):
        """Elimină mesajele expirate."""
        self.messages = [m for m in self.messages if current_time - m.timestamp <= self.max_age_ms]

    def resolve_agent(self, agent_id):
        return self._agent_index.get(agent_id)

    def broadcast_enemy_spotted(self, spotter_agent, enemy_agent):
        """Conveniență pentru a trimite un mesaj ENEMY_SPOTTED."""
        if not enemy_agent:
            return
        ts = pygame.time.get_ticks()
        msg = Message(
            sender_id=spotter_agent.agent_id,
            team_id=spotter_agent.team_id,
            msg_type="ENEMY_SPOTTED",
            payload={
                "enemy_id": getattr(enemy_agent, "agent_id", None),
                "x": enemy_agent.x,
                "y": enemy_agent.y
            },
            timestamp=ts
        )
        self.publish(msg)
