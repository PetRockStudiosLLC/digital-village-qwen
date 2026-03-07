"""
Village - The main village class that manages all villagers.
"""

import logging

logging.getLogger("httpx").setLevel(logging.WARNING)

from openai import OpenAI
from typing import Dict, Any, List, Optional, Callable
from .villager import DigitalVillager
from .memory import VillageMemory
from .config import DEFAULT_CHARACTERS


class Village:
    """
    Main village class that manages all digital villagers.

    The Village class provides:
    - Setup and initialization of multiple villagers
    - Shared memory system
    - Event broadcasting
    - Back-and-forth conversations
    - Streaming responses
    """

    def __init__(
        self, model: str = "qwen/qwen3.5-9b", api_host: str = "http://192.168.56.1:6842"
    ):
        """
        Initialize the village.

        Args:
            model: LM Studio model to use
            api_host: LM Studio API host URL
        """
        self.client = OpenAI(api_key="not-needed", base_url=f"{api_host}/v1")
        self.model_name = model
        self.api_host = api_host
        self.villagers: Dict[str, DigitalVillager] = {}
        self.village_memory = VillageMemory()

    def add_villager(
        self, name: str, system_prompt: str, description: str
    ) -> DigitalVillager:
        """
        Add a villager to the village.

        Args:
            name: Villager's name
            system_prompt: Personality-defining prompt
            description: Brief description

        Returns:
            The created villager instance
        """
        villager = DigitalVillager(
            client=self.client,
            model_name=self.model_name,
            name=name,
            system_prompt=system_prompt,
            description=description,
        )
        self.villagers[name] = villager
        return villager

    def setup_characters(self, characters: List[Dict]):
        """
        Setup villagers from a list of character configs.

        Args:
            characters: List of character dicts with 'name', 'system_prompt', 'description'
        """
        self.villagers.clear()
        for char in characters:
            self.add_villager(
                name=char["name"],
                system_prompt=char["system_prompt"],
                description=char.get("description", ""),
            )

    def setup_default_villagers(self, num_characters: int = 4):
        """
        Setup default villagers with predefined personalities.

        Args:
            num_characters: Number of characters to add (1-4)
        """
        self.villagers.clear()
        for char in DEFAULT_CHARACTERS[:num_characters]:
            self.add_villager(
                name=char["name"],
                system_prompt=char["system_prompt"],
                description=char["description"],
            )

    def get_character_names(self) -> List[str]:
        """Get list of all character names."""
        return list(self.villagers.keys())

    def broadcast_message(
        self,
        sender: str,
        message: str,
        stream_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, str]:
        """
        Broadcast a message to all villagers.

        Args:
            sender: Who is sending the message
            message: The message content
            stream_callback: Optional callback(villager_name, chunk) for streaming

        Returns:
            Dictionary of villager responses
        """
        responses = {}

        for villager_name, villager in self.villagers.items():
            if villager_name != sender:
                if stream_callback:
                    full_response = ""

                    def chunk_handler(chunk):
                        nonlocal full_response
                        full_response += chunk
                        stream_callback(villager_name, chunk)

                    response = villager.respond_to(
                        f"[Broadcast from {sender}]: {message}",
                        stream_callback=chunk_handler,
                    )
                else:
                    response = villager.respond_to(
                        f"[Broadcast from {sender}]: {message}"
                    )
                responses[villager_name] = response

        return responses

    def conversation(
        self, participants: List[str], messages: List[str], stream: bool = True
    ) -> Dict[str, List[str]]:
        """
        Run a back-and-forth conversation between characters.

        Args:
            participants: List of character names in order (first speaker, then responder, etc.)
            messages: List of messages, one per participant turn
            stream: Whether to stream responses

        Returns:
            Dict mapping character name to their response
        """
        responses = {}

        for i, (speaker, message) in enumerate(zip(participants, messages)):
            # Determine who the message is from
            if i == 0:
                context = f"Message from {speaker}: {message}"
            else:
                # Build context from previous responses
                context_parts = []
                for j, (prev_speaker, prev_response) in enumerate(responses.items()):
                    context_parts.append(f"{prev_speaker} said: {prev_response}")
                context = f"{message}\n\nPrevious conversation:\n" + "\n".join(
                    context_parts
                )

            villager = self.villagers[speaker]

            if stream:
                print(f"\n{speaker}: ", end="", flush=True)
                full_response = ""
                import sys

                def chunk_handler(chunk):
                    nonlocal full_response
                    full_response += chunk
                    try:
                        print(chunk, end="", flush=True)
                    except (UnicodeEncodeError, AttributeError):
                        sys.stdout.buffer.write(chunk.encode("utf-8"))
                        sys.stdout.buffer.flush()

                response = villager.respond_to(context, stream_callback=chunk_handler)
                print()  # New line after response
            else:
                response = villager.respond_to(context)

            responses[speaker] = response

        return responses

    def continuous_conversation(
        self,
        participants: List[str],
        starter_message: str,
        num_turns: int = 5,
        stream: bool = True,
    ) -> Dict[str, List[str]]:
        """
        Run a continuous looped conversation between characters.

        Args:
            participants: List of character names who will take turns
            starter_message: The first message to start the conversation
            num_turns: How many additional responses to generate (total = 1 + num_turns)
            stream: Whether to stream responses

        Returns:
            Dict mapping character name to their response
        """
        responses = {}

        # First message from first participant
        speaker = participants[0]
        context = f"Message from {speaker}: {starter_message}"
        villager = self.villagers[speaker]

        if stream:
            print(f"\n{speaker}: ", end="", flush=True)
            import sys

            full_response = ""

            def chunk_handler(chunk):
                nonlocal full_response
                full_response += chunk
                try:
                    print(chunk, end="", flush=True)
                except (UnicodeEncodeError, AttributeError):
                    sys.stdout.buffer.write(chunk.encode("utf-8"))
                    sys.stdout.buffer.flush()

            response = villager.respond_to(context, stream_callback=chunk_handler)
            print()
        else:
            response = villager.respond_to(context)

        responses[speaker] = response

        # Loop for remaining turns
        turn = 0
        while turn < num_turns:
            # Next participant in the list (cycles through)
            next_idx = (turn + 1) % len(participants)
            speaker = participants[next_idx]

            # Build context from ALL previous responses
            context_parts = []
            for prev_speaker, prev_response in responses.items():
                context_parts.append(f"{prev_speaker} said: {prev_response}")

            # Ask the character to respond naturally
            context = (
                f"Continue the conversation naturally. Respond to what was just said.\n\nConversation so far:\n"
                + "\n".join(context_parts)
            )

            villager = self.villagers[speaker]

            if stream:
                print(f"\n{speaker}: ", end="", flush=True)
                full_response = ""

                def chunk_handler(chunk):
                    nonlocal full_response
                    full_response += chunk
                    try:
                        print(chunk, end="", flush=True)
                    except (UnicodeEncodeError, AttributeError):
                        sys.stdout.buffer.write(chunk.encode("utf-8"))
                        sys.stdout.buffer.flush()

                response = villager.respond_to(context, stream_callback=chunk_handler)
                print()
            else:
                response = villager.respond_to(context)

            responses[speaker] = response
            turn += 1

        return responses

    def direct_message(
        self, sender: str, receiver: str, message: str, stream: bool = True
    ) -> str:
        """
        Send a direct message from one character to another.

        Args:
            sender: Who is sending the message
            receiver: Who receives the message
            message: The message content
            stream: Whether to stream the response

        Returns:
            The receiver's response
        """
        villager = self.villagers[receiver]
        full_message = f"[Direct message from {sender}]: {message}"

        if stream:
            print(f"\n{receiver}: ", end="", flush=True)

            def chunk_handler(chunk):
                print(chunk, end="", flush=True)

            response = villager.respond_to(full_message, stream_callback=chunk_handler)
            print()
        else:
            response = villager.respond_to(full_message)

        return response

    def share_with_village(self, villager: str, key: str, value: Any):
        """
        Share information with the entire village.

        Args:
            villager: Who is sharing
            key: Memory key
            value: Value to share
        """
        self.village_memory.write(key, value, villager)

    def read_from_village(self, villager: str, key: str, default: Any = None) -> Any:
        """
        Read shared information from village memory.

        Args:
            villager: Who is reading
            key: Memory key
            default: Default if not found

        Returns:
            The value or default
        """
        return self.village_memory.read(key, default)
