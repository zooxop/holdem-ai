# 필요한 모듈을 미리 다 불러온다.
import random


# 카드 순위 따지는 코드
def CardRank(cards):
    paircount = 0
    for n1 in range(0, 4):
        for n2 in range(n1 + 1, 5):
            if cards[n1][1] == cards[n2][1]:
                paircount = paircount + 1
    num = [cards[k][1] for k in range(5)]
    num.sort()
    straightox = False
    if paircount == 0:
        if (num[4] - num[0]) == 4:
            straightox = True
        if num[0] == 1 and num[1] == 10:
            straightox = True
    suit = [cards[k][0] for k in range(5)]
    suit.sort()
    flushox = False
    if suit[0] == suit[4]:
        flushox = True
    if straightox and flushox:
        rank = 1
    elif paircount == 6:
        rank = 2
    elif paircount == 4:
        rank = 3
    elif flushox:
        rank = 4
    elif straightox:
        rank = 5
    elif paircount == 3:
        rank = 6
    elif paircount == 2:
        rank = 7
    elif paircount == 1:
        rank = 8
    else:
        rank = 9
    return rank


# 게임머니 $2000을 저장한다.
Money = 2000
# 카드 한 팩을 만든다.
deck = [(suit, k) for suit in ["s", "h", "d", "c"] for k in range(1, 14)]
# 게임을 반복한다
while True:
    # 카드를 섞는다.
    random.shuffle(deck)
    # 배팅 1,2,3,4,5
    for n in [1, 2, 3, 4, 5]:
        answer = input("배팅하시겠습니까? (y/n)")
        if answer == 'n' or answer == 'N':
            break  #
        Money = Money - 10
        if n == 1:
            cards_A = [deck[k] for k in range(0, 2)]  # 컴퓨터
            cards_B = [deck[k] for k in range(2, 4)]  # 선수
        elif n < 4:
            cards_A.append(deck[n * 2])
            cards_B.append(deck[n * 2 + 1])
        elif n == 4:
            hiddencard = deck[n * 2]
            cards_B.append(deck[n * 2 + 1])
        else:
            cards_A.append(hiddencard)
            rank_A = CardRank(cards_A)
            rank_B = CardRank(cards_B)
            if rank_B < rank_A:
                Money = Money + 100
                print('당신이 이겼습니다.')
            elif rank_B == rank_A:
                print('비겼습니다')
            else:
                print('컴퓨터가 이겼습니다.')
        print("Money = ", Money)
        print("computer: ", cards_A)
        print("player  : ", cards_B)

    answer = input("게임을 더 하시겠습니까? (y/n)")
    if answer == 'n' or answer == 'N':
        break