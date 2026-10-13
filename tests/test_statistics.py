"""
Unit tests for Statistics tracking
"""
import unittest
import sys
import os
import pygame

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Initialize pygame for time functions
pygame.init()

from statistics import StatisticsTracker
from agent import Agent


class TestStatisticsTrackerInitialization(unittest.TestCase):
    """Test StatisticsTracker initialization"""
    
    def test_tracker_creation(self):
        """Test tracker is created with empty stats"""
        tracker = StatisticsTracker()
        
        self.assertIsNotNone(tracker.agent_stats)
        self.assertIsNotNone(tracker.team_stats)
        self.assertEqual(len(tracker.agent_stats), 0)
        self.assertEqual(len(tracker.team_stats), 0)
    
    def test_tracker_reset(self):
        """Test tracker can be reset"""
        tracker = StatisticsTracker()
        
        # Add some stats
        agent = Agent(100, 100, 0)
        tracker.on_agent_spawn(agent)
        
        # Reset
        tracker.reset()
        
        # Stats should be empty
        self.assertEqual(len(tracker.agent_stats), 0)


class TestAgentStatistics(unittest.TestCase):
    """Test agent-specific statistics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker = StatisticsTracker()
        self.agent = Agent(100, 100, team_id=0)
    
    def test_on_agent_spawn(self):
        """Test agent spawn is recorded"""
        self.tracker.on_agent_spawn(self.agent)
        
        agent_id = id(self.agent)
        self.assertIn(agent_id, self.tracker.agent_stats)
        self.assertIsNotNone(self.tracker.agent_stats[agent_id]['spawn_time'])
    
    def test_on_agent_death(self):
        """Test agent death is recorded"""
        self.tracker.on_agent_spawn(self.agent)
        self.tracker.on_agent_death(self.agent)
        
        agent_id = id(self.agent)
        self.assertEqual(self.tracker.agent_stats[agent_id]['deaths'], 1)
        self.assertIsNotNone(self.tracker.agent_stats[agent_id]['death_time'])
    
    def test_on_damage_dealt(self):
        """Test damage dealt is recorded"""
        target = Agent(200, 200, team_id=1)
        
        self.tracker.on_damage_dealt(self.agent, 25, target)
        
        agent_id = id(self.agent)
        target_id = id(target)
        
        self.assertEqual(self.tracker.agent_stats[agent_id]['damage_dealt'], 25)
        self.assertEqual(self.tracker.agent_stats[target_id]['damage_taken'], 25)
    
    def test_on_shot_fired(self):
        """Test shot fired is recorded"""
        self.tracker.on_shot_fired(self.agent)
        
        agent_id = id(self.agent)
        self.assertEqual(self.tracker.agent_stats[agent_id]['shots_fired'], 1)
    
    def test_on_shot_hit(self):
        """Test shot hit is recorded"""
        self.tracker.on_shot_hit(self.agent)
        
        agent_id = id(self.agent)
        self.assertEqual(self.tracker.agent_stats[agent_id]['shots_hit'], 1)
    
    def test_kill_recorded_on_death_with_killer(self):
        """Test killer gets kill credit"""
        killer = Agent(200, 200, team_id=1)
        
        self.tracker.on_agent_death(self.agent, killer=killer)
        
        killer_id = id(killer)
        self.assertEqual(self.tracker.agent_stats[killer_id]['kills'], 1)


class TestTeamStatistics(unittest.TestCase):
    """Test team-specific statistics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker = StatisticsTracker()
        self.agent_team0 = Agent(100, 100, team_id=0)
        self.agent_team1 = Agent(200, 200, team_id=1)
    
    def test_team_damage_dealt(self):
        """Test team damage dealt is tracked"""
        self.tracker.on_damage_dealt(self.agent_team0, 50, self.agent_team1)
        
        self.assertEqual(self.tracker.team_stats[0]['total_damage_dealt'], 50)
    
    def test_team_damage_taken(self):
        """Test team damage taken is tracked"""
        self.tracker.on_damage_dealt(self.agent_team0, 50, self.agent_team1)
        
        self.assertEqual(self.tracker.team_stats[1]['total_damage_taken'], 50)
    
    def test_team_kills(self):
        """Test team kills are tracked"""
        self.tracker.on_agent_death(self.agent_team1, killer=self.agent_team0)
        
        self.assertEqual(self.tracker.team_stats[0]['total_kills'], 1)
    
    def test_team_deaths(self):
        """Test team deaths are tracked"""
        self.tracker.on_agent_death(self.agent_team1)
        
        self.assertEqual(self.tracker.team_stats[1]['total_deaths'], 1)


