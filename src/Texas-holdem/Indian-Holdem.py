from pygame.locals import *
from Events import *
from CardCommon import *
from GameSprites import *

# To-do
# 1. 서로 턴을 넘기는 이벤트를 만들어 줘야 함. (ok)
# 2. 턴을 넘길 때 STATE를 보고, AI가 BET을 주면 내 턴이 되면서 다시 버튼이 보임.
#   - delay를 주는데, 버튼이 사라지지를 않네..
# 3. AI의 selectBet 이벤트 작업하면 주고받고 완성 가능.
#   - 맞게 계산하고 있는건지 검증 필요. (Bet 할 때 금액을 너무 크게 부른다 ㅡㅡ..)
# 4. AI의 선택을 UI로 보여줘야 함. (ok)
# 5. Round 종료 이벤트 만들어야 함.


class Game:
    """..."""
    STATE_INITIAL = 'initial'
    STATE_PREPARING = 'preparing'
    STATE_PREFLOP = 'preflop'
    STATE_FLOP = 'flop'
    STATE_SHOWDOWN = 'showdown'
    STATE_BET = 'bet'
    STATE_CALL = 'call'
    STATE_FOLD = 'fold'

    isProgress = False  # 게임 진행중 여부
    isPlayerTurn = True  # 플레이어(유저)의 차례 여부. True: 유저차례, False: AI 차례

    def __init__(self, evManager):
        self.pot = None
        self.game_deck = Deck()
        self.players = []
        self.community_cards = []
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        self.master = HoldemMaster()  #
        self.state = Game.STATE_INITIAL

    # Event Notify
    def Notify(self, event):
        if isinstance(event, GameStartRequest):
            if self.state == Game.STATE_INITIAL:
                self.Start()
                self.deal_preflop()
                self.deal_flop()

        if isinstance(event, NextTurnEvent):
            if self.state == Game.STATE_PREPARING:
                self.deal_preflop()
            elif self.state == Game.STATE_PREFLOP:
                self.deal_flop()
            # elif self.state == Game.STATE_FLOP:
            #     self.show_down()
            # elif self.state == Game.STATE_SHOWDOWN:
            #     self.InitializeRound()

        # 여기서 엔터키로 입력한 amount 값을 받아오고, 처리한다.
        if isinstance(event, BetAmountKeyPress):  # ward
            self.deal_bet(self.players[1], self.players[0], event.amount)  # mine, opponent, amount

        # 다음 라운드 넘어갈 때: 1. 이름 다시 써주기 2. 칩 금액 업데이트 해주기 3. 카드 새로 깔아주기
        if isinstance(event, DealPreFlops):
            self.deal_preflop()

        # 임시 이벤트(뒤집혀 있는 사용자 카드 보여주기)
        if isinstance(event, AKeyEvent):
            self.open_playerCard()

        if isinstance(event, MouseClickEvent):
            mouse = pygame.mouse.get_pos()

            btnWidth = 150
            btnHeight = 40
            inputWidth = 140

            btnX = 800
            btnBetY = 450
            btnCallY = 510
            btnFoldY = 570

            inputX = 600

            if mouse[0] in range(btnX, btnX + btnWidth):
                if mouse[1] in range(btnBetY, btnBetY + btnHeight):
                    # BET button click
                    self.ClickBetButton()
                elif mouse[1] in range(btnCallY, btnCallY + btnHeight):
                    # CALL button click
                    self.ClickCallButton()
                elif mouse[1] in range(btnFoldY, btnFoldY + btnHeight):
                    # FOLD button click
                    self.ClickFoldButton()
            elif mouse[0] in range(inputX, inputX + inputWidth):  # 베팅 금액 input box
                self.ClickInputBox(mouse)

        if isinstance(event, PlayerCallEvent):
            # player[0] = AI
            # player[1] = Player(user)
            self.deal_call(self.players[1], self.players[0])  # 자기 자신, 상대방 순.

        if isinstance(event, PlayerFoldEvent):
            self.deal_fold(self.players[1])  # player[1] = Player(user)

        if isinstance(event, CallAITurn):
            self.SelectBet(self.players[0], self.players[1])  # AI의 선택은? ward to-do

    def Start(self):
        print('-------------------------------------------------------')
        print('Initialize Game: ')
        self.community_cards = []
        self.InitializePlayers()
        self.InitializeRound()
        self.InitializePot()
        print('InitializeRound')

    def InitializeRound(self):
        self.state = Game.STATE_PREPARING
        # Initialize Round
        self.game_deck.InitializeDeck()
        self.game_deck.ShuffleDeck()
        # self.game_deck.PrintCurrentDeck()
        self.community_cards = []

        # Initialize Players's holecards
        for player in self.players:
            player.init_holecards()

        if not self.isProgress:  # 최초 Initial
            self.evManager.Post(InitializeRoundEvent())
            self.isProgress = True
        else:
            self.evManager.Post(NextRoundEvent(self.players, self.pot))  # 라운드 넘어가는 Event

    def InitializePlayers(self):
        self.players = []
        self.players.append(Player('Computer', 0))
        self.players.append(Player('User', 1))

    def InitializePot(self):
        self.pot = Pot()

    def ClickBetButton(self):
        self.evManager.Post(ClickBetButton())

    def ClickCallButton(self):
        self.evManager.Post(ClickCallButton())
        # self.check_top()

    def ClickFoldButton(self):
        self.evManager.Post(ClickFoldButton())

    def ClickInputBox(self, mouse):
        self.evManager.Post(ClickInputBox(mouse))

    def open_playerCard(self):
        self.evManager.Post(OpenPlayerCard(self.players[1]))

    def ReloadDeck(self):
        self.game_deck = None
        self.game_deck = Deck()
        self.game_deck.ShuffleDeck()

    # pre-flop: 플레이어들에게 카드를 1장씩 나눠준다.
    def deal_preflop(self):
        self.state = Game.STATE_PREFLOP
        print('-------------------------------------------------------')
        print('Pre-Flop Stage: Deal 2 Hold Cards for each players')
        player_count = len(self.players)

        for i in range(player_count):
            if len(self.game_deck.deck_cards) == 0:
                self.ReloadDeck()
            self.players[i % player_count].add_cards(self.game_deck.Pop_card())

        for player in self.players:
            player.withdraw_chip(1)  # 참가비 1개씩.
            self.pot.save_chip(1)

        self.evManager.Post(PreFlopEvent(self.players, self.pot, self.isPlayerTurn))
        self.PrintCards()

    # flop : 커뮤니티 카드 2장을 깔아준다.
    def deal_flop(self):
        self.state = Game.STATE_FLOP
        print('-------------------------------------------------------')
        print('Flop Stage: Deal 2 Community Cards')
        for i in range(2):
            self.community_cards.append(self.game_deck.Pop_card())

        self.players[0].SetCombineTop(self.community_cards)
        self.players[1].SetCombineTop(self.community_cards)  # 각 플레이어들의 Combine과 Top을 설정하고 넘어감.

        self.evManager.Post(FlopEvent(self.community_cards))
        self.PrintCards()

    # 플레이어의 top 확인.
    def check_top(self):
        print(self.players[0].SetCombineTop(self.community_cards))

    # AI의 베팅 선택
    def SelectBet(self, AI: Player, player: Player):
        print('-------------------------------------------------------')
        print('Select bet')
        # to-do: 이 펑션은 무조건 AI만 사용하는 걸로.
        AI.opponentCards = copy.copy(player.holecards)  # 플레이어의 카드 set.
        print(self.game_deck.deck_cards)

        self.master.GetRate(self.game_deck, AI, player)
        myBet: BetInfo = self.master.BetAlgorithm(AI, player)
        isRoundEnd = False
        ai_state = ''
        if myBet.betType == 1:
            ai_state = "AI: Bet / chips :" + str(myBet.betValue)
            self.bet_chips(AI, myBet.betValue)
            self.state = Game.STATE_BET
            isRoundEnd = False
        elif myBet.betType == 2:
            if self.state == Game.STATE_CALL:  # 플레이어가 이미 Call을 외친 상태라면.
                isRoundEnd = True
            ai_state = "AI: Call"
            temp = player.betChip - AI.betChip
            self.bet_chips(AI, temp)
            self.state = Game.STATE_CALL
        elif myBet.betType == 3:
            ai_state = "AI: Fold"
            isRoundEnd = True
            self.state = Game.STATE_FOLD
            if AI.combine.value == Combination.STRAIGHT.value:
                self.bet_chips(AI, 10)  # Fold를 했는데 스트레이트 였다면 10개를 패널티로 내야 함.

        print(ai_state)
        self.evManager.Post(RefreshSprites(self.players, self.pot, ai_state))
        self.isPlayerTurn = True
        self.evManager.Post(PassTurn(self.isPlayerTurn, isRoundEnd))  # 턴 넘기기

    # Chip 베팅
    def bet_chips(self, player, amount):
        # player.withdraw_chip(amount)
        player.bet_chip(amount)
        self.pot.save_chip(amount)

    # Pot에서 Chip 가져오기
    def get_chips(self, player, amount):
        player.save_chip(amount)
        self.pot.withdraw_chip(amount)

    # bet : 원하는 금액 베팅
    def deal_bet(self, mine: Player, opponent: Player, amount):
        self.state = Game.STATE_BET
        print('-------------------------------------------------------')
        print('Bet Stage: 베팅할 금액 입력')
        amount = int(amount)
        # to-do
        if amount > mine.current_chips or amount > opponent.current_chips:
            print("다시 입력")
        elif amount + mine.betChip <= opponent.betChip:
            print("over money:", opponent.betChip - mine.betChip)
        else:
            self.bet_chips(mine, amount)  # 여기 하는중
            self.evManager.Post(RefreshSprites(self.players, self.pot, ''))
            self.isPlayerTurn = False
            self.evManager.Post(PassTurn(self.isPlayerTurn, False))  # Deal을 한다면 Round를 종료할 수 없다.

    # call : 추가 베팅 없이 진행
    def deal_call(self, mine, opponent: Player):  # ward
        if self.state == Game.STATE_CALL:  # AI가 Call을 외친 상태였다면
            isRoundEnd = True
        else:
            isRoundEnd = False
        self.state = Game.STATE_CALL
        print('-------------------------------------------------------')
        print('Call Stage: 추가 베팅 없이 진행')

        self.bet_chips(mine, opponent.betChip)  # 상대방이 베팅한 만큼 내 칩도 베팅한다.
        self.evManager.Post(RefreshSprites(self.players, self.pot, ''))
        self.isPlayerTurn = False
        self.evManager.Post(PassTurn(self.isPlayerTurn, isRoundEnd))  # 턴 넘기기

    # fold : 현재 턴 포기
    def deal_fold(self, player: Player):
        self.state = Game.STATE_FOLD
        print('-------------------------------------------------------')
        print('Fold Stage: 현재 턴 포기')
        if player.combine.value == Combination.STRAIGHT.value:
            self.bet_chips(player, 10)  # Fold를 했는데 스트레이트 였다면 10개를 패널티로 내야 함.

        self.isPlayerTurn = False
        self.evManager.Post(PassTurn(self.isPlayerTurn, True))  # 턴 넘기기

    # show_down : 승자를 확인한다.
    def show_down(self):
        self.state = Game.STATE_SHOWDOWN
        print('-------------------------------------------------------')
        print('ShowDown Stage: Check BestCards and Choose Winner')
        for player in self.players:
            print('Player ' + str(player.position) + ': \n')
            player.choice_best_cards(self.community_cards)
            PokerHelper.PrintCards(player.round_result.hands)

        winner = self.GetWinner()
        self.evManager.Post(ShowDownEvent(winner, self.community_cards, winner.round_result.hands))

    def GetWinner(self):
        players = self.players
        sorted_player = sorted(players, key=PokerHelper.cmp_to_key(PokerHelper.CompareTwoPlayerHands), reverse=True)

        print('--------------------- sorted players ---------------------')
        for player in sorted_player:
            print(player.name)
            print(player.round_result)

        winner = sorted_player[0]

        print('\nWinner => ' + winner.name + ', P' + str(winner.position))
        print(winner.round_result)

        return winner

    def pot_to_winner(self):
        pass

    def PrintCards(self):
        # print hole cards
        print('Hole Cards:')
        for player in self.players:
            for card in player.holecards:
                print('player: ', player.name, card)

        print('Community Cards:')
        for card in self.community_cards:
            print(card)


