import pygame
import sys
import ctypes
import random
import time
from PIL import Image

suits = ['H', 'D', 'S', 'C']
cardValues = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 
            # 'K': 10, 
            'Q': 10,
            'J': 10,
            'A': -1}

class Card:
    def __init__(self, name: str):
        self.value = cardValues[name[1:]]
        self.name = name
        
    def __repr__(self):
        return self.name

class Hand:
    def __init__(self, cards: list[Card], firstCardHidden = False):
        self.cards = cards
        self.total = 0
        self.firstCardHidden = firstCardHidden
        self.setTotal()
    
    def __repr__(self):
        return " ".join([card.name for card in self.cards])
        
    def addCard(self, card: Card):
        self.cards.append(card)
        self.setTotal()
            
    def setTotal(self):
        self.total = 0
        aces = 0
        print(self.cards)
        for i, card in enumerate(self.cards):
            if self.firstCardHidden and i == 0:
                continue
            cardVal = card.value
            if cardVal != -1:
                self.total += cardVal
            else:
                aces += 1
        
        for i in range(aces):
            if self.total + 11 < 21:
                self.total += 11
            else:
                self.total += 1
        
    def revealCard(self):
        self.firstCardHidden = False
        self.setTotal()

class Deck:
    def __init__(self):
        self.cards = []
        self.setDeckCards()
    
    def setDeckCards(self):
        for s in suits:
            for val in cardValues.keys():
                self.cards.append(Card(s + val))
            
class Shoe:
    def __init__(self, deckN: int):
        self.cards = []
        self.cardAmount = 0
        self.setShoeDecks(deckN)
        self.shuffleShoe()
    
    def dealCard(self):
        card = self.cards[0]
        self.cards.pop(0)
        self.cardAmount -= 1
        return card
        
    def setShoeDecks(self, deckN: int):
        for i in range(deckN):
            deck = Deck()
            self.cards += deck.cards
        self.cardAmount = deckN * 13
    
    def shuffleShoe(self):
        random.shuffle(self.cards)

