import pygame, sys, random, math, os, json, time

pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Fishing")
clock = pygame.time.Clock()

# --- KOLORY / CZCIONKI ---
SKY = (135, 206, 235)
WATER = (0, 100, 255)
CLIFF = (110, 90, 70)
BLACK = (0,0,0)
WHITE = (255,255,255)
UI_BG = (238,238,238)
UI_BORDER = (40,40,40)
GREEN = (30,160,60)

FONT = pygame.font.SysFont("arial",18)
BIG = pygame.font.SysFont("arial",24,bold=True)

# --- STAN GRY ---
money = 0
backpack = []
MAX_BACKPACK = 50
CATCH_EVERY_MS = 10000
last_catch_ms = pygame.time.get_ticks()
legend_upgrade_level = 0
legend_upgrade_price = 100
legend_bonus_per_level = 0.02
player_name = ""
save_file = "save.txt"
leaderboard = {}  # real-time leaderboard

# --- RYBY ---
RARITY = [("Common",40,(170,170,170),1),
          ("Uncommon",30,(60,210,90),3),
          ("Rare",20,(70,90,220),7),
          ("Epic",9,(190,90,220),15),
          ("Legendary",1,(255,215,0),40)]
RARITY_POOL = [name for name,chance,_,_ in RARITY for _ in range(chance)]
RARITY_COLOR = {name:color for name,_,color,_ in RARITY}
RARITY_MULT = {name:mult for name,_,_,mult in RARITY}

FISH_SPAWN_MAX = 10
def spawn_fish_visual():
    rarity = random.choice(RARITY_POOL)
    rect = pygame.Rect(random.randint(260,WIDTH-40), random.randint(330,HEIGHT-30),26,12)
    basey = rect.y
    speed = random.uniform(0.5,1.5)
    phase = random.uniform(0,math.tau)
    return {"rarity":rarity,"rect":rect,"basey":basey,"speed":speed,"phase":phase}
water_fish = [spawn_fish_visual() for _ in range(FISH_SPAWN_MAX)]

# --- FUNKCJE ---
def save_game():
    data = {"money":money,"backpack":backpack,
            "legend_upgrade_level":legend_upgrade_level,
            "legend_upgrade_price":legend_upgrade_price,
            "player_name":player_name}
    with open(save_file,"w",encoding="utf-8") as f:
        json.dump(data,f)

def load_game():
    global money, backpack, legend_upgrade_level, legend_upgrade_price, player_name
    if os.path.exists(save_file):
        try:
            with open(save_file,"r",encoding="utf-8") as f:
                data = json.load(f)
                money = data.get("money",0)
                backpack = data.get("backpack",[])
                legend_upgrade_level = data.get("legend_upgrade_level",0)
                legend_upgrade_price = data.get("legend_upgrade_price",100)
                player_name = data.get("player_name","")
        except:
            pass
load_game()

def roll_caught_fish():
    pool = [name for name,chance,_,_ in RARITY if name!="Legendary" for _ in range(chance)]
    legend_chance = 1 + legend_upgrade_level*legend_bonus_per_level*100
    pool += ["Legendary"]*int(legend_chance)
    rarity = random.choice(pool)
    weight = round(random.uniform(0.5,3.0)*(1+0.6*math.log2(RARITY_MULT[rarity]+1)),2)
    return {"rarity":rarity,"weight":weight}

def fish_value(f):
    return int(max(1,f["weight"])*RARITY_MULT[f["rarity"]])

# --- REAL-TIME LEADERBOARD ---
def update_leaderboard_real_time():
    leaderboard[player_name] = {"caught":len(backpack), "money":money}

def draw_leaderboard_real_time():
    panel = pygame.Rect(WIDTH-300,80,280,280)
    pygame.draw.rect(screen,UI_BG,panel,border_radius=8)
    pygame.draw.rect(screen,UI_BORDER,panel,2,border_radius=8)
    title = BIG.render("Leaderboard",True,BLACK)
    screen.blit(title,(panel.x+50,panel.y+10))
    top5 = sorted(leaderboard.items(), key=lambda x:(x[1]["money"],x[1]["caught"]), reverse=True)[:5]
    y = panel.y+50
    for name, stats in top5:
        line = FONT.render(f"{name}: {stats['caught']} ryb, {stats['money']}$",True,BLACK)
        screen.blit(line,(panel.x+10,y))
        y+=30

# --- STICKMAN / WĘDKA ---
stickman = {"x":180,"y":480}

# --- SPRZEDAWCA ---
vendor_rect = pygame.Rect(WIDTH-200,HEIGHT-300,160,180)

# --- PANEL PLECAKA ---
def draw_backpack_ui():
    panel = pygame.Rect(10,50,260,320)
    pygame.draw.rect(screen,UI_BG,panel,border_radius=8)
    pygame.draw.rect(screen,UI_BORDER,panel,2,border_radius=8)
    title = BIG.render(f"Plecak {len(backpack)}/{MAX_BACKPACK}",True,BLACK)
    screen.blit(title,(panel.x+12,panel.y+10))
    y = panel.y + 50
    mouse = pygame.mouse.get_pos()
    for f in backpack[:12]:
        line = FONT.render(f"{f['rarity']} {f['weight']}kg",True,RARITY_COLOR[f['rarity']])
        screen.blit(line,(panel.x+12,y))
        rect = line.get_rect(topleft=(panel.x+12,y))
        if rect.collidepoint(mouse):
            val = fish_value(f)
            tip = FONT.render(f"Wartość: {val}$",True,BLACK)
            tip_bg = pygame.Rect(mouse[0]+12, mouse[1]-18, tip.get_width()+8, tip.get_height()+6)
            pygame.draw.rect(screen,(255,255,210),tip_bg,border_radius=6)
            pygame.draw.rect(screen,(160,160,120),tip_bg,1,border_radius=6)
            screen.blit(tip,(tip_bg.x+4,tip_bg.y+3))
        y+=24

