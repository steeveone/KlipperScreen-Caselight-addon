import logging
# Configuration
MACRO_WAKE = "CASELIGHT_ON"
MACRO_SLEEP = "CASELIGHT_OFF"

def send_macro(screen, macro_name):
    """Sends a G-code macro command using KlipperScreen's native WebSocket send_method."""
    try:
        # Check if the websocket client is connected and active
        if hasattr(screen, "_ws") and screen._ws and screen._ws.connected:
            logging.info(f"[Caselight Addon] Sending macro '{macro_name}' via native WebSocket method...")

            # The official KlipperScreen internal method to execute JSON-RPC commands
            # Method: printer.gcode.script, Params: {"script": "MACRO_NAME"}
            screen._ws.send_method("printer.gcode.script", {"script": macro_name})

        else:
            logging.error("[Caselight Addon] Native KlipperScreen WebSocket is not connected.")
    except Exception as e:
        logging.error(f"[Caselight Addon] Failed to send macro via native API: {e}")

def init(screen):
    """Initializes the addon and hooks into KlipperScreen events."""
    logging.info("[Caselight Addon] Initializing caselight handler extension...")

    # 1. Hook into screen WAKE event
    if hasattr(screen, 'wake_screen'):
        _original_wake = screen.wake_screen
        def custom_wake(*args, **kwargs):
            logging.info("[Caselight Addon] Screen woke up. Triggering WAKE macro.")
            send_macro(screen, MACRO_WAKE)
            return _original_wake(*args, **kwargs)
        screen.wake_screen = custom_wake
    else:
        logging.error("[Caselight Addon] Could not find wake_screen method!")

    # 2. Hook into screen BLANKING (Sleep) event via screensaver
    if hasattr(screen, 'screensaver') and hasattr(screen.screensaver, 'show'):
        _original_show = screen.screensaver.show
        def custom_show(*args, **kwargs):
            logging.info("[Caselight Addon] Screensaver activated. Triggering SLEEP macro.")
            send_macro(screen, MACRO_SLEEP)
            return _original_show(*args, **kwargs)
        screen.screensaver.show = custom_show
    else:
        logging.error("[Caselight Addon] Could not find screensaver module!")
