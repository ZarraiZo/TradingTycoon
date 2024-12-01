import pygame
from tkinter import simpledialog, messagebox
import sqlite3
import login

def zeigeMarkt(fenster_width, fenster_height, current_user=None):
    pygame.init()
    fenster = pygame.display.set_mode((fenster_width, fenster_height))
    pygame.display.set_caption("Trading Tycoon - Markt")

    black = (0, 0, 0)
    green = (0, 255, 0)
    turquoise = (64, 224, 208)
    button_color = (0, 0, 0)
    red = (255, 0, 0)

    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)
    status_font = pygame.font.Font(None, 25)
    small_time_font = pygame.font.Font(None, 20)

    title_text = font.render("Markt", True, green)
    center_x = fenster_width // 2
    center_y = fenster_height // 2
    title_rect = title_text.get_rect(center=(center_x, center_y - 450))

    button_height = 80
    button_width = 450

    buttons = [
        {"label": "Aktien kaufen", "rect": pygame.Rect(center_x - button_width // 2, center_y - 100, button_width, button_height)},
        {"label": "Aktien verkaufen", "rect": pygame.Rect(center_x - button_width // 2, center_y + 20, button_width, button_height)},
        {"label": "Depot ansehen", "rect": pygame.Rect(center_x - button_width // 2, center_y + 140, button_width, button_height)},
        {"label": "Schließen", "rect": pygame.Rect(center_x - button_width // 2, center_y + 260, button_width, button_height)},
    ]

    def draw_rounded_button(surface, x, y, width, height, border_radius, border_color, center_color, border_thickness=2):
        pygame.draw.rect(surface, border_color, (x, y, width, height), border_radius=border_radius)
        pygame.draw.rect(surface, center_color,
                         (x + border_thickness, y + border_thickness, width - 2 * border_thickness, height - 2 * border_thickness),
                         border_radius=border_radius)

    background_image = pygame.image.load("Hintergrund/Bild2.jpg").convert()
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
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT datum, uhrzeit FROM zeit LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            datum, uhrzeit = result
            return f"{datum} {uhrzeit}"
        else:
            return "01.01.2025 01:00"

    def depot_ansehen():
        angemeldeter_user = login.get_active_user()
        if not angemeldeter_user:
            messagebox.showerror("Fehler", "Kein Benutzer ist angemeldet.")
            return

        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT userid FROM user WHERE username = ?", (angemeldeter_user,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Fehler", "Benutzer nicht gefunden.")
                return
            user_id = result[0]

            cursor.execute("SELECT typ, name, menge, wert_pro_einheit, laufzeit FROM depot WHERE user_id = ?", (user_id,))
            depot = cursor.fetchall()
        except sqlite3.OperationalError as e:
            messagebox.showerror("Datenbankfehler", f"Fehler: {e}")
            return
        finally:
            conn.close()

        if not depot:
            messagebox.showinfo("Depot", "Ihr Depot ist leer.")
            return

        viewing = True
        while viewing:
            fenster.fill(black)
            fenster.blit(background_image, (0, 0))

            title_text = font.render(f"Depot von {angemeldeter_user}", True, green)
            fenster.blit(title_text, (fenster_width // 2 - title_text.get_width() // 2, 50))

            headers = ["Typ", "Name", "Menge", "Wert/Einheit (€)", "Laufzeit (Tage)"]
            row_height = 40
            start_y = 150

            for idx, header in enumerate(headers):
                header_text = small_font.render(header, True, green)
                fenster.blit(header_text, (50 + idx * 200, start_y))

            for row_idx, row in enumerate(depot):
                for col_idx, value in enumerate(row):
                    cell_text = status_font.render(str(value), True, green)
                    fenster.blit(cell_text, (50 + col_idx * 200, start_y + (row_idx + 1) * row_height))

            back_button_rect = pygame.Rect(fenster_width // 2 - 100, fenster_height - 100, 200, 50)
            pygame.draw.rect(fenster, turquoise, back_button_rect)
            back_button_text = small_font.render("Zurück", True, black)
            back_button_text_rect = back_button_text.get_rect(center=back_button_rect.center)
            fenster.blit(back_button_text, back_button_text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button_rect.collidepoint(pygame.mouse.get_pos()):
                        viewing = False

            pygame.display.update()

    def aktien_kaufen():
        messagebox.showinfo("Aktien kaufen", "Funktion zum Aktienkauf wird hier eingebaut.")

    def aktien_verkaufen():
        messagebox.showinfo("Aktien verkaufen", "Funktion zum Aktienverkauf wird hier eingebaut.")

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
                        if button["label"] == "Aktien kaufen":
                            aktien_kaufen()
                        elif button["label"] == "Aktien verkaufen":
                            aktien_verkaufen()
                        elif button["label"] == "Depot ansehen":
                            depot_ansehen()
                        elif button["label"] == "Schließen":
                            return None

        pygame.display.update()