# TODO - figure out the proper positioning/order of game, UI, etc
# it is a bit awkward how UI is at the end and game is at the very top
class Game:
    def __init__(self):
        self.status = 'waiting'
        self.balance = 1000
        self.shoe = Shoe(6)
        self.dealerHand = Hand(cards=[])
        self.playerHand = Hand(cards=[])
        self.handBet = 0
        self.timer = 0
        
        pygame.init()
        self.setWindowSettings()
        self.ui = UI(self)
        self.isHovering = False
        self.displayedPlayerTotal = 0
        self.displayedDealerTotal = 0
    
    
    def handleHit(self):
        if self.status == 'waiting':
            self.startRound()
            self.setHandBet(100)
            self.playerTurn()
        elif self.status == 'playerTurn':
            self.hit()
           
    def handleStand(self):
        if self.status == 'playerTurn':
            self.stand()
    
    def run(self):
        self.clock = pygame.time.Clock()
        self.running = True
        pic = False
        while self.running:
            dt = min(self.clock.tick(120) / 1000.0, 0.05)
            # print(f"FPS {self.clock.get_fps():.1f}")
                
            
            if self.status == 'dealAnimation' and self.timer + 1.5 < time.time():
                self.dealerHand.addCard(self.shoe.dealCard())
                print(f'Dealer cards: {self.dealerHand} total {self.dealerHand.total}')
                self.status = 'playerTurn'
                self.stand()
            
            if self.status == 'hitAnimation' and self.timer + 0.5 < time.time():
                newCard = self.shoe.dealCard()
                self.playerHand.addCard(newCard)
                print(f'Dealt cards: {self.playerHand} total {self.playerHand.total}')
                self.status = 'playerTurn'
                if self.playerHand.total > 21:
                    self.checkGameStatus()
            
            if self.status == 'finishAnimation' and self.timer + 2 < time.time():
                self.status = 'waiting'
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        print('pressed h')
                        self.handleHit()
                    elif event.key == pygame.K_s:
                        self.handleStand()
                        
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    # TODO - review this logic and move it to a separate function, too much indentation
                    
                    if self.status == 'waiting' and self.ui.startRect != None and self.ui.startRect.collidepoint(event.pos):
                        print("Start clicked")
                        self.handleHit()  
                    elif self.status != 'waiting' and self.ui.hitRect != None and self.ui.hitRect.collidepoint(event.pos):
                        print("Hit clicked")
                        self.handleHit()
                    elif self.status != 'waiting' and self.ui.standRect != None and self.ui.standRect.collidepoint(event.pos):
                        print("Stand clicked")
                        self.handleStand()
            
            self.ui.render(dt=dt)
            if not pic:
                pygame.image.save(self.ui.screen, f"screenshot.png")
                pic = True
        self.quit()
        
    def setWindowSettings(self):
        pygame.display.set_caption('MatFyz Blackjack')
        pygame.display.set_icon(pygame.image.load('assets/sprites/chips/red.png'))
        
        if sys.platform == 'win32':
            myappid = 'marmatakis.matfyzblackjack.0.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

            try:
                ctypes.windll.user32.SetProcessDPIAware()
                dpi = ctypes.windll.user32.GetDpiForSystem()
                return dpi / 96.0
            except AttributeError:
                pass
        return 1.0
    
    def quit(self):
        pygame.quit()
    
    def addToBalance(self, amount: int):
        self.balance += amount
        
    def startRound(self):
        assert self.status == 'waiting'
        self.playerHand, self.dealerHand = Hand(cards=[]), Hand(cards=[])
        self.status = 'betting'
        
    def setHandBet(self, amount: int):
        assert self.status == 'betting'
        if self.balance < self.handBet:
            return
        self.handBet = amount
    
    def playerTurn(self):
        assert self.status == 'betting'
        self.balance -= self.handBet
        self.dealerHand = Hand([self.shoe.dealCard(), self.shoe.dealCard()], firstCardHidden=True)
        self.status = 'playerTurn'
        self.playerHand = Hand([self.shoe.dealCard(), self.shoe.dealCard()])
        self.ui.chips.moveToHand()
    
    def hit(self):
        assert self.status == 'playerTurn'
        self.status = 'hitAnimation'
        self.timer = time.time()
            
    def stand(self):
        assert self.status == 'playerTurn'
        self.status = 'dealerTurn'
        if self.dealerHand.firstCardHidden:
            self.dealerHand.revealCard()
  
        # implementation of house/dealer rules - stand on 17+, hit on <16
        if self.dealerHand.total <= 16:
            self.status = 'dealAnimation'
            self.timer = time.time()
        else:
            self.checkGameStatus()
    
    def payoutWinnings(self, bet: int, condition: str):
        self.status = 'payout'
        # TODO - remove print statements everywhere here and display everything in the interface
        
        match condition:
            case 'blackjack':
                print(f'Blackjack! +{bet * 3 / 2}, Balance: {game.balance + bet + bet * 3 / 2}')
                self.addToBalance(bet + bet * 3 / 2)
            case 'win':
                self.ui.chips.moveToPlayer()
                print(f'Win +{bet}, Balance: {game.balance + 2*bet}')
                self.addToBalance(2 * bet)
            case 'doubleWin':
                print(f'Double win +{2 * bet}, Balance: {game.balance + 4*bet}')
                self.addToBalance(4 * bet)
            case 'tie':
                print(f'Tie! +0, Balance: {game.balance + bet}')
                self.addToBalance(bet)
            case 'loss':
                print(f'Loss:( Balance: {game.balance}')
                self.ui.chips.moveToDealer()
                pass
        self.status = 'waiting'
        
    def finishRound(self, condition: str):
        self.payoutWinnings(self.handBet, condition)
        self.status = 'finishAnimation'
        self.timer = time.time()
        # TODO - timeout doesn't work here for some reason :(
        
    
    def checkGameStatus(self):
        playerTotal = self.displayedPlayerTotal
        dealerTotal = self.displayedDealerTotal
        
        if dealerTotal != 0:
            print(f'player {playerTotal} dealer {dealerTotal}')
        
        # TODO - this logic is yandere dev type, definitely needs a rewrite
        if playerTotal == 21 and dealerTotal != 21 and len(self.playerHand.cards) == 2:
            self.finishRound('blackjack')
            return False
        if playerTotal == dealerTotal:
            self.finishRound('tie')
            return False
        if playerTotal > 21:
            self.finishRound('loss')
            return False
        if dealerTotal > 21:
            self.finishRound('win')
            return False
        if dealerTotal == 0:
            return True
        if playerTotal > dealerTotal:
            self.finishRound('win')
            return False
        if dealerTotal > playerTotal:
            self.finishRound('loss')
            return False


