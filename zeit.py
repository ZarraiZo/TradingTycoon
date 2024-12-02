import pygame
from datetime import datetime, timedelta
from tkinter import simpledialog, messagebox
import sqlite3
import login

def draw_rounded_button(surface, x, y, width, height, border_radius, border_color, center_color, border_thickness=2):
    pygame.draw.rect(surface, border_color, (x, y, width, height), border_radius=border_radius)
    pygame.draw.rect(surface, center_color,
                     (x + border_thickness, y + border_thickness, width - 2 * border_thickness, height - 2 * border_thickness),
                     border_radius=border_radius)

def aktualisiere_depotwerte():
    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT userid FROM user")
        benutzer = cursor.fetchall()

        for (user_id,) in benutzer:
            cursor.execute("""
                SELECT SUM(menge * wert_pro_einheit)
                FROM depot
                WHERE user_id = ?
            """, (user_id,))
            depotwert = cursor.fetchone()[0] or 0

            cursor.execute("UPDATE user SET depotwert = ? WHERE userid = ?", (depotwert, user_id))

        conn.commit()
        print("Depotwerte für alle Benutzer erfolgreich aktualisiert.")
    except sqlite3.Error as e:
        print(f"Fehler beim Aktualisieren der Depotwerte: {e}")
    finally:
        conn.close()

def aktualisiere_anleihen_und_depot():
    """
    Reduziert die Laufzeiten der Anleihen und Depot-Einträge,
    zahlt Zinsen und den Gesamtbetrag aus, und löscht abgelaufene Anleihen.
    """
    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE anleihen SET laufzeit = laufzeit - 1 WHERE laufzeit > 0")
        cursor.execute("UPDATE depot SET laufzeit = laufzeit - 1 WHERE laufzeit > 0")

        cursor.execute("""
            SELECT depot.user_id, depot.wert_pro_einheit, depot.menge, anleihen.zinssatz
            FROM depot
            JOIN anleihen ON depot.name = anleihen.name
            WHERE depot.laufzeit = 1
        """)
        auszahlungen = cursor.fetchall()

        for user_id, wert_pro_einheit, menge, zinssatz in auszahlungen:
            zinsen = wert_pro_einheit * menge * (zinssatz / 100)
            gesamtbetrag = wert_pro_einheit * menge
            gesamtauszahlung = zinsen + gesamtbetrag

            cursor.execute("UPDATE user SET geld = geld + ? WHERE userid = ?", (gesamtbetrag, user_id))
            print(f"Auszahlung von {gesamtbetrag:.2f}€ (inkl. Zinsen) an User {user_id}.")

        cursor.execute("DELETE FROM depot WHERE laufzeit <= 0")
        cursor.execute("DELETE FROM anleihen WHERE laufzeit <= 0")

        conn.commit()
        print("Anleihen und Depoteinträge erfolgreich aktualisiert.")
    except sqlite3.Error as e:
        print(f"Fehler bei der Aktualisierung von Anleihen und Depot: {e}")
    finally:
        conn.close()

def update_time(delta):
    """
    Aktualisiert die Zeit um einen bestimmten Zeitversatz.
    Reduziert die Laufzeiten, zahlt Zinsen aus und entfernt abgelaufene Anleihen.
    """
    nonlocal current_time
    previous_date = current_time.date()
    new_time = current_time + delta
    new_date = new_time.date()

    if new_date > previous_date:
        print("Ein neuer Tag beginnt, Laufzeiten werden angepasst...")
        aktualisiere_anleihen_und_depot()

    save_time_to_db(new_time)
    aktualisiere_depotwerte()

    current_time = new_time

def get_current_time_from_db():
    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()
    cursor.execute("SELECT datum FROM zeit LIMIT 1")
    result = cursor.fetchone()
    conn.close()

    if result:
        datum = result[0]
        return datetime.strptime(datum, "%d.%m.%Y")
    else:
        now = datetime(2025, 1, 1)
        save_time_to_db(now)
        return now

