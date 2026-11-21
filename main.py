import pygame
import sys
import ctypes
import random
import time
from PIL import Image

suits = ['H', 'D', 'S', 'C']
cardValues = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 
            #   'J': 10, 'Q': 10, 'K': 10, 
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
            self.clock.tick(30)
            
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
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # TODO - review this logic and move it to a separate function, too much indentation
                    if self.ui.standRect != None and self.ui.hitRect.collidepoint(event.pos):
                        self.handleHit()
                    if self.ui.standRect != None and self.ui.standRect.collidepoint(event.pos):
                        self.handleStand()
                    if self.ui.startRect != None and self.ui.startRect.collidepoint(event.pos):
                        self.handleHit()
                    
            
            self.ui.render()
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
        print(f'Hand bet: {self.handBet}')
        self.dealerHand = Hand([self.shoe.dealCard(), self.shoe.dealCard()], firstCardHidden=True)
        print(f'Dealer card: {self.dealerHand.cards[0]} total {self.dealerHand.total}')
        self.status = 'playerTurn'
        self.playerHand = Hand([self.shoe.dealCard(), self.shoe.dealCard()])
        
        print(f'Dealt cards: {self.playerHand} total {self.playerHand.total}')
    
    def hit(self):
        assert self.status == 'playerTurn'
        self.status = 'hitAnimation'
        self.timer = time.time()
            
    def stand(self):
        assert self.status == 'playerTurn'
        self.status = 'dealerTurn'
        self.dealerHand.revealCard()
        self.ui.render()
  
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
                pass
        self.status = 'waiting'
        
    def finishRound(self, condition: str):
        self.payoutWinnings(self.handBet, condition)
        self.status = 'finishAnimation'
        self.timer = time.time()
        
    
    def checkGameStatus(self):
        playerTotal = self.playerHand.total
        dealerTotal = self.dealerHand.total
        
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
    
    def render(self):
        newTexts = self.texts.copy()
        # TODO - make this system dynamic somehow, similar to the UI.texts
        if game.status != 'waiting':
            newTexts.append(Texts.Text(str(game.playerHand.total), self.ui.fonts.fontBold, (255, 255, 255), self.ui.width / 2 + self.ui.s(23), self.ui.s(242)))
            newTexts.append(Texts.Text(str(game.dealerHand.total), self.ui.fonts.fontBold, (255, 255, 255), self.ui.width / 2 + self.ui.s(43), self.ui.s(35)))
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
        self.Shoe = UI.Shoe((self.s(395), self.s(30)), len=4, ui=self)
        self.Cards = UI.Cards(self, [], [])
    
    class Chip:
        def __init__(self, val: int, position: tuple, ui):
            vals = {10: 'green', 20: 'blue', 50: 'yellow', 100: 'red'}
            self.position = position
            self.ui = ui
            self.val = val
            self.obj = pygame.image.load(f'assets/sprites/chips/{vals[val]}.png')
            self.obj = pygame.transform.smoothscale(self.obj, (ui.s(75), ui.s(75)))
            pass
        
        def blit(self):
            self.ui.screen.blit(self.obj, self.position)
        
    class Card:
        def __init__(self, position: tuple, name: str, ui):
            self.position = position
            self.obj = pygame.image.load(f'assets/sprites/cards/{name}.png')
            self.obj = pygame.transform.smoothscale(self.obj, (ui.s(90), ui.s(120)))
            self.ui = ui
            
        def setPosition(self, position: tuple):
            self.position = position
            
        def blit(self):
            self.ui.screen.blit(self.obj, self.position)
            
    class Cards:
        def __init__(self, ui, playerCards: list[Card] = [], dealerCards: list[Card] = []):
            self.playerCards = playerCards
            self.dealerCards = dealerCards
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
            
        def addPlayerCards(self, cards: list[str]):
            for c in cards:
                card = UI.Card((0, 0), name=c, ui=self.ui)
                self.addPlayerCard(card)
                totalLen = self.playerCardsLength()
                for i, card in enumerate(self.playerCards):
                    card.setPosition(self.playerPositions[totalLen - 1][i])
                        
        def addDealerCards(self, cards: list[str]):
            for c in cards:
                card = UI.Card((0, 0), name=c, ui=self.ui)
                self.addDealerCard(card)
                totalLen = self.dealerCardsLength()
                for i, card in enumerate(self.dealerCards):
                    card.setPosition(self.dealerPositions[totalLen - 1][i])
            
        def addPlayerCard(self, card: Card):
            self.playerCards.append(card)
        def addDealerCard(self, card: Card):
            self.dealerCards.append(card)
        def removeDealerCards(self):
            self.dealerCards = []
        def removePlayerCards(self):
            self.playerCards = []
        def removeCards(self):
            self.removeDealerCards()
            self.removePlayerCards()
        def playerCardsLength(self):
            return len(self.playerCards)
        def dealerCardsLength(self):
            return len(self.dealerCards)
        
        def blit(self):
            for card in self.dealerCards + self.playerCards:
                card.blit()
           
    class Shoe:
        def __init__(self, position: tuple, len: int, ui):
            self.position = position
            self.len = len
            self.cards = [UI.Card((position[0], position[1]-i*5), name='back_red', ui=ui) for i in range(self.len)]
        
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
            self.button = pygame.image.load(f'assets/sprites/buttons/{buttonType}.png')
            self.button = pygame.transform.smoothscale(self.button, (self.ui.s(self.width), self.ui.s(55)))
            self.rect = self.button.get_rect(topleft=position)
        
        def blit(self):
            self.ui.screen.blit(self.button, self.rect)
        
    # Multiply the value 1-500 to the calculated scale
    def s(self, val: int):
        return int(round(val * self.scale))
    
    # Render the UI wrapper function
    def render(self):
        self.screen.blit(self.background, (0, +0))

        chip = self.Chip(val=10, position=(self.s(50), self.s(195)), ui=self)
        chip.blit()
        
        self.Shoe.blit()
        
        if len(self.game.playerHand.cards) > 0:
            self.Cards.removePlayerCards()
            self.Cards.addPlayerCards(self.game.playerHand.cards)
        
        dealerCards = self.game.dealerHand.cards.copy()
        if len(dealerCards) > 0:
            self.Cards.removeDealerCards()
            if self.game.dealerHand.firstCardHidden:
                dealerCards[0] = 'back_red'
            self.Cards.addDealerCards(dealerCards)
        
        self.Cards.blit()
        
        if self.game.status not in ['waiting', 'dealerTurn', 'dealAnimation', 'finishAnimation']:
            hitButton = UI.Button('hit', (self.width / 2 + self.s(10), self.s(432)), ui=self)
            self.hitRect = hitButton.rect
            hitButton.blit()
        
        if self.game.status not in ['waiting', 'dealerTurn', 'finishAnimation', 'dealAnimation']:
            standButton = UI.Button('stand', (self.width / 2 - self.s(87), self.s(432)), ui=self)
            self.standRect = standButton.rect
            standButton.blit()
            
        if self.game.status in ['waiting']:
            startButton = UI.Button('start', (self.width / 2 - self.s(40), self.s(432)), ui=self)
            self.startRect = startButton.rect
            startButton.blit()
            
            statsButton = UI.Button('stats', (self.s(390), self.s(432)), ui=self)
            self.statsRect = statsButton.rect
            statsButton.blit()
           
        self.texts.render()
        pygame.display.flip()

game = Game()
game.run()
