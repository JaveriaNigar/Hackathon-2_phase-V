"""
Simple asyncio queue implementation as a Kafka alternative
This serves as a demonstration of pub/sub functionality without requiring Kafka
"""

import asyncio
import json
from typing import Dict, List, Callable, Any
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleEventQueue:
    """
    A simple asyncio-based event queue that mimics basic Kafka functionality
    """
    
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.running = True
        
    def create_topic(self, topic: str):
        """Create a topic(queue) if it doesn't exist"""
        if topic not in self.queues:
            self.queues[topic] = asyncio.Queue()
            self.subscribers[topic] = []
            logger.info(f"Created topic: {topic}")
    
    async def publish(self, topic: str, message: Any):
        """Publish a message to a topic"""
        self.create_topic(topic)
        
        # Prepare message with timestamp
        enriched_message = {
            "data": message,
            "timestamp": datetime.now().isoformat(),
            "topic": topic
        }
        
        await self.queues[topic].put(enriched_message)
        logger.info(f"Published message to topic '{topic}': {message}")
        
        # Notify subscribers if any
        for callback in self.subscribers[topic]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(enriched_message)
                else:
                    callback(enriched_message)
            except Exception as e:
                logger.error(f"Error in subscriber callback for topic {topic}: {e}")
    
    def subscribe(self, topic: str, callback: Callable[[Any], None]):
        """Subscribe to a topic with a callback function"""
        self.create_topic(topic)
        self.subscribers[topic].append(callback)
        logger.info(f"Added subscriber to topic: {topic}")
    
    async def consume(self, topic: str):
        """Consume a single message from a topic (blocking)"""
        self.create_topic(topic)
        message = await self.queues[topic].get()
        logger.info(f"Consumed message from topic '{topic}': {message}")
        return message
    
    async def consume_loop(self, topic: str, callback: Callable[[Any], None]):
        """Continuously consume messages from a topic"""
        self.create_topic(topic)
        
        while self.running:
            try:
                message = await self.queues[topic].get()
                logger.info(f"Consumed message from topic '{topic}': {message}")
                
                # Call the callback with the message
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                logger.error(f"Error consuming message from topic {topic}: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying


# Global instance
event_queue = SimpleEventQueue()


# Example usage functions
async def example_usage():
    """Example of how to use the event queue"""
    
    # Define a consumer callback
    def notification_handler(message):
        print(f"Notification received: {message['data']}")
    
    # Subscribe to a notifications topic
    event_queue.subscribe("notifications", notification_handler)
    
    # Publish some messages
    await event_queue.publish("notifications", {"type": "task_created", "task_id": 123})
    await event_queue.publish("notifications", {"type": "task_updated", "task_id": 123, "status": "completed"})
    
    # Consume one message directly
    msg = await event_queue.consume("notifications")
    print(f"Directly consumed: {msg}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage())