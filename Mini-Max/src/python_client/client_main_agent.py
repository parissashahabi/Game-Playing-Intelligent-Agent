import random
from base import BaseAgent, Action
from minimax import MinimaxAgent


class Agent(BaseAgent):
    def do_turn(self) -> Action:
        minimax = MinimaxAgent(self.grid_height, self.grid_width, ['W', 'R', 'Y', 'G'])
        return minimax.get_action(self.grid)


if __name__ == '__main__':
    data = Agent().play()
    print("FINISH : ", data)