# --- START SCREEN ---
def start_screen():
    global player_name
    input_box = pygame.Rect(WIDTH//2-150, HEIGHT//2-25, 300, 50)
    color_inactive = (100,100,100)
    color_active = (30,160,60)
    color = color_inactive
    active = False
    text = ''
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN and text.strip() != '':
                        player_name = text.strip()
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        screen.fill(SKY)
        msg = BIG.render("Wpisz nazwę gracza i ENTER", True, BLACK)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 100))
        pygame.draw.rect(screen,color,input_box,2)
        txt_surface = BIG.render(text,True,BLACK)
        screen.blit(txt_surface,(input_box.x+5,input_box.y+5))
        pygame.display.flip()
        clock.tick(60)

# --- START ---
start_screen()
running = True
last_catch_ms = pygame.time.get_ticks()

while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            running=False

    # --- ŁOWIENIE RYB ---
    now = pygame.time.get_ticks()
    if now - last_catch_ms > CATCH_EVERY_MS and len(backpack)<MAX_BACKPACK:
        backpack.append(roll_caught_fish())
        last_catch_ms = now

    # --- AKTUALIZACJA WODNYCH RYB ---
    t = pygame.time.get_ticks()/600.0
    for f in water_fish:
        f["rect"].x += 1 if random.random()<0.6 else -1
        f["rect"].x = max(240,min(WIDTH-30,f["rect"].x))
        f["rect"].y = int(f["basey"]+10*math.sin(t*f["speed"]+f["phase"]))
        f["rect"].y = max(HEIGHT-240,min(HEIGHT-30,f["rect"].y))

    # --- RYSOWANIE ---
    screen.fill(SKY)
    pygame.draw.rect(screen,WATER,(0,HEIGHT-250,WIDTH,250))
    pygame.draw.rect(screen,CLIFF,(0,HEIGHT-300,250,300))
    pygame.draw.rect(screen,(90,75,60),(100,HEIGHT-290,220,20))
    # Stickman
    x,y = stickman["x"], stickman["y"]
    pygame.draw.circle(screen,BLACK,(x,y-60),18,2)
    pygame.draw.line(screen,BLACK,(x,y-42),(x,y+20),2)
    pygame.draw.line(screen,BLACK,(x,y+20),(x-18,y+55),2)
    pygame.draw.line(screen,BLACK,(x,y+20),(x+18,y+55),2)
    pygame.draw.line(screen,BLACK,(x,y-28),(x-25,y),2)
    pygame.draw.line(screen,BLACK,(x,y-28),(x+25,y),2)
    tip_y = y-140
    rod_tip = (x+140,tip_y)
    pygame.draw.line(screen,(80,40,10),(x+25,y-28),rod_tip,4)
    pygame.draw.line(screen,BLACK,rod_tip,(rod_tip[0],HEIGHT-250),1)
    pygame.draw.circle(screen,BLACK,(rod_tip[0],HEIGHT-250),4)
    # Ryby w wodzie
    for f in water_fish:
        pygame.draw.ellipse(screen,RARITY_COLOR[f["rarity"]],f["rect"])
    # Sprzedawca
    pygame.draw.rect(screen,(150,110,80),vendor_rect,border_radius=10)
    txt = FONT.render("SPRZEDAWCA", True, WHITE)
    screen.blit(txt,(vendor_rect.x+12,vendor_rect.y-22))
    mouse = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0] and vendor_rect.collidepoint(mouse):
        if backpack:
            money += sum(fish_value(f) for f in backpack)
            backpack.clear()
    # Upgrade
    upgrade_rect = pygame.Rect(WIDTH//2-130,HEIGHT-60,260,50)
    pygame.draw.rect(screen,(50,140,60),upgrade_rect,border_radius=8)
    pygame.draw.rect(screen,(20,80,30),upgrade_rect,2,border_radius=8)
    upgrade_txt = BIG.render(f"Upgrade Legend +{legend_bonus_per_level*100:.0f}% (${legend_upgrade_price})",True,WHITE)
    screen.blit(upgrade_txt,(upgrade_rect.x+8,upgrade_rect.y+8))
    if pygame.mouse.get_pressed()[0] and upgrade_rect.collidepoint(mouse):
        if money>=legend_upgrade_price:
            money-=legend_upgrade_price
            legend_upgrade_level+=1
            legend_upgrade_price+=50
    # Plecak
    draw_backpack_ui()
    # Leaderboard
    update_leaderboard_real_time()
    draw_leaderboard_real_time()
    # Pieniądze
    info = FONT.render(f"Pieniądze: {money}$",True,BLACK)
    screen.blit(info,(10,10))

    pygame.display.flip()

save_game()
pygame.quit()
