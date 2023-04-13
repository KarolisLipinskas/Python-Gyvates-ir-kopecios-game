from math import ceil, degrees, sqrt, atan
from random import randint
from time import sleep
from pyllist import dllist
import json
import pygame
from pygame.locals import (KEYDOWN, K_ESCAPE, K_RETURN, K_SPACE, K_UP, K_DOWN, K_RIGHT, K_LEFT, K_a, K_d, K_c, K_x)

# numeriu teksturos
class Number_sprite(pygame.sprite.Sprite):
    def __init__(self, nr):
        super(Number_sprite, self).__init__()
        self.surf = pygame.image.load("./Sprites/Nr" + str(nr) + ".png")

# menu teksturos
class Menu_stuff(pygame.sprite.Sprite):
    def __init__(self, name):
        self.surf = pygame.image.load("./Sprites/" + name + ".png")

# snake'u ir ladder'iu teksturos
class Connect_tex():
    def __init__(self, surf, posX, posY):
        self.surf = surf
        self.posX = posX
        self.posY = posY
        self.absolutePosY = posY

# player'io klase
class Player(pygame.sprite.Sprite):
    def __init__(self, nr):
        super(Player, self).__init__()
        self.surf = pygame.image.load("./Sprites/Player" + str(nr) + ".png")
        self.nr = nr-1
        self.pos = 1

# langelio klase
class Tile:
    def __init__(self, nr):
        self.nr = nr
        self.ladder = None
        self.snake = None
        self.players = [False, False, False]
        self.sprite = pygame.image.load("./Sprites/Tile.png")
        self.posX = 0
        self.posY = 0
        self.absolutePosY = 0

    def changeNr(self, nr):
        self.nr = nr

    def removePlayer(self, nr):
        self.players[nr] = False
    
    def addPlayer(self, nr):
        self.players[nr] = True

    def addLadder(self, nr_ptr):
        self.ladder = nr_ptr

    def removeLadder(self):
        self.ladder = None

    def addSnake(self, nr_ptr):
        self.snake = nr_ptr

    def removeSnake(self):
        self.snake = None
       
# lentos sukurimas is json failo pavadinimu (board.json)
def createBoard(board):
    data = json.load(open("Board.json"))

    ladder = {}      # laikinas ladders map'as
    snake = {}       # laikinas snake map'as
    for i in data["Tiles"]:
        if i["connect"] != 0: 
            if i["connect"] > i["nr"]: ladder[i["nr"]-1] = i["connect"]-1   # prideda ladder'i (ladder[is kur] = i kur)
            else: snake[i["nr"]-1] = i["connect"]-1                         # prideda snake'a (snake[is kur] = i kur)
        if(board.last == None): st = 0
        else: st = board.last.value.nr
        if(st + 1 < i["nr"]):                  # automatiskai uzpildo praleistus tile'us
            for j in range(st + 1, i["nr"]):
                board.append(Tile(j))
        else: board.append(Tile(i["nr"]))      # prideda tile'a prie board list'o   

    st = 0
    if(board.first != None):
        st = board.last.value.nr
    for i in range(st, data["Auto"]-1):   # automatiskai uzpildo tile'us iki nustatyto auto skaiciaus
        board.append(Tile(i + 1))

    if(board.first == None): return     # jei board list'as tuscias grizta
    board.append(Tile(board.last.value.nr+1))
    cur = board.first
    st = 0
    for i in ladder:            # prideda ladder'ius i board list'a
        if(ladder[i]>board.size - 1):
            for j in range(board.size + 1, ladder[i] + 2): board.append(Tile(j))
        for j in range(st, i):
            cur = cur.next
        st = i
        temp = cur
        for j in range(ladder[i]-i):
            temp = temp.next
        cur.value.addLadder(temp)

    cur = board.first
    st = 0
    for i in snake:             #prideda snake'us i board list'a
        for j in range(st, i):
            cur = cur.next
        st = i
        temp = cur
        for j in range(i-snake[i]):
            temp = temp.prev
        cur.value.addSnake(temp)

