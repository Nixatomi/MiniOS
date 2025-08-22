import turtle as t
import random

t.speed(0)
t.hideturtle()
t.colormode(255)  
t.tracer(False)   

clicks = 0  # licznik kliknięć

# =====================
# Funkcja rysująca drzewko
# =====================
def draw_tree(x, y):
    """Rysuje proste drzewko w pozycji (x,y)."""
    t.penup()
    t.goto(x, y)
    t.pendown()
    
    # pień
    t.color("saddlebrown")
    t.begin_fill()
    for _ in range(2):
        t.forward(20)
        t.left(90)
        t.forward(40)
        t.left(90)
    t.end_fill()
    
    # korona
    t.penup(); t.goto(x+10, y+40); t.pendown()
    t.color("forestgreen")
    t.begin_fill()
    t.circle(30)
    t.end_fill()

# =====================
# Funkcja rysująca buźkę
# =====================
def draw_face(color="yellow"):
    """Rysuje buźkę w wybranym kolorze."""
    t.clear()
    
    # odrysuj drzewka po czyszczeniu
    draw_forest()
    
    # twarz
    t.penup(); t.goto(0,-100); t.pendown()
    t.color("black", color)  
    t.begin_fill()
    t.circle(100)
    t.end_fill()

    # lewe oko
    t.penup(); t.goto(-40,20); t.pendown()
    t.color("black", "black")
    t.begin_fill(); t.circle(10); t.end_fill()

    # prawe oko
    t.penup(); t.goto(40,20); t.pendown()
    t.begin_fill(); t.circle(10); t.end_fill()

    # uśmiech
    t.penup(); t.goto(-50,-10); t.setheading(-60); t.pendown()
    t.width(3)
    t.circle(60,120)
    t.width(1)

# =====================
# Tekst
# =====================
def draw_text():
    """Rysuje licznik i napis."""
    t.penup()
    t.color("black")
    t.goto(0,150)
    t.write(f"Kliknięcia: {clicks}", align="center", font=("Arial", 16, "bold"))
    
    t.goto(0,180)
    t.write("Zaraz wygrasz!", align="center", font=("Arial", 14, "italic"))

# =====================
# Kliknięcie myszką
# =====================
def change_color(x, y):
    global clicks
    clicks += 1
    
    # losowy kolor buzi
    new_face = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    
    draw_face(new_face)
    draw_text()
    t.update()

# =====================
# Rysowanie lasu
# =====================
def draw_forest():
    """Rysuje kilka drzew w tle."""
    positions = [(-200,-150), (-150,-120), (180,-140), (230,-130), (-250,-100)]
    for (x, y) in positions:
        draw_tree(x, y)

# =====================
# Start gry
# =====================
t.bgcolor("skyblue")  # tło tylko błękitne
draw_forest()
draw_face()
draw_text()
t.update()

# obsługa kliknięcia
t.onscreenclick(change_color, 1)

t.done()
