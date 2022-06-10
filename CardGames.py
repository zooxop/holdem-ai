import copy

import numpy as np

import Cards
from Cards import deck
from enum import Enum
from Cards import *
from tkinter import *
import random
import sklearn
import pandas as pd

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


class BetStd:
    stdMax: float = None
    stdMin: float = None

def GetCsvAvg(path) -> float:
    df = pd.read_csv(path)
    total = df['Result'].sum()
    return total / df['Result'].count()

class StandardInfo():
    def __init__(self, max, min, avg):
        self.max = max
        self.min = min
        self.avg = avg


def GetBestBetStd() -> BetStd:
    standard = BetStd()
    stds = []

    stds.append(StandardInfo(2, 1, GetCsvAvg('../Downloads/수정 파일/WinRate_2_1.csv')))
    stds.append(StandardInfo(3, 1, GetCsvAvg('../Downloads/수정 파일/WinRate_3_1.csv')))
    stds.append(StandardInfo(3, 2, GetCsvAvg('../Downloads/수정 파일/WinRate_3_2.csv')))
    stds.append(StandardInfo(4, 1, GetCsvAvg('../Downloads/수정 파일/WinRate_4_1.csv')))
    stds.append(StandardInfo(4, 2, GetCsvAvg('../Downloads/수정 파일/WinRate_4_2.csv')))
    stds.append(StandardInfo(4, 3, GetCsvAvg('../Downloads/수정 파일/WinRate_4_3.csv')))
    stds.append(StandardInfo(5, 2, GetCsvAvg('../Downloads/수정 파일/WinRate_5_2.csv')))
    stds.append(StandardInfo(5, 3, GetCsvAvg('../Downloads/수정 파일/WinRate_5_3.csv')))
    stds.append(StandardInfo(5, 4, GetCsvAvg('../Downloads/수정 파일/WinRate_5_4.csv')))
    stds.append(StandardInfo(6, 3, GetCsvAvg('../Downloads/수정 파일/WinRate_6_3.csv')))
    stds.append(StandardInfo(6, 4, GetCsvAvg('../Downloads/수정 파일/WinRate_6_4.csv')))
    stds.append(StandardInfo(6, 5, GetCsvAvg('../Downloads/수정 파일/WinRate_6_5.csv')))
    stds.append(StandardInfo(7, 6, GetCsvAvg('../Downloads/수정 파일/WinRate_7_6.csv')))
    stds.append(StandardInfo(8, 7, GetCsvAvg('../Downloads/수정 파일/WinRate_8_7.csv')))

    topStd = StandardInfo(0, 0, 0)
    for i in range(0,14):
        if topStd.avg <= stds[i].avg:
            topStd = stds[i]
    standard.stdMax = topStd.max
    standard.stdMin = topStd.min
    return standard


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
        self.betMoney = 0

    def GetCombine(self):
        hand_temp = copy.copy(self.hand)
        hand_temp.sort()
        if hand_temp[0] == hand_temp[1] == hand_temp[2]:
            self.combine = Combination.TRIPLE
            self.top = self.hand[2]
        elif hand_temp[0] == hand_temp[1] - 1 == hand_temp[2] - 9 or hand_temp[0] == hand_temp[1] - 1 == hand_temp[
            2] - 2:
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
        self.betMoney += value
        return value

    def PrintCards(self):
        print("public:{}, {}".format(Cards.Card(self.hand[0]), Cards.Card(self.hand[1])))
        print("opponent:{}".format(Cards.Card(self.hand[2])))

    def Win(self, oppoMoney):
        self.chip += self.betMoney + oppoMoney
        self.betMoney = 0

    def Defeat(self):
        self.betMoney = 0


class BetInfo:
    betType: int = None
    betValue: int = None