# Player'iu pasirinkimo langas
def createPlayers(screen, board, players):
    p = {1: False, 2: False, 3: False}

    #----------- player select menu texturos ir pradinis display'inimas ----------------
    p_menu = []
    p_menu.append(Menu_stuff("Player1"))
    p_menu.append(Menu_stuff("Player2"))
    p_menu.append(Menu_stuff("Player3"))
    p_menu.append(Menu_stuff("Start"))
    p_menu.append(Menu_stuff("Exit"))
    p_menu.append(Menu_stuff("Highlight"))
    p_menu.append(Menu_stuff("Highlight"))
    p_menu.append(Menu_stuff("Check"))
    p_menu[6].surf = pygame.transform.scale(p_menu[6].surf, (300, 75))
    p_menu[0].surf = pygame.transform.scale(p_menu[0].surf, (75, 75))
    p_menu[1].surf = pygame.transform.scale(p_menu[1].surf, (75, 75))
    p_menu[2].surf = pygame.transform.scale(p_menu[2].surf, (75, 75))
    black_box = pygame.Surface((75,75))
    black_box.fill((0,0,0))

    screen.fill((0, 0, 0))
    pygame.display.flip()
                                                    # p_menu[0] == pirmas player
    screen.blit(p_menu[0].surf, (300, 300))         # p_menu[1] == antras player
    screen.blit(p_menu[1].surf, (575, 300))         # p_menu[2] == trecias player
    screen.blit(p_menu[2].surf, (850, 300))         # p_menu[3] == Start mygtukas
    screen.blit(p_menu[3].surf, (500, 500))         # p_menu[4] == Exit mygtukas
    screen.blit(p_menu[4].surf, (500, 700))         # p_menu[5] == Highlight aplink players
    screen.blit(p_menu[5].surf, (300, 300))         # p_menu[6] == Highlight aplink Start ir Exit mygtukus
    pygame.display.flip()                           # p_menu[7] == Zalia varnele

    #----------- Menu navigavimas ir texturu display'inimas ----------
    row = 1
    col = 1
    selecting = True
    while selecting:
        for event in pygame.event.get():
            if(event.type == pygame.KEYDOWN):
                if(event.key == K_ESCAPE): return 1
                elif(event.key == K_RETURN or event.key == K_SPACE):
                    if(row == 1):                                                     #toggle'ina player'i
                        p[col] = not p[col]
                        if(p[col]): screen.blit(p_menu[7].surf, (312 + (col-1)*275, 312))
                        else:
                            screen.blit(black_box, (300 + (col-1)*275, 300))
                            screen.blit(p_menu[col-1].surf, (300 + (col-1)*275, 300))
                            screen.blit(p_menu[5].surf, (300 + (col-1)*275, 300))
                    elif(row == 2 and (p[1] or p[2] or p[3])): selecting = False      #paspaudzia Start (veikia jei pasirintas bent 1 player)
                    elif(row == 3): return 1                                          #paspaudzia Exit
                elif(event.key == K_UP):                        #naviguoja i virsu
                    if(row == 2): 
                        screen.blit(p_menu[3].surf, (500, 500))
                        screen.blit(p_menu[5].surf, (300 + (col-1)*275, 300))
                        row = 1
                    elif(row == 3): 
                        screen.blit(p_menu[4].surf, (500, 700))
                        screen.blit(p_menu[6].surf, (500, 500))
                        row = 2
                    else: 
                        screen.blit(black_box, (300 + (col-1)*275, 300))
                        screen.blit(p_menu[col-1].surf, (300 + (col-1)*275, 300))
                        if(p[col]): screen.blit(p_menu[7].surf, (312 + (col-1)*275, 312))
                        screen.blit(p_menu[6].surf, (500, 700))
                        row = 3
                elif(event.key == K_DOWN):                      #naviguoja i apacia
                    if(row == 1): 
                        screen.blit(black_box, (300 + (col-1)*275, 300))
                        screen.blit(p_menu[col-1].surf, (300 + (col-1)*275, 300))
                        if(p[col]): screen.blit(p_menu[7].surf, (312 + (col-1)*275, 312))
                        screen.blit(p_menu[6].surf, (500, 500))
                        row = 2
                    elif(row == 2):
                        screen.blit(p_menu[3].surf, (500, 500))
                        screen.blit(p_menu[6].surf, (500, 700))
                        row = 3
                    else: 
                        screen.blit(p_menu[4].surf, (500, 700))
                        screen.blit(p_menu[5].surf, (300 + (col-1)*275, 300))
                        row = 1
                elif(event.key == K_RIGHT and row == 1):        #naviguoja i desine (jei highlight yra ant player'iu)
                    screen.blit(black_box, (300 + (col-1)*275, 300))
                    screen.blit(p_menu[col-1].surf, (300 + (col-1)*275, 300))
                    if(p[col]): screen.blit(p_menu[7].surf, (312 + (col-1)*275, 312))
                    if(col != 3): col += 1
                    else: col = 1
                    screen.blit(p_menu[5].surf, (300 + (col-1)*275, 300))
                elif(event.key == K_LEFT and row == 1):        #naviguoja i kaire (jei highlight yra ant player'iu)
                    screen.blit(black_box, (300 + (col-1)*275, 300))
                    screen.blit(p_menu[col-1].surf, (300 + (col-1)*275, 300))
                    if(p[col]): screen.blit(p_menu[7].surf, (312 + (col-1)*275, 312))
                    if(col != 1): col -= 1
                    else: col = 3
                    screen.blit(p_menu[5].surf, (300 + (col-1)*275, 300))
                pygame.display.flip()
            if(event.type == pygame.QUIT): return 0       #uzdaro pygame langa

    for i in p:            #uzpildo players masyva ir pastato player'ius i pirma langeli
        if(p[i]): 
            board.first.value.addPlayer(i-1)
            players.append(Player(i))
    return 2