class EventManager:
    """this object is responsible for coordinating most communication
    between the Model, View, and Controller."""

    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()
        self.eventQueue = []
        self.listenersToAdd = []
        self.listenersToRemove = []

    # ----------------------------------------------------------------------
    def RegisterListener(self, listener):
        self.listenersToAdd.append(listener)

    # ----------------------------------------------------------------------
    def ActuallyUpdateListeners(self):
        for listener in self.listenersToAdd:
            self.listeners[listener] = 1
        for listener in self.listenersToRemove:
            if listener in self.listeners:
                del self.listeners[listener]

    # ----------------------------------------------------------------------
    def UnregisterListener(self, listener):
        self.listenersToRemove.append(listener)

    # ----------------------------------------------------------------------
    def Post(self, event):
        self.eventQueue.append(event)
        if isinstance(event, TickEvent):
            # Consume the event queue every Tick.
            self.ActuallyUpdateListeners()
            self.ConsumeEventQueue()

    # ----------------------------------------------------------------------
    def ConsumeEventQueue(self):
        i = 0
        while i < len(self.eventQueue):
            event = self.eventQueue[i]
            for listener in self.listeners:
                # Note: a side effect of notifying the listener
                # could be that more events are put on the queue
                # or listeners could Register / Unregister
                old = len(self.eventQueue)
                listener.Notify(event)
            i += 1
            if self.listenersToAdd:
                self.ActuallyUpdateListeners()
        # all code paths that could possibly add more events to
        # the eventQueue have been exhausted at this point, so
        # it's safe to empty the queue
        self.eventQueue = []


