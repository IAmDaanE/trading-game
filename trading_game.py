import pygame
import random
import io
import sys

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("trading treats")
clock = pygame.time.Clock()

import matplotlib  #type: ignore
matplotlib.use("Agg")
import matplotlib.pyplot as plt #type: ignore

def format_balance(n):
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000:
        return sign + f"{n / 1_000_000_000:.1f}".rstrip("0").rstrip(".") + " B"
    elif n >= 1_000_000:
        return sign + f"{n / 1_000_000:.1f}".rstrip("0").rstrip(".") + " M"
    elif n >= 1_000:
        return sign + f"{n / 1_000:.1f}".rstrip("0").rstrip(".") + " K"
    else:
        return sign + f"{n:,}".replace(",", " ")

def profit_percentage(owned, price, buyprice):
    if owned == 0 or buyprice == 0:
        return "0.00%"

    current_value = owned * price
    profit = current_value - buyprice
    percent = (profit / buyprice) * 100

    sign = "+" if percent > 0 else ""
    return f"{sign}{percent:.2f}%"

if True:
    mouse_sound = pygame.mixer.Sound("assets/mouse_click.mp3")
    level_up_sound = pygame.mixer.Sound("assets/level_up.mp3")

    font = pygame.font.Font("assets/DS-DIGII.ttf", 45)
    smallfont = pygame.font.Font("assets/DS-DIGII.ttf", 35)
    smallerfont = pygame.font.Font("assets/DS-DIGII.ttf", 30)

    green = (55, 148, 110)
    red = (172, 50, 50)

    balance = 2000
    networth = balance 
    day = 1
    amount = 0

    selected_stock = "apple"

    apple_price = 50
    microsoft_price = 50
    bmw_price = 50
    mcdonalds_price = 50
    nintendo_price = 50

    apple_owned = 0
    microsoft_owned = 0
    bmw_owned = 0
    mcdonalds_owned = 0
    nintendo_owned = 0

    apple_color = green
    microsoft_color = red
    bmw_color = red
    mcdonalds_color = green
    nintendo_color = green

    apple_owned_color = ((255,255,255))
    microsoft_owned_color = ((255,255,255))
    bmw_owned_color = ((255,255,255))
    mcdonalds_owned_color = ((255,255,255))
    nintendo_owned_color = ((255,255,255))

    apple_buyprice = 0
    microsoft_buyprice = 0
    bmw_buyprice = 0
    mcdonalds_buyprice = 0
    nintendo_buyprice = 0

    apple_lastprice = apple_price
    microsoft_lastprice = microsoft_price
    bmw_lastprice = bmw_price
    mcdonalds_lastprice = mcdonalds_price
    nintendo_lastprice = nintendo_price

    MAX_DAYS = 60
    market_state = "normal"
    market_timer = 0

    apple_ohlc = []
    microsoft_ohlc = []
    bmw_ohlc = []
    mcdonalds_ohlc = []
    nintendo_ohlc = []

    stock_graphs = {}

