class GameException(Exception):
    def __init__(self):
        self._message = "Game Exception"

    @property
    def message(self):
        return self._message

    def __str__(self):
        return self.message


class ExistTrap(GameException):
    def __init__(self, agent_id, tile_address):
        self.tile_address = tile_address
        self.agent_id = agent_id
        self._message = f"exist a trap in tile = {self.tile_address} , when agent {self.agent_id} wanted put "


class AgentNotHaveTrap(GameException):
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self._message = f"agent {self.agent_id} does not have trap"


class CantPutTrapInTeleport(GameException):
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self._message = f"can't put trap on teleport [agent = {self.agent_id}]"


class NotExistAvailableTeleport(GameException):
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self._message = f"agent {self.agent_id} can't use teleport because not exist available teleport "


class NotAvailableMove(GameException):
    def __init__(self, agent_id, move: str, tile_address):
        self.agent_id = agent_id
        self.move = move
        self.tile_address = tile_address
        self._message = f"can't go {self.move} in address = {self.tile_address} with agent {self.agent_id}"


class TrapConstraintFailed(GameException):
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self._message = f"trap constraint failed for agent {self.agent_id}"


class InValidAction(GameException):
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self._message = f"agent {self.agent_id} send invalid action or time out for sending it "


class TeleportOnInvalidTile(GameException):
    def __init__(self, agent_id, tile_address):
        self.tile_address = tile_address
        self.agent_id = agent_id
        self._message = f"agent {self.agent_id} can't teleport in tile {self.tile_address} "


class CantMoveInForbiddenTile(GameException):
    def __init__(self, agent_id, tile_address):
        self.tile_address = tile_address
        self.agent_id = agent_id
        self._message = f"agent {self.agent_id} can't move  in tile {self.tile_address} " \
                        f"because it is wall or forbidden tile"


class InValidMap(GameException):
    def __init__(self, why_invalid: str):
        self._message = f"Invalid map : {why_invalid}"


class InValidConfig(GameException):
    def __init__(self, why_invalid: str):
        self._message = f"Invalid Config : {why_invalid}"