class HoldemMaster:
    def __init__(self):
        self.deck = Cards.StandardDeck()
        self.rateWin: float = 0.0
        self.rateDraw: float = 0.0
        self.rateLose: float = 0.0
        self.rateStraight: float = 0.0
        self.myCharacter: Player = Player(10)
        self.opponent: Player = Player(10)
        self.turn = 0
        self.limitBet: int = 0
        self.result = 0
        # self.model

    def SetOpponent(self, p: Player):
        if len(self.deck) == 0:
            self.deck = StandardDeck()
        self.opponent = copy.copy(p)
        self.myCharacter.hand = copy.copy(p.hand)
        self.myCharacter.hand[2] = -1
        for i in range(3):
            self.deck.DeleteCard(self.opponent.hand[i])

    def UpdateOpponent(self, oppo: Player):
        self.opponent.chip = oppo.chip
        self.opponent.betMoney = oppo.betMoney

    def UpdateMe(self, me: Player):
        self.myCharacter.chip = me.chip
        self.myCharacter.betMoney = me.betMoney

    def UpdatePlayers(self, me: Player, oppo: Player):
        self.opponent.chip = oppo.chip
        self.opponent.betMoney = oppo.betMoney
        self.myCharacter.chip = me.chip
        self.myCharacter.betMoney = me.betMoney

        # self.limitBet = oppo.chip * self.rateWin

    def GetMatch(self):
        self.myCharacter.GetCombine()
        self.opponent.GetCombine()
        if self.myCharacter.combine == self.opponent.combine:
            if self.myCharacter.top == self.opponent.top:
                return 0
            elif self.myCharacter.top > self.opponent.top:
                return -1
            elif self.myCharacter.top < self.opponent.top:
                return 1
        elif self.myCharacter.combine.value > self.opponent.combine.value:
            return -1
        elif self.myCharacter.combine.value < self.opponent.combine.value:
            return 1

    def GetRate(self):
        if len(self.deck) == 0:
            self.deck = StandardDeck()
        win: int = 0
        draw: int = 0
        lose: int = 0
        straight: int = 0

        for i in range(0, len(self.deck)):
            self.myCharacter.hand[2] = self.deck[i].value
            result: int = self.GetMatch()
            if self.myCharacter.combine.value >= Combination.STRAIGHT.value:
                straight += 1
            if result == -1:
                win += 1
            elif result == 0:
                draw += 1
            elif result == 1:
                lose += 1
        total = len(self.deck)

        self.rateWin = win / total
        self.rateDraw = draw / total
        self.rateLose = lose / total
        self.rateStraight = straight / total

        self.limitBet = int((self.myCharacter.betMoney + self.myCharacter.chip) * self.rateWin)
        if self.limitBet >= self.opponent.chip:
            self.limitBet = copy.copy(self.opponent.chip)

    def BetAlogorithm(self, betStd: float, callStd: float) -> BetInfo:
        myBet = BetInfo()
        if self.rateWin > betStd:
            maxBet = 0
            if self.opponent.chip >= self.myCharacter.chip:
                maxBet = self.myCharacter.chip
            else:
                maxBet = self.opponent.chip

            maxBet = int(maxBet * self.rateWin)
            if self.myCharacter.betMoney >= self.limitBet:
                myBet.betType = 2
                myBet.betValue = 0

                print("call")

                return myBet
            baseBet = self.opponent.betMoney - self.myCharacter.betMoney
            if baseBet >= self.limitBet - self.myCharacter.betMoney:
                myBet.betType = 2
                myBet.betValue = 0

                print("call")

                return myBet
            moneyBet = random.randrange(baseBet, self.limitBet - self.myCharacter.betMoney)
            if baseBet == moneyBet:
                myBet.betType = 2
                myBet.betValue = 0

                print("call")

                return myBet
            myBet.betType = 1
            myBet.betValue = moneyBet
            self.turn += 1

            print("Bet:", myBet.betValue)

            return myBet
        elif self.rateWin > callStd:
            myBet.betType = 2
            myBet.betValue = 0
            self.turn += 1

            print("call")

            return myBet
        else:
            if not self.rateWin == 0:
                if 20 <= random.randrange(0, 100):
                    myBet.betType = 2
                    myBet.betValue = 0
                    self.turn += 1

            if self.rateStraight >= 0.4:
                if self.myCharacter.betMoney >= 10:
                    myBet.betType = 3
                    myBet.betValue = 0
                    self.turn += 1

                    print("fold")

                    return myBet
                myBet.betType = 2
                myBet.betValue = 0
                self.turn += 1

                print("call")

                return myBet
            else:
                myBet.betType = 3
                myBet.betValue = 0
                self.turn += 1

                print("fold")

                return myBet

    def SetResult(self, res: int, p1: Player):
        self.result = res
        self.myCharacter.hand[2] = copy.copy(p1.hand[2])
        self.deck.DeleteCard(copy.copy(p1.hand[2]))
        self.result = self.GetMatch()
        if self.result == -1:
            self.result = 2
        elif self.result == 0:
            self.result = 1
        elif self.result == 1:
            self.result = 0
        self.turn = 0


