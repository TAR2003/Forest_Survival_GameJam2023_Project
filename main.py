import pygame
import random
from pygame.locals import *


def isinit(a, b):
    for i in b:
        if i == a:
            return True
    return False


def gametime():
    gametimer = pygame.time.get_ticks() - currentpausetime
    scorefont = pygame.font.SysFont('Times new roman', 50)
    seconds = gametimer // 100
    second = seconds / 10
    min = int(second / 600)
    seconds = seconds / 10
    strmsg = "TIME:: " + str(min) + ":" + str(seconds)
    scorerender = scorefont.render(strmsg, False, (0, 0, 0))
    timerec = scorerender.get_rect(center=(960, 50))
    screen.blit(scorerender, timerec)


class player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.standing = pygame.image.load('pictures/player/playerstanding.png')
        self.running1 = pygame.image.load('pictures/player/playerrunleft.png')
        self.running2 = pygame.image.load('pictures/player/playeronairright.png')
        self.running3 = pygame.image.load('pictures/player/playerrunright.png')
        self.running4 = pygame.image.load('pictures/player/playeronairrleftt.png')
        self.duck = pygame.image.load('pictures/player/playerduck.png')
        self.rs = self.standing.get_rect(bottomleft=(200, 670))
        self.r1 = self.running1.get_rect(bottomleft=(200, 670))
        self.r2 = self.running2.get_rect(bottomleft=(200, 650))
        self.r3 = self.running3.get_rect(bottomleft=(200, 670))
        self.r4 = self.running4.get_rect(bottomleft=(200, 650))
        self.rd = self.duck.get_rect(bottomleft=(100, 700))
        self.runsituation = False
        self.isduck = False
        self.isjump = False
        self.g = -30
        self.pos = 200
        self.shieldpic = pygame.image.load('pictures/player/SHIELD.png')
        self.shieldrec = self.shieldpic.get_rect(bottomleft=(300, 650))
        self.isshield = True
        self.smode = 0
        self.sword = False
        self.swordpic = pygame.image.load('pictures/sword.png')
        self.swordrec = self.swordpic.get_rect(bottomleft=(270, 600))

    def stand(self):
        if self.isjump:
            self.jump()
            return
        if self.sword:
            screen.blit(self.swordpic, self.swordrec)
        if self.smode == 1:
            self.shieldrec.top = 470
        if self.smode == 0:
            self.shieldrec.top = 530
        if self.smode == -1:
            self.shieldrec.top = 600
        if self.isshield:
            screen.blit(self.shieldpic, self.shieldrec)
        if self.isduck == False:
            screen.blit(self.standing, self.rs)
        else:
            screen.blit(self.duck, self.rd)
            self.isduck = False

    def jump(self):
        self.r4.bottom += self.g
        self.g += 2
        self.shieldrec.top = self.r4.top + 50
        if (self.r4.bottom >= 670):
            self.isjump = False
            self.g = -30
        if self.isshield:
            screen.blit(self.shieldpic, self.shieldrec)
        screen.blit(self.running4, self.r4)

    def run(self):
        if self.isjump:
            self.jump()
            return
        curtime = pygame.time.get_ticks()
        curtime = curtime % 600
        if self.isduck == False:
            if self.smode == 1:
                self.shieldrec.top = 470
            if self.smode == 0:
                self.shieldrec.top = 530
            if self.smode == -1:
                self.shieldrec.top = 600
            if self.isshield:
                screen.blit(self.shieldpic, self.shieldrec)
            if self.isshield and not self.isduck:
                screen.blit(self.shieldpic, self.shieldrec)
            if curtime < 150:
                screen.blit(self.running1, self.r1)
            if 150 <= curtime < 300:
                screen.blit(self.running2, self.r2)
            if 300 <= curtime < 450:
                screen.blit(self.running3, self.r3)
            if 450 <= curtime < 600:
                screen.blit(self.running4, self.r4)

        else:
            screen.blit(self.duck, self.rd)
            # self.isduck = False

    def update(self):
        self.shieldrec.bottomleft = (250, 650)
        if self.smode == 1:
            self.shieldrec.top = 470
        if self.smode == 0:
            self.shieldrec.top = 559
        if self.smode == -1:
            self.shieldrec.top = 661
        if self.isshield and not self.isduck:
            screen.blit(self.shieldpic, self.shieldrec)
        if self.isjump:
            self.jump()
        if self.runsituation:
            self.run()
        else:
            self.stand()


