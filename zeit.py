import pygame
from datetime import datetime, timedelta
from tkinter import simpledialog, messagebox
import sqlite3
import login

def draw_rounded_button(surface, x, y, width, height, border_radius, border_color, center_color, border_thickness=2):
    """
    Zeichnet einen Button mit abgerundeten Ecken.
    """
    pygame.draw.rect(surface, border_color, (x, y, width, height), border_radius=border_radius)
    pygame.draw.rect(surface, center_color,
                     (x + border_thickness, y + border_thickness, width - 2 * border_thickness, height - 2 * border_thickness),
                     border_radius=border_radius)

def zeigeZeit(fenster_width, fenster_height, current_user=None):
    pygame.init()
    fenster = pygame.display.set_mode((fenster_width, fenster_height))
    pygame.display.set_caption("Trading Tycoon - Zeit")

    black = (0, 0, 0)
    green = (0, 255, 0)
    turquoise = (64, 224, 208)
    button_color = (0, 0, 0)
    red = (255, 0, 0)

    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)
    status_font = pygame.font.Font(None, 25)

    title_text = font.render("Zeitsteuerung", True, green)
    center_x = fenster_width // 2
    center_y = fenster_height // 2
    title_rect = title_text.get_rect(center=(center_x, center_y - 450))

    button_height = 80
    button_width = 300

    buttons = [
        {"label": "Stunde", "rect": pygame.Rect(center_x - button_width // 2, center_y - 100, button_width, button_height)},
        {"label": "Manuell", "rect": pygame.Rect(center_x - button_width // 2, center_y + 20, button_width, button_height)},
        {"label": "Schließen", "rect": pygame.Rect(center_x - button_width // 2, center_y + 140, button_width, button_height)},
    ]

    background_image = pygame.image.load("Hintergrund/Bild7.jpg").convert()
    background_image = pygame.transform.scale(background_image, (fenster_width, fenster_height))

    def get_current_time_from_db():
        """Holt die aktuelle Zeit aus der Datenbank."""
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT datum, uhrzeit FROM zeit LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            datum, uhrzeit = result
            return datetime.strptime(f"{datum} {uhrzeit}", "%d.%m.%Y %H:%M")
        else:
            now = datetime(2025, 1, 1, 1, 0)
            save_time_to_db(now)
            return now

    def save_time_to_db(new_time):
        """Speichert die aktuelle Zeit in der Datenbank."""
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()
        datum = new_time.strftime("%d.%m.%Y")
        uhrzeit = new_time.strftime("%H:%M")
        cursor.execute("DELETE FROM zeit")
        cursor.execute("INSERT INTO zeit (datum, uhrzeit) VALUES (?, ?)", (datum, uhrzeit))
        conn.commit()
        conn.close()

    def update_time(delta):
        """Aktualisiert die Zeit um einen bestimmten Zeitversatz."""
        nonlocal current_time
        current_time += delta
        save_time_to_db(current_time)

    def set_manual_time():
        """Ermöglicht die manuelle Eingabe einer neuen Zeit."""
        nonlocal current_time
        try:
            new_time_str = simpledialog.askstring("Zeit ändern", "Gib die neue Zeit im Format DD.MM.YYYY HH:MM ein:")
            new_time = datetime.strptime(new_time_str, "%d.%m.%Y %H:%M")
            current_time = new_time
            save_time_to_db(current_time)
        except (ValueError, TypeError):
            messagebox.showerror("Fehler", "Ungültiges Datum/Zeit-Format.")

    current_time = get_current_time_from_db()

    spielstatus = True

    while spielstatus:
        fenster.fill(black)
        fenster.blit(background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        fenster.blit(title_text, title_rect)

        time_text = font.render(current_time.strftime("%d.%m.%Y %H:%M"), True, green)
        time_rect = time_text.get_rect(center=(center_x, center_y - 250))
        fenster.blit(time_text, time_rect)

        angemeldeter_user = login.get_active_user()
        if angemeldeter_user:
            user_text = status_font.render(f"Angemeldet als: {angemeldeter_user}", True, green)
            fenster.blit(user_text, (center_x - user_text.get_width() // 2, center_y - 400))
        else:
            user_text = status_font.render("Kein Benutzer angemeldet", True, red)
            fenster.blit(user_text, (center_x - user_text.get_width() // 2, center_y - 400))

        for button in buttons:
            rect = button["rect"]
            hover = rect.collidepoint(mouse_pos)
            center_color = turquoise if hover else button_color
            text_color = red if hover else green

            draw_rounded_button(fenster, rect.x, rect.y, button_width, button_height, 20, turquoise, center_color, border_thickness=3)
            button_text = small_font.render(button["label"], True, text_color)
            button_text_rect = button_text.get_rect(center=rect.center)
            fenster.blit(button_text, button_text_rect)

        datum_uhrzeit_text = small_font.render(current_time.strftime("%d.%m.%Y %H:%M"), True, green)
        datum_uhrzeit_rect = datum_uhrzeit_text.get_rect(bottomright=(fenster_width - 10, fenster_height - 10))
        fenster.blit(datum_uhrzeit_text, datum_uhrzeit_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spielstatus = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        if button["label"] == "Stunde":
                            update_time(timedelta(hours=1))
                        elif button["label"] == "Manuell":
                            set_manual_time()
                        elif button["label"] == "Schließen":
                            return

        pygame.display.update()