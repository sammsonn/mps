"""
Unit tests for game modes
"""
import unittest
import sys
import os
import pygame

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Initialize pygame for time functions
pygame.init()

from survival_mode import SurvivalMode
from agent import Agent
from config import *


class TestSurvivalModeInitialization(unittest.TestCase):
    """Test Survival mode initialization"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agents = [
            Agent(100, 100, team_id=0),
            Agent(200, 100, team_id=0),
            Agent(100, 200, team_id=1),
            Agent(200, 200, team_id=1),
        ]
    
    def test_survival_mode_creation(self):
        """Test survival mode is created correctly"""
        mode = SurvivalMode(self.agents)
        
        self.assertEqual(mode.agents, self.agents)
        self.assertEqual(mode.time_limit, SURVIVAL_TIME_LIMIT)
        self.assertFalse(mode.game_over)
        self.assertIsNone(mode.winner)
    
    def test_survival_mode_start_time(self):
        """Test survival mode records start time"""
        mode = SurvivalMode(self.agents)
        
        self.assertIsNotNone(mode.start_time)
        self.assertGreater(mode.start_time, 0)


class TestSurvivalModeGameplay(unittest.TestCase):
    """Test Survival mode gameplay mechanics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agents = [
            Agent(100, 100, team_id=0),
            Agent(200, 100, team_id=0),
            Agent(100, 200, team_id=1),
            Agent(200, 200, team_id=1),
        ]
        self.mode = SurvivalMode(self.agents)
    
    def test_game_continues_with_both_teams_alive(self):
        """Test game continues when both teams have agents alive"""
        self.mode.update()
        
        self.assertFalse(self.mode.game_over)
        self.assertIsNone(self.mode.winner)
    
    def test_game_ends_when_one_team_eliminated(self):
        """Test game ends when one team is eliminated"""
        # Kill all agents from team 1
        self.agents[2].alive = False
        self.agents[3].alive = False
        
        self.mode.update()
        
        self.assertTrue(self.mode.game_over)
        self.assertEqual(self.mode.winner, 0)
    
    def test_game_ends_when_all_dead(self):
        """Test game ends when all agents are dead"""
        for agent in self.agents:
            agent.alive = False
        
        self.mode.update()
        
        self.assertTrue(self.mode.game_over)
    
    def test_winner_is_team_with_most_agents(self):
        """Test winner is determined by most agents when time expires"""
        # Kill one agent from team 1
        self.agents[3].alive = False
        
        self.mode.end_game_by_time()
        
        self.assertTrue(self.mode.game_over)
        self.assertEqual(self.mode.winner, 0)  # Team 0 has more agents


class TestSurvivalModeTimer(unittest.TestCase):
    """Test Survival mode timer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agents = [
            Agent(100, 100, team_id=0),
            Agent(200, 100, team_id=1),
        ]
        self.mode = SurvivalMode(self.agents)
    
    def test_get_remaining_time_at_start(self):
        """Test remaining time at start is full time limit"""
        remaining = self.mode.get_remaining_time()
        
        self.assertAlmostEqual(remaining, SURVIVAL_TIME_LIMIT, delta=1)
    
    def test_remaining_time_decreases(self):
        """Test remaining time decreases over time"""
        initial_remaining = self.mode.get_remaining_time()
        
        # Simulate time passing
        pygame.time.wait(100)
        
        new_remaining = self.mode.get_remaining_time()
        
        self.assertLess(new_remaining, initial_remaining)
    
    def test_remaining_time_never_negative(self):
        """Test remaining time never goes negative"""
        # Simulate time exceeding limit
        self.mode.start_time = pygame.time.get_ticks() - (SURVIVAL_TIME_LIMIT * 1000 + 5000)
        
        remaining = self.mode.get_remaining_time()
        
        self.assertGreaterEqual(remaining, 0)


class TestSurvivalModeEndConditions(unittest.TestCase):
    """Test various end conditions for Survival mode"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agents = [
            Agent(100, 100, team_id=0),
            Agent(200, 100, team_id=0),
            Agent(100, 200, team_id=1),
        ]
        self.mode = SurvivalMode(self.agents)
    
    def test_end_time_recorded_on_victory(self):
        """Test end time is recorded when game ends"""
        # Kill team 1
        self.agents[2].alive = False
        
        self.mode.update()
        
        self.assertIsNotNone(self.mode.end_time)
        self.assertTrue(self.mode.game_over)
    
    def test_end_time_recorded_on_timeout(self):
        """Test end time is recorded on time limit"""
        self.mode.end_game_by_time()
        
        self.assertIsNotNone(self.mode.end_time)
        self.assertTrue(self.mode.game_over)
    
    def test_game_stays_ended(self):
        """Test game stays ended after being set to game over"""
        # Kill team 1
        self.agents[2].alive = False
        self.mode.update()
        
        first_winner = self.mode.winner
        
        # Update again
        self.mode.update()
        
        # Should still be game over with same winner
        self.assertTrue(self.mode.game_over)
        self.assertEqual(self.mode.winner, first_winner)


class TestSurvivalModeWithMultipleTeams(unittest.TestCase):
    """Test Survival mode with various team configurations"""
    
    def test_single_team_remaining_wins(self):
        """Test single remaining team wins"""
        agents = [
            Agent(100, 100, team_id=0),
            Agent(200, 100, team_id=1),
            Agent(300, 100, team_id=2),
        ]
        mode = SurvivalMode(agents)
        
        # Kill teams 1 and 2
        agents[1].alive = False
        agents[2].alive = False
        
        mode.update()
        
        self.assertTrue(mode.game_over)
        self.assertEqual(mode.winner, 0)
    
    def test_uneven_team_sizes(self):
        """Test mode handles uneven team sizes"""
        agents = [
            Agent(100, 100, team_id=0),
            Agent(200, 100, team_id=0),
            Agent(300, 100, team_id=0),
            Agent(400, 100, team_id=1),
        ]
        mode = SurvivalMode(agents)
        
        # Kill team 1
        agents[3].alive = False
        
        mode.update()
        
        self.assertTrue(mode.game_over)
        self.assertEqual(mode.winner, 0)


if __name__ == '__main__':
    unittest.main()
