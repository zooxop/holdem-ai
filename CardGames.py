import Cards
from GameUI import *
from enum import Enum

'''
Indian Holdem
Rule:   플레이어는 2명으로 40장의 카드를 덱으로 구성
        한 라운드에 플레이어는 각 1장씩 패를 가지고 2장의 공유 패를 가짐
        플레이어는 자신의 패는 볼 수 없고 상대 패와 공유 패만 볼 수 있다
        자신의 턴에 상대 패을 보고 bet, call, fold 할 수 있다
        bet -> 라운드 진행
        call -> 라운드 종료, 패 확인 후 승패 결정
        fold -> 라운드 종료, 패배
        라운드 종료시 트리플>스트레이트>더블>탑 순서로 승자 결정
        라운드 시작시 칩이 없으면 패배
'''
'''
class CardGame:
    def __init__(self, r):
        s = Frame(r, height=720, width=1280, bg="white", cursor="hand2")
        s.pack()

        pt_card_back   = PhotoImage(file="asset//Card_Back.png")
        pt_table       = PhotoImage(file="asset//Board.png")
        pt_chips       = PhotoImage(file="asset//Chip.png")

        table = Label(pt_table)
        table.place(x=0, y=0)

window = Tk()
window.title("Indian Holdem")
window.geometry("1280x720")

wall       = PhotoImage(file="asset//Board.png")
wall_label = Label(image= wall)
wall_label.place(x = -3, y = -3)

window.mainloop()
'''


def DrawLine():
    print("=======================================")


class Combination(Enum):
    TOP = 0
    DOUBLE = 1
    STRAIGHT = 2
    TRIPLE = 3


class Player:
    def __init__(self, chip):
        self.chip: int = chip
        self.hand = [-1, -1, -1]
        self.combine = Combination.TOP
        self.top = -1

    def SetCombineTop(self):
        hand_temp = self.hand
        hand_temp.sort()
        if hand_temp[0] == hand_temp[1] == hand_temp[2]:
            self.combine = Combination.TRIPLE
            self.top = self.hand[2]
        elif hand_temp[0] == (hand_temp[1] - 1) == (hand_temp[2] - 9) or hand_temp[0] == (hand_temp[1] - 1) == (hand_temp[2] - 2):
            self.combine = Combination.STRAIGHT
            if hand_temp[1] == 1:
                self.top = self.hand[1]
            else:
                self.top = self.hand[2]
        elif hand_temp[0] == hand_temp[1] or hand_temp[1] == hand_temp[2]:
            self.combine = Combination.DOUBLE
            self.top = hand_temp[1]
        else:
            self.combine = Combination.TOP
            self.top = hand_temp[2]

    def BetChip(self, value: int) -> int:
        if value > self.chip:
            return 0
        self.chip -= value
        return value

    def PrintCards(self):
        print("public:{}, {}".format(Cards.Card(self.hand[0]), Cards.Card(self.hand[1])))
        print("opponent:{}".format(Cards.Card(self.hand[2])))


class GameLogic:
    def __init__(self):
        self.deck = Cards.StandardDeck()
        self.deck.shuffle()
        self.betMoney = 0
        self.carriedMoney = 0

    def DealCard(self, p1: Player, p2: Player):
        if len(self.deck) == 0:
            self.ReloadDeck()
        card1: Cards.Card = self.deck.deal()
        card2: Cards.Card = self.deck.deal()
        p1.hand = [card1.value, card2.value, self.deck.deal().value]
        p2.hand = [card1.value, card2.value, self.deck.deal().value]

    def PrintStatus(self, p1: Player):
        print("-----------------------------------")
        print("Opponent:", Cards.Card(p1.hand[2]))
        print("public:", Cards.Card(p1.hand[0]), Cards.Card(p1.hand[1]))
        print("-----------------------------------")

    def GetMatch(self, p1: Player, p2: Player):
        p1.SetCombineTop()
        p2.SetCombineTop()
        if p1.combine == p2.combine:
            if p1.top == p2.top:
                return 0
            elif p1.top > p2.top:
                return -1
            elif p1.top < p2.top:
                return 1
        elif p1.combine.value > p2.combine.value:
            return -1
        elif p1.combine.value < p2.combine.value:
            return 1

    def RoundResult(self, p1, p2, money):
        result = self.GetMatch(p1, p2)
        if result == -1:
            print("Player 1 won!")
            p1.chip += money
            self.carriedMoney = 0
            return 0
        elif result == 0:
            print("Draw")
            return money
        elif result == 1:
            print("Player 2 won!")
            p2.chip += money
            self.carriedMoney = 0
            return 0

    def ReloadDeck(self):
        self.deck = Cards.StandardDeck()
        self.deck.shuffle()


# ------------------------------------------------------
def main():
    while True:
        DrawLine()
        print("게임 시작")
        print("1. 시작")
        print("2. 종료")
        x = int(input("선택:"))

        if x == 1:
            DrawLine()
            money = int(input("시작 코인:"))
            game = GameLogic()
            # p1: 상대 p2: 나(플레이어)
            p1 = Player(money)
            p2 = Player(money)
            while True:
                DrawLine()
                if game.carriedMoney == 0:
                    if p1.chip <= 0:
                        print("Player2 won")
                        break
                    if p2.chip <= 0:
                        print("Player1 won")
                        break
                    game.betMoney = p1.BetChip(1) + p2.BetChip(1)
                else:
                    game.betMoney = game.carriedMoney
                    game.carriedMoney = 0

                # 보유 Chip 출력
                print("player1:", p1.chip, "player2:", p2.chip)
                print("Base:", game.betMoney)

                # 카드 분배
                game.DealCard(p1, p2)

                # 상대 카드 출력
                p1.PrintCards()

                print("1. Bet\n2. call\n3. fold")
                x = int(input("선택:"))

                while True:
                    if x == 1:
                        # 금액 베팅
                        while True:
                            # 베팅 금액 입력
                            money = int(input("Bet Chip:"))
                            # 내 칩이나 상대 칩이 모자르면 다시 입력
                            if p1.chip < money or p2.chip < money:
                                _max: int = 0
                                if p1.chip < p2.chip:
                                    _max = p1.chip
                                else:
                                    _max = p2.chip
                                print("No chips, try again(max value:{})".format(_max))
                            else:
                                game.betMoney += p1.BetChip(money) + p2.BetChip(money)
                                break
                        # 원래는 GetMatch도 하지말고 상대가 call 하면 GetMatch,break 해야 하는데 컴퓨터랑 하니깐 일단 한번만 돌려요
                        print("Player 1:")
                        p1.PrintCards()
                        print("Player 2:")
                        p2.PrintCards()
                        game.RoundResult(p1, p2, game.betMoney)
                        break
                    elif x == 2:
                        # 비교 후 종료
                        print("Player 1:")
                        p1.PrintCards()
                        print("Player 2:")
                        p2.PrintCards()
                        game.RoundResult(p1, p2, game.betMoney)
                        break
                    elif x == 3:
                        p2.SetCombineTop()
                        if p2.combine.value >= Combination.STRAIGHT.value:
                            p2.chip -= 10
                            game.betMoney += 10

                        p1.chip += game.betMoney
                        game.betMoney = 0
                        break
        elif x == 2:
            break


if __name__ == "__main__":
    # evManager = EventManager()
    #
    # keybd = KeyboardController(evManager)
    # spinner = CPUSpinnerController(evManager)
    # pygameView = PygameView(evManager)
    #
    # spinner.Run()

    main()
