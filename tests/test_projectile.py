"""
Unit tests for Projectile class
"""
import unittest
import sys
import os
import math
import pygame

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Initialize pygame for time functions
pygame.init()

from projectile import Projectile
from agent import Agent
from config import *


class TestProjectileInitialization(unittest.TestCase):
    """Test Projectile initialization"""
    
    def test_projectile_creation(self):
        """Test that a projectile is created with correct initial values"""
        projectile = Projectile(100, 200, math.pi/4, team_id=0)
        
        self.assertEqual(projectile.x, 100)
        self.assertEqual(projectile.y, 200)
        self.assertEqual(projectile.angle, math.pi/4)
        self.assertEqual(projectile.team_id, 0)
        self.assertEqual(projectile.damage, PROJECTILE_DAMAGE)
        self.assertTrue(projectile.alive)
        self.assertEqual(projectile.speed, PROJECTILE_SPEED)
    
    def test_projectile_with_custom_damage(self):
        """Test projectile creation with custom damage"""
        projectile = Projectile(100, 200, 0, team_id=0, damage=50)
        
        self.assertEqual(projectile.damage, 50)
    
    def test_projectile_with_owner(self):
        """Test projectile creation with owner agent"""
        owner = Agent(100, 200, team_id=0)
        projectile = Projectile(100, 200, 0, team_id=0, owner=owner)
        
        self.assertEqual(projectile.owner, owner)
    
    def test_projectile_velocity_calculation(self):
        """Test that projectile velocity is calculated correctly from angle"""
        # Test horizontal projectile (0 radians)
        proj = Projectile(0, 0, 0, team_id=0)
        self.assertAlmostEqual(proj.velocity_x, PROJECTILE_SPEED, places=5)
        self.assertAlmostEqual(proj.velocity_y, 0, places=5)
        
        # Test vertical projectile (pi/2 radians)
        proj = Projectile(0, 0, math.pi/2, team_id=0)
        self.assertAlmostEqual(proj.velocity_x, 0, places=5)
        self.assertAlmostEqual(proj.velocity_y, PROJECTILE_SPEED, places=5)


class TestProjectileMovement(unittest.TestCase):
    """Test Projectile movement"""
    
    def test_projectile_moves_forward(self):
        """Test that projectile moves in the direction of its angle"""
        projectile = Projectile(100, 100, 0, team_id=0)  # Horizontal right
        initial_x = projectile.x
        
        current_time = pygame.time.get_ticks()
        projectile.update(current_time)
        
        # Should move right
        self.assertGreater(projectile.x, initial_x)
        self.assertEqual(projectile.y, 100)  # Y should not change
    
    def test_projectile_moves_multiple_updates(self):
        """Test that projectile continues moving over multiple updates"""
        projectile = Projectile(100, 100, 0, team_id=0)
        current_time = pygame.time.get_ticks()
        
        initial_x = projectile.x
        
        # Update multiple times
        for _ in range(5):
            projectile.update(current_time)
        
        # Should have moved significantly
        distance_moved = projectile.x - initial_x
        expected_distance = PROJECTILE_SPEED * 5
        self.assertAlmostEqual(distance_moved, expected_distance, places=1)


class TestProjectileLifetime(unittest.TestCase):
    """Test Projectile lifetime and expiration"""
    
    def test_projectile_expires_after_lifetime(self):
        """Test that projectile expires after its lifetime"""
        projectile = Projectile(100, 100, 0, team_id=0)
        
        # Simulate time passing beyond lifetime
        future_time = projectile.creation_time + PROJECTILE_LIFETIME + 100
        projectile.update(future_time)
        
        self.assertFalse(projectile.alive)
    
    def test_projectile_dies_out_of_bounds(self):
        """Test that projectile dies when leaving map bounds"""
        # Create projectile near edge
        projectile = Projectile(MAP_WIDTH * TILE_SIZE + 10, 100, 0, team_id=0)
        
        current_time = pygame.time.get_ticks()
        projectile.update(current_time)
        
        self.assertFalse(projectile.alive)


class TestProjectileCollision(unittest.TestCase):
    """Test Projectile collision detection"""
    
    def test_collision_with_enemy_agent(self):
        """Test projectile collides with enemy agent"""
        agent = Agent(100, 100, team_id=1)
        projectile = Projectile(100, 100, 0, team_id=0)  # Different team
        
        collision = projectile.check_collision_with_agent(agent)
        
        self.assertTrue(collision)
        self.assertFalse(projectile.alive)
    
    def test_no_collision_with_friendly_agent(self):
        """Test projectile doesn't collide with same team agent"""
        agent = Agent(100, 100, team_id=0)
        projectile = Projectile(100, 100, 0, team_id=0)  # Same team
        
        collision = projectile.check_collision_with_agent(agent)
        
        self.assertFalse(collision)
        self.assertTrue(projectile.alive)
    
    def test_collision_damages_agent(self):
        """Test that collision damages the agent"""
        agent = Agent(100, 100, team_id=1)
        initial_health = agent.health
        projectile = Projectile(100, 100, 0, team_id=0, damage=30)
        
        projectile.check_collision_with_agent(agent)
        
        self.assertEqual(agent.health, initial_health - 30)
    
    def test_no_collision_with_dead_agent(self):
        """Test projectile doesn't collide with dead agent"""
        agent = Agent(100, 100, team_id=1)
        agent.alive = False
        projectile = Projectile(100, 100, 0, team_id=0)
        
        collision = projectile.check_collision_with_agent(agent)
        
        self.assertFalse(collision)
    
    def test_no_collision_when_far_away(self):
        """Test no collision when agent is far from projectile"""
        agent = Agent(100, 100, team_id=1)
        projectile = Projectile(500, 500, 0, team_id=0)  # Far away
        
        collision = projectile.check_collision_with_agent(agent)
        
        self.assertFalse(collision)


if __name__ == '__main__':
    unittest.main()