class ninja(pygame.sprite.Sprite):
    def __init__(self):
        super(ninja, self).__init__()
        self.ninjapic = pygame.image.load('pictures/ninja.png')
        self.ninjaattackpic = pygame.image.load('pictures/ninjaattack.png')
        self.nrec = self.ninjapic.get_rect(bottomleft=(6000, 670))
        self.narec = self.ninjaattackpic.get_rect(bottomleft=(2500, 670))
        self.palace = pygame.image.load('pictures/palace.png')
        self.palacerec = self.palace.get_rect(bottomleft=(6000, 620))
        self.ninjamode = False
        self.ninjaactive = False
        self.g = -14
        self.leftpos = 6000
        self.bottompos = 670
        self.wpic = pygame.image.load('pictures/weapon.png')
        self.wrec1 = self.wpic.get_rect(bottomleft=(1500, 610))
        self.wrec2 = self.wpic.get_rect(bottomleft=(1500, 610))
        self.wrec3 = self.wpic.get_rect(bottomleft=(1500, 610))

        self.wmode = False
        self.interval = 25
        self.currently = []
        self.currently.append([self.wpic, self.wrec1])
        self.currently.append([self.wpic, self.wrec2])
        self.currently.append([self.wpic, self.wrec3])
        self.inair = []
        self.readytolaunch = True
        self.lastitme = 0

        self.pause = False
        self.isjump = False
        self.attackinterval = 20
        self.attacktimer = 0
        self.count = 0
        self.at = pygame.mixer.Sound('audio/attack.wav')

    def showpalace(self):
        self.palacerec.left = self.leftpos - 1300
        screen.blit(self.palace, self.palacerec)

    def update(self):
        if self.isjump:
            self.jump()
        if self.leftpos < 1500:
            self.wmode = True
        if self.wmode:
            for i in self.inair:
                i[1].left -= 10
        if self.leftpos <= 400:
            self.ninjaactive = True
        if self.leftpos <= 700:
            self.wmode = False
        self.leftpos -= change_bg * 13

        # self.lastitme += 1
        # self.show()

    def show(self):
        if self.isjump:
            self.jump()
        if self.ninjamode:
            self.isjump = True
            self.attacktimer += 1
        self.nrec.left = self.narec.left = self.leftpos
        self.nrec.bottom = self.narec.bottom = self.bottompos
        for ea in self.inair:
            screen.blit(ea[0], ea[1])
        if 100 < self.leftpos < 400:
            self.isjump = True
        if self.leftpos >= 400:
            self.isjump = False
            screen.blit(self.ninjapic, self.nrec)
        else:
            self.ninjaactive = True
            self.isjump = True
            self.jump()
            if self.ninjamode:
                self.narec.left -= 85
                screen.blit(self.ninjaattackpic, self.narec)
            else:
                screen.blit(self.ninjapic, self.nrec)

    def getpos(self):
        if self.ninjamode:
            return self.narec.left
        else:
            return self.nrec.left
    def setpos(self):
        self.leftpos = -100
    def midpos(self):
        return self.bottompos - 90

    def jump(self):
        self.bottompos += self.g
        self.g += 2
        if self.bottompos <= 640:
            self.at.play(loops=1)
            self.ninjamode = True
        else:
            self.ninjamode = False
        if (self.bottompos >= 670):
            self.isjump = False
            self.g = -14


    def wattack(self):
        lastpos = 0
        if len(self.inair) == 0:
            self.readytolaunch = True
        if len(self.currently) == 0:
            self.readytolaunch = False
        if self.wmode:
            for i in self.inair:
                i[1].left -= 15
                lastpos = i[1].right
        if self.readytolaunch and self.lastitme > self.interval:
            a = self.currently[0]
            self.currently.pop(0)
            a[1].left = self.leftpos
            r = random.randint(0, 2)
            if r == 0:
                a[1].top = 480
            if r == 1:
                a[1].top = 540
            if r == 2:
                a[1].top = 610
            self.inair.append(a)
            self.lastitme = 0
        if len(self.inair) > 0:
            if self.inair[0][1].right < 0:
                a = self.inair[0]
                self.inair.pop(0)
                self.currently.append(a)
        self.lastitme += 1