# pajudina player'i atitinkama kieki langeliu
def movePlayer(screen, cur, players, turn, Nr, connTex, board, winners, dice):
    move = Roll(screen, dice)                   # gaunamas random langeliu pajudejimo skaicius
    start = players[turn].pos
    end = start + move

    nr = players[turn].nr
    for i in range(start, end):                 # player'is juda atitinkama kieki langeliu
        cur.value.removePlayer(nr)
        if(cur.next == None):                           # pachek'ina ar pasieke finisa
            return Win(screen, turn, winners, players)
        cur.next.value.addPlayer(nr)
        players[turn].pos = i + 1
        Update_board(screen, cur, players, Nr, connTex) # display'ina player'io pozicijos pasikeitima
        cur = cur.next
        sleep(0.2)

    if(cur.value.ladder != None):                       #uzkyla ladder'iu
        cur.value.removePlayer(nr)
        cur.value.ladder.value.addPlayer(nr)
        players[turn].pos = cur.value.ladder.value.nr
        cur = cur.value.ladder
        sleep(0.3)
        Change(screen, players, Nr, connTex, cur, board, True)   # display'ina visa lenta (100 langeliu) taip, kad playeris butu per viduri
    elif(cur.value.snake != None):                      #nuciuozia snake'u
        cur.value.removePlayer(nr)
        cur.value.snake.value.addPlayer(nr)
        players[turn].pos = cur.value.snake.value.nr
        cur = cur.value.snake
        sleep(0.3)
        Change(screen, players, Nr, connTex, cur, board, True)

    if(cur.next == None):                               # pachek'ina ar pasieke finisa
        return Win(screen, turn, winners, players)

    sleep(1)
    return turn    # grazina kuris player'is katik paeijo

# papildo winners masyva ir i atitinkama vieta display'ina zaidima pabaigusi player'i
def Win(screen, turn, winners, players):
    winners.append(players[turn])
    if(len(winners) == 1): screen.blit(winners[0].surf, (1190, 624))
    elif(len(winners) == 2): screen.blit(winners[1].surf, (990, 736))
    else: screen.blit(winners[2].surf, (1190, 736))
    players.pop(turn)
    turn -= 1
    return turn 

# kauliuko sukimosi animacija ir random reiksmes pasirinkimas
def Roll(screen, dice):
    t = 0.05
    nr = 0
    for i in range(5):
        temp = nr
        nr = randint(1, 6)
        while(nr == temp): nr = randint(1, 6)
        screen.blit(dice[nr-1], (950, 200))
        pygame.display.flip()
        sleep(t)
        t = t*2
    sleep(1)
    return nr    # grazina random reiksme (1-6)

# display'ina visa lenta (100 langeliu) taip, kad playeris butu per viduri
def Change(screen, players, Nr, connTex, cur, board, up):
    if(board.size == 0): return Display_board(screen, None, None, None, None)  # jei board list'as tuscias

    sk = ceil(cur.value.nr/10)                     # gaunamas player'io eilutes numeris
    e = ceil(board.last.value.nr / 10)             # gaunamas paskutines eilutes numeris
    if(sk <= 5 or (sk < 10 and e < 10)): sk = 0    # pradzia bus nuo list'o prazios
    elif(sk >= e-4): sk = e - 10                   # pradzia bus 10 eiluciu nuo listo pabaigos
    elif(up): sk -= 5                              # pradzia bus player'io eilutes nr - 5
    else: sk -= 6                                  # pradzia bus player'io eilutes nr - 6

    Change_pos(board.first, sk, connTex)  # pakeicia ekrane matomu langeliu koordinatas
    temp = cur
    sk = sk * 10 + 1                      # gaunamas pradzios langelio numeris
    while(temp.value.nr != sk):           # nukeliauja list'u iki pradzios langelio
        if(temp.value.nr < sk): temp = temp.next
        else: temp = temp.prev
    Display_board(screen, temp, players, Nr, connTex)

