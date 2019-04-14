import random
class RandomBot:
    def __init__(self):
        pass
    def get_move(self, currentState):
        return random.choice(currentState.getPossibleActions())