class wizard(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        t = pygame.time.get_ticks() - currentpausetime
        self.wizpic = pygame.image.load('pictures/wizard.png')
        self.wizrect = self.wizpic.get_rect(bottomleft=(1500, 490))
        self.isactive = False
        self.attack = False
        self.vel = 10

    def startit(self):
        screen.blit(self.wizpic, self.wizrect)
        self.wizrect.left -= self.vel
        if self.wizrect.right <= 0:
            self.isactive = False
            self.wizrect.left = 1500

    def move(self):
        if self.isactive:
            self.wizrect.left -= change_bg * 4


class owltree(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.owlopenpic = pygame.image.load('pictures/trees/treewithowlopen.png')
        self.owlclosepic = pygame.image.load('pictures/trees/treewithowlclosed.png')
        self.owlopenrec = self.owlopenpic.get_rect(bottomleft=(500, 600))
        self.owlcloserec = self.owlclosepic.get_rect(bottomleft=(500, 600))

    def update(self):
        self.owlcloserec.bottomleft = self.owlopenrec.bottomleft
        self.curtime = pygame.time.get_ticks()
        self.curtime = self.curtime % 2000
        opos = self.owlopenrec
        if (self.curtime < 300):
            screen.blit(self.owlclosepic, self.owlcloserec)
            opos = self.owlcloserec
        else:
            screen.blit(self.owlopenpic, self.owlopenrec)
            opos = self.owlopenrec
        if (opos.right <= 0):
            opos.left = 1500


class dangertree(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.dangertree1 = pygame.image.load('pictures/trees/dangertree1.png')
        self.dangertree2 = pygame.image.load('pictures/trees/dangertree2.png')
        self.dangertree3 = pygame.image.load('pictures/trees/dangertree3.png')
        self.dangertree4 = pygame.image.load('pictures/trees/dangertree4.png')
        self.rectdangertree1 = self.dangertree1.get_rect(bottomleft=(1500, 560))
        self.rectdangertree2 = self.dangertree2.get_rect(bottomleft=(1500, 560))
        self.rectdangertree3 = self.dangertree3.get_rect(bottomleft=(1500, 560))
        self.rectdangertree4 = self.dangertree4.get_rect(bottomleft=(1500, 630))
        self.a11 = [self.dangertree1, self.rectdangertree1]
        self.a12 = [self.dangertree2, self.rectdangertree2]
        self.a13 = [self.dangertree3, self.rectdangertree3]
        self.a14 = [self.dangertree4, self.rectdangertree4]
        self.dangertreeseq = [self.a11, self.a12, self.a13, self.a14]
        self.currently = self.a11
        self.istaken = False

    def update(self):

        self.currently[1].x -= change_bg * 10
        self.show()

    def show(self):
        if self.istaken == False:
            pos = self.currently[1].left
            for i in self.dangertreeseq:
                i[1].left = pos
            t = pygame.time.get_ticks()
            t = t % 6000
            if t < 3000 and allowed:
                if t < 600 or t >= 2400:
                    self.currently = self.a12
                    screen.blit(self.a12[0], self.a12[1])
                if 600 <= t < 1200 or 1800 <= t < 2400:
                    self.currently = self.a13
                    screen.blit(self.a13[0], self.a13[1])
                if 1200 <= t < 1800:
                    self.currently = self.a14
                    screen.blit(self.a14[0], self.a14[1])
            else:
                self.currently = self.a11
                screen.blit(self.a11[0], self.a11[1])
            if self.currently[1].right <= 0:
                self.currently[1].left = random.randint(0, 1300) + 1500
        else:
            screen.blit(self.a14[0], self.a14[1])


class alltrees(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.tree1 = pygame.image.load('pictures/trees/treenormal.png')
        self.tree2 = pygame.image.load('pictures/trees/treered.png')
        self.tree3 = pygame.image.load('pictures/trees/treepink.png')
        self.tree4 = pygame.image.load('pictures/trees/treeorange.png')
        self.tree5 = pygame.image.load('pictures/trees/treepink2.png')
        self.tree6 = pygame.image.load('pictures/trees/treewithdalpala.png')
        self.tree7 = pygame.image.load('pictures/trees/treewithdalpalapink.png')
        self.tree8 = pygame.image.load('pictures/trees/treewithdalpalared.png')
        self.tree9 = pygame.image.load('pictures/trees/treewithdalpalayellow.png')
        self.tree10 = pygame.image.load('pictures/trees/treeyellow.png')
        self.pine1 = pygame.image.load('pictures/trees/pine1.png')
        self.pine2 = pygame.image.load('pictures/trees/pine2.png')
        self.pine3 = pygame.image.load('pictures/trees/pine3.png')
        self.pine4 = pygame.image.load('pictures/trees/pine4.png')
        self.recttree1 = self.tree1.get_rect(bottomleft=(1500, 550))
        self.recttree2 = self.tree2.get_rect(bottomleft=(1500, 540))
        self.recttree3 = self.tree3.get_rect(bottomleft=(1500, 550))
        self.recttree4 = self.tree4.get_rect(bottomleft=(1500, 560))
        self.recttree5 = self.tree5.get_rect(bottomleft=(1500, 530))
        self.recttree6 = self.tree6.get_rect(bottomleft=(1500, 530))
        self.recttree7 = self.tree7.get_rect(bottomleft=(1500, 530))
        self.recttree8 = self.tree8.get_rect(bottomleft=(1500, 510))
        self.recttree9 = self.tree9.get_rect(bottomleft=(1500, 540))
        self.recttree10 = self.tree10.get_rect(bottomleft=(1500, 500))
        self.rectpinetree1 = self.pine1.get_rect(bottomleft=(1500, 560))
        self.rectpinetree2 = self.pine2.get_rect(bottomleft=(1500, 560))
        self.rectpinetree3 = self.pine3.get_rect(bottomleft=(1500, 560))
        self.rectpinetree4 = self.pine4.get_rect(bottomleft=(1500, 560))
        picturearray = []
        self.a1 = [self.tree1, self.recttree1]
        self.a2 = [self.tree2, self.recttree2]
        self.a3 = [self.tree3, self.recttree3]
        self.a4 = [self.tree4, self.recttree4]
        self.a5 = [self.tree5, self.recttree5]
        self.a6 = [self.tree6, self.recttree6]
        self.a7 = [self.tree7, self.recttree7]
        self.a8 = [self.tree8, self.recttree8]
        self.a9 = [self.tree9, self.recttree9]
        self.a10 = [self.tree10, self.recttree10]
        self.a15 = [self.pine1, self.rectpinetree1]
        self.a16 = [self.pine2, self.rectpinetree2]
        self.a17 = [self.pine3, self.rectpinetree3]
        self.a18 = [self.pine4, self.rectpinetree4]
        self.picturearray = [self.a2, self.a3, self.a8, self.a10, self.a15]
        self.pinetree = [self.a15, self.a16, self.a17, self.a18]
        self.currpic = [self.a1, self.a6, self.a4, self.a9, self.a5, self.a7]
        self.a1[1].left = 0
        self.a6[1].left = 275
        self.a4[1].left = 550
        self.a9[1].left = 825
        self.a5[1].left = 1100
        self.a7[1].left = 1325

    def update(self):
        m = 0

    def moving(self):
        self.currpic[0][1].left -= change_bg * 10
        self.currpic[1][1].left -= change_bg * 10
        self.currpic[2][1].left -= change_bg * 10
        self.currpic[3][1].left -= change_bg * 10
        self.currpic[4][1].left -= change_bg * 10
        self.currpic[5][1].left -= change_bg * 10
        self.show()

    def show(self):
        # self.currpic[0][1].x =
        ispinetree = False
        w = 0
        ind = 0
        if isinit(self.a15, self.currpic):
            ispinetree = True
            ind = self.currpic.index(self.a15)
            w = self.a15[1].left
        elif isinit(self.a16, self.currpic):
            ispinetree = True
            ind = self.currpic.index(self.a16)
            w = self.a16[1].left
        elif isinit(self.a17, self.currpic):
            ispinetree = True
            ind = self.currpic.index(self.a17)
            w = self.a17[1].left
        elif isinit(self.a18, self.currpic):
            ispinetree = True
            ind = self.currpic.index(self.a18)
            w = self.a18[1].left
        if ispinetree:
            totaltime = pygame.time.get_ticks()
            totaltime = totaltime % 1800
            if totaltime < 300:
                self.currpic[ind][0] = self.a15[0]
                self.currpic[ind][1] = self.a15[1]
            elif 300 <= totaltime < 600 or totaltime >= 1500:
                self.currpic[ind][0] = self.a16[0]
                self.currpic[ind][1] = self.a16[1]
            elif 600 <= totaltime < 900 or 1200 <= totaltime < 1500:
                self.currpic[ind][0] = self.a17[0]
                self.currpic[ind][1] = self.a17[1]
            elif 900 <= totaltime < 1200:
                self.currpic[ind][0] = self.a18[0]
                self.currpic[ind][1] = self.a18[1]

            self.currpic[ind][1].left = w
            ispinetree = False
        screen.blit(self.currpic[0][0], self.currpic[0][1])
        screen.blit(self.currpic[1][0], self.currpic[1][1])
        screen.blit(self.currpic[2][0], self.currpic[2][1])
        screen.blit(self.currpic[3][0], self.currpic[3][1])
        screen.blit(self.currpic[4][0], self.currpic[4][1])
        screen.blit(self.currpic[5][0], self.currpic[5][1])
        if self.currpic[0][1].right < 0:
            temp = self.currpic[0]
            self.currpic.pop(0)
            r = random.randint(0, 4)
            self.currpic.append(self.picturearray[r])
            self.picturearray.pop(r)
            self.picturearray.append(temp)
            self.currpic[5][1].left = self.currpic[4][1].right - 30


pygame.init()
screen = pygame.display.set_mode((1300, 800))
pygame.display.set_caption('Forest Survival')
clock = pygame.time.Clock()
test_font = pygame.font.SysFont('Times new roman', 50)
test_render = test_font.render('The game', False, (255, 255, 0))
test_rect = test_render.get_rect(center=(600, 400))
mode = 'menu'
score = 0
bg_x = 0
bg_pic1 = pygame.image.load('pictures/bg.png')
bg_rect1 = bg_pic1.get_rect(topleft=(bg_x, -70))
bg_pic2 = pygame.image.load('pictures/bg.png')
bg_rect2 = bg_pic2.get_rect(topleft=(bg_x + 805, -70))
bg_pic3 = pygame.image.load('pictures/bg.png')
bg_rect3 = bg_pic3.get_rect(topleft=(bg_x + 805 + 805, -70))
bg1strow = 'pictures/bgfront1strow.png'
bg2ndrow = 'pictures/bgfront2ndrow.png'
bg3rdrow = 'pictures/bgfront3rdrow.png'
walkway = 'pictures/walkway.png'

menupic = pygame.image.load('pictures/newgame.png')
menurec = menupic.get_rect(topleft=(0, 0))
pausepicbg = pygame.image.load('pictures/pause.png')
pauserecbg = pausepicbg.get_rect(topleft=(0, 0))
ymusicpic = pygame.image.load('pictures/musicyes.png')
yesrec = ymusicpic.get_rect(topright=(1200, 40))
nmusicpic = pygame.image.load('pictures/musicno.png')
norec = nmusicpic.get_rect(topright=(1200, 40))
music = True

bg1_pic = pygame.image.load(bg1strow)
bg1_rect1 = bg1_pic.get_rect(bottomleft=(0, 480))
bg1_rect2 = bg1_pic.get_rect(bottomleft=(1300, 480))
# 724,730
bg2_pic = pygame.image.load(bg2ndrow)
bg3_pic = pygame.image.load(bg3rdrow)
bg2_rec1 = bg2_pic.get_rect(bottomleft=(0, 370))
bg2_rec2 = bg2_pic.get_rect(bottomleft=(730, 370))
bg2_rec3 = bg2_pic.get_rect(bottomleft=(1460, 370))
bg3_rec1 = bg3_pic.get_rect(bottomleft=(0, 300))
bg3_rec2 = bg3_pic.get_rect(bottomleft=(724, 300))
bg3_rec3 = bg3_pic.get_rect(bottomleft=(1448, 300))
walkpic = pygame.image.load(walkway)
walkrec1 = walkpic.get_rect(bottomleft=(0, 800))
walkrec2 = walkpic.get_rect(bottomleft=(walkrec1.right, 800))
walkrec3 = walkpic.get_rect(bottomleft=(walkrec2.right, 800))
greenbg1 = pygame.image.load('pictures/justgreen.png')
greenrec1 = greenbg1.get_rect(topleft=(0, bg1_rect1.bottom))
greenrec2 = greenbg1.get_rect(topleft=(greenrec1.right, bg1_rect2.bottom))
greenrec3 = greenbg1.get_rect(topleft=(greenrec2.right, bg1_rect1.bottom))
pausepic = pygame.image.load('pictures/pauselogo.png')
pauserec = pausepic.get_rect(topright=(1270, 30))
p1 = player()
otree = owltree()
global currentpausetime
currentpausetime = 0
pausedtime = 0
tree1 = alltrees()
danger = dangertree()
screenfreeze = False
health = 3
healthpic = pygame.image.load('pictures/health.png')
h1 = healthpic.get_rect(topleft=(20, 10))
h2 = healthpic.get_rect(topleft=(h1.right + 10, 10))
h3 = healthpic.get_rect(topleft=(h2.right + 10, 10))
screenfreezetimer = 0
game_over = False
global change_bg
change_bg = 1
wiz1 = wizard()
crocodile = pygame.image.load('pictures/croc.png')
crocrec = crocodile.get_rect(bottomleft=(random.randint(0, 1300) + 1500, 700))
iscrocattack = False
step = 0
carefulpic = pygame.image.load('pictures/careful.png')
carerec = carefulpic.get_rect(topleft=(100,100))
over = pygame.image.load('pictures/gameover.png')
overrec = over.get_rect(topleft=(0,0))
###
global allowed
allowed = True
mwtest = 1
preestimer = 0
ninja1 = ninja()
update = False
showmessage = 'Welcome to the game, my friend'

allmusic = []
thememusic = pygame.mixer.Sound('audio/theme.wav')
allmusic.append(thememusic)
ingamemusic = pygame.mixer.Sound('audio/ingame.wav')
allmusic.append(ingamemusic)
overmusic = pygame.mixer.Sound('audio/string.wav')
overmusic.set_volume(0.1)
allmusic.append(overmusic)
click = pygame.mixer.Sound('audio/click.wav')
allmusic.append(click)
swipe = pygame.mixer.Sound('audio/slide.wav')
allmusic.append(swipe)
jumpmusic = pygame.mixer.Sound('audio/jump.wav')
allmusic.append(jumpmusic)
lossmusic = pygame.mixer.Sound('audio/mont.wav')
allmusic.append(lossmusic)
lossmusic.set_volume(0.02)
thememusic.set_volume(0.1)
levelup = pygame.mixer.Sound('audio/levelup.wav')
levelup.set_volume(0.08)
siren = pygame.mixer.Sound('audio/siren.wav')
siren.set_volume(0.1)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if mode == 'menu':
            if event.type == pygame.MOUSEBUTTONDOWN:
                click.play(loops=0)
                click.set_volume(0.3)
                position = pygame.mouse.get_pos()
                if 1120 <= position[0] <= 1200 and 40 <= position[1] <= 170:
                    music = not music
                    if not music:
                        for m in allmusic:
                            m.stop()

        if mode == 'playingday':
            if event.type == pygame.MOUSEBUTTONDOWN:

                pos = pygame.mouse.get_pos()
                if 1200 <= pos[0] <= 1270 and 30 <= pos[1] <= 100:
                    mode = 'pause'
                    click.play(loops=0)
                    click.set_volume(0.3)
                    pausedtime = pygame.time.get_ticks() - currentpausetime
            if event.type == pygame.MOUSEWHEEL:
                swipe.play(loops=0)
                swipe.set_volume(0.4)
                if mode == 'playingday':
                    if p1.isshield:
                        if event.y == -1:
                            if p1.smode != -1:
                                p1.smode -= 1
                        if event.y == 1:
                            if p1.smode != 1:
                                p1.smode += 1
        if mode == 'pause':
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                click.play(loops=0)
                click.set_volume(0.3)
                if 0 <= pos[0] <= 200 and 0 <= pos[1] <= 100:
                    mode = 'playingday'
                    print('pressesin the mode')
                    currentpausetime = pygame.time.get_ticks()
                    currentpausetime -= pausedtime
    if mode == 'menu':
        levelup.stop()
        if music:

            thememusic.play(loops=-1)
        screen.blit(menupic, menurec)
        if music:
            screen.blit(ymusicpic, yesrec)
        else:
            screen.blit(nmusicpic, norec)
        k = pygame.key.get_pressed()
        if k[pygame.K_SPACE]:
            mode = 'playingday'
            currentpausetime = pygame.time.get_ticks()
        fo = pygame.mouse.get_pressed()
        if fo == (True, False, False):
            click.play(loops=0)
            click.set_volume(0.3)
            pos = pygame.mouse.get_pos()
            if 360 <= pos[0] <= 892 and 134 <= pos[1] <= 280:
                mode = 'playingday'
                currentpausetime = pygame.time.get_ticks()
            if 353 <= pos[0] <= 888 and 545 <= pos[1] <= 678:
                pygame.quit()
                exit()

    if mode == 'pause':
        if music:

            thememusic.play(loops=-1)
        levelup.stop()
        screen.blit(pausepicbg, pauserecbg)
        fo = pygame.mouse.get_pressed()
        if fo == (True, False, False):
            pos = pygame.mouse.get_pos()
            click.play(loops=0)
            click.set_volume(0.3)
            if 321 <= pos[0] <= 876 and 147 <= pos[1] <= 266:
                mode = 'playingday'
                click.play(loops=0)
                click.set_volume(0.3)
                currentpausetime = pygame.time.get_ticks()
                currentpausetime -= pausedtime
            if 321 <= pos[0] <= 876 and 319 <= pos[1] <= 436:
                mode = 'newgame'
                click.play(loops=0)
                click.set_volume(0.3)
            if 991 <= pos[0] <= 1300 and 713 <= pos[1] <= 783:
                mode = 'reset'
                click.play(loops=0)
                click.set_volume(0.3)
            if 321 <= pos[0] <= 876 and 500 <= pos[1] <= 617:
                pygame.quit()
                exit()

    if mode == 'reset':
        pos = pygame.mouse.get_pos()
        mode = 'menu'
        p1 = player()
        danger = dangertree()
        wiz1 = wizard()
        otree = owltree()
        tree1 = alltrees()
        change_bg = 1
        crocrec.left = 1500
        score = 0
        step = 0
        health = 3
        allowed = True
        iscrocattack = False
        currentpausetime = pygame.time.get_ticks()
        ninja1 = ninja()
        showmessage = 'Welcome to the game, my friend'
    if mode == 'gameover':
        levelup.stop()
        if music:

            thememusic.play(loops=-1)
        screen.blit(over,overrec)
        finalfont = pygame.font.SysFont('consolas', 100)
        scorestr1 = 'Your score is: ' + str(score)
        tr = finalfont.render(scorestr1,False,(0,0,0))
        trec = tr.get_rect(topleft=(200,400))
        screen.blit(tr,trec)
        fo = pygame.mouse.get_pressed()
        if fo == (True, False, False):
            pos = pygame.mouse.get_pos()
            if 991 <= pos[0] <= 1300 and 713 <= pos[1] <= 783:
                mode = 'reset'
    if mode == 'newgame':
        pos = pygame.mouse.get_pos()
        mode = 'playingday'
        p1 = player()
        danger = dangertree()
        wiz1 = wizard()
        otree = owltree()
        tree1 = alltrees()
        change_bg = 1
        crocrec.left = 1500
        score = 0
        step = 0
        health = 3
        allowed = True
        iscrocattack = False
        currentpausetime = pygame.time.get_ticks()
        ninja1 = ninja()
        showmessage = 'Welcome to the game, my friend'
    if mode == 'playingday':
        thememusic.stop()
        ingame = pygame.time.get_ticks() - currentpausetime
        screen.fill('grey')
        screen.blit(greenbg1, greenrec1)
        screen.blit(greenbg1, greenrec2)
        screen.blit(greenbg1, greenrec3)
        screen.blit(bg_pic3, bg_rect3)
        screen.blit(bg_pic2, bg_rect2)
        screen.blit(bg_pic1, bg_rect1)
        screen.blit(bg3_pic, bg3_rec1)
        screen.blit(bg3_pic, bg3_rec2)
        screen.blit(bg3_pic, bg3_rec3)
        screen.blit(bg2_pic, bg2_rec1)
        screen.blit(bg2_pic, bg2_rec2)
        screen.blit(bg2_pic, bg2_rec3)

        screen.blit(bg1_pic, bg1_rect2)
        screen.blit(bg1_pic, bg1_rect1)

        screen.blit(walkpic, walkrec1)
        screen.blit(walkpic, walkrec2)
        screen.blit(walkpic, walkrec3)
        for all in ninja1.inair:
            if all[1].left <= 300 and all[1].right > 200:
                if p1.isduck:
                    showmessage = 'Good job'
                    print('welll')
                elif p1.isjump:
                    if p1.r4.bottom >= 610 and all[1].top == 610:
                        screenfreeze = True
                        ninja1.wmode = False
                        for a in ninja1.inair:
                            a[1].right = -100
                    if p1.r4.bottom >= 540 and all[1].top == 540:
                        screenfreeze = True
                        ninja1.wmode = False
                        for a in ninja1.inair:
                            a[1].right = -100
                    if p1.r4.bottom >= 480 and all[1].top == 480:
                        screenfreeze = True
                        ninja1.wmode = False
                        for a in ninja1.inair:
                            a[1].right = -100

                elif not p1.isshield:
                    screenfreeze = True
                    ninja1.wmode = False
                    for a in ninja1.inair:
                        a[1].right = -100
                else:
                    if all[1].top == 480 and p1.smode != 1:
                        screenfreeze = True
                        ninja1.wmode = False
                        for a in ninja1.inair:
                            a[1].right = -100
                    if all[1].top == 540 and p1.smode != 0:
                        screenfreeze = True
                        ninja1.wmode = False
                        for a in ninja1.inair:
                            a[1].right = -100
                    if all[1].top == 610 and p1.smode != -1:
                        screenfreeze = True
                        ninja1.wmode = False
                        for a in ninja1.inair:
                            a[1].right = -100
                    else:
                        all[1].right = -100

        if ninja1.wmode and not screenfreeze:
            ninja1.wattack()
        if allowed:
            screen.blit(crocodile, crocrec)
        if ingame % 5000 < 100 and wiz1.isactive == False and ingame > 5000:
            wiz1.isactive = True
        if allowed:
            if wiz1.isactive:
                wiz1.startit()
        k = pygame.key.get_pressed()
        preestimer += 1
        if k[pygame.K_s]:
            if preestimer > 10:
                p1.isshield = not p1.isshield
                preestimer = 0
        if k[pygame.K_UP]:
            print("UP")
            if p1.isshield:
                p1.smode = 1
        if k[pygame.K_DOWN]:
            print('down here')
            if p1.isshield:
                p1.smode = 0
        if k[pygame.K_LEFT]:
            if p1.isshield:
                p1.smode = 1
            ninja1.isjump = True
        if k[pygame.K_RIGHT]:
            if p1.isshield:
                p1.smode = -1
        if k[pygame.K_d]:
            swipe.play(loops=0)
            swipe.set_volume(0.3)
            p1.isduck = True
        if k[pygame.K_j]:
            jumpmusic.play(loops=0)
            jumpmusic.set_volume(0.05)
            p1.isjump = True
        if k[pygame.K_a]:
            p1.sword = True
        if ninja1.wmode:
            allowed = False
            crocrec.right = 2000
            wiz1.wizrect.right = 2000
        if 240 <= wiz1.wizrect.left <= 260 and p1.isduck == False and allowed and wiz1.attack == False:
            screenfreeze = True
            wiz1.attack = True
        if 240 <= crocrec.left <= 265 and allowed and p1.isjump == False and not iscrocattack:
            iscrocattack = True
            screenfreeze = True
        if 240 <= ninja1.getpos() <= 265 and p1.isjump == False:
            screenfreeze = True
            ninja1.ninjaactive = True
        if screenfreeze == False:
            danger.istaken = False

            if k[pygame.K_SPACE]:
                step += 1
                bg_rect1.x -= change_bg
                bg_rect2.x -= change_bg
                bg_rect3.x -= change_bg
                bg1_rect1.x -= change_bg * 5
                bg1_rect2.x -= change_bg * 5
                bg2_rec1.x -= change_bg * 3
                bg2_rec2.x -= change_bg * 3
                bg2_rec3.x -= change_bg * 3
                bg3_rec1.x -= change_bg * 2
                bg3_rec2.x -= change_bg * 2
                bg3_rec3.x -= change_bg * 2
                walkrec1.x -= change_bg * 13
                walkrec2.x -= change_bg * 13
                walkrec3.x -= change_bg * 13
                ninja1.update()
                tree1.moving()
                otree.owlopenrec.x -= change_bg * 10
                otree.owlcloserec.x -= change_bg * 10
                crocrec.left -= change_bg * 13
                otree.update()
                danger.update()
                ninja1.showpalace()
                p1.run()
                if allowed:
                    wiz1.move()


            else:
                tree1.show()
                otree.update()
                danger.show()
                ninja1.showpalace()
                p1.stand()
            if ingame % 8000 < 100 and wiz1.isactive == False and ingame > 5000:
                wiz1.isactive = True
            if allowed:
                if wiz1.isactive:
                    wiz1.startit()


        else:
            tree1.show()
            otree.update()
            danger.show()
            ninja1.showpalace()
            p1.stand()
            screen.blit(wiz1.wizpic, wiz1.wizrect)
            lossmusic.play(loops=-1)
            screenfreezetimer += 1
            if health>1:
                screen.blit(carefulpic,carerec)
            showmessage = 'BE VERY CAREFUL NOW!!!'
            if screenfreezetimer > 60:
                lossmusic.stop()
                danger.currently[1].left = -400
                crocrec.right = 2000
                ninja1 = ninja()
                ninja1.leftpos = 8000

                wiz1.wizrect.left -= 100
                screenfreezetimer = 0
                screenfreeze = False

                if (health > 1):
                    health -= 1
                else:
                    game_over = True
                    mode = 'gameover'
                if danger.istaken:

                    danger.istaken = False
                if wiz1.attack:

                    wiz1.attack = False
                if iscrocattack:
                    iscrocattack = False

                if ninja1.ninjaactive:
                    ninja1.ninjaactive = False


        if bg_rect1.x <= -805:
            bg_rect1.x = 805 + 805
        if bg_rect2.x <= -805:
            bg_rect2.x = 805 + 805
        if bg_rect3.x <= -805:
            bg_rect3.x = 805 + 805
        if bg1_rect2.x <= -1300:
            bg1_rect2.x = bg1_rect1.right
        if bg1_rect1.x <= -1300:
            bg1_rect1.x = bg1_rect2.right
        if bg2_rec1.right <= 0:
            bg2_rec1.left = bg2_rec3.right
        if bg2_rec2.right <= 0:
            bg2_rec2.left = bg2_rec1.right
        if bg2_rec3.right <= 0:
            bg2_rec3.left = bg2_rec2.right
        if bg3_rec1.right <= 0:
            bg3_rec1.left = bg3_rec3.right
        if bg3_rec2.right <= 0:
            bg3_rec2.left = bg3_rec1.right
        if bg3_rec3.right <= 0:
            bg3_rec3.left = bg3_rec2.right
        if walkrec1.right <= 0:
            walkrec1.left = walkrec3.right
        if walkrec2.right <= 0:
            walkrec2.left = walkrec1.right
        if walkrec3.right <= 0:
            walkrec3.left = walkrec2.right
        if greenrec1.right <= 0:
            greenrec1.left = greenrec3.right
        if greenrec2.right <= 0:
            greenrec2.left = greenrec1.right
        if greenrec3.right <= 0:
            greenrec3.left = greenrec2.right
        if crocrec.right <= 0:
            crocrec.left = random.randint(0, 1000) + 1300
        screen.blit(pausepic, pauserec)
        gametime()
        if health > 0:
            screen.blit(healthpic, h1)
            if (health > 1):
                screen.blit(healthpic, h2)
                if health > 2:
                    screen.blit(healthpic, h3)

        fo = pygame.mouse.get_pressed()
        if fo == (True, False, False):
            pos = pygame.mouse.get_pos()
            print(pos)

            # if pos[0]
        if 360 <= danger.currently[1].centerx <= 470 and (
                p1.isduck == False and p1.isjump == False) and allowed and danger.currently == danger.a14:
            danger.istaken = True
            screenfreeze = True
            danger.show()
        if wiz1.isactive and allowed:
            if (ingame % 1000 > 500):
                showmessage = 'Be prepared!!! Wizard is coming'
        if danger.currently != danger.a11 and not wiz1.isactive and allowed:
            if (ingame % 1000 > 500):
                showmessage = 'Attention!!!The deadly tree'
        p1.isduck = False
        if 0 < ninja1.getpos() < 1700:
            allowed = False
            if ingame % 1000 > 500:

                if ninja1.getpos() > 400:
                    showmessage = 'Be prepared!!!There is no escape'
                if ninja1.ninjaactive:
                    showmessage = 'HURRY!! jump over'
        if 700 < ninja1.getpos() < 1700:
            if ingame %2000<200:
                siren.play()
        if ninja1.getpos() < 1800:
            allowed = False
        if ninja1.getpos() < -100:
            allowed = True

        ninja1.show()
        p1.sword = False
        if step >= 10:
            score += 1
            step = 0
        scorestr = "YOUR SCORE: " + str(score)
        scorrender = test_font.render(scorestr, False, (0, 0, 0))
        msgr= scorrender.get_rect(bottomleft=(300, 80))
        screen.blit(scorrender, msgr)
        msgrender = test_font.render('Press SPACE to move, d to slide, j to jump, s to toggle shield', False, (255, 255, 255))
        msgrect = msgrender.get_rect(bottomleft=(40, 790))
        screen.blit(msgrender, msgrect)
        # print(bg_rect1.x,bg_rect2.x,bg_rect3.x)
        # print(bg2_rec1.right)
        if score > 100:
            change_bg = 2
            if 100 <= score <= 110:
                levelup.play(loops=-1)
                showmessage = ' LEVEL 2'
            else:
                levelup.stop()
            wiz1.vel = 18
        if score > 200:
            change_bg = 3
            wiz1.vel = 20
            if 200 <= score <= 220:
                levelup.play(loops=-1)
                showmessage = ' LEVEL 3'
            else:
                levelup.stop()
        if ninja1.getpos() > 1800:
            allowed = True

    pygame.display.update()
    clock.tick(60)
