import keyboard
import time
import sys

def press_arrow(key, with_ctrl=False):
    """
    Send the arrow key press with proper key codes
    If with_ctrl is True, simulates Ctrl+Arrow for word skipping
    """
    if with_ctrl:
        print(f"Simulating Ctrl+{key} arrow key (word skipping)")
        # Simulate Ctrl+Arrow for word skipping
        keyboard.send(f"ctrl+{key}")
    else:
        print(f"Simulating {key} arrow key")
        # Use direct key codes for standard arrow movement
        keyboard.send(key)
    
def handle_alt_hotkey(key):
    """Handle Alt+IJKL hotkey presses"""
    # Release the alt key first to avoid interference
    keyboard.release('alt')
    time.sleep(0.01)  # Small delay
    press_arrow(key, with_ctrl=False)
    return False  # This prevents the original key from being typed

def handle_ctrl_alt_hotkey(key):
    """Handle Ctrl+Alt+IJKL hotkey presses for word skipping"""
    # Release modifier keys to avoid interference
    keyboard.release('alt')
    keyboard.release('ctrl')
    time.sleep(0.01)  # Small delay
    press_arrow(key, with_ctrl=True)
    return False  # This prevents the original key from being typed

def handle_home_end_keys(key):
    """Handle Alt+U/O for Home/End functionality instead of Alt+Shift+J/K"""
    # Release modifier keys
    keyboard.release('alt')
    time.sleep(0.01)  # Small delay
    print(f"Simulating {key} key")
    keyboard.send(key)
    return False  # This prevents the original key from being typed

def main():
    """
    Simulate arrow keys with multiple modes:
    
    1. Alt+I/J/K/L: Regular arrow keys
    - Alt+I: Up arrow
    - Alt+J: Left arrow
    - Alt+K: Down arrow
    - Alt+L: Right arrow
    
    2. Ctrl+Alt+I/J/K/L: Ctrl+Arrow keys (word skipping)
    - Ctrl+Alt+I: Ctrl+Up arrow
    - Ctrl+Alt+J: Ctrl+Left arrow (skip word left)
    - Ctrl+Alt+K: Ctrl+Down arrow
    - Ctrl+Alt+L: Ctrl+Right arrow (skip word right)
    
    3. Alt+U/O: Home/End keys
    - Alt+U: Home key (move to beginning of line)
    - Alt+O: End key (move to end of line)
    """
    print("Starting Enhanced Arrow Key Simulator")
    print("Hotkeys:")
    print("- Alt+I/J/K/L: Regular arrow keys")
    print("- Ctrl+Alt+I/J/K/L: Word skipping (like Ctrl+Arrow)")
    print("- Alt+U: Home key (beginning of line)")
    print("- Alt+O: End key (end of line)")
    print("Press Ctrl+C to exit")
    
    try:
        # Define and register Alt+IJKL hotkeys (regular arrow keys)
        keyboard.add_hotkey('alt+i', lambda: handle_alt_hotkey("up"), suppress=True)
        keyboard.add_hotkey('alt+j', lambda: handle_alt_hotkey("left"), suppress=True)
        keyboard.add_hotkey('alt+k', lambda: handle_alt_hotkey("down"), suppress=True)
        keyboard.add_hotkey('alt+l', lambda: handle_alt_hotkey("right"), suppress=True)
        
        # Define and register Ctrl+Alt+IJKL hotkeys (word skipping)
        # Using more specific hotkey patterns with exact_match=True to avoid interfering with other Ctrl combinations
        keyboard.add_hotkey('ctrl+alt+i', lambda: handle_ctrl_alt_hotkey("up"), suppress=True, exact_match=True)
        keyboard.add_hotkey('ctrl+alt+j', lambda: handle_ctrl_alt_hotkey("left"), suppress=True, exact_match=True)
        keyboard.add_hotkey('ctrl+alt+k', lambda: handle_ctrl_alt_hotkey("down"), suppress=True, exact_match=True)
        keyboard.add_hotkey('ctrl+alt+l', lambda: handle_ctrl_alt_hotkey("right"), suppress=True, exact_match=True)
        
        # Define and register Alt+U/O for Home/End functionality
        keyboard.add_hotkey('alt+u', lambda: handle_home_end_keys("home"), suppress=True)
        keyboard.add_hotkey('alt+o', lambda: handle_home_end_keys("end"), suppress=True)
        
        print("All hotkeys registered successfully.")
        print("Regular movement: Alt+I/J/K/L")
        print("Word skipping: Ctrl+Alt+I/J/K/L")
        print("Line navigation: Alt+U (Home), Alt+O (End)")
        print("Browser functionality like Ctrl+Click remains unaffected")
        
        # Keep the program running
        while True:
            time.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")
        print("Troubleshooting tips:")
        print("1. Make sure you run this script with admin/root privileges")
        print("2. Check if keyboard module is correctly installed")
        print("3. On macOS, verify accessibility permissions are granted")
    except KeyboardInterrupt:
        print("Exiting Arrow Key Simulator")
    finally:
        keyboard.unhook_all()

if __name__ == "__main__":
    main()