# ------------------------------------------------------
# Events and EventManager
class Event:
    """this is a superclass for any events that might be generated by an
    object and sent to the EventManager"""

    def __init__(self):
        self.name = "Generic Event"

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__,
                            id(self))


class GameStartRequest(Event):
    def __init__(self):
        self.name = "Game Start Request"


class MouseClickEvent(Event):
    def __init__(self):
        self.name = "Mouse Button Click Event"


class ClickBetButton(Event):
    def __init__(self):
        self.name = "Bet Button Click Event"


class ClickFoldButton(Event):
    def __init__(self):
        self.name = "Fold Button Click Event"


class ClickCallButton(Event):
    def __init__(self):
        self.name = "Call Button Click Event"


class PlayerCallEvent(Event):
    def __init__(self):
        self.name = "Player Select Call"


class ClickInputBox(Event):
    def __init__(self, mouse):
        self.name = "Input Box Click Event"
        self.mouse = mouse


class ReturnKeyPress(Event):
    def __init__(self):
        self.name = "Return-key press Event"


class BetAmountKeyPress(Event):  # Betting 금액 결정 Return key
    def __init__(self, amount):
        self.name = "Press Return key for Betting chip"
        self.amount = amount


class BackSpaceEvent(Event):
    def __init__(self):
        self.name = "input Backspace key"


class InputNumbers(Event):
    def __init__(self, value):
        self.name = "input betting amount"
        self.value = value - 48


class TickEvent(Event):
    def __init__(self):
        self.name = "CPU Tick Event"


class QuitEvent(Event):
    def __init__(self):
        self.name = "Program Quit Event"


class NextTurnEvent(Event):
    def __init__(self):
        self.name = "Next Turn Event"


class PreFlopEvent(Event):
    def __init__(self, players, pot, isPlayerTurn):
        self.name = "Pre-Flop Event"
        self.players = players
        self.pot = pot
        self.isPlayerTurn = isPlayerTurn


class FlopEvent(Event):
    def __init__(self, card_list):
        self.name = "Flop Event"
        self.card_list = card_list


class ShowDownEvent(Event):
    def __init__(self, player, community_cards, card_list):
        self.name = "ShowDown"
        self.player = player
        self.community_cards = community_cards
        self.card_list = card_list


class InitializeRoundEvent(Event):
    def __init__(self):
        self.name = "Initialize Round"


class NextRoundEvent(Event):
    def __init__(self, players, pot):
        self.name = "Next Round Event"
        self.players = players
        self.pot = pot


class DealPreFlops(Event):
    def __init__(self):
        self.name = "PreFlops event only"


class AKeyEvent(Event):
    def __init__(self):
        self.name = "Input A Key Event"


class OpenPlayerCard(Event):
    def __init__(self, player):
        self.name = "Open the player's hidden card"
        self.player = player


class RefreshSprites(Event):
    def __init__(self, players, pot):
        self.name = "Refresh Sprites"
        self.players = players
        self.pot = pot


class PassTurn(Event):
    def __init__(self, isPlayerTurn):
        self.name = "Pass Turn Event"
        self.isPlayerTurn = isPlayerTurn