# atitinkamai pakeicia board list'o langeliu koordinates kad tinkami matytusi ekrane
def Change_pos(cur, sk, connTex):
    while(cur != None):
        cur.value.posY = cur.value.absolutePosY + 75 * sk
        cur = cur.next

    for i in connTex:    # atitinkamai pakeicia ladder'iu ir snake'u teksturu koordinates
        i.posY = i.absolutePosY + 75 * sk

# istrina player'ius is board list'o
def resetBoard(board):
    cur = board.first
    while(cur != None):
        for i in range(3):
            cur.value.players[i] = False
        cur = cur.next

# setup'ina board list'o langeliu koordinates ir ladder'iu ir snake'u teksturas
def Game_board(board, connTex):
    startX = 75
    endX = 750
    posX = startX
    posY = 750
    mode = True

        #setup'ina board list'o koordinates
    temp = board.first
    while(temp != None):
        temp.value.posX = posX
        temp.value.posY = posY
        temp.value.absolutePosY = posY
        if(mode):
            if(posX == endX): 
                posY -= 75
                mode = False
            else: posX += 75
        else:
            if(posX == startX):
                posY -= 75
                mode = True
            else: posX -= 75
        temp = temp.next

        #setup'ina snake'u and ladder'iu texturas ir ju koordinates
    connTex.clear()
    ltex = pygame.image.load("./Sprites/Ladder.png")
    stex = pygame.image.load("./Sprites/Snake.png")
    temp = board.first
    while(temp != None):
        if(temp.value.ladder != None):
            xpos = temp.value.posX + 35
            ypos = temp.value.ladder.value.posY + 35
            st1 = temp.value.ladder.value.posX - temp.value.posX     # horizontalus statinis 
            st2 = temp.value.ladder.value.posY - temp.value.posY     # vertikalus statinis
            c = sqrt(st1*st1 + st2*st2)                              # izambine
            temptex = pygame.transform.scale(ltex, (45, c))          # atitinkamai pakeiciamas ladder'io ilgis
            if(st2 != 0):
                if(st1 == 0): xpos = xpos -22
                angle = atan(abs(st1)/st2)
                angle = degrees(angle)
                if(st1 < 0): 
                    angle = angle * -1
                    xpos = temp.value.ladder.value.posX + 35
                temptex = pygame.transform.rotate(temptex, angle)    # pasukamas ladderis apskaiciutu kampu
            elif(st1 < 0):
                xpos = temp.value.ladder.value.posX + 37
                ypos = temp.value.posY + 15
                temptex = pygame.transform.rotate(temptex, 90)       # pasukamas ladderis horizontaliai i kaire
            else:
                ypos = temp.value.posY + 15
                temptex = pygame.transform.rotate(temptex, -90)      # pasukamas ladderis horizontaliai i desine
            connTex.append(Connect_tex(temptex, xpos, ypos))         # pridedama ladder'io textura i masyvo gala
        elif(temp.value.snake != None):
            xpos = temp.value.posX + 35
            ypos = temp.value.posY + 35
            st1 = temp.value.snake.value.posX - temp.value.posX      # statinis
            st2 = temp.value.posY - temp.value.snake.value.posY      # statinis
            c = sqrt(st1*st1 + st2*st2)                              # izambinis
            temptex = pygame.transform.scale(stex, (45, c))          # snake'o ilgis
            if(st2 != 0):
                angle = atan(abs(st1)/st2)
                angle = degrees(angle)
                if(st1 == 0): xpos = xpos -22
                elif(st1 < 0): xpos = temp.value.snake.value.posX + 35
                else: angle = angle * -1
                temptex = pygame.transform.rotate(temptex, angle)    # pasukama
            elif(st1 < 0):
                xpos = temp.value.snake.value.posX + 35
                ypos = temp.value.posY + 15
                temptex = pygame.transform.rotate(temptex, -90)      # pasukama horizontaliai i kaire
            else:
                ypos = temp.value.posY + 15
                temptex = pygame.transform.rotate(temptex, 90)       # pasukama horizontaliai i kaire
            connTex.insert(0, Connect_tex(temptex, xpos, ypos))      # pridedama snake'o textura i masyvo pradzia
        temp = temp.next