class GameLogic():
    def __init__(self):
        self.deck = Cards.StandardDeck()
        self.deck.shuffle()
        self.round = 1
        self.player1 = Player(30)
        self.player2 = Player(30)
        self.master = HoldemMaster()
        self.master2 = HoldemMaster()
        # self.df = pd.read_csv('WinRate_2D5_1.csv', header=0)
        # self.featureName = list(self.df.columns.values)
        # self.arr = self.df.values
        self.limit: BetStd = GetBestBetStd()

    def ReloadDeck(self):
        self.deck = Cards.StandardDeck()
        self.deck.shuffle()

    def DealCard(self):
        if len(self.deck) == 0:
            self.ReloadDeck()
        card1: Cards.Card = self.deck.deal()
        card2: Cards.Card = self.deck.deal()
        self.player1.hand = [card1.value, card2.value, self.deck.deal().value]
        self.player2.hand = [card1.value, card2.value, self.deck.deal().value]

    def PrintStatus(self, p1: Player):
        print("-----------------------------------")
        print("Opponent:", Cards.Card(p1.hand[2]))
        print("public:", Cards.Card(p1.hand[0]), Cards.Card(p1.hand[1]))
        print("-----------------------------------")

    def PrintRoundInfo(self):
        print("Round: ", self.round)
        print("Player1:", self.player1.chip, "Player2:", self.player2.chip)
        print("Base:", self.player1.betMoney + self.player2.betMoney)

    def GetMatch(self, p1: Player, p2: Player):
        p1.GetCombine()
        p2.GetCombine()
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

    def SelectBet(self, num: int) -> bool:
        DrawLine()

        # Player1의 배팅 페이즈
        if num == 1:
            print("Player1's turn")
            self.master2.UpdatePlayers(copy.copy(self.player1), copy.copy(self.player2))

            myBet: BetInfo = self.master2.BetAlogorithm(0.6, 0.5)

            if myBet.betType == 1:
                self.player1.BetChip(myBet.betValue)

                return True
            elif myBet.betType == 2:
                temp = self.player2.betMoney - self.player1.betMoney
                self.player1.BetChip(temp)

                return True
            elif myBet.betType == 3:
                self.player1.GetCombine()
                if self.player1.combine.value >= Combination.STRAIGHT.value:
                    self.player1.BetChip(10)

                return False

        # Player2의 배팅 페이즈
        elif num == 2:
            print("Player2's turn")
            self.master.UpdatePlayers(copy.copy(self.player2), copy.copy(self.player1))

            myBet: BetInfo = self.master.BetAlogorithm(self.limit.stdMax, self.limit.stdMin)

            if myBet.betType == 1:
                self.player2.BetChip(myBet.betValue)

                return True
            elif myBet.betType == 2:
                temp = self.player1.betMoney - self.player2.betMoney
                self.player2.BetChip(temp)

                return True
            elif myBet.betType == 3:
                self.player2.GetCombine()
                if self.player2.combine.value >= Combination.STRAIGHT.value:
                    self.player2.BetChip(10)

                return False

    def RoundProcess(self) -> bool:
        # 라운드가 홀수면 Player1 선 배팅
        # 라운드가 짝수면 Player2 선 배팅
        if self.round % 2 == 1:
            while 1:
                if not self.SelectBet(1):
                    print("Player2 Won")
                    self.player2.Win(self.player1.betMoney)
                    self.player1.Defeat()
                    return False
                if not self.SelectBet(2):
                    print("Player1 Won")
                    self.player1.Win(self.player2.betMoney)
                    self.player2.Defeat()
                    return False
                if self.player1.betMoney == self.player2.betMoney:
                    return True
        else:
            while True:
                if not self.SelectBet(2):
                    print("Player1 Won")
                    self.player1.Win(self.player2.betMoney)
                    self.player2.Defeat()
                    return False
                if not self.SelectBet(1):
                    print("Player2 Won")
                    self.player2.Win(self.player1.betMoney)
                    self.player1.Defeat()
                    return False
                if self.player1.betMoney == self.player2.betMoney:
                    return True

    def FinishRound(self):
        result = self.GetMatch(self.player1, self.player2)
        if result == -1:
            # player1 승
            print("Player1 Won")
            self.player1.Win(self.player2.betMoney)
            self.player2.Defeat()
        elif result == 1:
            # player2 승
            print("Player2 Won")
            self.player2.Win(self.player1.betMoney)
            self.player1.Defeat()

    def Start(self):
        while 1:
            DrawLine()
            # 플레이어1 잔액 확인 후 없으면 게임 종료
            if self.player1.betMoney <= 0:
                if self.player1.chip <= 0:
                    # self.arr = np.append(self.arr, np.array([[1]]), axis=0)  # player2 win
                    # self.df = pd.DataFrame(self.arr, columns=['Result'])
                    # self.df.to_csv('WinRate_2D5_1.csv', index=False)
                    print("Player2 won")
                    break
            # 플레이어2 잔액 확인 후 없으면 게임 종료
            if self.player2.betMoney <= 0:
                if self.player2.chip <= 0:
                    # self.arr = np.append(self.arr, np.array([[0]]), axis=0)  # player2 win
                    # self.df = pd.DataFrame(self.arr, columns=['Result'])
                    # self.df.to_csv('WinRate_2D5_1.csv', index=False)
                    print("Player1 won")
                    break
            if not (self.player1.betMoney and self.player2.betMoney):
                self.player1.BetChip(1)
                self.player2.BetChip(1)

            # 보유 칩 출력
            self.PrintRoundInfo()
            self.DealCard()
            self.master.SetOpponent(self.player1)
            self.master.GetRate()
            self.master2.SetOpponent(self.player2)
            self.master2.GetRate()

            # 라운드 진행
            result = self.RoundProcess()

            # 라운드 종료 후 돈 배분
            if result:
                self.FinishRound()
            self.master.SetResult(result, copy.copy(self.player2))
            self.round += 1



DrawLine()

game = GameLogic()
game.Start()