def update_prices():
    global apple_price, microsoft_price, bmw_price
    global mcdonalds_price, nintendo_price
    global market_state, market_timer

    market_timer += 1

    # ---- MARKET STATE TRANSITIONS (more dramatic) ----
    if market_state == "normal" and random.random() < 0.06:
        market_state = "boom"
        market_timer = 0

    elif market_state == "boom" and market_timer > random.randint(4, 7):
        market_state = "bubble"
        market_timer = 0

    elif market_state == "bubble" and random.random() < 0.35:
        market_state = "crash"
        market_timer = 0

    elif market_state == "crash" and market_timer > random.randint(3, 6):
        market_state = "normal"
        market_timer = 0

    # ---- MARKET FORCE ----
    if market_state == "boom":
        market_drift = +6
        volatility = 1.2

    elif market_state == "bubble":
        market_drift = +2   # still up… but fragile
        volatility = 2.2

    elif market_state == "crash":
        market_drift = -10
        volatility = 2.8

    else:  # normal
        market_drift = 0
        volatility = 1.0

    # ---- STOCK BEHAVIOR ----

    # APPLE – defensive growth, overbought correction
    apple_price += int(
        random.uniform(-4, 6) * volatility
        + market_drift * 0.4
        - max(0, apple_price - 120) * 0.03   # soft cap
    )

    # MICROSOFT – momentum but slower to react
    microsoft_price += int(
        random.uniform(-6, 8) * volatility
        + market_drift * 0.5
        - max(0, microsoft_price - 140) * 0.025
    )

    # BMW – cyclical, trader-friendly
    bmw_price += int(
        random.uniform(-14, 16) * volatility
        + market_drift * 0.9
        - max(0, bmw_price - 100) * 0.05
    )

    # MCDONALDS – defensive, boring (by design)
    mcdonalds_price += int(
        random.uniform(-3, 4) * volatility
        + market_drift * 0.2
    )

    # NINTENDO – momentum stock, NOT pure chaos
    momentum = random.uniform(-20, 30) * volatility
    if random.random() < 0.6:
        momentum *= 1.4  # trends persist

    nintendo_price += int(
        momentum
        + market_drift * 1.1
    )

    # ---- PRICE FLOORS ----
    apple_price = max(10, apple_price)
    microsoft_price = max(10, microsoft_price)
    bmw_price = max(8, bmw_price)
    mcdonalds_price = max(12, mcdonalds_price)
    nintendo_price = max(5, nintendo_price)

def make_ohlc(prev_close, close_price, wick_factor=1.5):
    body = abs(close_price - prev_close)

    # Minimum wick so flat days still look normal
    body = max(body, close_price * 0.005)

    wick = body * random.uniform(0.5, wick_factor)

    high = max(prev_close, close_price) + wick
    low = min(prev_close, close_price) - wick

    return (prev_close, high, low, close_price)

def update_ohlc_histories():
    global apple_ohlc, microsoft_ohlc, bmw_ohlc, mcdonalds_ohlc, nintendo_ohlc

    if apple_ohlc:
        apple_ohlc.append(make_ohlc(apple_ohlc[-1][3], apple_price, 0.02))
        microsoft_ohlc.append(make_ohlc(microsoft_ohlc[-1][3], microsoft_price, 0.03))
        bmw_ohlc.append(make_ohlc(bmw_ohlc[-1][3], bmw_price, 0.06))
        mcdonalds_ohlc.append(make_ohlc(mcdonalds_ohlc[-1][3], mcdonalds_price, 0.015))
        nintendo_ohlc.append(make_ohlc(nintendo_ohlc[-1][3], nintendo_price, 0.08))
    else:
        # first day bootstrap
        apple_ohlc.append((apple_price, apple_price, apple_price, apple_price))
        microsoft_ohlc.append((microsoft_price, microsoft_price, microsoft_price, microsoft_price))
        bmw_ohlc.append((bmw_price, bmw_price, bmw_price, bmw_price))
        mcdonalds_ohlc.append((mcdonalds_price, mcdonalds_price, mcdonalds_price, mcdonalds_price))
        nintendo_ohlc.append((nintendo_price, nintendo_price, nintendo_price, nintendo_price))

    # keep last 60 days
    apple_ohlc = apple_ohlc[-MAX_DAYS:]
    microsoft_ohlc = microsoft_ohlc[-MAX_DAYS:]
    bmw_ohlc = bmw_ohlc[-MAX_DAYS:]
    mcdonalds_ohlc = mcdonalds_ohlc[-MAX_DAYS:]
    nintendo_ohlc = nintendo_ohlc[-MAX_DAYS:]

def draw_candlesticks(ax, ohlc, title):
    ax.clear()
    ax.set_title(title)
    ax.set_xlim(0, len(ohlc))
    ax.grid(alpha=0.3)

    for i, (o, h, l, c) in enumerate(ohlc):
        color = "green" if c >= o else "red"
        # Wick
        ax.plot([i, i], [l, h], color=color, linewidth=1)
        # Body
        ax.add_patch(
            plt.Rectangle(
                (i - 0.3, min(o, c)),
                0.6,
                abs(c - o) or 0.1,
                color=color,
                alpha=0.8
            )
        )

