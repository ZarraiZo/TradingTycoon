import pygame
import sqlite3
from datetime import datetime
import login
from tkinter import messagebox

def zeigeAnleihen(fenster_width, fenster_height):
    pygame.init()
    fenster = pygame.display.set_mode((fenster_width, fenster_height))
    pygame.display.set_caption("Trading Tycoon - Anleihen")

    black = (0, 0, 0)
    green = (0, 255, 0)
    turquoise = (64, 224, 208)
    red = (255, 0, 0)
    white = (255, 255, 255)
    dark_black = (30, 30, 30)

    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)
    table_font = pygame.font.Font(None, 30)
    status_font = pygame.font.Font(None, 20)

    title_text = font.render("Anleihen", True, green)
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

    def fetch_anleihen():
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, zinssatz, laufzeit, wert FROM anleihen ORDER BY laufzeit ASC")
        anleihen = cursor.fetchall()
        conn.close()
        return anleihen

    def kaufe_anleihe(anleihe_id):
        angemeldeter_user = login.get_active_user()
        if not angemeldeter_user:
            messagebox.showerror("Fehler", "Kein Benutzer angemeldet. Bitte melden Sie sich an, um Anleihen zu kaufen.")
            return

        betrag = 1000
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT userid, geld FROM user WHERE username = ?", (angemeldeter_user,))
            result = cursor.fetchone()
            if not result:
                print("Fehler: Benutzer nicht gefunden.")
                return
            user_id, user_geld = result

            cursor.execute("SELECT name, zinssatz, laufzeit, wert FROM anleihen WHERE id = ?", (anleihe_id,))
            anleihe = cursor.fetchone()
            if not anleihe:
                print("Fehler: Anleihe nicht gefunden.")
                return

            name, zinssatz, laufzeit, wert = anleihe
            if wert < betrag:
                print("Nicht genügend Anleihen verfügbar!")
                return

            if user_geld < betrag:
                print("Nicht genügend Geld auf dem Konto!")
                return

            neuer_wert = wert - betrag
            cursor.execute("UPDATE anleihen SET wert = ? WHERE id = ?", (neuer_wert, anleihe_id))

            cursor.execute("""
                INSERT INTO depot (user_id, typ, name, menge, wert_pro_einheit, laufzeit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, "Anleihe", name, 1, betrag, laufzeit))

            neues_geld = user_geld - betrag
            cursor.execute("UPDATE user SET geld = ? WHERE userid = ?", (neues_geld, user_id))

            conn.commit()
            print("Anleihe erfolgreich gekauft, ins Depot eingetragen und Geld abgezogen!")
        except sqlite3.Error as e:
            print(f"Fehler beim Kauf der Anleihe: {e}")
        finally:
            conn.close()

    spielstatus = True

    while spielstatus:
        fenster.fill(black)
        fenster.blit(background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        fenster.blit(title_text, title_rect)

        anleihen_data = fetch_anleihen()

        table_x = 50
        table_y = 200
        table_width = fenster_width - 100
        table_height = 500
        row_height = 40

        pygame.draw.rect(fenster, dark_black, (table_x, table_y, table_width, table_height))
        pygame.draw.rect(fenster, white, (table_x, table_y, table_width, table_height), width=2)

        headers = ["Name", "Zinssatz (%)", "Laufzeit (Tage)", "Wert (€)", "Aktion"]
        col_widths = [300, 150, 150, 200, 150]

        for col_idx, header in enumerate(headers):
            header_text = table_font.render(header, True, green)
            header_x = table_x + sum(col_widths[:col_idx])
            header_rect = header_text.get_rect(center=(header_x + col_widths[col_idx] // 2, table_y + row_height // 2))
            fenster.blit(header_text, header_rect)

        kauf_buttons = []
        for row_idx, anleihe in enumerate(anleihen_data):
            anleihe_id, name, zinssatz, laufzeit, wert = anleihe
            row_y = table_y + row_height * (row_idx + 1.5)

            anleihe_data = [name, f"{zinssatz:.2f}", laufzeit, f"{wert:.2f}"]
            for col_idx, value in enumerate(anleihe_data):
                cell_x = table_x + sum(col_widths[:col_idx])
                cell_y = row_y

                cell_surface = pygame.Surface((col_widths[col_idx], row_height))
                cell_surface.fill(dark_black)
                fenster.blit(cell_surface, (cell_x, cell_y))

                cell_text = table_font.render(str(value), True, green)
                cell_rect = cell_text.get_rect(center=(cell_x + col_widths[col_idx] // 2, cell_y + row_height // 2))
                fenster.blit(cell_text, cell_rect)

            button_x = table_x + sum(col_widths[:-1])
            button_y = row_y
            button_rect = pygame.Rect(button_x, button_y, col_widths[-1], row_height)
            pygame.draw.rect(fenster, turquoise, button_rect, border_radius=10)

            button_text = table_font.render("Kauf", True, black)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            fenster.blit(button_text, button_text_rect)

            kauf_buttons.append((button_rect, anleihe_id))

        rect = buttons[0]["rect"]
        hover = rect.collidepoint(mouse_pos)
        if hover:
            pygame.draw.rect(fenster, turquoise, rect, border_radius=20)
            button_text = small_font.render("Schließen", True, red)
        else:
            pygame.draw.rect(fenster, black, rect, border_radius=20)
            pygame.draw.rect(fenster, turquoise, rect, 5, border_radius=20)
            button_text = small_font.render("Schließen", True, green)

        button_text_rect = button_text.get_rect(center=rect.center)
        fenster.blit(button_text, button_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spielstatus = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button_rect, anleihe_id in kauf_buttons:
                    if button_rect.collidepoint(mouse_pos):
                        kaufe_anleihe(anleihe_id)
                if rect.collidepoint(mouse_pos):
                    return None

        pygame.display.update()