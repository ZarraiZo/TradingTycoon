import pygame

pygame.init()

# Fenstergröße und Anzeige
fenster_width = 1800
fenster_height = 1000
fenster = pygame.display.set_mode((fenster_width, fenster_height))
pygame.display.set_caption("Trading Tycoon")

# Farben und Schriftarten
black = (0, 0, 0)
green = (0, 255, 0)
turquoise = (64, 224, 208)
button_color = (0, 0, 0)
red = (255, 0, 0)

font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 50)

# Titeltext
title_text = font.render("Trading Tycoon", True, green)
center_x = fenster_width // 2
center_y = fenster_height // 2
title_rect = title_text.get_rect(center=(center_x, center_y - 450))

# Button-Einstellungen
button_height = 80
button_width = 250

start_rect = pygame.Rect(center_x - button_width // 2, center_y, button_width, button_height)

# Funktion für abgerundete Buttons
def draw_rounded_button(surface, x, y, width, height, border_radius, border_color, center_color, border_thickness=2):
    pygame.draw.rect(surface, border_color, (x, y, width, height), border_radius=border_radius)
    pygame.draw.rect(surface, center_color,
                     (x + border_thickness, y + border_thickness, width - 2 * border_thickness, height - 2 * border_thickness),
                     border_radius=border_radius)

# Hintergrundbild
background_image = pygame.image.load("Hintergrund/Bild1.jpg").convert()
background_image = pygame.transform.scale(background_image, (fenster_width, fenster_height))

spielstatus = True

while spielstatus:
    fenster.fill(black)
    fenster.blit(background_image, (0, 0))
    mouse_pos = pygame.mouse.get_pos()

    # Button-Farben
    start_button_hover = start_rect.collidepoint(mouse_pos)
    start_center_color = turquoise if start_button_hover else button_color
    start_text_color = red if start_button_hover else green

    # Start-Button-Text
    start_text = small_font.render("Start", True, start_text_color)
    start_text_rect = start_text.get_rect(center=start_rect.center)

    # Zeichnen
    draw_rounded_button(fenster, start_rect.x, start_rect.y, button_width, button_height, 20, turquoise, start_center_color, border_thickness=3)
    fenster.blit(title_text, title_rect)
    fenster.blit(start_text, start_text_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            spielstatus = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_rect.collidepoint(mouse_pos):
                print("Spiel gestartet!")  # Hier könnte der Übergang in das Spiel erfolgen.

    pygame.display.update()

pygame.quit()