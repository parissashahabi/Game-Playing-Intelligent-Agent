import json

from logics.map import Map, Tile
from logics.agent import Agent
from logics.actions import Actions
import random
import numpy as np
from logics import Exceptions, game_rules
from datetime import datetime
from logics.utils import bcolors


class Game:
    def __init__(self, time_out: int, agents: list, game_map: Map, turn_count):
        self.time_out = time_out
        self.agents = agents
        self.game_map = game_map
        self.max_turn_count = turn_count
        self.turn_number = 0
        self.turn_logs = []
        self.current_report = ""
        self.outs_file = open("outs.txt", "w")

    @staticmethod
    def create_game(config, player_connections: list, game_map: Map):
        addresses = [(0, 0), (game_map.height - 1, game_map.width - 1), (0, game_map.width - 1),
                     (game_map.height - 1, 0)]

        if config["init_random_location"]:
            random.shuffle(addresses)

        agents = []
        for i, conn in enumerate(player_connections):
            y, x = addresses[i]
            agents.append(
                Agent(agent_id=i, tile=game_map.get_tile(y=y, x=x), init_score=config["init_score"], connection=conn))

        time_out = config["time_out"]
        turn_count = config["turn_count"]
        return Game(time_out=time_out, agents=agents, game_map=game_map, turn_count=turn_count)

    def get_show(self, for_player=None):
        # change_it maybe
        map_array = self.game_map.get_show()
        map_array = map_array.astype(dtype=np.dtype("U25"))
        for agent in self.agents:
            y, x = agent.tile.address
            map_array[y][x] = map_array[y][x] + agent.character

        return map_array

    def do_turn_init(self, agent):
        height, width = self.game_map.tiles.shape
        content = {"height": height, "width": width, "character": agent.character, "id": agent.id, "score": agent.score,
                   "max_turn_count": self.max_turn_count, "agent_count": len(self.agents),
                   "probabilities": game_rules.PROBABILITIES}
        # content = f"{height} {width} {agent.character} {agent.id} {agent.score} {self.max_turn_count} {len(self.agents)} "
        agent.connection.write_utf(msg=str(json.dumps(content)))
        confirm_data = agent.connection.read_data()
        if confirm_data is None or confirm_data.lower() != "confirm":
            raise Exception(f"agent with id={agent.id} not send confirm")

    def send_turn_info(self, agent):
        print(' '.join([' '.join([str(item) for item in player.get_gems_count().values()]) for player in self.agents]))
        map_chars = self.get_show(for_player=agent).reshape(self.game_map.height * self.game_map.width, ).tolist()
        content = f" {self.turn_number} {' '.join([str(player.score) for player in self.agents])}" \
                  f" {' '.join([' '.join([str(item) for item in player.get_gems_count().values()]) for player in self.agents])}" \
                  f" {' '.join(map_chars)}"

        agent.connection.write_utf(msg=content)

    def do_turn(self, agent: Agent):
        try:
            self.send_turn_info(agent)
            turn_action_request = agent.connection.read_data()
            action = Actions(turn_action_request)

        except Exception as e:
            print(bcolors.WARNING + f"not valid action " + bcolors.reset)
            action = Actions.NOOP
        self.do_action(action=action, agent=agent)
        agent.add_action_history(action=action)

    def add_gem(self, agent: Agent, gem):
        # todo add gem constraints
        agent.add_gem(gem)
        agent.tile.tile_type = Tile.TileType.EMPTY

    @staticmethod
    def add_key(agent: Agent, key):
        # todo  constraint for add key
        agent.add_key(key=key)
        agent.tile.tile_type = Tile.TileType.EMPTY

    def go_target(self, agent, target: Tile):

        for other_agent in self.agents:
            if other_agent == agent:
                continue
            if other_agent.tile == target:
                if agent.score >= other_agent.score:
                    other_agent.hit_hurts.append(agent)
                else:
                    agent.hit_hurts.append(other_agent)
                return

        if target.is_wall():
            raise Exceptions.CantMoveInForbiddenTile(agent_id=agent.id, tile_address=target.address)

        target_door_type = target.get_door()
        if target_door_type is not None:
            if target_door_type == Tile.TileType.DOOR1 and not agent.has_key(Tile.TileType.KEY1):
                raise Exceptions.CantMoveInForbiddenTile(agent_id=agent.id, tile_address=target.address)
            if target_door_type == Tile.TileType.DOOR2 and not agent.has_key(Tile.TileType.KEY2):
                raise Exceptions.CantMoveInForbiddenTile(agent_id=agent.id, tile_address=target.address)
            if target_door_type == Tile.TileType.DOOR3 and not agent.has_key(Tile.TileType.KEY3):
                raise Exceptions.CantMoveInForbiddenTile(agent_id=agent.id, tile_address=target.address)

        agent.tile = target
        gem = target.get_gem()

        if gem is not None:
            self.add_gem(agent=agent, gem=gem)

        key = target.get_key()
        if key is not None:
            self.add_key(agent=agent, key=key)

        if target.is_barbed():
            agent.add_barbed_history(tile=target)
        return

    def get_move_target(self, agent: Agent, action_type: Actions):
        current_y, current_X = agent.tile.address
        if action_type == Actions.RIGHT:
            X, Y = current_X + 1, current_y

        if action_type == Actions.LEFT:
            X, Y = current_X - 1, current_y

        if action_type == Actions.DOWN:
            X, Y = current_X, current_y + 1

        if action_type == Actions.UP:
            X, Y = current_X, current_y - 1

        if action_type == Actions.UP_LEFT:
            X, Y = current_X - 1, current_y - 1

        if action_type == Actions.UP_RIGHT:
            X, Y = current_X + 1, current_y - 1

        if action_type == Actions.DOWN_LEFT:
            X, Y = current_X - 1, current_y + 1

        if action_type == Actions.DOWN_RIGHT:
            X, Y = current_X + 1, current_y + 1

        target = self.game_map.get_tile(y=Y, x=X)
        if target is None:
            raise Exceptions.NotAvailableMove(agent_id=agent.id, move=str(action_type.value),
                                              tile_address=agent.tile.address)
        return target

    def get_probabilities(self, tile, action_type: Actions):
        tile_state = "normal"
        if tile.tile_type in [Tile.TileType.EMPTY, Tile.TileType.DOOR1, Tile.TileType.DOOR2, Tile.TileType.DOOR3]:
            tile_state = "normal"
        elif tile.tile_type == Tile.TileType.BARBED:
            tile_state = "barbed"
        elif tile.tile_type in [Tile.TileType.KEY1, Tile.TileType.KEY2, Tile.TileType.KEY3,
                                Tile.TileType.GEM1, Tile.TileType.GEM2, Tile.TileType.GEM3, Tile.TileType.GEM4]:
            tile_state = "slider"

        elif tile.tile_type == Tile.TileType.TELEPORT:
            tile_state = "teleport"

        return game_rules.PROBABILITIES[tile_state][action_type.value]

    def get_probability_move(self, tile: Tile, action_type: Actions):
        probabilities = self.get_probabilities(tile, action_type)
        rand_number = random.random()
        for action_state, p in probabilities.items():
            if rand_number <= p:
                return Actions(action_state)
            rand_number -= p

        return Actions.NOOP

    def do_move_action(self, agent: Agent, action_type: Actions):
        target = self.get_move_target(agent=agent,
                                      action_type=action_type)
        self.go_target(agent=agent, target=target)

    def do_teleport(self, agent: Agent):
        teleports = self.game_map.get_teleports().copy()
        if not agent.tile.tile_type == Tile.TileType.TELEPORT:
            raise Exceptions.TeleportOnInvalidTile(agent_id=agent.id, tile_address=agent.tile.address)
        teleports.remove(agent.tile)

        if len(teleports) > 0:
            target = random.choice(teleports)
            self.go_target(agent=agent, target=target)
        else:
            raise Exceptions.NotExistAvailableTeleport(agent_id=agent.id)

    def do_action(self, action, agent):
        try:
            if action not in Actions.accepted_action():
                raise Exceptions.InValidAction(agent_id=agent.id)
            print(f"posted action={action}")
            action = self.get_probability_move(tile=agent.tile, action_type=action)
            print(f"selected action= {action}")
            if action in [Actions.UP, Actions.UP_LEFT, Actions.UP_RIGHT, Actions.DOWN, Actions.DOWN_LEFT,
                          Actions.DOWN_RIGHT, Actions.RIGHT, Actions.LEFT]:
                self.do_move_action(agent=agent, action_type=action)
            # #
            elif action == Actions.TELEPORT:
                self.do_teleport(agent=agent)

            elif action == Actions.NOOP:
                pass

            else:
                raise Exceptions.InValidAction(agent_id=agent.id)

            self.current_report = f"accepted action : {action.value}"
        except Exception as e:
            self.current_report = f"{e}"
        finally:
            for player in self.agents:
                if player == agent:
                    continue

    def turn_log(self, agent_id, finish=False, winner_id=None, report=""):
        # change_it
        self.turn_logs.append(

            {
                "turn": self.turn_number,
                "agent": agent_id,
                "agents_info": [player.get_information() for player in self.agents],
                "finish": finish,
                "winner_id": winner_id,
                "map": self.get_show().tolist(),
                "report": report
            }

        )

    def log_map(self):
        # change_it
        lines = [f"TURN {self.turn_number} \n"]
        for row in self.get_show().tolist():
            row_str = ""
            for item in row:
                row_str += str(item).ljust(4)
            lines.append(row_str + "\n")
        lines.append("-" * 10 + "\n")
        self.outs_file.writelines(lines)

    def is_game_finish_early(self):
        return len(self.agents) < 2 and not self.game_map.has_any_gems()

    def get_winner(self):
        # TODO for two players
        agents = sorted(self.agents, key=lambda agent: -agent.score)

        if len(agents) == 1:
            return None
        else:
            agent1, agent2 = agents[0], agents[1]
            if agent1.score < agent2.score:
                return [agent2]
            if agent2.score < agent1.score:
                return [agent1]
            else:
                return [agent1, agent2]

    def run(self, first_round=True, last_round=True):
        # change_it
        if first_round:
            for agent in self.agents:
                self.do_turn_init(agent=agent)
                agent.connection.set_time_out(self.time_out)

        report = ""
        for turn_number in range(1, self.max_turn_count + 1):
            self.turn_number = turn_number
            print("_" * 20)
            print(f"turn : {turn_number} \n ")
            if turn_number == 1:
                self.turn_log(agent_id=None, finish=False, winner_id=None,
                              report=f"")

            for agent in self.agents:
                self.log_map()
                agent.turn_age = turn_number
                self.do_turn(agent=agent)

                gem1_count, gem2_count, gem3_count, gem4_count = agent.get_gems_count().values()
                report = f"agent {agent.id} => score:{agent.score} gem1:{gem1_count} gem2:{gem2_count} gem3:{gem3_count} gem4:{gem4_count} report: {self.current_report}"
                print(report)

                self.turn_log(agent_id=agent.id, finish=False, winner_id=None,
                              report=f"agent {agent.id} :{self.current_report}")

            if self.is_game_finish_early():
                break

        winners = self.get_winner()

        if winners is None:
            winner = None
            for agent in self.agents:
                try:
                    if last_round:
                        agent.connection.write_utf(msg=f"finish!")
                    self.turn_log(agent_id=None, finish=True, winner_id=None,
                                  report=f"finish!")
                except:
                    pass

        elif len(winners) == 1:
            winner = winners[0]
            for agent in self.agents:
                try:
                    if last_round:
                        agent.connection.write_utf(msg=f"finish! winner = agent {winner.id}")
                    self.turn_log(agent_id=None, finish=True, winner_id=winner.id,
                                  report=f"finish! winner = agent {winner.id}")
                except:
                    pass
        else:
            winner = None
            for agent in self.agents:
                try:
                    if last_round:
                        agent.connection.write_utf(msg=f"finish! Draw the game")
                except:
                    pass

            self.turn_log(agent_id=None, finish=True, winner_id=None, report=f"finish! The game ended in a draw")

        now_time = datetime.now()
        with open(
                f"game_logs/{now_time.month}_{now_time.day}_{now_time.hour}_{now_time.minute}_{now_time.second}_{now_time.microsecond}.json",
                "w") as file:
            json.dump(self.turn_logs, file)
