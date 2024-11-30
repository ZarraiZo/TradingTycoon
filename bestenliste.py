import pygame
from tkinter import messagebox
import sqlite3
from datetime import datetime

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
    dark_black = (30, 30, 30)  # Dunkles Schwarz für die Hintergrundzellen

    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)
    table_font = pygame.font.Font(None, 30)
    status_font = pygame.font.Font(None, 25)

    title_text = font.render("Bestenliste", True, green)
    center_x = fenster_width // 2
    center_y = fenster_height // 2
    title_rect = title_text.get_rect(center=(center_x, center_y - 450))

    button_height = 80
    button_width = 450

    buttons = [
        {"label": "Schließen", "rect": pygame.Rect(center_x - button_width // 2, center_y + 350, button_width, button_height)},
    ]

    def draw_rounded_button(surface, x, y, width, height, border_radius, border_color, center_color, border_thickness=2):
        pygame.draw.rect(surface, border_color, (x, y, width, height), border_radius=border_radius)
        pygame.draw.rect(surface, center_color,
                         (x + border_thickness, y + border_thickness, width - 2 * border_thickness, height - 2 * border_thickness),
                         border_radius=border_radius)

    background_image = pygame.image.load("Hintergrund/Bild4.jpg").convert()
    background_image = pygame.transform.scale(background_image, (fenster_width, fenster_height))

    def get_current_year_from_db():
        """Holt das aktuelle Jahr aus der Tabelle 'zeit'."""
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT datum FROM zeit LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            datum = result[0]
            return int(datum.split('.')[-1])  # Extrahiere das Jahr (z.B., '2025')
        return datetime.now().year  # Fallback: aktuelles Systemjahr

    def fetch_users(page, users_per_page):
        """
        Holt Benutzer aus der Datenbank und gibt sie in Seiten aufgeteilt zurück.
        """
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()

        offset = (page - 1) * users_per_page
        cursor.execute("SELECT username, jahr, land, geld, depotwert FROM user ORDER BY geld + depotwert DESC LIMIT ? OFFSET ?", 
                       (users_per_page, offset))
        users = cursor.fetchall()

        # Gesamtanzahl der Benutzer für Seitenzahl-Berechnung
        cursor.execute("SELECT COUNT(*) FROM user")
        total_users = cursor.fetchone()[0]
        conn.close()

        return users, total_users

    def calculate_age(birth_year, current_year):
        """Berechnet das Alter eines Benutzers basierend auf dem Geburtsjahr."""
        return current_year - birth_year

    current_page = 1
    users_per_page = 10
    current_year = get_current_year_from_db()

    spielstatus = True

    while spielstatus:
        fenster.fill(black)
        fenster.blit(background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        fenster.blit(title_text, title_rect)

        # Daten abrufen
        users, total_users = fetch_users(current_page, users_per_page)
        total_pages = (total_users + users_per_page - 1) // users_per_page

        # Tabelle zeichnen
        table_x = 100
        table_y = 200
        table_width = fenster_width - 200
        table_height = 400
        row_height = 40

        pygame.draw.rect(fenster, white, (table_x, table_y, table_width, table_height), width=2)

        headers = ["Name", "Alter", "Land", "Gesamtwert (€)"]
        col_widths = [table_width // len(headers)] * len(headers)

        # Header zeichnen
        for col_idx, header in enumerate(headers):
            header_text = table_font.render(header, True, green)
            header_x = table_x + sum(col_widths[:col_idx])
            header_rect = header_text.get_rect(center=(header_x + col_widths[col_idx] // 2, table_y + row_height // 2))
            fenster.blit(header_text, header_rect)

        # Benutzer in die Tabelle einfügen
        for row_idx, user in enumerate(users):
            username, geburtsjahr, land, geld, depotwert = user
            alter = calculate_age(geburtsjahr, current_year)  # Hier wird das Jahr verwendet
            gesamtwert = geld + depotwert
            user_data = [username, alter, land, f"{gesamtwert:.2f}"]

            for col_idx, value in enumerate(user_data):
                cell_x = table_x + sum(col_widths[:col_idx])
                cell_y = table_y + row_height * (row_idx + 1.5)

                # Halbtransparenter schwarzer Hintergrund für die Zelle
                cell_surface = pygame.Surface((col_widths[col_idx], row_height))
                cell_surface.set_alpha(180)  # Transparenz (0-255)
                cell_surface.fill(dark_black)  # Dunkles Schwarz für den Hintergrund

                fenster.blit(cell_surface, (cell_x, cell_y))  # Zelle einfügen

                cell_text = table_font.render(str(value), True, turquoise)
                cell_rect = cell_text.get_rect(center=(cell_x + col_widths[col_idx] // 2, cell_y + row_height // 2))
                fenster.blit(cell_text, cell_rect)

        # Seiteninformationen anzeigen
        page_info = f"Seite {current_page} von {total_pages}"
        page_text = status_font.render(page_info, True, green)
        page_text_rect = page_text.get_rect(center=(fenster_width // 2, table_y + table_height + 40))
        fenster.blit(page_text, page_text_rect)

        # Schaltflächen zeichnen
        for button in buttons:
            rect = button["rect"]
            hover = rect.collidepoint(mouse_pos)
            center_color = turquoise if hover else button_color
            text_color = red if hover else green

            draw_rounded_button(fenster, rect.x, rect.y, button_width, button_height, 20, turquoise, center_color, border_thickness=3)
            button_text = small_font.render(button["label"], True, text_color)
            button_text_rect = button_text.get_rect(center=rect.center)
            fenster.blit(button_text, button_text_rect)

        # Navigation (vor/zurück)
        if current_page > 1:
            prev_text = small_font.render("< Vorherige", True, green)
            prev_rect = prev_text.get_rect(center=(table_x + 100, table_y + table_height + 40))
            fenster.blit(prev_text, prev_rect)

        if current_page < total_pages:
            next_text = small_font.render("Nächste >", True, green)
            next_rect = next_text.get_rect(center=(table_x + table_width - 100, table_y + table_height + 40))
            fenster.blit(next_text, next_rect)

        # Ereignisse abfangen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spielstatus = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_page > 1 and prev_rect.collidepoint(mouse_pos):
                    current_page -= 1
                elif current_page < total_pages and next_rect.collidepoint(mouse_pos):
                    current_page += 1
                for button in buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        if button["label"] == "Schließen":
                            return None

        pygame.display.update()