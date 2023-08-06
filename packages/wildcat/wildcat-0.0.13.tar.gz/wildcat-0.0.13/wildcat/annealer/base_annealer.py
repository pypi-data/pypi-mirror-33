"""Annealer class base implementation
"""
class BaseAnnealer:
    """Annealer class base implementation

    """
    def anneal(self, hamiltonian):
        """Method to do annealing once.

               Args:
                   hamiltonian: numpy ndarray of 2 dim, that represents J/h
               Returns:
                   numpy ndarray of 1 dim, that represents final spins

        """
        raise NotImplementedError()