class TestKOTHStatistics(unittest.TestCase):
    """Test KOTH-specific statistics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker = StatisticsTracker()
    
    def test_koth_stats_initialized(self):
        """Test KOTH stats are initialized"""
        self.assertIn('dps_in_zone', self.tracker.koth_stats)
        self.assertIn('dps_out_zone', self.tracker.koth_stats)
        self.assertIn('time_in_zone', self.tracker.koth_stats)
    
    def test_koth_stats_defaultdict(self):
        """Test KOTH stats use defaultdict"""
        # Accessing non-existent key should return default value (0 or empty)
        self.assertIsNotNone(self.tracker.koth_stats['time_in_zone'][0])
        self.assertIsNotNone(self.tracker.koth_stats['damage_in_zone'][0])


class TestCTFStatistics(unittest.TestCase):
    """Test CTF-specific statistics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker = StatisticsTracker()
        self.agent = Agent(100, 100, team_id=0)
    
    def test_ctf_stats_initialized(self):
        """Test CTF stats are initialized"""
        self.assertIn('flag_captures', self.tracker.ctf_stats)
        self.assertIn('flag_deliveries', self.tracker.ctf_stats)
        self.assertIn('delivery_times', self.tracker.ctf_stats)
    
    def test_on_flag_captured(self):
        """Test flag capture is recorded"""
        agent_id = id(self.agent)
        current_time = pygame.time.get_ticks()
        
        self.tracker.on_flag_captured(self.agent, current_time)
        
        self.assertEqual(self.tracker.ctf_stats['flag_captures'][agent_id], 1)
    
    def test_on_flag_delivered(self):
        """Test flag delivery is recorded"""
        agent_id = id(self.agent)
        capture_time = pygame.time.get_ticks()
        
        # First capture
        self.tracker.on_flag_captured(self.agent, capture_time)
        
        # Wait a bit
        pygame.time.wait(100)
        
        # Then deliver
        delivery_time = pygame.time.get_ticks()
        self.tracker.on_flag_delivered(self.agent, delivery_time)
        
        self.assertEqual(self.tracker.ctf_stats['flag_deliveries'][agent_id], 1)


class TestAccuracyCalculations(unittest.TestCase):
    """Test accuracy and ratio calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker = StatisticsTracker()
        self.agent = Agent(100, 100, team_id=0)
    
    def test_manual_accuracy_calculation(self):
        """Test manual accuracy calculation from stats"""
        agent_id = id(self.agent)
        
        # Fire 10 shots, hit 6
        for _ in range(10):
            self.tracker.on_shot_fired(self.agent)
        
        for _ in range(6):
            self.tracker.on_shot_hit(self.agent)
        
        shots_fired = self.tracker.agent_stats[agent_id]['shots_fired']
        shots_hit = self.tracker.agent_stats[agent_id]['shots_hit']
        
        self.assertEqual(shots_fired, 10)
        self.assertEqual(shots_hit, 6)
        
        # Calculate accuracy manually
        accuracy = (shots_hit / shots_fired * 100) if shots_fired > 0 else 0
        self.assertEqual(accuracy, 60.0)
    
    def test_accuracy_no_shots(self):
        """Test accuracy stats when no shots fired"""
        agent_id = id(self.agent)
        
        shots_fired = self.tracker.agent_stats[agent_id]['shots_fired']
        shots_hit = self.tracker.agent_stats[agent_id]['shots_hit']
        
        self.assertEqual(shots_fired, 0)
        self.assertEqual(shots_hit, 0)
    
    def test_manual_kda_calculation(self):
        """Test manual KDA ratio calculation"""
        agent_id = id(self.agent)
        
        # Set stats
        self.tracker.agent_stats[agent_id]['kills'] = 10
        self.tracker.agent_stats[agent_id]['deaths'] = 5
        self.tracker.agent_stats[agent_id]['assists'] = 5
        
        kills = self.tracker.agent_stats[agent_id]['kills']
        deaths = self.tracker.agent_stats[agent_id]['deaths']
        assists = self.tracker.agent_stats[agent_id]['assists']
        
        # KDA = (Kills + Assists) / Deaths = (10 + 5) / 5 = 3.0
        kda = (kills + assists) / deaths if deaths > 0 else (kills + assists)
        self.assertEqual(kda, 3.0)
    
    def test_kda_no_deaths(self):
        """Test KDA calculation when no deaths (perfect score)"""
        agent_id = id(self.agent)
        
        self.tracker.agent_stats[agent_id]['kills'] = 10
        self.tracker.agent_stats[agent_id]['deaths'] = 0
        self.tracker.agent_stats[agent_id]['assists'] = 5
        
        kills = self.tracker.agent_stats[agent_id]['kills']
        deaths = self.tracker.agent_stats[agent_id]['deaths']
        assists = self.tracker.agent_stats[agent_id]['assists']
        
        # Should return kills + assists when deaths = 0
        kda = (kills + assists) / deaths if deaths > 0 else (kills + assists)
        self.assertEqual(kda, 15.0)


if __name__ == '__main__':
    unittest.main()
