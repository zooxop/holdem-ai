from Cards import deck
from Cards import *
from tkinter import *
import random

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
#for card in deck:
#    print(card)
class Player(object):
    def __init__(self, chip):
        self.card = [-1,-1,-1]
        self.chip = chip

    def SetCards(self, a, b, c):
        self.card = [a,b,c]

    def GetCombine(self):
        self.card.sort()
        if(self.card[0] == self.card[1] == self.card[2]):
            return 3
        elif(self.card[0] == self.card[1]-1 == self.card[2]-2):
            return 2
        elif(self.card[0] == self.card[1] or self.card[1] == self.card[2]):
            return 1
        else:
            return 0

    def PrintCards(self):
        print(self.card[0], self.card[1], self.card[2])
movedMoney = 0

while(1):
    print("게임 시작")
    print("1. 시작")
    print("2. 종료")
    x = input()
    x = int(x)
    if(x == 1):
        money = int(input("시작 코인:"))
        deck.shuffle()
        p1 = Player(money)
        p2 = Player(money)
        while(1):
            if(p1.chip <= 0):
                print("Player2 won")
                break
            if (p2.chip <= 0):
                print("Player1 won")
                break

            if(len(deck)==0):
                deck = StandardDeck()
                deck.shuffle()
            print("player1:", p1.chip, "player2:", p2.chip)

            card1 = deck.deal()
            card2 = deck.deal()
            p1.chip -= 1
            p1.SetCards(card1.value, card2.value, deck.deal().value)
            p2.chip -= 1
            p2.SetCards(card1.value, card2.value, deck.deal().value)
            bet = 2 + movedMoney

            print("public:", card1.value,", ",card2.value)
            print("p1:",p1.card[2])

            print("1. Bet\n2. call\n3. fold")
            x = input()
            x = int(x)

            while(1):
                if(x == 1):
                    #금액 베팅
                    while(1):
                        money = int(input("Bet Chip:"))
                        if(p2.chip < money):
                            print("No money")
                        else:
                            p1.chip -= money
                            p2.chip -= money
                            bet += money*2
                            break
                    combine1 = int(p1.GetCombine())
                    combine2 = int(p2.GetCombine())
                    if(combine1 == combine2):
                        match = int(p1.GetCombine())
                        result1 = 0
                        result2 = 0
                        if(match == 1):
                            result1 = p1.card[1]
                            result2 = p2.card[1]
                            if(result1 == result2):
                                result1 = p1.card[2]
                                result2 = p2.card[2]
                        else:
                            result1 = p1.card[2]
                            result2 = p2.card[2]

                        if(result1 == result2):
                            print("draw")
                            movedMoney = bet
                            #Draw
                            break
                        elif(result1 > result2):
                            print("player1 won")
                            p1.chip += bet
                            movedMoney = 0
                            break
                        elif(result1 < result2):
                            print("player2 won")
                            p2.chip += bet
                            movedMoney = 0
                            break
                    elif(combine1 > combine2):
                        print("player1 won")
                        p1.chip += bet
                        movedMoney = 0
                        break
                    elif (combine1 < combine2):
                        print("player2 won")
                        p2.chip += bet
                        movedMoney = 0
                        break
                elif(x == 2):
                    #비교 후 종료
                    combine1 = int(p1.GetCombine())
                    combine2 = int(p2.GetCombine())
                    if (combine1 == combine2):
                        match = int(p1.GetCombine())
                        result1 = 0
                        result2 = 0
                        if (match == 1):
                            result1 = p1.card[1]
                            result2 = p2.card[1]
                            if (result1 == result2):
                                result1 = p1.card[2]
                                result2 = p2.card[2]
                        else:
                            result1 = p1.card[2]
                            result2 = p2.card[2]

                        if (result1 == result2):
                            print("draw")
                            movedMoney = bet
                            # Draw
                            break
                        elif (result1 > result2):
                            print("player1 won")
                            p1.chip += bet
                            movedMoney = 0
                            break
                        elif (result1 < result2):
                            print("player2 won")
                            p2.chip += bet
                            movedMoney = 0
                            break
                    elif (combine1 > combine2):
                        print("player1 won")
                        p1.chip += bet
                        movedMoney = 0
                        break
                    elif (combine1 < combine2):
                        print("player2 won")
                        p2.chip += bet
                        movedMoney = 0
                        break
                elif(x == 3):
                    combine2 = int(p2.GetCombine())
                    if(combine2 >= 2):
                        p2.chip -= 10
                        bet += 10

                    p1.chip += bet
                    break

            print("player1:")
            p1.PrintCards()
            print("player2:")
            p2.PrintCards()

    elif(x==2):
        break




