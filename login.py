current_user = None

def set_active_user(username):
    """
    Setzt den aktuell angemeldeten Benutzer.
    
    Args:
        username (str): Der Benutzername des angemeldeten Benutzers.
    """
    global current_user
    current_user = username

def get_active_user():
    """
    Gibt den aktuell angemeldeten Benutzer zurück.
    
    Returns:
        str: Der Benutzername des angemeldeten Benutzers oder None, wenn niemand angemeldet ist.
    """
    global current_user
    return current_user

def clear_active_user():
    """
    Meldet den aktuellen Benutzer ab und setzt den Status auf None.
    """
    global current_user
    current_user = None

def is_user_logged_in():
    """
    Prüft, ob ein Benutzer angemeldet ist.
    
    Returns:
        bool: True, wenn ein Benutzer angemeldet ist, sonst False.
    """
    return current_user is not None

if __name__ == "__main__":
    print("Kein Benutzer angemeldet:", get_active_user())
    set_active_user("test_user")
    print("Aktuell angemeldeter Benutzer:", get_active_user())
    print("Ist ein Benutzer angemeldet?", is_user_logged_in())
    clear_active_user()
    print("Benutzer nach Abmeldung:", get_active_user())
    print("Ist ein Benutzer angemeldet?", is_user_logged_in())