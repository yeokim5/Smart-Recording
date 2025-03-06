import time
import datetime
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
import pygetwindow as gw

class SportsRecorder:
    def __init__(self):
        self.driver = None
        self.recording = False
        self.unmuted = False
        self.output_dir = "recordings"
        self.main_window = None
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def setup_browser(self):
        """Initialize the web browser with strict tab blocking settings"""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-new-tab-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-features=EnableMdns")
        options.add_argument("--disable-features=OpenLinkInNewTab,OpenLinkInNewWindow")
        options.add_argument("--block-new-web-contents")
        options.add_argument("--force-single-window")
        
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.popups": 2,
            "profile.default_content_settings.popups": 2,
            "profile.block_third_party_popups": True,
            "browser.link.open_newwindow": 1,
            "browser.link.open_newwindow.restriction": 0,
            "browser.link.open_newwindow.override.external": 1,
            "browser.link.open_newwindow.disabled": True,
            "profile.managed_default_content_settings.popups": 2,
            "profile.content_settings.exceptions.popups": {"*": {"setting": 2}}
        })
        self.driver = webdriver.Chrome(options=options)
        self.main_window = self.driver.current_window_handle
        
        self.driver.execute_script("""
            window.open = function(url) { 
                if (url) {
                    window.location.href = url; 
                }
                return window;
            };
            Object.defineProperty(window, 'open', { 
                writable: false,
                configurable: false
            });
            
            document.addEventListener('click', function(e) {
                var target = e.target;
                while (target && target.tagName !== 'A') {
                    target = target.parentNode;
                    if (!target) break;
                }
                if (target && target.tagName === 'A') {
                    e.preventDefault();
                    var href = target.getAttribute('href');
                    if (href && !href.startsWith('#') && !href.startsWith('javascript:')) {
                        window.location.href = href;
                    }
                }
            }, true);
        """)
        self.driver.execute_script("""
            window.open = function() { return null; };
            window.open = function(url) { window.location.href = url; return null; };
            Object.defineProperty(window, 'open', { writable: false });
        """)

    def block_new_tabs(self):
        """Actively monitor and close any new tabs that manage to open"""
        try:
            current_windows = self.driver.window_handles
            if len(current_windows) > 1:
                for window in current_windows:
                    if window != self.main_window:
                        self.driver.switch_to.window(window)
                        self.driver.close()
                self.driver.switch_to.window(self.main_window)
        except Exception as e:
            print(f"Error in tab blocking: {str(e)}")

    def schedule_recording(self, search_url, start_time, duration_minutes):
        start_datetime = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        print(f"Waiting for start time: {start_datetime}")
        
        while datetime.datetime.now() < start_datetime:
            time_remaining = start_datetime - datetime.datetime.now()
            seconds_remaining = int(time_remaining.total_seconds())
            print(f"Time until recording starts: {seconds_remaining} seconds", end='\r')
            time.sleep(1)
        
        print("\nStarting recording...")
        self.start_recording(search_url, duration_minutes)

    def find_game_link(self, search_url):
        """Find the game link from the search results page"""
        try:
            print(f"Opening search page: {search_url}")
            self.driver.get(search_url)
            time.sleep(3)
            
            article = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-result"))
            )
            
            game_link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
            print(f"Found game link: {game_link}")
            return game_link
        except Exception as e:
            print(f"Error finding game link: {str(e)}")
            return None

    def find_embed_src(self, game_url):
        """Find the embed source from the game page"""
        try:
            print(f"Opening game page: {game_url}")
            self.driver.get(game_url)
            time.sleep(3)
            
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src")
                if src:
                    if "thedaddy.to" in src:
                        print(f"Found embed source: {src}")
                        self.update_test_html(src, "thedaddy.to")
                        return src
                    elif "embedsports.me" in src:
                        print(f"Found embed source: {src}")
                        self.update_test_html(src, "embedsports.me")
                        return src
            
            page_source = self.driver.page_source
            thedaddy_match = re.search(r'src="(https://thedaddy\.to/embed/[^"]+)"', page_source)
            embedsports_match = re.search(r'src="(https://embedsports\.me/[^"]+)"', page_source)
            
            if thedaddy_match:
                src = thedaddy_match.group(1)
                self.update_test_html(src, "thedaddy.to")
                return src
            elif embedsports_match:
                src = embedsports_match.group(1)
                self.update_test_html(src, "embedsports.me")
                return src
            
            print("No embed source found")
            return None
        except Exception as e:
            print(f"Error finding embed source: {str(e)}")
            return None

    def handle_popups(self):
        """Handle any popups that appear on the page"""
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.is_displayed() and (
                    "play" in button.text.lower() or 
                    "close" in button.text.lower() or
                    "start" in button.text.lower()
                ):
                    button.click()
                    print("Clicked a popup button")
                    time.sleep(1)
                    self.block_new_tabs()
            
            try:
                play_buttons = self.driver.find_elements(By.CLASS_NAME, "play-button")
                for button in play_buttons:
                    if button.is_displayed():
                        button.click()
                        print("Clicked play button")
                        time.sleep(1)
                        self.block_new_tabs()
            except:
                pass
                
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    if iframe.is_displayed():
                        self.driver.execute_script("arguments[0].click();", iframe)
                        print("Clicked on iframe")
                        time.sleep(1)
                        self.block_new_tabs()
            except:
                pass
                
        except Exception as e:
            print(f"Error handling popups: {str(e)}")

    def start_recording(self, search_url, duration_minutes):
        try:
            self.setup_browser()
            
            game_url = self.find_game_link(search_url)
            if not game_url:
                raise Exception("Failed to find game link")
            
            embed_src = self.find_embed_src(game_url)
            if not embed_src:
                raise Exception("Failed to find embed source")
            
            embed_type = "thedaddy.to" if "thedaddy.to" in embed_src else "embedsports.me" if "embedsports.me" in embed_src else "unknown"
            
            test_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.html")
            test_html_url = f"file:///{test_html_path.replace(os.sep, '/')}"
            print(f"Navigating to local test.html: {test_html_url}")
            self.driver.get(test_html_url)
            time.sleep(3)
            
            self.handle_popups()
            self.check_and_refresh_stream(embed_type)
            
            # Make sure to focus the browser window before recording
            self.focus_browser_window()
            self.record_screen(duration_minutes)
            
        except Exception as e:
            print(f"Error during recording: {str(e)}")
            self.stop_recording()

    def focus_browser_window(self):
        """Focus the Chrome browser window to ensure it's what gets recorded"""
        try:
            # Get all Chrome windows
            chrome_windows = gw.getWindowsWithTitle('Chrome')
            
            # Find the window that matches our session
            for window in chrome_windows:
                if window.isMinimized:
                    window.restore()
                window.activate()
                time.sleep(0.5)
                
                # Check if this is the right window
                if "test.html" in window.title or self.driver.title in window.title:
                    print(f"Found and focused the correct Chrome window: {window.title}")
                    # Bring window to foreground
                    window.maximize()
                    window.activate()
                    time.sleep(1)
                    return
            
            print("Could not find the exact Chrome window, activating the first available Chrome window")
            if chrome_windows:
                chrome_windows[0].maximize()
                chrome_windows[0].activate()
                time.sleep(1)
                
        except Exception as e:
            print(f"Error focusing Chrome window: {str(e)}")
    
    def record_screen(self, duration_minutes):
        """Record the Chrome browser window using Windows Game Bar (Win + Alt + R)"""
        try:
            if self.recording:
                print("Recording already in progress")
                return
            
            # Make sure the browser window is focused before recording
            pyautogui.hotkey('f11')
            self.focus_browser_window()
            time.sleep(1)
            
            
            print("Starting screen recording with Windows Game Bar")
            # Open Game Bar
            pyautogui.hotkey('win', 'g')
            time.sleep(2)
            
            # Start recording using Win+Alt+R
            pyautogui.hotkey('win', 'alt', 'r')
            self.recording = True
            print(f"Recording started, will continue for {duration_minutes} minutes")
            time.sleep(3)
            pyautogui.hotkey('esc')
            time.sleep(5)
            
            
            # Record for the specified duration
            time.sleep(duration_minutes * 60)
            
            # Stop recording using the same hotkey
            pyautogui.hotkey('win', 'alt', 'r')
            self.recording = False
            print("Recording stopped")
            
        except Exception as e:
            print(f"Error in screen recording: {str(e)}")
            self.recording = False
            # Try to stop recording in case it started
            try:
                pyautogui.hotkey('win', 'alt', 'r')
                
            except:
                pass

    def check_and_refresh_stream(self, embed_type):
        try:
            if not self.unmuted:
                print("Attempting to navigate stream controls...")
                self.driver.execute_script("document.activeElement.blur();")
                
                self.driver.execute_script("""
                    window.checkFocusedElement = function() {
                        let element = document.activeElement;
                        let isUnmuteButton = element.getAttribute('aria-label') === 'Unmute' ||
                                       element.classList.contains('unmute-button') ||
                                       element.title === 'Unmute';
                        return {
                            isUnmute: isUnmuteButton,
                            element: element.outerHTML
                        };
                    }
                """)
                
                tab_count = 10 if embed_type == "thedaddy.to" else 2
                print(f"Using {tab_count} tabs for {embed_type}")
                
                for i in range(tab_count):
                    pyautogui.press('tab')
                    self.block_new_tabs()
                    time.sleep(0.5)
                pyautogui.press('enter')
                
                self.block_new_tabs()
                print("Stream controls navigation completed")
                self.unmuted = True
            else:
                print("Stream controls already handled")
            
        except Exception as e:
            print(f"Error checking stream: {str(e)}")
            self.driver.refresh()
            self.handle_popups()
            self.unmuted = False

    def stop_recording(self):
        """Stop the recording and clean up resources"""
        if self.recording:
            try:
                # Stop Windows Game Bar recording
                pyautogui.hotkey('win', 'alt', 'r')
                print("Recording stopped manually")
            except Exception as e:
                print(f"Error stopping recording: {str(e)}")
        
        self.recording = False
        if self.driver:
            self.driver.quit()

    def update_test_html(self, embed_src, embed_type):
        """Update the test.html file with the embed source URL"""
        try:
            test_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.html")
            
            with open(test_html_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            updated_content = re.sub(r'src="[^"]*"', f'src="{embed_src}"', content)
            
            with open(test_html_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            
            print(f"Updated test.html with {embed_type} embed source")
        except Exception as e:
            print(f"Error updating test.html: {str(e)}")


def main():
    recorder = SportsRecorder()
    search_url = "https://phd1.live//?s=terrapins"
    start_time = "2025-03-04 15:19"
    duration_minutes = 0.5
    
    recorder.schedule_recording(search_url, start_time, duration_minutes)

if __name__ == "__main__":
    print('hi')
    main()