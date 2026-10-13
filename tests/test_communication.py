"""
Unit tests for Communication system (Message and MessageBus)
"""
import unittest
import sys
import os
import pygame

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Initialize pygame for time functions
pygame.init()

from communication import Message, MessageBus
from agent import Agent


class TestMessage(unittest.TestCase):
    """Test Message class"""
    
    def test_message_creation(self):
        """Test that a message is created with correct attributes"""
        timestamp = pygame.time.get_ticks()
        payload = {"enemy_id": "agent_1_0", "x": 100, "y": 200}
        
        message = Message(
            sender_id="agent_0_0",
            team_id=0,
            msg_type="ENEMY_SPOTTED",
            payload=payload,
            timestamp=timestamp
        )
        
        self.assertEqual(message.sender_id, "agent_0_0")
        self.assertEqual(message.team_id, 0)
        self.assertEqual(message.type, "ENEMY_SPOTTED")
        self.assertEqual(message.payload, payload)
        self.assertEqual(message.timestamp, timestamp)
    
    def test_message_with_position(self):
        """Test message creation with sender position"""
        message = Message(
            sender_id="agent_0_0",
            team_id=0,
            msg_type="DISTRESS_CALL",
            payload={},
            timestamp=0,
            sender_x=100,
            sender_y=200
        )
        
        self.assertEqual(message.sender_x, 100)
        self.assertEqual(message.sender_y, 200)
    
    def test_limited_communication_flag(self):
        """Test limited communication flag"""
        message = Message(
            sender_id="agent_0_0",
            team_id=0,
            msg_type="ENEMY_SPOTTED",
            payload={},
            timestamp=0,
            is_limited=True
        )
        
        self.assertTrue(message.is_limited)