class Texts:
    class Fonts:
        def __init__(self, ui):
            self.fontRegular = pygame.font.Font('assets/fonts/Unbounded-Regular.ttf', ui.s(16))
            self.fontSemiBold = pygame.font.Font('assets/fonts/Unbounded-SemiBold.ttf', ui.s(23))
            self.fontBold = pygame.font.Font('assets/fonts/Unbounded-Bold.ttf', ui.s(28))
    class Text:
        def __init__(self, text: str, font : pygame.font.Font, color: tuple, centerx: int, top: int):
            self.text = text
            self.color = color
            self.centerx = centerx
            self.top = top
            self.textObj = font.render(
                text,
                True,
                color
            )
            self.textSurface = self.textObj.get_rect(
                centerx = centerx,
                top = top
            )
    
    def __init__(self, texts: list[Text], screen, ui):
        self.texts = texts
        self.screen = screen
        self.ui = ui
        
    def addText(self, text: Text):
        self.texts.append(text)
    
    def calcTotal(self, cards):
        total = 0
        aces = 0
        for i, card in enumerate(cards):
            if card.hidden:
                continue
            cardVal = cardValues[str(card.name)[1:]]
            if cardVal != -1:
                total += cardVal
            else:
                aces += 1
        
        for i in range(aces):
            if total + 11 < 21:
                total += 11
            else:
                total += 1
        return total

    def render(self):
        newTexts = self.texts.copy()
        # TODO - make this system dynamic somehow, similar to the UI.texts
        if game.status != 'waiting':
            playerHandTotal = self.calcTotal(game.ui.cards.playerCards)
            dealerHandTotal = self.calcTotal(game.ui.cards.dealerCards)
            game.displayedPlayerTotal = playerHandTotal
            game.displayedDealerTotal = dealerHandTotal
                
            newTexts.append(Texts.Text(str(playerHandTotal), self.ui.fonts.fontBold, (255, 255, 255), self.ui.width / 2 + self.ui.s(23), self.ui.s(242)))
            newTexts.append(Texts.Text(str(dealerHandTotal), self.ui.fonts.fontBold, (255, 255, 255), self.ui.width / 2 + self.ui.s(43), self.ui.s(35)))
            newTexts.append( Texts.Text('DEALER', self.ui.fonts.fontRegular, (255, 255, 255), self.ui.width / 2 - self.ui.s(27), self.ui.s(39)))
            newTexts.append(Texts.Text('YOU', self.ui.fonts.fontRegular, (255, 255, 255), self.ui.width / 2 - self.ui.s(27), self.ui.s(245)))

        newTexts.append(Texts.Text(f'{game.balance}$', self.ui.fonts.fontSemiBold, (237, 218, 53), self.ui.s(60), self.ui.s(460)))  
            
        for text in newTexts:
            self.screen.blit(text.textObj, text.textSurface)

