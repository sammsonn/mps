# Unit Tests for Synapse Strike

This directory contains comprehensive unit tests for the Synapse Strike game.

## Test Structure

```
tests/
├── __init__.py              # Test package init
├── run_tests.py             # Main test runner
├── test_agent.py            # Agent class tests
├── test_projectile.py       # Projectile class tests
├── test_communication.py    # Message & MessageBus tests
├── test_game_map.py         # GameMap & Wall tests
├── test_survival_mode.py    # Survival mode tests
├── test_statistics.py       # Statistics tracking tests
└── README.md                # This file
```

## Running Tests

### Run All Tests
```bash
# Make sure venv is activated
source venv/bin/activate

# Run all tests
python tests/run_tests.py

# Run with verbose output
python tests/run_tests.py -v
```

### Run Specific Test Module
```bash
# Run only agent tests
python tests/run_tests.py test_agent

# Run only projectile tests
python tests/run_tests.py test_projectile

# Run with unittest directly
python -m unittest tests.test_agent
```

### Run Individual Test Class
```bash
# Run specific test class
python -m unittest tests.test_agent.TestAgentInitialization

# Run specific test method
python -m unittest tests.test_agent.TestAgentInitialization.test_agent_creation
```

## Test Coverage

### Agent Tests (`test_agent.py`)
- ✓ Agent initialization and attributes
- ✓ Health and damage mechanics
- ✓ Death conditions
- ✓ Communication features (limited vs. normal)
- ✓ Distance calculations
- ✓ Role assignments (Attacker, Defender, Carrier, Chaser)

### Projectile Tests (`test_projectile.py`)
- ✓ Projectile initialization
- ✓ Custom damage and owner assignment
- ✓ Velocity calculation from angle
- ✓ Movement and trajectory
- ✓ Lifetime and expiration
- ✓ Collision with agents (friendly fire prevention)
- ✓ Collision damage
- ✓ Boundary checking

### Communication Tests (`test_communication.py`)
- ✓ Message creation and attributes
- ✓ MessageBus publish/collect
- ✓ Team-specific message filtering
- ✓ Message expiration and cleanup
- ✓ Agent resolution by ID
- ✓ Limited communication range
- ✓ Distance-based message filtering

### GameMap Tests (`test_game_map.py`)
- ✓ Wall creation and destruction
- ✓ Border walls (indestructible)
- ✓ Wall damage mechanics
- ✓ Map initialization for different modes
- ✓ Spawn position generation
- ✓ Pathfinding utilities (walkable tiles, neighbors)
- ✓ Mode-specific features (KOTH zones, CTF flags)

### Survival Mode Tests (`test_survival_mode.py`)
- ✓ Mode initialization
- ✓ Victory conditions (team elimination)
- ✓ Time limit mechanics
- ✓ Timer functionality
- ✓ End game conditions
- ✓ Winner determination
- ✓ Multiple team configurations

### Statistics Tests (`test_statistics.py`)
- ✓ Tracker initialization and reset
- ✓ Agent statistics (spawns, deaths, damage)
- ✓ Team statistics aggregation
- ✓ Shot tracking (fired, hit)
- ✓ Kill/death/assist tracking
- ✓ KOTH-specific stats (zone time, damage)
- ✓ CTF-specific stats (captures, deliveries)
- ✓ Accuracy and KDA calculations

## Writing New Tests

### Test Template
```python
import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from your_module import YourClass

class TestYourClass(unittest.TestCase):
    """Test YourClass functionality"""
    
    def setUp(self):
        """Set up test fixtures - runs before each test"""
        self.obj = YourClass()
    
    def tearDown(self):
        """Clean up after test - runs after each test"""
        pass
    
    def test_something(self):
        """Test description"""
        # Arrange
        expected = "value"
        
        # Act
        result = self.obj.method()
        
        # Assert
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
```

### Common Assertions
```python
self.assertEqual(a, b)              # a == b
self.assertNotEqual(a, b)           # a != b
self.assertTrue(x)                  # bool(x) is True
self.assertFalse(x)                 # bool(x) is False
self.assertIs(a, b)                 # a is b
self.assertIsNone(x)                # x is None
self.assertIn(a, b)                 # a in b
self.assertIsInstance(a, b)         # isinstance(a, b)
self.assertAlmostEqual(a, b)        # round(a-b, 7) == 0
self.assertGreater(a, b)            # a > b
self.assertLess(a, b)               # a < b
self.assertRaises(SomeException)    # Checks if exception raised
```

## Best Practices

1. **One Test, One Assert**: Each test should verify one specific behavior
2. **Descriptive Names**: Use clear, descriptive test method names
3. **AAA Pattern**: Arrange, Act, Assert structure
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Tests**: Unit tests should run quickly
6. **Mock External Dependencies**: Mock pygame, file I/O, etc. when needed

## Continuous Integration

These tests are designed to be run in CI/CD pipelines:

```bash
# In your CI script
source venv/bin/activate
pip install -r requirements.txt
python tests/run_tests.py -v
```

## Future Test Coverage

Areas that could benefit from additional tests:
- [ ] KOTH mode gameplay
- [ ] CTF mode gameplay  
- [ ] PettingZoo environment
- [ ] Menu system
- [ ] Integration tests
- [ ] Performance tests
- [ ] AI behavior tests

## Troubleshooting

### Common Issues

**ImportError: No module named 'pygame'**
```bash
# Activate venv and install dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**Tests fail with "No such file or directory"**
```bash
# Run tests from project root
cd /path/to/lu-12-14-luckycharm
python tests/run_tests.py
```

**Pygame video system not initialized**
- Some tests may require pygame.init() - already handled in test files
- Tests run in headless mode (no display required)

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all existing tests still pass
3. Add tests for edge cases
4. Document test coverage in this README
