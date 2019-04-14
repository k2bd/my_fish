from enum import Enum
import random

class WarioBot:
    """
        Dumb meme bot that makes moves based on what maximizes potential target value out of the moves that maximize target value
    """
    def __init__(self, pnum, greed=0.7):
        self.pnum = pnum
        self.greed = greed

    def get_move(self, currentState):
        currentState.PROTAGONIST = self.pnum

        best_move_score = 0
        best_actions = set()

        if random.random() < self.greed:
            print("GREED")
            for action in currentState.getPossibleActions():
                tgt_value = currentState.board[action[1]].value

                if tgt_value > best_move_score:
                    best_actions = set([action])
                    best_move_score = tgt_value
                elif tgt_value == best_move_score:
                    best_actions.add(action)
        else:
            best_actions = set(currentState.getPossibleActions())
            
        best_potential_pts = 0
        best_action = None

        for action in best_actions:
            state = currentState.takeAction(action)

            potential_pts = sum(state.board[a[1]].value for a in \
                                state.getPossibleActions(objects_to_consider=state.players[self.pnum].pieces))

            if potential_pts > best_potential_pts:
                best_action = action
                best_potential_pts = potential_pts

        if best_action is None:
            return random.choice(currentState.getPossibleActions())
        return best_action