class UI:
    def __init__(self, game):
        if sys.platform == 'win32':
            try:
                self.scale = ctypes.windll.user32.GetDpiForSystem() / 96.0
            except AttributeError:
                self.scale = 1.0
        else:
            self.scale = 1.0
            
        self.game = game
        self.base_width, self.base_height = 500, 500
        self.width = int(round(self.base_width * self.scale))
        self.height = int(round(self.base_height * self.scale))
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = pygame.image.load('assets/sprites/table.jpg').convert()
        self.background = pygame.transform.smoothscale(self.background, (self.width, self.height))
        self.fonts = Texts.Fonts(self)
        # TODO - implement same system for Sprites, not only Texts
        self.texts = Texts(
            [], 
            screen = self.screen,
            ui = self
        )
        self.hitRect = None
        self.standRect = None
        self.doubleRect = None
        self.shoe = UI.Shoe((self.s(395), self.s(30)), length=4, ui=self)
        self.cards = UI.Cards(self, [], [])
        
        chip = self.Chip(val=100, position=(self.s(-70), self.s(-70)), target=(self.s(-70), self.s(-70)), ui=self)
        self.chips = UI.Chips([chip], self)
        
        chip10 = self.Chip(val=10, position=(self.s(107), self.s(350)), target=(self.s(100), self.s(350)), ui=self)
        chip20 = self.Chip(val=20, position=(self.s(187), self.s(350)), target=(self.s(180), self.s(350)), ui=self)
        chip50 = self.Chip(val=50, position=(self.s(267), self.s(350)), target=(self.s(260), self.s(350)), ui=self)
        chip100 = self.Chip(val=100, position=(self.s(347), self.s(350)), target=(self.s(340), self.s(350)), ui=self)
        
        self.bettingChips = UI.Chips([chip10, chip20, chip50, chip100], self)
        
        self.startButton = UI.Button('start', (self.width / 2 - self.s(40), self.s(432)), ui=self)
        self.startRect = self.startButton.rect
        self.statsButton = UI.Button('stats', (self.s(390), self.s(432)), ui=self)
        self.statsRect = self.statsButton.rect
        self.standButton = UI.Button('stand', (self.width / 2 - self.s(97), self.s(432)), ui=self)
        self.standRect = self.standButton.rect
        self.hitButton = UI.Button('hit', (self.width / 2 + self.s(10), self.s(432)), ui=self)
        self.hitRect = self.hitButton.rect
    
    class Chip:
        def __init__(self, val: int, position: tuple, target: tuple, ui):
            vals = {10: 'green', 20: 'blue', 50: 'yellow', 100: 'red'}
            self.position = pygame.math.Vector2(position)
            self.target = pygame.math.Vector2(target)
            
            self.isMoving = self.position != self.target
            self.speed = 700
            
            self.ui = ui
            self.val = val
            self.obj = pygame.image.load(f'assets/sprites/chips/{vals[val]}.png').convert_alpha()
            self.obj = pygame.transform.smoothscale(self.obj, (ui.s(75), ui.s(75)))

        def update(self, dt):
            if not self.isMoving:
                return
        
            self.position = self.position.move_towards(self.target, self.speed * dt)
            if self.position == self.target:
                self.isMoving = False
        
        def setTarget(self, target):
            self.target = pygame.math.Vector2(target)
            self.isMoving = self.position != self.target
        
        def setPosition(self, position):
            self.position = pygame.math.Vector2(position)
            self.isMoving = self.position != self.target
        
        def blit(self):
            self.ui.screen.blit(self.obj, self.position)
            
    class Chips:
        def __init__(self, handChips: list, ui):
            self.ui = ui
            self.handChips = handChips
        
        def moveToDealer(self):
            for chip in self.handChips:
                chip.setTarget((self.ui.s(50), self.ui.s(-70)))
                
        def moveToPlayer(self):
            for chip in self.handChips:
                chip.setTarget((self.ui.s(50), self.ui.s(570)))
        
        def moveToHand(self):
            for chip in self.handChips:
                chip.setPosition((self.ui.s(50), self.ui.s(195)))
                chip.setTarget((self.ui.s(50), self.ui.s(195)))
        
        def update(self, dt):
            for chip in self.handChips:
                chip.update(dt)
                chip.blit()
        
    class Card:
        def __init__(self, position: tuple, target: tuple, name: str, img: str, ui, hidden=False):
            self.position = pygame.math.Vector2(position)
            self.target = pygame.math.Vector2(target)
            self.isMoving = self.position != self.target
            self.speed = 700
            
            self.obj = pygame.image.load(f'assets/sprites/cards/{img}.png').convert_alpha()
            self.obj = pygame.transform.smoothscale(self.obj, (ui.s(90), ui.s(120)))
            self.img = img
            print('initial hidden', hidden)
            self.hidden = hidden
            self.dealerCard = False
            self.ui = ui
            self.name = name
        
        def update(self, dt):
            # print('update called')
            if not self.isMoving:
                return
            self.position = self.position.move_towards(self.target, self.speed * dt)
            if self.position == self.target:
                if game.status == 'dealerCardAnimation':
                    self.setImg(self.name)
                    self.dealerCard = False
                    game.status = 'dealerCardAnimation2'
                    self.setTarget(self.ui.cards.dealerPositions[1][0])
                    return
                if game.status == 'dealerCardAnimation2':
                    game.status = 'playerTurn'
                    game.stand()
                if self.hidden and not self.dealerCard:
                    self.setImg(self.name)
                    print('setting hidden to False', self.position, self.target, self.name, self.img)
                    self.hidden = False
                    self.speed = 200
                self.isMoving = False
        
        def setImg(self, name):
            self.obj = pygame.image.load(f'assets/sprites/cards/{name}.png').convert_alpha()
            self.obj = pygame.transform.smoothscale(self.obj, (self.ui.s(90), self.ui.s(120)))
        
        def setTarget(self, target):
            print('setTarget called')
            self.target = pygame.math.Vector2(target)
            self.isMoving = self.position != self.target
            print(self.target, self.isMoving)
                
        def setPosition(self, position):
            self.position = pygame.math.Vector2(position)
            self.isMoving = self.position != self.target
            
        def blit(self):
            self.ui.screen.blit(self.obj, self.position)
            
    class Cards:
        def __init__(self, ui, playerCards: list[Card] = [], dealerCards: list[Card] = []):
            self.playerCards = []
            self.dealerCards = []
            self.playerCardNames = []
            self.dealerCardNames = []
            self.dealerCardHidden = True
            self.ui = ui

            self.playerPositions = [
                [(self.ui.width / 2 + self.ui.s(40 * i) - self.ui.s(22 * x) - self.ui.s(40), self.ui.s(275))
                for i in range(8)]
                for x in range(8)
            ]
            self.dealerPositions = [
                [(self.ui.width / 2 + self.ui.s(40 * i) - self.ui.s(22 * x) - self.ui.s(40), self.ui.s(70))
                for i in range(8)]
                for x in range(8)
            ]
        
        def update(self, dt, dealerCards, playerCards, dealerCardHidden):
            dealerCards = dealerCards.copy()
            # TODO - still, for the future only add cards that haven't been added yet instead of rewriting
            if playerCards != self.playerCardNames:
                if len(playerCards) <= len(self.playerCardNames) and self.playerCardNames[:len(playerCards)] != playerCards:
                    self.removePlayerCards()
                self.addPlayerCards(playerCards)
            
            if self.dealerCardHidden != dealerCardHidden and len(dealerCards) > 0:
                self.dealerCardHidden = dealerCardHidden
                self.addDealerCards(dealerCards, firstCardHidden=dealerCardHidden)
                
            if dealerCards != self.dealerCardNames:
                if len(dealerCards) <= len(self.dealerCardNames) and self.dealerCardNames[:len(dealerCards)] != dealerCards:
                    self.removeDealerCards()
                self.addDealerCards(dealerCards, firstCardHidden=self.dealerCardHidden)
            
            self.blit(dt)
            
        def addPlayerCards(self, cards: list[str]):
            
            for i, c in enumerate(cards):
                card = None
                initialLen = len(self.playerCardNames)
                # print('initial len' , initialLen)
                if i + 1 > initialLen:
                    card = UI.Card((0, 0), (0, 0), img='back_red', name=c, hidden=True, ui=self.ui)
                    self.addPlayerCard(card)
                else:
                    card = self.playerCards[i]
                
                totalLen = self.playerCardsLength()
                for j, card in enumerate(self.playerCards):
                    if j + 1 > initialLen:
                        card.setPosition((self.ui.s(395), self.ui.s(10)))
                    card.setTarget(self.playerPositions[totalLen - 1][j])
                
        def addDealerCards(self, cards: list[str], firstCardHidden=False):
            if firstCardHidden:
                self.firstCardHidden = True
                
            excludeFirstCard = False
            for i, c in enumerate(cards):
                card = None
                initialLen = len(self.dealerCardNames)
                if i + 1 > initialLen:
                    card = UI.Card((0, 0), (0, 0), name=c, img='back_red', hidden=True, ui=self.ui)
                    if i == 0 and firstCardHidden:
                        card.dealerCard = True
                    self.addDealerCard(card)
                else:
                    card = self.dealerCards[i]
                    if i == 0 and self.firstCardHidden and not firstCardHidden:
                        print('setting not hidden')
                        self.firstCardHidden = False
                        card.setTarget((self.ui.width / 2 - self.ui.s(120), self.ui.s(70)))
                        card.speed = 300
                        game.status = 'dealerCardAnimation'
                        excludeFirstCard = True
                
                self.setDealerPositions(initialLen, excludeFirstCard)
                
               
        # TODO - for the future - write one function for both player and dealer cards, no repetitions
        def setDealerPositions(self, initialLen, excludeFirstCard):
            totalLen = self.dealerCardsLength()
            for j, card in enumerate(self.dealerCards):
                if j == 0 and excludeFirstCard:
                    continue
                if j + 1 > initialLen:
                    card.setPosition((self.ui.s(395), self.ui.s(10)))
                card.setTarget(self.dealerPositions[totalLen - 1][j])
            
        def addPlayerCard(self, card: Card):
            self.playerCards.append(card)
            self.playerCardNames.append(card.name)
        def addDealerCard(self, card: Card, append=True):
            self.dealerCards.append(card)
            if append:
                self.dealerCardNames.append(card.name)
        def removeDealerCards(self):
            self.dealerCards = []
            self.dealerCardNames = []
        def removePlayerCards(self):
            self.playerCards = []
            self.playerCardNames = []
        def removeCards(self):
            self.removeDealerCards()
            self.removePlayerCards()
            self.dealerCardNames = []
            self.playerCardNames = []
        def playerCardsLength(self):
            return len(self.playerCardNames)
        def dealerCardsLength(self):
            return len(self.dealerCardNames)
        
        def blit(self, dt):
            for card in self.dealerCards + self.playerCards:
                card.update(dt)
                card.blit()
           
    class Shoe:
        def __init__(self, position: tuple, length: int, ui):
            self.position = position
            self.len = length
            self.cards = [
                UI.Card(
                    position=(position[0], position[1]-i*5), 
                    target=(position[0], position[1]-i*5), 
                    name='back_red', img='back_red', ui=ui
                ) 
                for i in range(self.len)
            ]
        
        def setLen(self, len: int):
            self.len = len

        def blit(self):
            for card in self.cards:
                card.blit()
                
    class Button:
        def __init__(self, buttonType, position, ui):
            self.buttonType = buttonType
            self.width = 0
            self.ui = ui
            with Image.open(f'assets/sprites/buttons/{buttonType}.png') as img:
                self.width = img.width / img.height * 55
            self.button = pygame.image.load(f'assets/sprites/buttons/{buttonType}.png').convert_alpha()
            self.button = pygame.transform.smoothscale(self.button, (self.ui.s(self.width), self.ui.s(55)))
            self.rect = self.button.get_rect(topleft=position)
        
        def blit(self):
            self.ui.screen.blit(self.button, self.rect)
        
    # Multiply the value 1-500 to the calculated scale
    def s(self, val: int):
        return int(round(val * self.scale))
    
    # Render the UI wrapper function
    def render(self, dt):
        self.screen.blit(self.background, (0, 0))
        self.shoe.blit()
        
        if self.game.status not in ['waiting', 'dealerTurn', 'dealAnimation', 'finishAnimation']:
            self.hitButton.blit()
        
        if self.game.status not in ['waiting', 'dealerTurn', 'finishAnimation', 'dealAnimation']:
            self.standButton.blit()
            
        if self.game.status in ['waiting']:
            self.startButton.blit()
            self.statsButton.blit()
        if self.game.status == 'betting':
            self.bettingChips.update(dt)
      
        self.texts.render()
        self.cards.update(dt, self.game.dealerHand.cards, self.game.playerHand.cards, self.game.dealerHand.firstCardHidden)
        self.chips.update(dt)
        
        pygame.display.flip()

game = Game()
game.run()