# display'ina pajudejusi player'i ir visus ladder'ius ir snake'us
def Update_board(screen, cur, players, Nr, connTex):
            # uzdengia buvusioj vietoj player'i
    screen.blit(cur.value.sprite, (cur.value.posX, cur.value.posY))
    nrPos = cur.value.posX + 72 - (len(str(cur.value.nr)) * 9)
    for sk in str(cur.value.nr):
        screen.blit(Nr[int(sk)].surf, (nrPos, cur.value.posY + 2))
        nrPos += 9

    finish = pygame.image.load("./Sprites/Finish.png")
    temp = cur
    while(temp.next != None): temp = temp.next
    screen.blit(finish, (temp.value.posX, temp.value.posY))  # display'ina finisa

    for i in connTex:                          # display'ina visus ladders ir snakes
        screen.blit(i.surf, (i.posX, i.posY))

    temp = cur
    for i in players:                          # display'ina visus players
        while(temp.value.nr != i.pos):
            if(temp.value.nr < i.pos): temp = temp.next
            else: temp = temp.prev
        screen.blit(i.surf, (temp.value.posX + 15, temp.value.posY + 15))

    border = pygame.image.load("./Sprites/BoardBorder.png")
    screen.blit(border, (0, 0))                # displainia lentos border'i
    pygame.display.flip()

# display'ina visa lenta (100 langeliu)
def Display_board(screen, cur, players, nr, connTex):
    black_box = pygame.Surface((750,750))
    black_box.fill((0,0,0))
    screen.blit(black_box, (75, 75))
    if(cur == None): return  # jei board list'as tuscias display'ina jouda kvadrata ir grizta
    finish = pygame.image.load("./Sprites/Finish.png")

    temp = cur
    end = cur.value.nr + 100
    while(cur != None and cur.value.nr != end):            # display'ina visus tile's
        screen.blit(cur.value.sprite, (cur.value.posX, cur.value.posY))
        nrPos = cur.value.posX + 72 - (len(str(cur.value.nr)) * 9)
        for sk in str(cur.value.nr): 
            screen.blit(nr[int(sk)].surf, (nrPos, cur.value.posY + 2))
            nrPos += 9
        fin = cur
        cur = cur.next

    while(fin.next != None): fin = fin.next
    screen.blit(finish, (fin.value.posX, fin.value.posY))   # display'ina finisa

    for i in connTex:                       # display'ina visus ladder'ius ir snake'us
        screen.blit(i.surf, (i.posX, i.posY))

    for i in players:                       # display'ina visus player'ius
        while(temp.value.nr != i.pos):
            if(temp.value.nr < i.pos): temp = temp.next
            else: temp = temp.prev
        screen.blit(i.surf, (temp.value.posX + 15, temp.value.posY + 15))

    border = pygame.image.load("./Sprites/BoardBorder.png")
    screen.blit(border, (0, 0))             # displainia lentos border'i
    pygame.display.flip()

