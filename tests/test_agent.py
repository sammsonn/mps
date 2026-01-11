"""
Unit tests for Agent class
"""
import unittest
import sys
import os
import math

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import Agent
from config import *


class TestAgentInitialization(unittest.TestCase):
    """Test Agent initialization"""
    
    def test_agent_creation(self):
        """Test that an agent is created with correct initial values"""
        agent = Agent(100, 200, team_id=0)
        
        self.assertEqual(agent.x, 100)
        self.assertEqual(agent.y, 200)
        self.assertEqual(agent.team_id, 0)
        self.assertEqual(agent.health, AGENT_MAX_HEALTH)
        self.assertTrue(agent.alive)
        self.assertEqual(agent.speed, AGENT_SPEED)
    
    def test_agent_with_role(self):
        """Test agent creation with specific role"""
        agent = Agent(100, 200, team_id=0, role=ROLE_ATTACKER)
        
        self.assertEqual(agent.role, ROLE_ATTACKER)
    
    def test_agent_color_assignment(self):
        """Test that agents get correct team colors"""
        agent0 = Agent(100, 200, team_id=0)
        agent1 = Agent(100, 200, team_id=1)
        
        self.assertEqual(agent0.color, TEAM_COLORS[0])
        self.assertEqual(agent1.color, TEAM_COLORS[1])
    
    def test_agent_velocity_initialization(self):
        """Test that agent has random initial velocity"""
        agent = Agent(100, 200, team_id=0)
        
        # Velocity should not be zero
        self.assertNotEqual(agent.velocity_x, 0)
        self.assertNotEqual(agent.velocity_y, 0)
        
        # Velocity magnitude should be approximately equal to speed
        velocity_magnitude = math.sqrt(agent.velocity_x**2 + agent.velocity_y**2)
        self.assertAlmostEqual(velocity_magnitude, AGENT_SPEED, places=1)


class TestAgentHealth(unittest.TestCase):
    """Test Agent health and damage mechanics"""
    
    def test_take_damage(self):
        """Test that agent takes damage correctly"""
        agent = Agent(100, 200, team_id=0)
        initial_health = agent.health
        
        agent.take_damage(25)
        
        self.assertEqual(agent.health, initial_health - 25)
        self.assertTrue(agent.alive)
    
    def test_death_on_zero_health(self):
        """Test that agent dies when health reaches zero"""
        agent = Agent(100, 200, team_id=0)
        
        agent.take_damage(AGENT_MAX_HEALTH)
        
        self.assertEqual(agent.health, 0)
        self.assertFalse(agent.alive)
    
    def test_death_on_excessive_damage(self):
        """Test that agent dies when taking excessive damage"""
        agent = Agent(100, 200, team_id=0)
        
        agent.take_damage(AGENT_MAX_HEALTH + 50)
        
        self.assertEqual(agent.health, 0)
        self.assertFalse(agent.alive)
    
    def test_health_does_not_go_negative(self):
        """Test that health doesn't go below zero"""
        agent = Agent(100, 200, team_id=0)
        
        agent.take_damage(200)
        
        self.assertEqual(agent.health, 0)


class TestAgentCommunication(unittest.TestCase):
    """Test Agent communication features"""
    
    def test_limited_communication_color(self):
        """Test that agents with limited communication have different color"""
        agent = Agent(100, 200, team_id=0)
        agent.has_limited_communication = True
        agent.update_color()
        
        self.assertEqual(agent.color, TEAM_COLORS_LIMITED[0])
    
    def test_normal_communication_color(self):
        """Test that agents with normal communication have standard color"""
        agent = Agent(100, 200, team_id=0)
        agent.has_limited_communication = False
        agent.update_color()
        
        self.assertEqual(agent.color, TEAM_COLORS[0])
    
    def test_get_color_method(self):
        """Test get_color method returns correct color"""
        agent = Agent(100, 200, team_id=1)
        
        # Normal communication
        agent.has_limited_communication = False
        self.assertEqual(agent.get_color(), TEAM_COLORS[1])
        
        # Limited communication
        agent.has_limited_communication = True
        self.assertEqual(agent.get_color(), TEAM_COLORS_LIMITED[1])


class TestAgentDistance(unittest.TestCase):
    """Test Agent distance calculations"""
    
    def test_distance_to_same_position(self):
        """Test distance to same position is zero"""
        agent1 = Agent(100, 200, team_id=0)
        agent2 = Agent(100, 200, team_id=1)
        
        distance = agent1.distance_to(agent2)
        
        self.assertEqual(distance, 0)
    
    def test_distance_to_horizontal(self):
        """Test horizontal distance calculation"""
        agent1 = Agent(0, 0, team_id=0)
        agent2 = Agent(100, 0, team_id=1)
        
        distance = agent1.distance_to(agent2)
        
        self.assertEqual(distance, 100)
    
    def test_distance_to_vertical(self):
        """Test vertical distance calculation"""
        agent1 = Agent(0, 0, team_id=0)
        agent2 = Agent(0, 100, team_id=1)
        
        distance = agent1.distance_to(agent2)
        
        self.assertEqual(distance, 100)
    
    def test_distance_to_diagonal(self):
        """Test diagonal distance calculation (Pythagorean)"""
        agent1 = Agent(0, 0, team_id=0)
        agent2 = Agent(3, 4, team_id=1)
        
        distance = agent1.distance_to(agent2)
        
        self.assertEqual(distance, 5)


class TestAgentRoles(unittest.TestCase):
    """Test Agent role-based behavior"""
    
    def test_attacker_role(self):
        """Test attacker role assignment"""
        agent = Agent(100, 200, team_id=0, role=ROLE_ATTACKER)
        
        self.assertEqual(agent.role, ROLE_ATTACKER)
    
    def test_defender_role(self):
        """Test defender role assignment"""
        agent = Agent(100, 200, team_id=0, role=ROLE_DEFENDER)
        
        self.assertEqual(agent.role, ROLE_DEFENDER)
    
    def test_carrier_role(self):
        """Test carrier role assignment"""
        agent = Agent(100, 200, team_id=0, role=ROLE_CARRIER)
        
        self.assertEqual(agent.role, ROLE_CARRIER)
    
    def test_chaser_role(self):
        """Test chaser role assignment"""
        agent = Agent(100, 200, team_id=0, role=ROLE_CHASER)
        
        self.assertEqual(agent.role, ROLE_CHASER)
    
    def test_no_role(self):
        """Test agent without specific role"""
        agent = Agent(100, 200, team_id=0)
        
        self.assertIsNone(agent.role)


if __name__ == '__main__':
    unittest.main()
