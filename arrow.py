import keyboard
import time
import sys
import threading
import atexit

# Global flag to control script execution
running = True
script_enabled = True

# Track the hotkey state
is_hotkey_active = False
suppressed_keys = set()

# Define the toggle key
TOGGLE_KEY = 'scroll lock'  # ScrollLock key to toggle the script on/off

# Define the activation key
ACTIVATION_KEY = 'caps lock'  # Changed from 'right alt' to 'caps lock'

def simulate_key(target_key, with_modifier=None):
    """Simulate pressing and releasing a key with an optional modifier."""
    try:
        if with_modifier:
            keyboard.press(with_modifier)
        keyboard.press(target_key)
        time.sleep(0.02)
        keyboard.release(target_key)
        if with_modifier:
            keyboard.release(with_modifier)
        return True
    except Exception as e:
        print(f"Error simulating key {target_key}: {e}")
        return False

def handle_hotkey(e):
    """Process key events when hotkey is active."""
    global is_hotkey_active, suppressed_keys
    
    # Only process if the script is enabled
    if not script_enabled:
        return True
    
    key = e.name.lower()
    
    # Handle key activation and deactivation
    if key == ACTIVATION_KEY:
        if e.event_type == keyboard.KEY_DOWN:
            is_hotkey_active = True
        elif e.event_type == keyboard.KEY_UP:
            is_hotkey_active = False
            suppressed_keys.clear()
        return False  # Suppress the caps lock key event to prevent state change
    
    # Process navigation when activation key is held down
    if is_hotkey_active:
        action_map = {
            'i': 'up', 'k': 'down', 'j': 'left', 'l': 'right',
            'u': 'home', 'o': 'end', 'h': 'page up', 'n': 'page down',
            'y': ('left', 'ctrl'), 'p': ('right', 'ctrl')
        }
        
        if e.event_type == keyboard.KEY_DOWN and key in action_map:
            action = action_map[key]
            if isinstance(action, tuple):
                simulate_key(action[0], action[1])
            else:
                simulate_key(action)
            suppressed_keys.add(key)
            return False  # Suppress keypress so it doesn't type
        
        elif e.event_type == keyboard.KEY_UP and key in suppressed_keys:
            suppressed_keys.remove(key)
            return False
    
    return True

def toggle_script():
    """Toggle the script on/off"""
    global script_enabled
    script_enabled = not script_enabled
    print(f"Script is now {'ENABLED' if script_enabled else 'DISABLED'}")

def emergency_shutdown():
    """Ensure all hooks are removed when exiting"""
    keyboard.unhook_all()
    print("All keyboard hooks removed")

def main():
    """
    Main function to run the script
    """
    print("=== Natural Key Navigator ===")
    print(f"Hold {ACTIVATION_KEY.upper()} and press these keys for navigation:")
    print("- I: Up arrow")
    print("- K: Down arrow")
    print("- J: Left arrow")
    print("- L: Right arrow")
    print("- U: Home")
    print("- O: End")
    print("- H: Page Up")
    print("- N: Page Down")
    print("- Y: Word left (Ctrl+Left)")
    print("- P: Word right (Ctrl+Right)")
    print("")
    print(f"Press {TOGGLE_KEY.upper()} to toggle the script on/off")
    print("Press Ctrl+C to exit")
    
    # Register cleanup function
    atexit.register(emergency_shutdown)
    
    try:
        # Register the toggle hotkey
        keyboard.add_hotkey(TOGGLE_KEY, toggle_script)
        
        # Hook the keyboard for navigation, suppressing only handled keys
        keyboard.hook(handle_hotkey, suppress=True)
        
        # Keep the program running
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        emergency_shutdown()

if __name__ == "__main__":
    main()