def update_all_graphs():
    global stock_graphs

    update_ohlc_histories()

    for stock_name, ohlc in [
        ("apple", apple_ohlc),
        ("microsoft", microsoft_ohlc),
        ("bmw", bmw_ohlc),
        ("mcdonalds", mcdonalds_ohlc),
        ("nintendo", nintendo_ohlc),
    ]:
        # Create figure
        fig = plt.figure(figsize=(7, 4), dpi=100)
        ax = fig.add_axes([0.04, 0.06, 0.92, 0.9])

        draw_candlesticks(ax, ohlc, stock_name.capitalize())

        # Convert to pygame surface
        stock_graphs[stock_name] = fig_to_surface(fig)

        # IMPORTANT: free memory
        plt.close(fig)


def fig_to_surface(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="PNG", transparent=True)
    buf.seek(0)
    image = pygame.image.load(buf).convert_alpha()
    buf.close()
    return image

if True:
    loading_screen = pygame.image.load("assets/loading_screen.png").convert_alpha()
    
    background = pygame.image.load("assets/background.png").convert_alpha()

    apple_button_img = pygame.image.load("assets/apple_button.png").convert_alpha()
    microsoft_button_img = pygame.image.load("assets/microsoft_button.png").convert_alpha()
    bmw_button_img = pygame.image.load("assets/bmw_button.png").convert_alpha()
    mcdonalds_button_img = pygame.image.load("assets/mcdonalds_button.png").convert_alpha()
    nintendo_button_img = pygame.image.load("assets/nintendo_button.png").convert_alpha()

    nextday_button_img = pygame.image.load("assets/nextday_button.png").convert_alpha()
    nextday10_button_img = pygame.image.load("assets/nextday10_button.png").convert_alpha()
    plus_button_img = pygame.image.load("assets/plus_button.png").convert_alpha()
    plus20_button_img = pygame.image.load("assets/plus20_button.png").convert_alpha()
    min_button_img = pygame.image.load("assets/min_button.png").convert_alpha()
    min20_button_img = pygame.image.load("assets/min20_button.png").convert_alpha()
    max_button_img = pygame.image.load("assets/max_button.png").convert_alpha()
    buy_button_img = pygame.image.load("assets/buy_button.png").convert_alpha()
    sell_button_img = pygame.image.load("assets/sell_button.png").convert_alpha()

    nextday_button_clicked_img = pygame.image.load("assets/nextday_button_clicked.png").convert_alpha()
    nextday10_button_clicked_img = pygame.image.load("assets/nextday10_button_clicked.png").convert_alpha()
    plus_button_clicked_img = pygame.image.load("assets/plus_button_clicked.png").convert_alpha()
    plus20_button_clicked_img = pygame.image.load("assets/plus20_button_clicked.png").convert_alpha()
    min_button_clicked_img = pygame.image.load("assets/min_button_clicked.png").convert_alpha()
    min20_button_clicked_img = pygame.image.load("assets/min20_button_clicked.png").convert_alpha()
    max_button_clicked_img = pygame.image.load("assets/max_button_clicked.png").convert_alpha()
    buy_button_clicked_img = pygame.image.load("assets/buy_button_clicked.png").convert_alpha()
    sell_button_clicked_img = pygame.image.load("assets/sell_button_clicked.png").convert_alpha()

if True:
    apple_button = apple_button_img.get_rect(topleft=(1055, 12))
    microsoft_button = microsoft_button_img.get_rect(topleft=(1055, 105))
    bmw_button = bmw_button_img.get_rect(topleft=(1055, 198))
    mcdonalds_button = mcdonalds_button_img.get_rect(topleft=(1055, 291))
    nintendo_button = nintendo_button_img.get_rect(topleft=(1055, 383))
    
    nextday_button = nextday_button_img.get_rect(topleft=(268, 470))
    nextday10_button = nextday10_button_img.get_rect(topleft=(326, 470))
    plus_button = plus_button_img.get_rect(topleft=(632, 470))
    min_button = min_button_img.get_rect(topleft=(500, 470))
    plus20_button = plus20_button_img.get_rect(topleft=(672, 470))
    min20_button = min20_button_img.get_rect(topleft=(460, 470))
    max_button = max_button_img.get_rect(topleft=(713, 470))
    buy_button = buy_button_img.get_rect(topleft=(934, 470))
    sell_button = sell_button_img.get_rect(topleft=(825, 470))

