class LoadMap():

    def __init__(self, map_file):
        pass


class Navigation():

    def __init__(self, current_loc):
        pass

    def move(self, direction):
        pass


class Boundary():

    def __init__(self, coordinate):
        pass

    def find_boundary(self):
        pass


class Item():

    def __init__(self, coordinate):
        pass

    def find_item(self):
        pass


class Lighting():

    def __init__(self, torch):
        pass

    def torch_check(self):
        pass


class Battle():

    def __init__(self, health, armor, attack):
        pass


class Scene():

    def enter(self):
        pass


class Entrance(Scene):

    def enter(self):
        pass


class Death(Scene):

    def enter(self):
        pass


class Minotaur(Scene):

    def enter(scene):
        pass


class Manticore(Scene):

    def enter(self):
        pass


class WayOut(Scene):

    def enter(self):
        pass


class HiddenDoor(Scene):

    def enter(self):
        pass


class Progress():

    def bar(self, secs, prefix):
        pass