# startinamas zaidimas ir vartotojas numetamas i player'iu pasirinkimo langa
def Game(board, screen, nr, connTex):
    if(board.size == 0): return True  # jei board list'as tuscias grista i main meniu (startuoti neleidzia)

    resetBoard(board)    # jei startuoja ne pirma karta istrinami playeriai
    players = []
    a = createPlayers(screen, board, players)  # sukuriami player'iai
    if(a==0): return False   # jei uzdare pygame langa
    elif(a==1): return True  # jei paspaude Exit

    screen.fill((0, 0, 0))
    diceborder = pygame.image.load("./Sprites/DiceBorder.png")
    screen.blit(diceborder, (850, 0))   # display'inamas border'is aplink kauliuka
    dice = []
    for i in range(6):                  # uzpildomas kauliuko teksturu masyvas
        dice.append(pygame.image.load("./Sprites/Dice" + str(i+1) + ".png"))
    screen.blit(dice[0], (950, 200))    # display'inamas 1 akutes kauliukas
    screen.blit(players[0].surf, (1105, 108)) # display'inama pirmo player'io eile
    pygame.display.flip()
    resPl = pygame.Surface((45, 45))
    resPl.fill((156, 156, 156))

    winners = []
    psize = len(players)
    for i in range(psize):              # display'inamos viso galimos pozicijos (winner, 2nd, 3rd)
        pedast = pygame.image.load("./Sprites/Pedastal" + str(i+1) + ".png")
        if(i == 0): screen.blit(pedast, (888, 607))
        elif(i == 1): screen.blit(pedast, (888, 719))
        else: screen.blit(pedast, (1088, 719))

    cur = board.first
    Change(screen, players, nr, connTex, cur, board, True) # display'inama visa lenta (100 langeliu)

    turn = 0        # pirmo player'io eile
    while True:
        for event in pygame.event.get():
            if(event.type == pygame.KEYDOWN):
                if(event.key == K_ESCAPE): return True         # jei paspaude ESC
                elif(event.key == K_RETURN or event.key == K_SPACE):
                    turn = movePlayer(screen, cur, players, turn, nr, connTex, board, winners, dice)  # paeina player'is

                    if(len(winners) == psize):                 # jei visi player'iai finisavo
                        Change(screen, players, nr, connTex, cur, board, True)
                        sleep(5)
                        return True

                    if(turn != len(players)-1): turn += 1         # pakeiciama kieno dabar eile
                    else: turn = 0

                    screen.blit(resPl, (1105, 108))
                    screen.blit(players[turn].surf, (1105, 108))  # eiles pakeitimas matosi vizualiai

                    while(cur.value.nr != players[turn].pos):     # board list'u cur nukeliauja prie kito player'io
                        if(cur.value.nr < players[turn].pos): cur = cur.next
                        else: cur = cur.prev
                    Change(screen, players, nr, connTex, cur, board, True)
            if(event.type == pygame.QUIT): return False

# peskaiciujami langeliu numeriai ir ladder'iu ir snake'u tekturos
def Recalculate(board, connTex, cur, add):
    temp = cur
    while(temp != None):
        temp.value.changeNr(temp.value.nr+add)
        temp = temp.next
    temp = board.first
    while(temp != None):
        if(temp.value.ladder != None and temp.value.ladder.value.nr > cur.value.nr):
            temp.value.addLadder(temp.value.ladder)
        elif(temp.value.snake != None and temp.value.snake.value.nr > cur.value.nr):
            temp.value.addSnake(temp.value.snake)
        temp = temp.next
    Game_board(board, connTex)

