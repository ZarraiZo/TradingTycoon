﻿import pygame
import sqlite3
from datetime import datetime
from anmelden import zeigeAnmelden
from markt import zeigeMarkt
from zeit import zeigeZeit
from bestenliste import zeigeBestenliste
from anleihen import zeigeAnleihen
import login

pygame.init()

fenster_width = 1800
fenster_height = 1000
fenster = pygame.display.set_mode((fenster_width, fenster_height))
pygame.display.set_caption("Trading Tycoon")

black = (0, 0, 0)
green = (0, 255, 0)
turquoise = (64, 224, 208)
button_color = (0, 0, 0)
red = (255, 0, 0)

font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 50)
status_font = pygame.font.Font(None, 25)
small_time_font = pygame.font.Font(None, 20)

title_text = font.render("Trading Tycoon", True, green)
center_x = fenster_width // 2
center_y = fenster_height // 2
title_rect = title_text.get_rect(center=(center_x, center_y - 450))

button_height = 80
button_width = 250

buttons = [
    {"label": "Anmelden", "rect": pygame.Rect(center_x - button_width // 2, center_y - 200, button_width, button_height)},
    {"label": "Markt", "rect": pygame.Rect(center_x - button_width // 2, center_y - 80, button_width, button_height)},
    {"label": "Anleihen", "rect": pygame.Rect(center_x - button_width // 2, center_y + 40, button_width, button_height)},
    {"label": "Bestenliste", "rect": pygame.Rect(center_x - button_width // 2, center_y + 160, button_width, button_height)},
    {"label": "Zeit", "rect": pygame.Rect(center_x - button_width // 2, center_y + 280, button_width, button_height)},
    {"label": "Beenden", "rect": pygame.Rect(center_x - button_width // 2, center_y + 400, button_width, button_height)},
]

def draw_rounded_button(surface, x, y, width, height, border_radius, border_color, center_color, border_thickness=2):
    pygame.draw.rect(surface, border_color, (x, y, width, height), border_radius=border_radius)
    pygame.draw.rect(surface, center_color,
                     (x + border_thickness, y + border_thickness, width - 2 * border_thickness, height - 2 * border_thickness),
                     border_radius=border_radius)

background_image = pygame.image.load("Hintergrund/Bild1.jpg").convert()
background_image = pygame.transform.scale(background_image, (fenster_width, fenster_height))

def get_user_data(username):
    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    cursor.execute("SELECT geld, depotwert FROM user WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {"geld": result[0], "depotwert": result[1]}
    else:
        return {"geld": 0.0, "depotwert": 0.0}

def get_time_from_db():
    """Liest das Datum aus der Tabelle 'zeit' in der Datenbank."""
    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()
    cursor.execute("SELECT datum FROM zeit LIMIT 1")
    result = cursor.fetchone()
    conn.close()

    if result:
        datum = result[0]
        return datum
    else:
        return "01.01.2025"

spielstatus = True

while spielstatus:
    fenster.fill(black)
    fenster.blit(background_image, (0, 0))
    mouse_pos = pygame.mouse.get_pos()

    fenster.blit(title_text, title_rect)

    angemeldeter_user = login.get_active_user()
    if angemeldeter_user:
        benutzer_daten = get_user_data(angemeldeter_user)

        user_text = status_font.render(f"Angemeldet als: {angemeldeter_user}", True, green)
        geld_text = status_font.render(f"Geld: {benutzer_daten['geld']}€", True, green)
        depot_text = status_font.render(f"Depotwert: {benutzer_daten['depotwert']}€", True, green)

        fenster.blit(user_text, (center_x - user_text.get_width() // 2, center_y - 400))
        fenster.blit(geld_text, (center_x - geld_text.get_width() // 2, center_y - 375))
        fenster.blit(depot_text, (center_x - depot_text.get_width() // 2, center_y - 350))
    else:
        user_text = status_font.render("Kein Benutzer angemeldet", True, red)
        fenster.blit(user_text, (center_x - user_text.get_width() // 2, center_y - 400))

    db_time = get_time_from_db()
    bottom_right_text = small_time_font.render(db_time, True, green)
    bottom_right_pos = (fenster_width - bottom_right_text.get_width() - 10, fenster_height - bottom_right_text.get_height() - 10)
    fenster.blit(bottom_right_text, bottom_right_pos)

    for button in buttons:
        rect = button["rect"]
        hover = rect.collidepoint(mouse_pos)
        center_color = turquoise if hover else button_color
        text_color = red if hover else green

        draw_rounded_button(fenster, rect.x, rect.y, button_width, button_height, 20, turquoise, center_color, border_thickness=3)
        button_text = small_font.render(button["label"], True, text_color)
        button_text_rect = button_text.get_rect(center=rect.center)
        fenster.blit(button_text, button_text_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            spielstatus = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button["rect"].collidepoint(mouse_pos):
                    if button["label"] == "Anmelden":
                        zeigeAnmelden(fenster_width, fenster_height)
                    elif button["label"] == "Markt":
                        zeigeMarkt(fenster_width, fenster_height, current_user=login.get_active_user())
                    elif button["label"] == "Anleihen":
                        zeigeAnleihen(fenster_width, fenster_height)
                    elif button["label"] == "Zeit":
                        zeigeZeit(fenster_width, fenster_height)
                    elif button["label"] == "Bestenliste":
                        zeigeBestenliste(fenster_width, fenster_height)
                    elif button["label"] == "Beenden":
                        spielstatus = False

    pygame.display.update()

pygame.quit()