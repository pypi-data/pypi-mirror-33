class TemperatureSchedule:
    """Strategy class that represents annealing schedule

    Either specifying this for annealer or not is optional.

    Attributes:
        initial_temperature (float): Annealing initial temperature
        last_temperature (float): Annealing last templerature
        scale: (float): Scaling coefficient applied on each annealing step.
        current_temperature (float): Stateful temperature that changes during annealing.

    """
    def __init__(self, scale=0.95, initial_temperature=5.0, last_temperature=0.2):
        self.initial_temperature = initial_temperature
        self.last_temperature = last_temperature
        self.scale = scale
        self.current_temperature = None

    def reset(self):
        """Resetting `current_temperature` to restart annelaing.
        :return: `None`
        """
        self.current_temperature = None

    def __iter__(self):
        """Generator for enumeration that returns updated temperature

        :return: `current_temperature` after scaling for this step.
        """
        if self.current_temperature is None:
            self.current_temperature = self.initial_temperature
        while self.current_temperature > self.last_temperature:
            yield self.current_temperature
            self.current_temperature *= self.scale