if True:
    nextday_button_clicked = False
    nextday10_button_clicked = False
    min20_button_clicked = False
    min_button_clicked = False
    plus_button_clicked = False
    plus20_button_clicked = False
    max_button_clicked = False
    sell_button_clicked = False
    buy_button_clicked = False

    nextday_button_clicktime = 0
    nextday10_button_clicktime = 0
    min20_button_clicktime = 0
    min_button_clicktime = 0
    plus20_button_clicktime = 0
    plus_button_clicktime = 0
    max_button_clicktime = 0
    sell_button_clicktime = 0
    buy_button_clicktime = 0

CLICK_DURATION = 80
running = True

screen.blit(loading_screen, (0,0))
pygame.display.update()

for i in range(60):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    update_prices()
    update_all_graphs()

    load_progress = font.render(f"{i+1}/60", True, (255, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(loading_screen, (0, 0))
    screen.blit(load_progress, (585, 535))
    pygame.display.update()
    pygame.time.delay(5)

while running:
    now = pygame.time.get_ticks()
    networth = (balance + (apple_owned * apple_price) + (microsoft_owned * microsoft_price)
    + (bmw_owned * bmw_price) + (mcdonalds_owned * mcdonalds_price) + (nintendo_owned * nintendo_price))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if plus_button.collidepoint(pos):
                plus_button_clicked = True
                plus_button_clicktime = now
                amount += 1
                mouse_sound.play()

            if min_button.collidepoint(pos) and amount - 1 >= 0:
                min_button_clicked = True
                min_button_clicktime = now
                amount -= 1
                mouse_sound.play()

            if plus20_button.collidepoint(pos):
                plus20_button_clicked = True
                plus20_button_clicktime = now
                amount += 20
                mouse_sound.play()

            if min20_button.collidepoint(pos) and amount - 20 >= 0:
                min20_button_clicked = True
                min20_button_clicktime = now
                amount -= 20
                mouse_sound.play()

            if max_button.collidepoint(pos):
                max_button_clicked = True
                max_button_clicktime = now
                mouse_sound.play()
                if selected_stock == "apple":
                    amount = apple_owned
                if selected_stock == "microsoft":
                    amount = microsoft_owned
                if selected_stock == "bmw":
                    amount = bmw_owned
                if selected_stock == "mcdonalds":
                    amount = mcdonalds_owned
                if selected_stock == "nintendo":
                    amount = nintendo_owned

            if nextday_button.collidepoint(pos):
                nextday_button_clicked = True
                nextday_button_clicktime = now
                day += 1
                level_up_sound.play()
                
                apple_lastprice = apple_price
                microsoft_lastprice = microsoft_price
                bmw_lastprice = bmw_price
                mcdonalds_lastprice = mcdonalds_price
                nintendo_lastprice = nintendo_price

                update_prices()
                update_all_graphs()
            
            if nextday10_button.collidepoint(pos):
                nextday10_button_clicked = True
                nextday10_button_clicktime = now
                day += 10
                level_up_sound.play()
                
                apple_lastprice = apple_price
                microsoft_lastprice = microsoft_price
                bmw_lastprice = bmw_price
                mcdonalds_lastprice = mcdonalds_price
                nintendo_lastprice = nintendo_price
                
                for i in range(10):
                    update_prices()
                    update_all_graphs()

            if buy_button.collidepoint(pos):
                buy_button_clicked = True
                buy_button_clicktime = now
                mouse_sound.play()
                if selected_stock == "apple" and balance - apple_price * amount >= 0:
                    balance -= apple_price * amount
                    apple_owned += amount
                    apple_buyprice += apple_price * amount
                    amount = 0

                if selected_stock == "microsoft" and balance - microsoft_price * amount >= 0:
                    balance -= microsoft_price * amount
                    microsoft_owned += amount
                    microsoft_buyprice += microsoft_price * amount
                    amount = 0

                if selected_stock == "bmw" and balance - bmw_price * amount >= 0:
                    balance -= bmw_price * amount
                    bmw_owned += amount
                    bmw_buyprice += bmw_price * amount
                    amount = 0

                if selected_stock == "mcdonalds" and balance - mcdonalds_price * amount >= 0:
                    balance -= mcdonalds_price * amount
                    mcdonalds_owned += amount
                    mcdonalds_buyprice += mcdonalds_price * amount
                    amount = 0

                if selected_stock == "nintendo" and balance - nintendo_price * amount >= 0:
                    balance -= nintendo_price * amount
                    nintendo_owned += amount
                    nintendo_buyprice += nintendo_price * amount
                    amount = 0

            if sell_button.collidepoint(pos):
                sell_button_clicked = True
                sell_button_clicktime = now
                mouse_sound.play()
                
                if selected_stock == "apple" and apple_owned >= amount and amount > 0:
                    avg_price = apple_buyprice / apple_owned
                    apple_owned -= amount
                    apple_buyprice -= avg_price * amount
                    balance += apple_price * amount
                    if apple_owned == 0:
                        apple_buyprice = 0
                    amount = 0

                if selected_stock == "microsoft" and microsoft_owned >= amount and amount > 0:
                    avg_price = microsoft_buyprice / microsoft_owned
                    microsoft_owned -= amount
                    microsoft_buyprice -= avg_price * amount
                    balance += microsoft_price * amount
                    if microsoft_owned == 0:
                        microsoft_buyprice = 0
                    amount = 0

                if selected_stock == "bmw" and bmw_owned >= amount and amount > 0:
                    avg_price = bmw_buyprice / bmw_owned
                    bmw_owned -= amount
                    bmw_buyprice -= avg_price * amount
                    balance += bmw_price * amount
                    if bmw_owned == 0:
                        bmw_buyprice = 0
                    amount = 0

                if selected_stock == "mcdonalds" and mcdonalds_owned >= amount and amount > 0:
                    avg_price = mcdonalds_buyprice / mcdonalds_owned
                    mcdonalds_owned -= amount
                    mcdonalds_buyprice -= avg_price * amount
                    balance += mcdonalds_price * amount
                    if mcdonalds_owned == 0:
                        mcdonalds_buyprice = 0
                    amount = 0

                if selected_stock == "nintendo" and nintendo_owned >= amount and amount > 0:
                    avg_price = nintendo_buyprice / nintendo_owned
                    nintendo_owned -= amount
                    nintendo_buyprice -= avg_price * amount
                    balance += nintendo_price * amount
                    if nintendo_owned == 0:
                        nintendo_buyprice = 0
                    amount = 0
                
            if apple_button.collidepoint(pos):
                selected_stock = "apple" 
                mouse_sound.play()

            if microsoft_button.collidepoint(pos):
                selected_stock = "microsoft"
                mouse_sound.play()

            if bmw_button.collidepoint(pos):
                selected_stock = "bmw"
                mouse_sound.play()

            if mcdonalds_button.collidepoint(pos):
                selected_stock = "mcdonalds"
                mouse_sound.play()

            if nintendo_button.collidepoint(pos):
                selected_stock = "nintendo"
                mouse_sound.play()
    
    if True:
        if apple_price * apple_owned - apple_buyprice > 0:
            apple_owned_color = green
        elif apple_price * apple_owned - apple_buyprice == 0:
            apple_owned_color = ((255,255,255))
        else:
            apple_owned_color = red

        if microsoft_price * microsoft_owned - microsoft_buyprice > 0:
            microsoft_owned_color = green
        elif microsoft_price * microsoft_owned - microsoft_buyprice == 0:
            microsoft_owned_color = ((255,255,255))
        else:
            microsoft_owned_color = red
        
        if bmw_price * bmw_owned - bmw_buyprice > 0:
            bmw_owned_color = green
        elif bmw_price * bmw_owned - bmw_buyprice == 0:
            bmw_owned_color = ((255,255,255))
        else:
            bmw_owned_color = red
        
        if mcdonalds_price * mcdonalds_owned - mcdonalds_buyprice > 0:
            mcdonalds_owned_color = green
        elif mcdonalds_price * mcdonalds_owned - mcdonalds_buyprice == 0:
            mcdonalds_owned_color = ((255,255,255))
        else:
            mcdonalds_owned_color = red
        
        if nintendo_price * nintendo_owned - nintendo_buyprice > 0:
            nintendo_owned_color = green
        elif nintendo_price * nintendo_owned - nintendo_buyprice == 0:
            nintendo_owned_color = ((255,255,255))
        else:
            nintendo_owned_color = red

    if True:
        if apple_lastprice < apple_price:
            apple_color = green
        elif apple_lastprice == apple_price:
            apple_color = ((255,255,255))
        else:
            apple_color = red
        
        if microsoft_lastprice < microsoft_price:
            microsoft_color = green
        elif microsoft_lastprice == microsoft_price:
            microsoft_color = ((255,255,255))
        else:
            microsoft_color = red

        if bmw_lastprice < bmw_price:
            bmw_color = green
        elif bmw_lastprice == bmw_price:
            bmw_color = ((255,255,255))
        else:
            bmw_color = red
        
        if mcdonalds_lastprice < mcdonalds_price:
            mcdonalds_color = green
        elif mcdonalds_lastprice == mcdonalds_price:
            mcdonalds_color = ((255,255,255))
        else:
            mcdonalds_color = red

        if nintendo_lastprice < nintendo_price:
            nintendo_color = green
        elif nintendo_lastprice == nintendo_price:
            nintendo_color = ((255,255,255))
        else:
            nintendo_color = red
        
    if True:
        if plus_button_clicked and now - plus_button_clicktime > CLICK_DURATION:
            plus_button_clicked = False
        if min_button_clicked and now - min_button_clicktime > CLICK_DURATION:
            min_button_clicked = False
        if plus20_button_clicked and now - plus20_button_clicktime > CLICK_DURATION:
            plus20_button_clicked = False
        if min20_button_clicked and now - min20_button_clicktime > CLICK_DURATION:
            min20_button_clicked = False
        if nextday_button_clicked and now - nextday_button_clicktime > CLICK_DURATION:
            nextday_button_clicked = False
        if nextday10_button_clicked and now - nextday10_button_clicktime > CLICK_DURATION:
            nextday10_button_clicked = False
        if max_button_clicked and now - max_button_clicktime > CLICK_DURATION:
            max_button_clicked = False
        if buy_button_clicked and now - buy_button_clicktime > CLICK_DURATION:
            buy_button_clicked = False
        if sell_button_clicked and now - sell_button_clicktime > CLICK_DURATION:
            sell_button_clicked = False
    
    if True:
        market_state_text = smallfont.render(market_state, True, (255,255,255))
        
        balance_text = font.render(format_balance(balance), True, (255, 255, 255))
        networth_text = font.render(format_balance(networth), True, (255, 255, 255))
        day_text = font.render(f"day {day}", True, (255, 255, 255))
        amount_text = smallerfont.render(str(amount), True, (0, 0, 0))

        apple_text = font.render(format_balance(apple_price), True, apple_color)
        microsoft_text = font.render(format_balance(microsoft_price), True, microsoft_color)
        bmw_text = font.render(format_balance(bmw_price), True, bmw_color)
        mcdonalds_text = font.render(format_balance(mcdonalds_price), True, mcdonalds_color)
        nintendo_text = font.render(format_balance(nintendo_price), True, nintendo_color)

        apple_owned_text = smallfont.render(f"apple: {apple_owned}", True, apple_owned_color)
        microsoft_owned_text = smallfont.render(f"microsoft: {microsoft_owned}", True, microsoft_owned_color)
        bmw_owned_text = smallfont.render(f"bmw: {bmw_owned}", True, bmw_owned_color)
        mcdonalds_owned_text = smallfont.render(f"mcdonalds: {mcdonalds_owned}", True, mcdonalds_owned_color)
        nintendo_owned_text = smallfont.render(f"nintendo: {nintendo_owned}", True, nintendo_owned_color)
        
        apple_percentage = profit_percentage(apple_owned, apple_price, apple_buyprice)
        microsoft_percentage = profit_percentage(microsoft_owned, microsoft_price, microsoft_buyprice)
        bmw_percentage = profit_percentage(bmw_owned, bmw_price, bmw_buyprice)
        mcdonalds_percentage = profit_percentage(mcdonalds_owned, mcdonalds_price, mcdonalds_buyprice)
        nintendo_percentage = profit_percentage(nintendo_owned, nintendo_price, nintendo_buyprice)

        apple_profit = smallerfont.render(f"{format_balance(apple_price * apple_owned - apple_buyprice)}   {apple_percentage}", True, apple_owned_color)
        microsoft_profit = smallerfont.render(f"{format_balance(microsoft_price * microsoft_owned - microsoft_buyprice)}   {microsoft_percentage}", True, microsoft_owned_color)
        bmw_profit = smallerfont.render(f"{format_balance(bmw_price * bmw_owned - bmw_buyprice)}   {bmw_percentage}", True, bmw_owned_color)
        mcdonalds_profit = smallerfont.render(f"{format_balance(mcdonalds_price * mcdonalds_owned - mcdonalds_buyprice)}   {mcdonalds_percentage}", True, mcdonalds_owned_color)
        nintendo_profit = smallerfont.render(f"{format_balance(nintendo_price * nintendo_owned - nintendo_buyprice)}   {nintendo_percentage}", True, nintendo_owned_color)

        screen.blit(background, (0, 0))

        screen.blit(stock_graphs[selected_stock], (285, 37))

        screen.blit(balance_text, (42, 14))
        screen.blit(networth_text, (42, 465))
        #screen.blit(day_text, (1107, 467))
        screen.blit(amount_text, (555, 473))
        screen.blit(market_state_text, (1107,467))

        screen.blit(apple_owned_text, (18, 80))
        screen.blit(microsoft_owned_text, (18, 155))
        screen.blit(bmw_owned_text, (18, 230))
        screen.blit(mcdonalds_owned_text, (18, 305))
        screen.blit(nintendo_owned_text, (18, 380))

        screen.blit(apple_profit, (18, 110))
        screen.blit(microsoft_profit, (18, 185))
        screen.blit(bmw_profit, (18, 260))
        screen.blit(mcdonalds_profit, (18, 335))
        screen.blit(nintendo_profit, (18, 410))

        screen.blit(apple_button_img, apple_button)
        screen.blit(microsoft_button_img, microsoft_button)
        screen.blit(bmw_button_img, bmw_button)
        screen.blit(mcdonalds_button_img, mcdonalds_button)
        screen.blit(nintendo_button_img, nintendo_button)

        screen.blit(apple_text, (1072,25))
        screen.blit(microsoft_text, (1072,118))
        screen.blit(bmw_text, (1072,211))
        screen.blit(mcdonalds_text, (1072,304))
        screen.blit(nintendo_text, (1072,397))

        screen.blit(nextday_button_clicked_img if nextday_button_clicked else nextday_button_img, nextday_button)
        screen.blit(nextday10_button_clicked_img if nextday10_button_clicked else nextday10_button_img, nextday10_button)
        screen.blit(plus_button_clicked_img if plus_button_clicked else plus_button_img, plus_button)
        screen.blit(plus20_button_clicked_img if plus20_button_clicked else plus20_button_img, plus20_button)
        screen.blit(min_button_clicked_img if min_button_clicked else min_button_img, min_button)
        screen.blit(min20_button_clicked_img if min20_button_clicked else min20_button_img, min20_button)
        screen.blit(max_button_clicked_img if max_button_clicked else max_button_img, max_button)
        screen.blit(buy_button_clicked_img if buy_button_clicked else buy_button_img, buy_button)
        screen.blit(sell_button_clicked_img if sell_button_clicked else sell_button_img, sell_button)

    pygame.display.update()
    clock.tick(60)
pygame.quit()