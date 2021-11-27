
class State:
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    TESTING = "testing"
    COMPLETE = "complete"


class StateMachine:
    """
    State machine for Toaster
    """
    def __init__(self, config_path: str):
        super()