def save_time_to_db(new_time):
    conn = sqlite3.connect("datenbank.db")
    cursor = conn.cursor()
    datum = new_time.strftime("%d.%m.%Y")
    cursor.execute("DELETE FROM zeit")
    cursor.execute("INSERT INTO zeit (datum) VALUES (?)", (datum,))
    conn.commit()
    conn.close()

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
    small_time_font = pygame.font.Font(None, 20)

    title_text = font.render("Zeitsteuerung", True, green)
    center_x = fenster_width // 2
    center_y = fenster_height // 2
    title_rect = title_text.get_rect(center=(center_x, center_y - 450))

    button_height = 80
    button_width = 300

    buttons = [
        {"label": "Tag", "rect": pygame.Rect(center_x - button_width // 2, center_y - 100, button_width, button_height)},
        {"label": "Manuell", "rect": pygame.Rect(center_x - button_width // 2, center_y + 20, button_width, button_height)},
        {"label": "Schließen", "rect": pygame.Rect(center_x - button_width // 2, center_y + 140, button_width, button_height)},
    ]

    background_image = pygame.image.load("Hintergrund/Bild7.jpg").convert()
    background_image = pygame.transform.scale(background_image, (fenster_width, fenster_height))

    current_time = get_current_time_from_db()

    def get_user_data(username):
        conn = sqlite3.connect("datenbank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT geld, depotwert FROM user WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {"geld": result[0], "depotwert": result[1]}
        return {"geld": 0.0, "depotwert": 0.0}

    def set_manual_time():
        nonlocal current_time
        try:
            new_time_str = simpledialog.askstring("Zeit ändern", "Gib die neue Zeit im Format DD.MM.YYYY ein:")
            new_time = datetime.strptime(new_time_str, "%d.%m.%Y")
            current_time = new_time
            save_time_to_db(current_time)

            aktualisiere_anleihen_und_depot()
            aktualisiere_depotwerte()
        except (ValueError, TypeError):
            messagebox.showerror("Fehler", "Ungültiges Datum/Zeit-Format.")

    spielstatus = True

    while spielstatus:
        fenster.fill(black)
        fenster.blit(background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        fenster.blit(title_text, title_rect)

        time_text = font.render(current_time.strftime("%d.%m.%Y"), True, green)
        time_rect = time_text.get_rect(center=(center_x, center_y - 250))
        fenster.blit(time_text, time_rect)

        angemeldeter_user = login.get_active_user()
        if angemeldeter_user:
            benutzer_daten = get_user_data(angemeldeter_user)
            geld_text = status_font.render(f"Geld: {benutzer_daten['geld']}€", True, green)
            depot_text = status_font.render(f"Depotwert: {benutzer_daten['depotwert']}€", True, green)

            user_text = status_font.render(f"Angemeldet als: {angemeldeter_user}", True, green)
            fenster.blit(user_text, (center_x - user_text.get_width() // 2, center_y - 400))
            fenster.blit(geld_text, (center_x - geld_text.get_width() // 2, center_y - 375))
            fenster.blit(depot_text, (center_x - depot_text.get_width() // 2, center_y - 350))
        else:
            user_text = status_font.render("Kein Benutzer angemeldet", True, red)
            fenster.blit(user_text, (center_x - user_text.get_width() // 2, center_y - 400))

        bottom_right_text = small_time_font.render(current_time.strftime("%d.%m.%Y"), True, green)
        bottom_right_pos = (fenster_width - bottom_right_text.get_width() - 10, fenster_height - bottom_right_text.get_height() - 10)
        fenster.blit(bottom_right_text, bottom_right_pos)

        for button in buttons:
            draw_rounded_button(fenster, button["rect"].x, button["rect"].y, button_width, button_height, 15, green, button_color)
            button_label = small_font.render(button["label"], True, green)
            button_label_rect = button_label.get_rect(center=button["rect"].center)
            fenster.blit(button_label, button_label_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0]["rect"].collidepoint(mouse_pos):
                    update_time(timedelta(days=1))
                elif buttons[1]["rect"].collidepoint(mouse_pos):
                    set_manual_time()
                elif buttons[2]["rect"].collidepoint(mouse_pos):
                    pygame.quit()
                    quit()

        pygame.display.update()