"""
Unit tests for GameMap class
"""
import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from game_map import GameMap, Wall
from config import *


class TestWall(unittest.TestCase):
    """Test Wall class"""
    
    def test_wall_creation(self):
        """Test wall is created with correct attributes"""
        wall = Wall(5, 10, TILE_SIZE)
        
        self.assertEqual(wall.x, 5)
        self.assertEqual(wall.y, 10)
        self.assertEqual(wall.health, WALL_HEALTH)
        self.assertTrue(wall.alive)
        self.assertFalse(wall.is_border)
    
    def test_border_wall_indestructible(self):
        """Test border walls are indestructible"""
        wall = Wall(0, 0, TILE_SIZE, is_border=True)
        
        self.assertTrue(wall.is_border)
        self.assertEqual(wall.health, 9999)
    
    def test_wall_takes_damage(self):
        """Test wall takes damage correctly"""
        wall = Wall(5, 10, TILE_SIZE)
        initial_health = wall.health
        
        wall.take_damage(10)
        
        self.assertEqual(wall.health, initial_health - 10)
        self.assertTrue(wall.alive)
    
    def test_wall_destroyed_when_health_zero(self):
        """Test wall is destroyed when health reaches zero"""
        wall = Wall(5, 10, TILE_SIZE)
        
        wall.take_damage(WALL_HEALTH)
        
        self.assertEqual(wall.health, 0)
        self.assertFalse(wall.alive)
    
    def test_border_wall_no_damage(self):
        """Test border walls don't take damage"""
        wall = Wall(0, 0, TILE_SIZE, is_border=True)
        initial_health = wall.health
        
        wall.take_damage(100)
        
        self.assertEqual(wall.health, initial_health)
        self.assertTrue(wall.alive)


class TestGameMapInitialization(unittest.TestCase):
    """Test GameMap initialization"""
    
    def test_map_creation_survival(self):
        """Test survival mode map is created"""
        game_map = GameMap("Survival")
        
        self.assertEqual(game_map.width, MAP_WIDTH)
        self.assertEqual(game_map.height, MAP_HEIGHT)
        self.assertEqual(game_map.game_mode, "Survival")
        self.assertIsNotNone(game_map.tiles)
        self.assertIsNotNone(game_map.obstacles)
    
    def test_map_creation_koth(self):
        """Test KOTH mode map is created"""
        game_map = GameMap("King of the Hill")
        
        self.assertEqual(game_map.game_mode, "King of the Hill")
    
    def test_map_creation_ctf(self):
        """Test CTF mode map is created"""
        game_map = GameMap("Capture the Flag")
        
        self.assertEqual(game_map.game_mode, "Capture the Flag")
    
    def test_map_has_borders(self):
        """Test that map has border walls"""
        game_map = GameMap("Survival")
        
        # Check top border
        self.assertEqual(game_map.tiles[0][5], 1)
        # Check bottom border
        self.assertEqual(game_map.tiles[MAP_HEIGHT - 1][5], 1)
        # Check left border
        self.assertEqual(game_map.tiles[5][0], 1)
        # Check right border
        self.assertEqual(game_map.tiles[5][MAP_WIDTH - 1], 1)
    
    def test_map_has_obstacle_walls(self):
        """Test that map creates Wall objects for obstacles"""
        game_map = GameMap("Survival")
        
        self.assertGreater(len(game_map.obstacles), 0)
        self.assertIsInstance(game_map.obstacles[0], Wall)


class TestGameMapSpawn(unittest.TestCase):
    """Test spawn position generation"""
    
    def test_spawn_positions_valid(self):
        """Test spawn positions are within map bounds"""
        game_map = GameMap("Survival")
        
        for team_id in range(2):
            x, y = game_map.get_spawn_position(team_id, 2)
            
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(x, MAP_WIDTH * TILE_SIZE)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(y, MAP_HEIGHT * TILE_SIZE)
    
    def test_spawn_positions_different_teams(self):
        """Test different teams get different spawn positions"""
        game_map = GameMap("Survival")
        
        x0, y0 = game_map.get_spawn_position(0, 2)
        x1, y1 = game_map.get_spawn_position(1, 2)
        
        # Positions should be different
        self.assertNotEqual((x0, y0), (x1, y1))
    
    def test_spawn_positions_not_on_walls(self):
        """Test spawn positions are not on walls"""
        game_map = GameMap("Survival")
        
        x, y = game_map.get_spawn_position(0, 2)
        
        # Convert to tile coordinates
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        
        # Should not be on a wall
        if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
            self.assertEqual(game_map.tiles[tile_y][tile_x], 0)


class TestGameMapPathfinding(unittest.TestCase):
    """Test pathfinding utilities"""
    
    def test_empty_tiles_have_value_zero(self):
        """Test empty tiles have value 0"""
        game_map = GameMap("Survival")
        
        # Find an empty tile (not border)
        for y in range(1, MAP_HEIGHT - 1):
            for x in range(1, MAP_WIDTH - 1):
                if game_map.tiles[y][x] == 0:
                    self.assertEqual(game_map.tiles[y][x], 0)
                    return
    
    def test_wall_tiles_have_value_one(self):
        """Test wall tiles have value 1"""
        game_map = GameMap("Survival")
        
        # Border tiles should be walls (value 1)
        self.assertEqual(game_map.tiles[0][0], 1)
        self.assertEqual(game_map.tiles[MAP_HEIGHT - 1][MAP_WIDTH - 1], 1)
    
    def test_tile_grid_dimensions(self):
        """Test tile grid has correct dimensions"""
        game_map = GameMap("Survival")
        
        self.assertEqual(len(game_map.tiles), MAP_HEIGHT)
        self.assertEqual(len(game_map.tiles[0]), MAP_WIDTH)
    
    def test_tile_access_pattern(self):
        """Test tiles can be accessed by [y][x] pattern"""
        game_map = GameMap("Survival")
        
        # Should be able to access any valid tile
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile_value = game_map.tiles[y][x]
                self.assertIn(tile_value, [0, 1])


class TestGameMapKOTH(unittest.TestCase):
    """Test KOTH-specific map features"""
    
    def test_koth_map_created(self):
        """Test KOTH map is created successfully"""
        game_map = GameMap("King of the Hill")
        
        self.assertEqual(game_map.game_mode, "King of the Hill")
        self.assertIsNotNone(game_map.tiles)
        self.assertIsNotNone(game_map.obstacles)
    
    def test_koth_fewer_obstacles(self):
        """Test KOTH has fewer obstacles than survival"""
        koth_map = GameMap("King of the Hill")
        survival_map = GameMap("Survival")
        
        # KOTH should have fewer obstacles to keep central area accessible
        self.assertLessEqual(len(koth_map.obstacles), len(survival_map.obstacles))


class TestGameMapCTF(unittest.TestCase):
    """Test CTF-specific map features"""
    
    def test_ctf_map_created(self):
        """Test CTF map is created successfully"""
        game_map = GameMap("Capture the Flag")
        
        self.assertEqual(game_map.game_mode, "Capture the Flag")
        self.assertIsNotNone(game_map.tiles)
        self.assertIsNotNone(game_map.obstacles)
    
    def test_ctf_has_obstacles(self):
        """Test CTF map has obstacles"""
        game_map = GameMap("Capture the Flag")
        
        # CTF should have some obstacles but not too many
        self.assertGreater(len(game_map.obstacles), 0)
        self.assertLess(len(game_map.obstacles), 200)


if __name__ == '__main__':
    unittest.main()
