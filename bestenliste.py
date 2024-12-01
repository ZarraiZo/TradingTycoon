import pygame
from tkinter import messagebox
import sqlite3
from datetime import datetime
import login

def zeigeBestenliste(fenster_width, fenster_height):
    pygame.init()
    fenster = pygame.display.set_mode((fenster_width, fenster_height))
    pygame.display.set_caption("Trading Tycoon - Bestenliste")

    black = (0, 0, 0)
    green = (0, 255, 0)
    turquoise = (64, 224, 208)
    button_color = (0, 0, 0)
    red = (255, 0, 0)
    white = (255, 255, 255)
    dark_black = (30, 30, 30)

    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)
    table_font = pygame.font.Font(None, 30)
    status_font = pygame.font.Font(None, 20)

    title_text = font.render("Bestenliste", True, green)
    center_x = fenster_width // 2
    center_y = fenster_height // 2
    title_rect = title_text.get_rect(center=(center_x, center_y - 450))

    button_height = 80
    button_width = 450

    buttons = [
        {"label": "Schließen", "rect": pygame.Rect(center_x - button_width // 2, center_y + 350, button_width, button_height)},
    ]

    background_image = pygame.image.load("Hintergrund/Bild4.jpg").convert()
    background_image = pygame.transform.scale(background_image, (fenster_width, fenster_height))

    def get_current_datetime():
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT datum, uhrzeit FROM zeit LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            datum, uhrzeit = result
            return f"{datum} - {uhrzeit}"
        return "Kein Datum verfügbar"

    def fetch_users(page, users_per_page):
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()

        offset = (page - 1) * users_per_page
        cursor.execute("SELECT username, jahr, land, geld, depotwert FROM user ORDER BY geld + depotwert DESC LIMIT ? OFFSET ?", 
                       (users_per_page, offset))
        users = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM user")
        total_users = cursor.fetchone()[0]
        conn.close()
        return users, total_users

    def calculate_age(birth_year, current_year):
        return current_year - birth_year

    def get_user_data(username):
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT geld, depotwert FROM user WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {"geld": result[0], "depotwert": result[1]}
        return {"geld": 0.0, "depotwert": 0.0}

    current_year = datetime.now().year
    angemeldeter_user = login.get_active_user()
    current_page = 1
    users_per_page = 10

    spielstatus = True

    while spielstatus:
        fenster.fill(black)
        fenster.blit(background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        fenster.blit(title_text, title_rect)

        user_y_offset = center_y - 400
        if angemeldeter_user:
            benutzer_daten = get_user_data(angemeldeter_user)
            geld = benutzer_daten['geld']
            depotwert = benutzer_daten['depotwert']
            gesamtwert = geld + depotwert

            user_text = status_font.render(f"Angemeldet: {angemeldeter_user} | Geld: {geld}€ | Depotwert: {depotwert}€ | Gesamtwert: {gesamtwert}€", True, green)
        else:
            user_text = status_font.render("Kein Benutzer angemeldet", True, red)
        fenster.blit(user_text, (center_x - user_text.get_width() // 2, user_y_offset))

        users, total_users = fetch_users(current_page, users_per_page)
        total_pages = (total_users + users_per_page - 1) // users_per_page

        table_x = 50
        table_y = 200
        table_width = fenster_width - 100
        table_height = 500
        row_height = 40

        pygame.draw.rect(fenster, dark_black, (table_x, table_y, table_width, table_height))

        pygame.draw.rect(fenster, white, (table_x, table_y, table_width, table_height), width=2)

        headers = ["Platz", "Name", "Alter", "Land", "Gesamtwert (€)"]
        col_widths = [80, 300, 100, 150, 300]

        for col_idx, header in enumerate(headers):
            header_text = table_font.render(header, True, green)
            header_x = table_x + sum(col_widths[:col_idx])
            header_rect = header_text.get_rect(center=(header_x + col_widths[col_idx] // 2, table_y + row_height // 2))
            fenster.blit(header_text, header_rect)

        for row_idx, user in enumerate(users):
            username, geburtsjahr, land, geld, depotwert = user
            alter = calculate_age(geburtsjahr, current_year)
            gesamtwert = geld + depotwert
            platz = (current_page - 1) * users_per_page + row_idx + 1

            user_data = [platz, username, alter, land, f"{gesamtwert:.2f}"]

            for col_idx, value in enumerate(user_data):
                cell_x = table_x + sum(col_widths[:col_idx])
                cell_y = table_y + row_height * (row_idx + 1.5)

                cell_surface = pygame.Surface((col_widths[col_idx], row_height))
                cell_surface.fill(dark_black)
                fenster.blit(cell_surface, (cell_x, cell_y))

                cell_text = table_font.render(str(value), True, green if col_idx == 0 else turquoise)
                cell_rect = cell_text.get_rect(center=(cell_x + col_widths[col_idx] // 2, cell_y + row_height // 2))
                fenster.blit(cell_text, cell_rect)

        nav_y = table_y + table_height + 20
        if current_page > 1:
            prev_text = small_font.render("< Vorherige", True, green)
            prev_rect = prev_text.get_rect(center=(table_x + 100, nav_y))
            fenster.blit(prev_text, prev_rect)
        else:
            prev_rect = pygame.Rect(0, 0, 0, 0)

        if current_page < total_pages:
            next_text = small_font.render("Nächste >", True, green)
            next_rect = next_text.get_rect(center=(table_x + table_width - 100, nav_y))
            fenster.blit(next_text, next_rect)
        else:
            next_rect = pygame.Rect(0, 0, 0, 0)

        current_datetime = get_current_datetime()
        datetime_text = status_font.render(current_datetime, True, green)
        fenster.blit(datetime_text, (fenster_width - datetime_text.get_width() - 10, fenster_height - 30))

        rect = buttons[0]["rect"]
        hover = rect.collidepoint(mouse_pos)
        
        if hover:
            pygame.draw.rect(fenster, turquoise, rect, border_radius=20)
            button_text = small_font.render("Schließen", True, red)
        else:
            pygame.draw.rect(fenster, button_color, rect, border_radius=20)
            pygame.draw.rect(fenster, turquoise, rect, 5, border_radius=20)
            button_text = small_font.render("Schließen", True, green)

        button_text_rect = button_text.get_rect(center=rect.center)
        fenster.blit(button_text, button_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spielstatus = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if prev_rect.collidepoint(mouse_pos) and current_page > 1:
                    current_page -= 1
                elif next_rect.collidepoint(mouse_pos) and current_page < total_pages:
                    current_page += 1
                elif rect.collidepoint(mouse_pos):
                    return None

        pygame.display.update()