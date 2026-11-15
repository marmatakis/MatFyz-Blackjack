import pygame
import sys
import ctypes
import random

pygame.init()
pygame.display.set_caption('MatFyz Blackjack')
icon = pygame.image.load('assets/images/card.png')
pygame.display.set_icon(icon)


if sys.platform == 'win32':
    # change the taskbar icon from pygame by changing app id
    myappid = 'marmatakis.matfyzblackjack.0.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass

width, height = 500, 500
screen = pygame.display.set_mode((width, height))
background = pygame.image.load('assets/sprites/table.jpg').convert()
background = pygame.transform.scale(background, (width, height))

fontRegular = pygame.font.Font('assets/fonts/Unbounded-Regular.ttf', 16)
fontSemiBold = pygame.font.Font('assets/fonts/Unbounded-SemiBold.ttf', 25)
fontBold = pygame.font.Font('assets/fonts/Unbounded-Bold.ttf', 28)

testText = fontSemiBold.render(
    '900$',
    True,
    (237, 218, 53)
)
testTextSurface = testText.get_rect(
    centerx=width / 2,
    top=455
)

# dealer's texts
dealerCountText = fontBold.render(
    '18',
    True,
    (255, 255, 255)
)
dealerCountTextSurface = dealerCountText.get_rect(
    centerx=width / 2,
    top=50
)
dealerText = fontRegular.render(
    'DEALER',
    True,
    (255, 255, 255)
)
dealerTextSurface = dealerText.get_rect(
    centerx=width / 2 - 72,
    top=54
)

# player's texts
playerCountText = fontBold.render(
    '9', 
    True, 
    (255, 255, 255)
)
playerCountTextSurface = playerCountText.get_rect(
    centerx = width / 2,
    top = 270
)
playerText = fontRegular.render(
    'YOU',
    True,
    (255, 255, 255)
)
playerTextSurface = playerText.get_rect(
    centerx = (width / 2) - 46,
    top = 274
)

suits = ['H', 'D', 'S', 'C']
cardValues = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': -1}

class Card:
    def __init__(self, name: str):
        self.value = cardValues[name[1:]]
        self.name = name

class Hand:
    def __init__(self, cards: list[Card]):
        self.cards = cards
        self.total = 0
        self.setTotal()
        
    def addCard(self, card: Card):
        self.cards.append(card)
        self.setTotal()
            
    def setTotal(self):
        self.total = 0
        aces = 0
        for card in self.cards:
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
    
class Game:
    def __init__(self):
        self.status = 'waiting'
        self.balance = 1000
        self.shoe = Shoe(6)
        self.dealerHand = Hand(cards=[])
        self.playerHand = Hand(cards=[])
        self.handBet = 0
        
    def overrideBalance(self, amount: int):
        self.balance = amount
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
        
        self.status = 'playerTurn'
        self.playerHand = Hand([self.shoe.dealCard(), self.shoe.dealCard()])
        handCards = self.playerHand.cards
        
        print(f'Dealt cards: {cardsString(self.playerHand)}total {self.playerHand.total}')
    
    def hit(self):
        assert self.status == 'playerTurn'
        newCard = self.shoe.dealCard()
        self.playerHand.addCard(newCard)
        print(f'Dealt cards: {cardsString(self.playerHand)}total {self.playerHand.total}')
        if self.playerHand.total <= 21:
            return
        
        self.checkGameStatus()
            
    def stand(self):
        assert self.status == 'playerTurn'
        self.status = 'dealerTurn'
        if not self.checkGameStatus():
            return
        self.dealerHand = Hand([self.shoe.dealCard(), self.shoe.dealCard()])
        print(f'Dealer cards: {cardsString(self.dealerHand)}total {self.dealerHand.total}')
        while self.dealerHand.total <= 16:
            self.dealerHand.addCard(self.shoe.dealCard())
            print(f'Dealer cards: {cardsString(self.dealerHand)}total {self.dealerHand.total}')
        self.checkGameStatus()
    
    def payoutWinnings(self, bet: int, condition: str):
        self.status = 'payout'
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
        
    def finishRound(self, condition):
        self.payoutWinnings(self.handBet, condition)
        self.status = 'waiting'
    
    def checkGameStatus(self):
        playerTotal = self.playerHand.total
        dealerTotal = self.dealerHand.total
        
        if dealerTotal != 0:
            print(f'player {playerTotal} dealer {dealerTotal}')
        
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
    
def cardsString(hand: Hand):
    s = ""
    for card in hand.cards:
        s += card.name + " "
    return s

game = Game()
print(f'Your balance: {game.balance}')
while game.balance > 0:
    s = input("---- Start new round? (h) ")
    if s != "h":
        exit()
    game.startRound()
    game.setHandBet(100)
    game.playerTurn()
    
    while game.status == 'playerTurn' and game.playerHand.total <= 21:
        move = input("Enter move (h/s): ")
        if move == "h":
            game.hit()
        else:
            game.stand()


clock = pygame.time.Clock()

running = True
while running:
    clock.tick(30)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(background, (0, 0))
    screen.blit(testText, testTextSurface)
    
    screen.blit(dealerCountText, dealerCountTextSurface)
    screen.blit(dealerText, dealerTextSurface)
    
    screen.blit(playerCountText, playerCountTextSurface)
    screen.blit(playerText, playerTextSurface)
    
    pygame.display.flip()
    
pygame.quit()