class BaseSimulatedAnnealingStrategy:
    """Strategy class that represents annealing algorithm

    Either specifying this for annealer or not is optional.

    """
    def update(self, annealer, T):
        """

        :param annealer: Annealer that holds current state (i.e. spins).
            This is expected to be a subclass of `BaseAnnealer`.
        :param T: Current temperature on which this algorithm updates spins.
        :return: `None`.
        """
        raise NotImplementedError()