class TestMessageBus(unittest.TestCase):
    """Test MessageBus class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bus = MessageBus(max_age_ms=2000)
        self.current_time = pygame.time.get_ticks()
    
    def test_bus_initialization(self):
        """Test MessageBus is initialized correctly"""
        self.assertEqual(len(self.bus.messages), 0)
        self.assertEqual(self.bus.max_age_ms, 2000)
    
    def test_publish_message(self):
        """Test publishing a message to the bus"""
        message = Message(
            sender_id="agent_0_0",
            team_id=0,
            msg_type="ENEMY_SPOTTED",
            payload={},
            timestamp=self.current_time
        )
        
        self.bus.publish(message)
        
        self.assertEqual(len(self.bus.messages), 1)
        self.assertEqual(self.bus.messages[0], message)
    
    def test_collect_messages_for_team(self):
        """Test collecting messages for a specific team"""
        # Publish messages for different teams
        msg1 = Message("agent_0_0", 0, "TEST", {}, self.current_time)
        msg2 = Message("agent_1_0", 1, "TEST", {}, self.current_time)
        msg3 = Message("agent_0_1", 0, "TEST", {}, self.current_time)
        
        self.bus.publish(msg1)
        self.bus.publish(msg2)
        self.bus.publish(msg3)
        
        # Collect for team 0
        team0_messages = self.bus.collect(0, self.current_time)
        
        self.assertEqual(len(team0_messages), 2)
        self.assertIn(msg1, team0_messages)
        self.assertIn(msg3, team0_messages)
        self.assertNotIn(msg2, team0_messages)
    
    def test_collect_filters_expired_messages(self):
        """Test that expired messages are filtered out"""
        old_message = Message("agent_0_0", 0, "TEST", {}, self.current_time - 3000)
        new_message = Message("agent_0_1", 0, "TEST", {}, self.current_time)
        
        self.bus.publish(old_message)
        self.bus.publish(new_message)
        
        messages = self.bus.collect(0, self.current_time)
        
        self.assertEqual(len(messages), 1)
        self.assertIn(new_message, messages)
        self.assertNotIn(old_message, messages)
    
    def test_cleanup_removes_old_messages(self):
        """Test cleanup removes expired messages"""
        old_message = Message("agent_0_0", 0, "TEST", {}, self.current_time - 3000)
        new_message = Message("agent_0_1", 0, "TEST", {}, self.current_time)
        
        self.bus.publish(old_message)
        self.bus.publish(new_message)
        
        self.bus.cleanup(self.current_time)
        
        self.assertEqual(len(self.bus.messages), 1)
        self.assertIn(new_message, self.bus.messages)
    
    def test_set_agents(self):
        """Test setting agent index"""
        agent1 = Agent(100, 100, 0)
        agent1.agent_id = "agent_0_0"
        agent2 = Agent(200, 200, 1)
        agent2.agent_id = "agent_1_0"
        
        agent_index = {
            "agent_0_0": agent1,
            "agent_1_0": agent2
        }
        
        self.bus.set_agents(agent_index)
        
        self.assertEqual(self.bus._agent_index, agent_index)
    
    def test_resolve_agent(self):
        """Test resolving agent by ID"""
        agent = Agent(100, 100, 0)
        agent.agent_id = "agent_0_0"
        
        self.bus.set_agents({"agent_0_0": agent})
        
        resolved = self.bus.resolve_agent("agent_0_0")
        
        self.assertEqual(resolved, agent)
    
    def test_resolve_nonexistent_agent(self):
        """Test resolving non-existent agent returns None"""
        resolved = self.bus.resolve_agent("nonexistent")
        
        self.assertIsNone(resolved)


class TestLimitedCommunication(unittest.TestCase):
    """Test limited communication range feature"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bus = MessageBus(max_age_ms=2000)
        self.current_time = pygame.time.get_ticks()
    
    def test_limited_message_within_range(self):
        """Test limited message is received when within range"""
        sender = Agent(100, 100, 0)
        sender.agent_id = "agent_0_0"
        sender.has_limited_communication = True
        
        receiver = Agent(120, 120, 0)  # Close by
        receiver.agent_id = "agent_0_1"
        
        # Create limited message
        message = Message(
            sender_id="agent_0_0",
            team_id=0,
            msg_type="ENEMY_SPOTTED",
            payload={},
            timestamp=self.current_time,
            sender_x=100,
            sender_y=100,
            is_limited=True
        )
        
        self.bus.publish(message)
        
        # Receiver should get the message (within range)
        messages = self.bus.collect(0, self.current_time, receiving_agent=receiver)
        
        self.assertEqual(len(messages), 1)
    
    def test_limited_message_out_of_range(self):
        """Test limited message is not received when out of range"""
        from config import COMMUNICATION_RANGE
        
        sender = Agent(100, 100, 0)
        sender.agent_id = "agent_0_0"
        sender.has_limited_communication = True
        
        # Receiver far away
        receiver = Agent(100 + COMMUNICATION_RANGE + 50, 100, 0)
        receiver.agent_id = "agent_0_1"
        
        # Create limited message
        message = Message(
            sender_id="agent_0_0",
            team_id=0,
            msg_type="ENEMY_SPOTTED",
            payload={},
            timestamp=self.current_time,
            sender_x=100,
            sender_y=100,
            is_limited=True
        )
        
        self.bus.publish(message)
        
        # Receiver should NOT get the message (out of range)
        messages = self.bus.collect(0, self.current_time, receiving_agent=receiver)
        
        self.assertEqual(len(messages), 0)
    
    def test_non_limited_message_always_received(self):
        """Test non-limited messages are received regardless of distance"""
        receiver = Agent(1000, 1000, 0)  # Very far away
        receiver.agent_id = "agent_0_1"
        
        # Create non-limited message
        message = Message(
            sender_id="agent_0_0",
            team_id=0,
            msg_type="ENEMY_SPOTTED",
            payload={},
            timestamp=self.current_time,
            sender_x=100,
            sender_y=100,
            is_limited=False
        )
        
        self.bus.publish(message)
        
        # Receiver should get the message (not limited)
        messages = self.bus.collect(0, self.current_time, receiving_agent=receiver)
        
        self.assertEqual(len(messages), 1)


if __name__ == '__main__':
    unittest.main()
