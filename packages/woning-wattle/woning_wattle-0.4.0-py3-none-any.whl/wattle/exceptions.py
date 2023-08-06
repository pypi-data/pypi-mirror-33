class WattleError(Exception):
    pass


class MissingFieldError(WattleError):
    def __init__(self):
        self.layers = []

    def add_layer(self, layer_name):
        self.layers.append(layer_name)

    def __str__(self):
        return "Missing value in {}".format('.'.join(reversed(self.layers)))


class InvalidValueError(WattleError):
    pass