# ------------------------------------------------------

# ------------------------------------------------------
# Controllers
class CPUSpinnerController:
    """..."""

    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.keepGoing = 1

    # ----------------------------------------------------------------------
    def Run(self):
        while self.keepGoing:
            event = TickEvent()
            self.evManager.Post(event)

    # ----------------------------------------------------------------------
    def Notify(self, event):
        if isinstance(event, QuitEvent):
            # this will stop the while loop from running
            self.keepGoing = False


class KeyboardController:
    """KeyboardController takes Pygame events generated by the
    keyboard and uses them to control the model, by sending Requests
    or to control the Pygame display directly, as with the QuitEvent
    """

    def __init__(self, evManager, playerName=None):
        '''playerName is an optional argument; when given, this
        keyboardController will control only the specified player
        '''
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.activePlayer = None
        self.playerName = playerName
        self.players = []

    # ----------------------------------------------------------------------
    def Notify(self, event):
        if isinstance(event, TickEvent):
            # Handle Input Events
            for event in pygame.event.get():
                ev = None
                if event.type == QUIT:
                    ev = QuitEvent()
                elif event.type == KEYDOWN \
                        and event.key == pygame.K_ESCAPE:
                    ev = QuitEvent()
                elif event.type == KEYDOWN \
                        and event.key == (K_DOWN or K_UP or K_LEFT or K_RIGHT):
                    # print 'key down up left right pressed'
                    ev = NextTurnEvent()
                elif event.type == pygame.KEYDOWN \
                        and event.key == K_SPACE:
                    ev = GameStartRequest()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    ev = MouseClickEvent()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    ev = ReturnKeyPress()  # 베팅 금액 합산 로직 to-do
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    ev = BackSpaceEvent()
                elif event.type == pygame.KEYDOWN \
                        and event.key in range(K_0, K_9 + 1):
                    ev = InputNumbers(event.key)
                elif event.type == pygame.KEYDOWN \
                        and event.key == K_a:
                    ev = AKeyEvent()  # 임시기능 : A키를 누르면 뒤집힌 카드를 확인한다.

                if ev:
                    self.evManager.Post(ev)


