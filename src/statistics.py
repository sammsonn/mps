import pygame
from collections import defaultdict

class StatisticsTracker:
    """Tracker pentru statistici generale și specifice modurilor de joc"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Resetează toate statisticile"""
        # Statistici generale per agent
        self.agent_stats = defaultdict(lambda: {
            'damage_dealt': 0,
            'damage_taken': 0,
            'kills': 0,
            'deaths': 0,
            'assists': 0,
            'shots_fired': 0,
            'shots_hit': 0,
            'distance_traveled': 0,
            'time_alive': 0,
            'last_position': None,
            'spawn_time': None,
            'death_time': None
        })
        
        # Statistici per echipă
        self.team_stats = defaultdict(lambda: {
            'total_damage_dealt': 0,
            'total_damage_taken': 0,
            'total_kills': 0,
            'total_deaths': 0,
            'agents_alive': 0
        })
        
        # Statistici specifice KOTH
        self.koth_stats = {
            'dps_in_zone': defaultdict(float),  # {team_id: dps}
            'dps_out_zone': defaultdict(float),  # {team_id: dps}
            'time_in_zone': defaultdict(float),  # {team_id: seconds}
            'damage_in_zone': defaultdict(float),  # {team_id: total damage acumulat}
            'damage_out_zone': defaultdict(float),  # {team_id: total damage acumulat}
        }
        
        # Statistici specifice CTF
        self.ctf_stats = {
            'flag_captures': defaultdict(int),  # {agent_id: count}
            'flag_deliveries': defaultdict(int),  # {agent_id: count}
            'delivery_times': [],  # Lista de timpi de livrare (seconds)
            'flag_carry_times': defaultdict(list),  # {agent_id: [time1, time2, ...]}
            'flag_capture_times': defaultdict(list),  # {agent_id: [time1, time2, ...]}
            'current_carriers': {}  # {agent_id: capture_time}
        }
        
        self.start_time = pygame.time.get_ticks()
    
    def on_agent_spawn(self, agent):
        """Apelat când un agent spawn-uiește"""
        agent_id = id(agent)
        self.agent_stats[agent_id]['spawn_time'] = pygame.time.get_ticks()
        self.agent_stats[agent_id]['last_position'] = (agent.x, agent.y)
    
    def on_agent_death(self, agent, killer=None):
        """Apelat când un agent moare"""
        agent_id = id(agent)
        current_time = pygame.time.get_ticks()
        
        # Actualizează timpul de viață
        if self.agent_stats[agent_id]['spawn_time']:
            time_alive = (current_time - self.agent_stats[agent_id]['spawn_time']) / 1000.0
            self.agent_stats[agent_id]['time_alive'] += time_alive
        
        self.agent_stats[agent_id]['death_time'] = current_time
        self.agent_stats[agent_id]['deaths'] += 1
        self.team_stats[agent.team_id]['total_deaths'] += 1
        
        # Dacă există killer, actualizează kill-urile
        if killer:
            killer_id = id(killer)
            self.agent_stats[killer_id]['kills'] += 1
            self.team_stats[killer.team_id]['total_kills'] += 1
    
    def on_damage_dealt(self, agent, damage, target):
        """Apelat când un agent provoacă damage"""
        agent_id = id(agent)
        target_id = id(target)
        
        self.agent_stats[agent_id]['damage_dealt'] += damage
        self.agent_stats[target_id]['damage_taken'] += damage
        self.team_stats[agent.team_id]['total_damage_dealt'] += damage
        self.team_stats[target.team_id]['total_damage_taken'] += damage
    
    def on_shot_fired(self, agent):
        """Apelat când un agent trage"""
        agent_id = id(agent)
        self.agent_stats[agent_id]['shots_fired'] += 1
    
    def on_shot_hit(self, agent):
        """Apelat când un agent lovește ținta"""
        agent_id = id(agent)
        self.agent_stats[agent_id]['shots_hit'] += 1
    
    def update_agent_movement(self, agent):
        """Actualizează distanța parcursă de agent"""
        agent_id = id(agent)
        last_pos = self.agent_stats[agent_id]['last_position']
        
        if last_pos:
            dx = agent.x - last_pos[0]
            dy = agent.y - last_pos[1]
            distance = (dx*dx + dy*dy) ** 0.5
            self.agent_stats[agent_id]['distance_traveled'] += distance
        
        self.agent_stats[agent_id]['last_position'] = (agent.x, agent.y)
    
    # ========== KOTH Statistics ==========
    
    def update_koth_dps(self, agents, zones, current_time):
        """Actualizează DPS pentru KOTH (în zonă și în afara zonei)"""
        # Calculează timpul total de joc
        total_elapsed = (current_time - self.start_time) / 1000.0
        
        # Calculează DPS bazat pe damage total acumulat până acum
        # DPS = damage total / timp total
        if total_elapsed > 0:
            for team_id in [0, 1]:
                # DPS total în zonă
                total_damage_in = self.koth_stats['damage_in_zone'][team_id]
                self.koth_stats['dps_in_zone'][team_id] = total_damage_in / total_elapsed if total_elapsed > 0 else 0.0
                
                # DPS total în afara zonei
                total_damage_out = self.koth_stats['damage_out_zone'][team_id]
                self.koth_stats['dps_out_zone'][team_id] = total_damage_out / total_elapsed if total_elapsed > 0 else 0.0
    
    def on_koth_damage(self, agent, damage, in_zone):
        """Apelat când se provoacă damage în KOTH"""
        if agent is None:
            return
        team_id = agent.team_id
        if in_zone:
            self.koth_stats['damage_in_zone'][team_id] += damage
        else:
            self.koth_stats['damage_out_zone'][team_id] += damage
    
    def get_koth_dps(self, team_id, in_zone=True):
        """Returnează DPS pentru o echipă în KOTH"""
        if in_zone:
            return self.koth_stats['dps_in_zone'][team_id]
        else:
            return self.koth_stats['dps_out_zone'][team_id]
    
    # ========== CTF Statistics ==========
    
    def on_flag_captured(self, agent, current_time):
        """Apelat când un agent capturează un steag"""
        agent_id = id(agent)
        self.ctf_stats['flag_captures'][agent_id] += 1
        self.ctf_stats['flag_capture_times'][agent_id].append(current_time)
        self.ctf_stats['current_carriers'][agent_id] = current_time
    
    def on_flag_delivered(self, agent, current_time):
        """Apelat când un agent livrează un steag"""
        agent_id = id(agent)
        self.ctf_stats['flag_deliveries'][agent_id] += 1
        
        # Calculează timpul de livrare
        if agent_id in self.ctf_stats['current_carriers']:
            capture_time = self.ctf_stats['current_carriers'][agent_id]
            delivery_time = (current_time - capture_time) / 1000.0  # în secunde
            self.ctf_stats['delivery_times'].append(delivery_time)
            
            # Actualizează timpul în viață cu steagul
            if agent_id in self.ctf_stats['flag_capture_times']:
                # Găsește ultimul timp de captură
                capture_times = self.ctf_stats['flag_capture_times'][agent_id]
                if capture_times:
                    last_capture = capture_times[-1]
                    carry_time = (current_time - last_capture) / 1000.0
                    self.ctf_stats['flag_carry_times'][agent_id].append(carry_time)
            
            # Elimină din current_carriers
            del self.ctf_stats['current_carriers'][agent_id]
    
    def on_flag_dropped(self, agent, current_time):
        """Apelat când un agent scapă un steag (moare)"""
        agent_id = id(agent)
        if agent_id in self.ctf_stats['current_carriers']:
            capture_time = self.ctf_stats['current_carriers'][agent_id]
            carry_time = (current_time - capture_time) / 1000.0
            self.ctf_stats['flag_carry_times'][agent_id].append(carry_time)
            del self.ctf_stats['current_carriers'][agent_id]
    
    def get_avg_delivery_time(self):
        """Returnează timpul mediu de livrare pentru CTF"""
        if not self.ctf_stats['delivery_times']:
            return 0.0
        return sum(self.ctf_stats['delivery_times']) / len(self.ctf_stats['delivery_times'])
    
    def get_avg_flag_carry_time(self, agent_id=None):
        """Returnează timpul mediu în viață cu steagul"""
        if agent_id:
            times = self.ctf_stats['flag_carry_times'].get(agent_id, [])
        else:
            # Toate timpurile pentru toți agenții
            times = []
            for agent_times in self.ctf_stats['flag_carry_times'].values():
                times.extend(agent_times)
        
        if not times:
            return 0.0
        return sum(times) / len(times)
    
    # ========== General Statistics ==========
    
    def get_agent_kda(self, agent_id):
        """Returnează KDA pentru un agent"""
        stats = self.agent_stats[agent_id]
        deaths = stats['deaths']
        if deaths == 0:
            deaths = 1  # Evită împărțirea la zero
        return (stats['kills'] + stats['assists'] * 0.5) / deaths
    
    def get_agent_dps(self, agent_id, elapsed_time):
        """Returnează DPS pentru un agent"""
        if elapsed_time == 0:
            return 0.0
        return self.agent_stats[agent_id]['damage_dealt'] / elapsed_time
    
    def get_summary(self):
        """Returnează un sumar al statisticilor"""
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
        
        summary = {
            'elapsed_time': elapsed,
            'agents': {},
            'teams': dict(self.team_stats),
            'koth': {
                'dps_in_zone': dict(self.koth_stats['dps_in_zone']),
                'dps_out_zone': dict(self.koth_stats['dps_out_zone'])
            },
            'ctf': {
                'avg_delivery_time': self.get_avg_delivery_time(),
                'avg_flag_carry_time': self.get_avg_flag_carry_time()
            }
        }
        
        return summary