# board editor
def Editor(screen, nr, connTex, board):
    # --------- editor teksturos ---------
    e_menu = []
    e_menu.append(Menu_stuff("Add"))
    e_menu.append(Menu_stuff("Remove"))
    e_menu.append(Menu_stuff("AddConnection"))
    e_menu.append(Menu_stuff("RemoveConnection"))
    e_menu.append(Menu_stuff("Remove"))
    e_menu[4].surf = pygame.transform.scale(e_menu[4].surf, (750, 750))

    border = pygame.image.load("./Sprites/BoardBorder.png")
    selection = pygame.image.load("./Sprites/Selection.png")
    screen.blit(border, (0, 0))
    screen.blit(selection, (850, 0))
    pygame.display.flip()
                                                            # e_menu[0] == langelio pridejimo tektura
    cur = board.first                                       # e_menu[1] == langelio istrinimo tektura
    Change(screen, [], nr, connTex, cur, board, True)       # e_menu[2] == ladder'io arba snake'o pridejimo ...
    screen.blit(e_menu[0].surf, (75, 750))                  # e_menu[3] == ladder'io arba snake'o istrinimo ...
    pygame.display.flip()                                   # e_menu[4] == visos lentos istrinimo ...

    # -------- lentos editinimas ---------
    mode = 0   # langelio pridejimas
    con = False
    start = None
    up = True
    while True:
        for event in pygame.event.get():
            if(event.type == KEYDOWN):
                if(event.key == K_ESCAPE): return True   # paspaude ESC
                elif(event.key == K_RETURN or event.key == K_SPACE):
                    if(mode == 0): 
                        if(board.size == 0):                        # jei lenta tuscia prideda pirma langeli
                            board.append(Tile(0))
                            cur = board.first
                        else: board.insert(Tile(cur.value.nr), cur) # kitu atveju prideda langeli pries ten kur stovi
                        Recalculate(board, connTex, cur, 1)
                    elif(mode == 1 and board.size != 0):            # istrina langeli kur stovi
                        temp = board.first
                        while(temp != None):
                            if(temp.value.ladder != None):
                                if(temp.value.ladder.value.nr == cur.value.nr): 
                                   if(cur.prev.value.nr == temp.value.nr): temp.value.removeLadder()
                                   else: temp.value.addLadder(cur.prev)
                            temp = temp.next
                        if(cur.next != None):
                            temp = cur.next
                            board.remove(cur)
                            cur = temp
                            Recalculate(board, connTex, cur, -1)
                            if(cur.prev != None): cur = cur.prev
                        else:
                            temp = cur.prev
                            board.remove(cur)
                            cur = temp
                            Recalculate(board, connTex, cur, 0)
                        if(cur == None): mode = 0
                    elif(mode == 2 and board.size != 0):            # prideda ladder'i arba snake'a
                        if(not con): 
                            con = True
                            start = cur
                        else:
                            con = False
                            if(start.value.nr < cur.value.nr): start.value.addLadder(cur)
                            elif(start.value.nr > cur.value.nr): start.value.addSnake(cur)
                            Recalculate(board, connTex, cur, 0)
                    elif(mode == 3 and board.size != 0):            # istrina ladder'i arba snake'a
                        if(cur.value.ladder != None): cur.value.removeLadder()
                        else: cur.value.removeSnake()
                        Recalculate(board, connTex, cur, 0)
                    elif(mode == 4):                                # istrina visa lenta
                        while(board.size != 0): board.pop()
                        Recalculate(board, connTex, cur, 0)
                        mode = 0
                    Change(screen, [], nr, connTex, cur, board, up)
                    if(board.size == 0): screen.blit(e_menu[mode].surf, (75, 750))
                    else: screen.blit(e_menu[mode].surf, (cur.value.posX, cur.value.posY))

                elif(event.key == K_a and board.size != 0):         # pasirenkamas pridejimo mode
                    con = False
                    mode = 0
                    Change(screen, [], nr, connTex, cur, board, up)
                    screen.blit(e_menu[mode].surf, (cur.value.posX, cur.value.posY))
                elif(event.key == K_d and board.size != 0):         # pasirenkamas istrinimo mode
                    con = False
                    mode = 1
                    Change(screen, [], nr, connTex, cur, board, up)
                    screen.blit(e_menu[mode].surf, (cur.value.posX, cur.value.posY))
                elif(event.key == K_c and board.size != 0):         # pasirenkamas ladder'io arba snake'o pridejimo/istrinimo mode
                    con = False
                    if(cur.value.ladder == None and cur.value.snake == None): mode = 2
                    else: mode = 3
                    Change(screen, [], nr, connTex, cur, board, up)
                    screen.blit(e_menu[mode].surf, (cur.value.posX, cur.value.posY))
                elif(event.key == K_x and board.size != 0):         # pasirenkamas visos lentos istrinimo mode
                    con = False
                    mode = 4
                    Update_board(screen, cur, [], nr, connTex)
                    screen.blit(e_menu[mode].surf, (75, 75))

                elif(event.key == K_UP and mode != 4):              # naviguoja aukstyn
                    up = False
                    temp = cur
                    while(temp.value.posY != cur.value.posY - 75 or temp.value.posX != cur.value.posX):
                        temp = temp.next
                        if(temp == None): break
                    Change(screen, [], nr, connTex, cur, board, True)
                    if(temp != None): cur = temp
                    if(con and start.value.posY <= 750 and start.value.posY >= 0): screen.blit(e_menu[2].surf, (start.value.posX, start.value.posY))
                    screen.blit(e_menu[mode].surf, (cur.value.posX, cur.value.posY))

                elif(event.key == K_DOWN and mode != 4):            # naviguoja zemyn
                    up = True
                    temp = cur
                    while(temp.value.posY != cur.value.posY + 75 or temp.value.posX != cur.value.posX):
                        temp = temp.prev
                        if(temp == None): break
                    Change(screen, [], nr, connTex, cur, board, False)
                    if(temp != None): cur = temp
                    if(con and start.value.posY <= 750 and start.value.posY >= 0): screen.blit(e_menu[2].surf, (start.value.posX, start.value.posY))
                    screen.blit(e_menu[mode].surf, (cur.value.posX, cur.value.posY))

                elif(event.key == K_RIGHT and mode != 4):           # naviguoja i desine
                    if(cur.next != None and cur.value.posX + 75 == cur.next.value.posX):
                        Update_board(screen, cur, [], nr, connTex)
                        cur = cur.next
                    elif(cur.prev != None and cur.value.posX + 75 == cur.prev.value.posX):
                        Update_board(screen, cur, [], nr, connTex)
                        cur = cur.prev
                    if(con and start.value.posY <= 750 and start.value.posY >= 0): screen.blit(e_menu[2].surf, (start.value.posX, start.value.posY))
                    screen.blit(e_menu[mode].surf, (cur.value.posX, cur.value.posY))

                elif(event.key == K_LEFT and mode != 4):            # naviguoja i kaire
                    if(cur.next != None and cur.value.posX - 75 == cur.next.value.posX):
                        Update_board(screen, cur, [], nr, connTex)
                        cur = cur.next
                    elif(cur.prev != None and cur.value.posX - 75 == cur.prev.value.posX):
                        Update_board(screen, cur, [], nr, connTex)
                        cur = cur.prev
                    if(con and start.value.posY <= 750 and start.value.posY >= 0): screen.blit(e_menu[2].surf, (start.value.posX, start.value.posY))
                    screen.blit(e_menu[mode].surf, (cur.value.posX, cur.value.posY))

                # atitinkamai parenkamas pridejimo arba istrinimo mode'as priklauso nuo to ar ten jau yra snake'as arba ladder'is
                if(mode == 2 and (cur.value.ladder != None or cur.value.snake != None)):
                    mode = 3
                    screen.blit(e_menu[mode].surf, (cur.value.posX, cur.value.posY))
                elif(mode == 3 and (cur.value.ladder == None and cur.value.snake == None)): 
                    mode = 2
                    screen.blit(e_menu[mode].surf, (cur.value.posX, cur.value.posY))

                pygame.display.flip()
            if(event.type == pygame.QUIT): return False