# ------------------------------------------------------
# PygameView
class PygameView:
    DECK_POSITION = [750, 50]
    isButtonsVisible = False
    inputBox1 = None
    player_bet_amount = 0

    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)
        self.isButtonsVisible = False

        pygame.init()
        self.window = pygame.display.set_mode((1300, 700))
        pygame.display.set_caption('Indian Holdem')
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill((25, 65, 25))

        self.window.blit(self.background, (0, 0))

        font = pygame.font.Font(None, 60)
        textSurf = font.render("""Press SPACE BAR to start""", True, (120, 120, 120))
        textSurf = textSurf.convert_alpha()
        self.window.blit(textSurf, (400, 270))

        teststr = """Press an Arrows to progress"""
        textSurf = font.render(teststr, True, (120, 120, 120))
        textSurf = textSurf.convert_alpha()
        self.window.blit(textSurf, (370, 350))

        pygame.display.flip()

        self.backSprites = pygame.sprite.RenderUpdates()
        self.playerSprites = pygame.sprite.RenderUpdates()
        self.communitySprites = pygame.sprite.RenderUpdates()
        self.staticSprites = pygame.sprite.RenderUpdates()
        self.inputBoxSprites = pygame.sprite.RenderUpdates()
        self.buttonSprites = pygame.sprite.RenderUpdates()
        self.aiStateSprites = pygame.sprite.RenderUpdates()

    def ShowCommunityCards(self, card_list):
        i = 0
        for card in card_list:
            i += 2
            CardSprite(card, self.DECK_POSITION, (350 + i * 100, 350), COMMUNITY_CARD, self.communitySprites)

    def ShowShowDownResult(self, player, community_cards, card_list):

        for aSprite in self.playerSprites:
            if isinstance(aSprite, TextSprite):
                if aSprite.text == player.name:
                    aSprite.ChangeMakeBigger()

        # Remove previouse community fileds
        for cardSprite in self.communitySprites:
            cardSprite.kill()

        # Redraw Comminity Card with small size above Winner Announcing
        RectSprite((400, 140), 500, 120, self.communitySprites)

        i = 0
        for card in community_cards:
            i += 1
            CardSprite(card, self.DECK_POSITION, (350 + i * 100, 200), COMMUNITY_CARD, self.communitySprites)

        i = 0
        for card in card_list:
            i += 1
            CardSprite(card, self.DECK_POSITION, (350 + i * 100, 450), COMMUNITY_CARD, self.communitySprites)

        TextSprite("The Winner is " + player.name, (550, 300), 60, (200, 30, 10), self.communitySprites)
        TextSprite("\"" + player.round_result.result_name + "\"", (550, 360), 50, (200, 40, 200), self.communitySprites)

        self.isButtonsVisible = False

    def ShowPreFlopCards(self, players, isPlayerTurn: bool):

        POS_LEFT = 0
        POS_TOP = 0

        for player in players:
            player_pos = player.position
            bottomMultiply = -1
            player_type = ""

            if player_pos == 0:
                POS_LEFT = 235
                POS_TOP = 160
                player_type = AI_CARD
            elif player_pos == 1:
                POS_LEFT = 1200
                POS_TOP = 450
                bottomMultiply = 1
                player_type = PLAYER_CARD

            CardSprite(player.holecards[0], self.DECK_POSITION,
                                   (POS_LEFT - 15, POS_TOP + (bottomMultiply) * 30), player_type, self.playerSprites)
            TextSprite(player.name, (POS_LEFT - 20, POS_TOP - (bottomMultiply) * 40), 30, (150, 150, 150), self.playerSprites)

        self.ShowButtons(isPlayerTurn)
        self.isButtonsVisible = True

    def InitializeFrontSprites(self):
        for cardSprite in self.communitySprites:
            cardSprite.kill()

        for cardSprite in self.playerSprites:
            cardSprite.kill()

        for textSprite in self.communitySprites:
            textSprite.kill()

        for textSprite in self.playerSprites:
            textSprite.kill()

        self.inputBox1 = None
        for inputBoxSprite in self.inputBoxSprites:
            inputBoxSprite.kill()

    def ShowButtons(self, isPlayerTurn: bool):
        if isPlayerTurn:
            ButtonSprite("BET", (800, 450), 150, 40, self.buttonSprites)
            ButtonSprite("CALL", (800, 510), 150, 40, self.buttonSprites)
            ButtonSprite("FOLD", (800, 570), 150, 40, self.buttonSprites)
        else:
            self.HideButtons()

    def HideButtons(self):
        for buttonSprite in self.buttonSprites:
            buttonSprite.kill()

    def ShowTable(self):
        TableSprite(self.backSprites)

    def ShowAIState(self, ai_state):
        for _sprite in self.aiStateSprites:
            _sprite.kill()

        TextSprite(ai_state, (100, 400), 50, (220, 220, 220), self.aiStateSprites)

    def ShowChips(self, players, pot):
        for _sprite in self.staticSprites:
            _sprite.kill()

        # AI
        ChipSprite([320, 50], self.staticSprites)
        TextSprite('X', (370, 50), 40, (200, 200, 200), self.staticSprites)

        # Player
        ChipSprite([1100, 600], self.staticSprites)  # Player
        TextSprite('X', (1150, 600), 40, (200, 200, 200), self.staticSprites)

        # Pot
        TextSprite('POT', (1000, 50), 50, (220, 220, 220), self.staticSprites)
        ChipSprite([1100, 50], self.staticSprites)
        TextSprite('X', (1150, 50), 40, (200, 200, 200), self.staticSprites)
        TextSprite(str(pot.pot_chip), (1180, 50), 40, (200, 200, 200), self.staticSprites)

        i = 0
        for player in players:
            if i == 0:
                TextSprite(str(player.current_chips), (400, 50), 40, (200, 200, 200), self.staticSprites)
            elif i == 1:
                TextSprite(str(player.current_chips), (1180, 600), 40, (200, 200, 200), self.staticSprites)
            i += 1

    def ShowInputBox(self, isPlayerTurn):  # 베팅 금액 input box show
        if isPlayerTurn and self.inputBox1 is None:
            self.inputBox1 = InputBoxSprite((600, 450), 140, 32, self.inputBoxSprites)
        else:
            self.HideInputBox()

    def HideInputBox(self):
        self.inputBox1 = None
        for inputBox in self.inputBoxSprites:
            inputBox.kill()

    def InputBettingAmount(self, value):
        if self.inputBox1.active:
            self.inputBox1.text += str(value)
            self.inputBox1.textProcess()

    def OpenPlayerCardEvent(self, player):
        print(player.holecards[0].rank, player.holecards[0].suit)

        for cardSprite in self.playerSprites:
            if cardSprite.__class__ == CardSprite and cardSprite.type == PLAYER_CARD:
                cardSprite.ChangeCardImage()  # 사용자 카드 뒤집기

    def InputBackspace(self):
        if self.inputBox1.active:
            self.inputBox1.text = self.inputBox1.text[:-1]
            self.inputBox1.textProcess()

    def DecideBettingAmount(self):
        if self.inputBox1.active and len(self.inputBox1.text) > 0:
            return self.inputBox1.text
        else:
            return ''

    # 베팅 금액 InputBox 활성화/비활성화 event
    def ClickInputBox(self, mouse):
        if self.isButtonsVisible:
            if self.inputBox1:
                if self.inputBox1.rect.collidepoint(mouse):
                    self.inputBox1.active = not self.inputBox1.active
                else:
                    self.inputBox1.active = False
                self.inputBox1.color = COLOR_ACTIVE if self.inputBox1.active else COLOR_INACTIVE
                self.inputBox1.draw()

    def NextRoundInitial(self, players, pot):
        for cardSprite in self.communitySprites:
            cardSprite.kill()

        for cardSprite in self.playerSprites:
            cardSprite.kill()

        for inputBoxSprite in self.inputBoxSprites:
            inputBoxSprite.kill()

        # 플레이어 이름 글씨 다시 써주기
        self.evManager.Post(DealPreFlops())

    def TurnOverEvent(self, isPlayerTurn: bool, isRoundEnd: bool):
        self.HideInputBox()  # inputBox visible 처리
        self.ShowButtons(isPlayerTurn)  # Button visible 처리
        if isRoundEnd:
            # 라운드 종료 이벤트
            print("라운드 종료해주삼")
            pygame.time.wait(1000)  # 1초 딜레이
        else:
            if not isPlayerTurn:
                self.evManager.Post(CallAITurn())  # AI의 차례 호출.

    def ShowInitGame(self):
        pass

    # ----------------------------------------------------------------------
    def Notify(self, event):
        for buttonSprite in self.buttonSprites:
            buttonSprite.isHover(pygame.mouse.get_pos())

        if isinstance(event, TickEvent):
            # Draw Everything
            self.backSprites.clear(self.window, self.background)
            self.playerSprites.clear(self.window, self.background)
            self.communitySprites.clear(self.window, self.background)
            self.staticSprites.clear(self.window, self.background)
            self.inputBoxSprites.clear(self.window, self.background)
            self.buttonSprites.clear(self.window, self.background)
            self.aiStateSprites.clear(self.window, self.background)

            seconds = 50

            self.backSprites.update(seconds)
            self.playerSprites.update(seconds)
            self.communitySprites.update(seconds)
            self.staticSprites.update(seconds)
            self.inputBoxSprites.update(seconds)
            self.buttonSprites.update(seconds)
            self.aiStateSprites.update(seconds)

            dirtyRects1 = self.backSprites.draw(self.window)
            dirtyRects2 = self.playerSprites.draw(self.window)
            dirtyRects3 = self.communitySprites.draw(self.window)
            dirtyRects4 = self.staticSprites.draw(self.window)
            dirtyRects5 = self.inputBoxSprites.draw(self.window)
            dirtyRects6 = self.buttonSprites.draw(self.window)
            dirtyRects7 = self.aiStateSprites.draw(self.window)

            dirtyRects = dirtyRects1 + dirtyRects2 + dirtyRects3 + dirtyRects4 + dirtyRects5 + dirtyRects6 + dirtyRects7
            pygame.display.update(dirtyRects)

        if isinstance(event, GameStartRequest):
            # self.ShowInitGame()
            self.ShowTable()

        # 베팅 금액 입력 후 엔터 눌렀을 때.
        if isinstance(event, ReturnKeyPress):
            amount = self.DecideBettingAmount()
            if amount != '':
                self.player_bet_amount = int(amount)
                self.evManager.Post(BetAmountKeyPress(amount))  # 여기서 Game 클래스로 입력값을 보낸다.

        # 백스페이스 입력 이벤트
        if isinstance(event, BackSpaceEvent):
            self.InputBackspace()

        # 숫자 입력 이벤트
        if isinstance(event, InputNumbers):
            self.InputBettingAmount(event.value)

        # 뒤집혀 있는 플레이어 카드 확인하기
        if isinstance(event, OpenPlayerCard):
            self.OpenPlayerCardEvent(event.player)

        # "BET" 버튼 클릭 이벤트.
        if isinstance(event, ClickBetButton):
            if self.isButtonsVisible:  # 버튼이 보이는 상태일때만 작동.
                self.ShowInputBox(True)

        # "Call" 버튼 클릭 이벤트.
        if isinstance(event, ClickCallButton):
            self.evManager.Post(PlayerCallEvent())

        # "Fold" 버튼 클릭 이벤트.
        if isinstance(event, ClickFoldButton):
            self.evManager.Post(PlayerFoldEvent())

        # InputBox 클릭(=>활성화/비활성화) 이벤트.
        if isinstance(event, ClickInputBox):
            if self.isButtonsVisible:
                self.ClickInputBox(event.mouse)

        # 턴 넘기는 이벤트
        if isinstance(event, PassTurn):
            self.TurnOverEvent(event.isPlayerTurn, event.isRoundEnd)

        if isinstance(event, PreFlopEvent):
            self.ShowPreFlopCards(event.players, event.isPlayerTurn)
            self.ShowChips(event.players, event.pot)

        if isinstance(event, FlopEvent):
            self.ShowCommunityCards(event.card_list)

        if isinstance(event, ShowDownEvent):
            self.ShowShowDownResult(event.player, event.community_cards, event.card_list)

        if isinstance(event, InitializeRoundEvent):
            self.InitializeFrontSprites()

        if isinstance(event, NextRoundEvent):
            self.NextRoundInitial(event.players, event.pot)

        if isinstance(event, RefreshSprites):
            self.ShowChips(event.players, event.pot)
            self.ShowAIState(event.ai_state)


# ------------------------------------------------------
def main():
    evManager = EventManager()

    keybd = KeyboardController(evManager)
    spinner = CPUSpinnerController(evManager)
    pygameView = PygameView(evManager)

    texas_holdem = Game(evManager)

    spinner.Run()


if __name__ == "__main__":
    main()
