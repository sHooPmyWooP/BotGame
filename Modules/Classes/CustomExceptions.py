class NoShipsAvailableError(Exception):
    def __init__(self, celestial):
        print(f"You tried to send a fleet from {celestial} but no ships were available")
