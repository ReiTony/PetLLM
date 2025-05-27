from enum import Enum
from typing import Dict


class Mood(str, Enum):
    HAPPY = "happy"
    HUNGRY = "hungry"
    TIRED = "tired"
    STRESSED = "stressed"
    DIRTY = "dirty"
    NEUTRAL = "neutral"


class BehaviorEngine:
    def __init__(self, status: Dict[str, int]):
        """
        status = {
            "energy": 85,
            "hunger": 20,
            "stress": 40,
            "cleanliness": 75
        }
        """
        self.status = status

    def get_primary_mood(self) -> Mood:
        """Determine the dominant mood based on thresholds."""
        if self.status.get("hunger", 0) < 70:
            return Mood.HUNGRY
        if self.status.get("energy", 100) < 30:
            return Mood.TIRED
        if self.status.get("stress", 0) > 60:
            return Mood.STRESSED
        if self.status.get("cleanliness", 100) < 40:
            return Mood.DIRTY
        if (
            self.status.get("hunger", 0) < 30 and
            self.status.get("energy", 100) > 60 and
            self.status.get("stress", 0) < 40 and
            self.status.get("cleanliness", 100) > 60
        ):
            return Mood.HAPPY
        return Mood.NEUTRAL

    def get_prompt_modifier(self) -> str:
        """Injects behavioral tone into LLM prompt."""
        mood = self.get_primary_mood()
        match mood:
            case Mood.HUNGRY:
                return "The pet is whining and looking for food."
            case Mood.TIRED:
                return "The pet is yawning and sluggish."
            case Mood.STRESSED:
                return "The pet is visibly anxious and needs comfort."
            case Mood.DIRTY:
                return "The pet feels grimy and irritated."
            case Mood.HAPPY:
                return "The pet is cheerful, energetic, and affectionate!"
            case _:
                return "The pet is calm and passive right now."

    def get_behavior_tag(self) -> str:
        """Optional tags that can guide behavior logic."""
        mood = self.get_primary_mood()
        return {
            Mood.HUNGRY: "avoid_physical_activities",
            Mood.TIRED: "sleep_preferred",
            Mood.STRESSED: "needs_care",
            Mood.DIRTY: "refuses_cuddles",
            Mood.HAPPY: "play_ready",
            Mood.NEUTRAL: "passive"
        }[mood]

    def get_summary(self) -> Dict[str, str]:
        """Returns both mood and prompt modifier for injection."""
        return {
            "mood": self.get_primary_mood(),
            "modifier": self.get_prompt_modifier(),
            "behavior_tag": self.get_behavior_tag()
        }
