class StepType:
    PREHEAT = "preheat"
    SOAK = "soak"
    RAMP = "ramp"
    REFLOW = "reflow"
    COOL = "cool"


class Step:
    def __init__(self, name: str, step_type: StepType, target_temp: float, duration: float):
        super()

        self.name = name
        self.step_type = step_type
        self.target_temp = target_temp
        self.duration = duration

        self.start_time = 0.0

    def start(self, current_time: float):
        """
        Start the step
        @param current_time: the current time for the step
        """
        self.start_time = current_time

    def is_complete(self, current_temp: float, current_time: float) -> bool:
        """
        Check if the current step is complete
        @param current_temp: the current temperature
        @param current_time: the current time
        @return: whether or not the temp has hit the target or enough time has elapsed
        """
        if self.step_type in [StepType.PREHEAT, StepType.RAMP]:
            return current_temp >= self.target_temp
        if self.step_type in [StepType.SOAK, StepType.REFLOW]:
            return current_time - self.start_time >= self.duration
        if self.step_type == StepType.COOL:
            return current_time - self.start_time >= self.duration or current_temp <= 50.0
