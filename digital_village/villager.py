"""
DigitalVillager - Represents a single AI agent with personality and memory.
"""

from openai import OpenAI
from typing import Dict, List, Optional, Callable
import json
import time


class DigitalVillager:
    """
    Represents a single digital villager with personality, memory, and conversation history.

    Each villager has:
    - A unique personality defined by system prompts
    - Memory for storing facts and knowledge
    - Conversation history for context-aware responses
    """

    def __init__(
        self,
        client: OpenAI,
        model_name: str,
        name: str,
        system_prompt: str,
        description: str,
        memory: Optional[Dict] = None,
    ):
        """
        Initialize a digital villager.

        Args:
            client: OpenAI client instance (connected to LM Studio)
            model_name: LM Studio model identifier
            name: Villager's name
            system_prompt: System prompt defining personality
            description: Brief description of the villager
            memory: Initial memory dictionary (optional)
        """
        self.client = client
        self.model_name = model_name
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
        self.memory = memory or {}
        self.chat_history: List[Dict] = []
        self.conversation_context = ""
        self.last_response_time = 0

        self._messages: List[Dict] = [{"role": "system", "content": system_prompt}]

    def reset_conversation(self):
        """Reset the conversation history."""
        self._messages = [{"role": "system", "content": self.system_prompt}]
        self.conversation_context = ""

    def remember(self, fact: str):
        """Store a fact in the villager's memory."""
        self.memory[fact] = True
        print(f"[{self.name}] Remembered: {fact}")

    def forget(self, fact: str):
        """Remove a fact from memory."""
        if fact in self.memory:
            del self.memory[fact]
            print(f"[{self.name}] Forgot: {fact}")

    def get_memory_summary(self) -> str:
        """Get a summary of what the villager knows."""
        return json.dumps(self.memory, indent=2)

    def respond_to(
        self,
        message: str,
        context: Optional[str] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """
        Generate a response to a message.

        Args:
            message: The incoming message
            context: Additional context (optional)
            stream_callback: Optional callback to receive streamed chunks

        Returns:
            The AI's response
        """
        # Build the full message with context
        user_message = message
        if context:
            user_message = f"{context}\n\n{message}"

        # Add user message to conversation
        self._messages.append({"role": "user", "content": user_message})

        # Get streaming response from the model
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self._messages,
            temperature=0.8,
            max_tokens=100,  # Short responses for quick TTS
            stream=True,
        )

        full_response = ""
        try:
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        content = delta.content
                        full_response += content
                        if stream_callback:
                            stream_callback(content)
        except Exception as e:
            print(f"Stream error: {e}")

        if not full_response:
            # Fallback to non-streaming if streaming fails
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self._messages,
                temperature=0.8,
                max_tokens=100,
            )
            full_response = response.choices[0].message.content or ""
            if stream_callback:
                stream_callback(full_response)

        full_response = full_response.strip()

        # Add assistant response to conversation
        self._messages.append({"role": "assistant", "content": full_response})

        # Keep conversation history manageable
        if len(self._messages) > 20:
            # Keep system prompt and last 18 messages
            self._messages = [self._messages[0]] + self._messages[-18:]

        # Update conversation context
        self.conversation_context += f"\nUser: {message}\nAssistant: {full_response}"

        # Add to history
        self.chat_history.append(
            {"role": "user", "content": message, "response": full_response}
        )

        # Update last response time
        self.last_response_time = time.time()

        return full_response

    def get_personality(self) -> str:
        """Get formatted personality description."""
        return f"""You are {self.name}, {self.description}.

Your personality traits:
{json.dumps(self.memory, indent=2)}

Current conversation:
{self.conversation_context}"""