# display'inamos main menu teksturos
def mainMenu(screen, menu):
    pygame.display.flip()
    screen.fill((0, 0, 0))
    screen.blit(menu[0].surf, (150, 50))
    screen.blit(menu[1].surf, (500, 500))
    screen.blit(menu[2].surf, (500, 625))
    screen.blit(menu[3].surf, (500, 750))
    menu[4].surf = pygame.transform.scale(menu[4].surf, (300, 75))
    screen.blit(menu[4].surf, (500, 500))
    pygame.display.flip()
    return 0     # grazinama highlight pozicija

#-------------------- M A I N --------------------#
board = dllist()
createBoard(board)   # sukuriama lenta is failo

connTex = []
Game_board(board, connTex)  # setup'ina board ir (ladder ir snake teksturas)

nr = []
for i in range(10):         # uzpildomas numeriu teksturu masyvas
    nr.append(Number_sprite(i))

menu = []
menu.append(Menu_stuff("Title"))            # menu[0] == pavadinimas
menu.append(Menu_stuff("Start"))            # menu[1] == start mygtukas
menu.append(Menu_stuff("Edit"))             # menu[2] == edit mygtukas
menu.append(Menu_stuff("Exit"))             # menu[3] == exit mygtukas
menu.append(Menu_stuff("Highlight"))        # menu[4] == highlight

on = True
state = 0

Width = 1300
Height = 900

pygame.init()
screen = pygame.display.set_mode((Width, Height))
mainMenu(screen, menu)     # display'ina main meniu

# --------- meniu navigavimas ----------
while(on):
    for event in pygame.event.get():
        if(event.type == KEYDOWN):
            if(event.key == K_ESCAPE): on = False
            elif(event.key == K_RETURN or event.key == K_SPACE):
                if(state == 0): 
                    on = Game(board, screen, nr, connTex)
                    if(on): state = mainMenu(screen, menu)
                elif(state == 1): 
                    on = Editor(screen, nr, connTex, board)
                    if(on): state = mainMenu(screen, menu)
                else: on = False
            elif(event.key == K_UP): 
                screen.blit(menu[state+1].surf, (500, 500 + state*125))
                if(state != 0): state -= 1
                else: state = 2
                screen.blit(menu[4].surf, (500, 500 + state*125))
            elif(event.key == K_DOWN): 
                screen.blit(menu[state+1].surf, (500, 500 + state*125))
                if(state != 2): state += 1
                else: state = 0
                screen.blit(menu[4].surf, (500, 500 + state*125))
            pygame.display.flip()
        if(event.type == pygame.QUIT): on = False
pygame.quit()