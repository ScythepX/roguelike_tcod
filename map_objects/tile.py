class Tile:
    """
    A tile on map. It may or may not be blocked, and may or may not blocked sight
    """
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight

        self.explored = False
