import os
import time
import requests
import json
import re
import threading
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import sys

class OSINTTool:
    def __init__(self):
        self.settings = {
            "timeout": 8,
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
            ],
            "max_threads": 5,
            "delay_between_requests": 0.3,
            "output_file": "osint_results.txt",
            "save_format": "both",  # txt, json, both
            "proxy_enabled": False,
            "proxies": {}
        }
        
        self.platforms = {
            "Instagram": {
                "url": "https://www.instagram.com/{}/",
                "method": "direct",
                "enabled": True,
                "risk_level": "medium"
            },
            "GitHub": {
                "url": "https://github.com/{}",
                "method": "direct", 
                "enabled": True,
                "risk_level": "low"
            },
            "Reddit": {
                "url": "https://www.reddit.com/user/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "TikTok": {
                "url": "https://www.tiktok.com/@{}",
                "method": "search",
                "enabled": True,
                "risk_level": "medium"
            },
            "Facebook": {
                "url": "https://www.facebook.com/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "high"
            },
            "Twitter": {
                "url": "https://twitter.com/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "medium"
            },
            "YouTube": {
                "url": "https://www.youtube.com/@{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "LinkedIn": {
                "url": "https://www.linkedin.com/in/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "high"
            },
            "Pinterest": {
                "url": "https://www.pinterest.com/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "Telegram": {
                "url": "https://t.me/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "medium"
            },
            "Discord": {
                "url": "https://discord.com/users/{}",
                "method": "api",
                "enabled": True,
                "risk_level": "high"
            },
            "Twitch": {
                "url": "https://www.twitch.tv/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "Spotify": {
                "url": "https://open.spotify.com/user/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "Snapchat": {
                "url": "https://www.snapchat.com/add/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "high"
            },
            "Medium": {
                "url": "https://medium.com/@{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "DevianArt": {
                "url": "https://www.deviantart.com/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "Vimeo": {
                "url": "https://vimeo.com/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "SoundCloud": {
                "url": "https://soundcloud.com/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "Blogger": {
                "url": "https://{}.blogspot.com",
                "method": "direct",
                "enabled": True,
                "risk_level": "medium"
            },
            "Flickr": {
                "url": "https://www.flickr.com/people/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "GitLab": {
                "url": "https://gitlab.com/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "Keybase": {
                "url": "https://keybase.io/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "high"
            },
            "HackerNews": {
                "url": "https://news.ycombinator.com/user?id={}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "CodePen": {
                "url": "https://codepen.io/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "Behance": {
                "url": "https://www.behance.net/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            },
            "Dribbble": {
                "url": "https://dribbble.com/{}",
                "method": "direct",
                "enabled": True,
                "risk_level": "low"
            }
        }
        
        self.results = {
            "username": "",
            "found": [],
            "not_found": [],
            "errors": [],
            "timestamp": "",
            "summary": {}
        }
        
        self.load_config()

    def banner(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print(r"""
    ╔═══════════════════════════════════════════╗
    ║              OSINT TOOL v1.0             ║
    ║         Enhanced Intelligence Suite       ║
    ║          team c00lkidd // by Faqih        ║
    ║                                           ║
    ║  🔍 Multi-Platform • 🚀 Multi-Threaded   ║
    ║  📊 Advanced Analysis • 💾 JSON Export   ║
    ║  🛡️  Proxy Support • ⚡ Fast Scanning    ║
    ╚═══════════════════════════════════════════╝
        """)

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    self.settings.update(config.get("settings", {}))
                    
                    # Update platform enabled status
                    for platform, data in config.get("platforms", {}).items():
                        if platform in self.platforms:
                            self.platforms[platform]["enabled"] = data.get("enabled", True)
                print("[✓] Configuration loaded successfully")
        except Exception as e:
            print(f"[!] Error loading config: {e}")

    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                "settings": self.settings,
                "platforms": {name: {"enabled": data["enabled"]} for name, data in self.platforms.items()}
            }
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"[!] Error saving config: {e}")

    def validate_username(self, username):
        """Enhanced username validation"""
        if not username or len(username.strip()) == 0:
            return False, "Username cannot be empty"
        
        username = username.strip()
        
        # Length validation
        if len(username) < 2:
            return False, "Username too short (min 2 characters)"
        if len(username) > 30:
            return False, "Username too long (max 30 characters)"
        
        # Character validation
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            return False, "Username contains invalid characters"
        
        # Reserved names check
        reserved_names = ['admin', 'administrator', 'null', 'undefined', 'test', 'root']
        if username.lower() in reserved_names:
            return False, "Username not allowed"
        
        return True, username

    def get_random_user_agent(self):
        """Get random user agent for rotation"""
        return random.choice(self.settings['user_agents'])

    def get_proxies(self):
        """Get proxies if enabled"""
        if self.settings['proxy_enabled'] and self.settings['proxies']:
            return self.settings['proxies']
        return None

    def make_request(self, url, platform):
        """Make HTTP request with enhanced error handling"""
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        try:
            time.sleep(self.settings['delay_between_requests'])
            
            proxies = self.get_proxies()
            
            if platform == "TikTok":
                # Special handling for TikTok
                search_url = f"https://www.tiktok.com/search/user?q={self.results['username']}"
                response = requests.get(search_url, headers=headers, timeout=self.settings['timeout'], proxies=proxies)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for username in search results
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if f"@{self.results['username']}".lower() in href.lower():
                        return True, f"https://www.tiktok.com{href}"
                return False, None
                
            else:
                response = requests.get(url, headers=headers, timeout=self.settings['timeout'], proxies=proxies)
                
                if response.status_code == 200:
                    # Additional checks for specific platforms
                    if platform == "Instagram" and "Sorry, this page isn't available." in response.text:
                        return False, None
                    elif platform == "Facebook" and "Content Not Found" in response.text:
                        return False, None
                    elif platform == "Twitter" and "Account suspended" in response.text:
                        return True, url + " [SUSPENDED]"
                    elif platform == "Reddit" and "Sorry, nobody on Reddit goes by that name." in response.text:
                        return False, None
                    elif platform == "GitHub" and "This is not the web page you are looking for" in response.text:
                        return False, None
                    
                    return True, url
                    
                elif response.status_code == 404:
                    return False, None
                else:
                    return None, f"HTTP {response.status_code}"
                    
        except requests.exceptions.Timeout:
            return None, "Timeout"
        except requests.exceptions.ConnectionError:
            return None, "Connection Error"
        except requests.exceptions.RequestException as e:
            return None, f"Request Error: {str(e)}"
        except Exception as e:
            return None, f"Unexpected Error: {str(e)}"

    def check_platform(self, platform_data):
        """Check single platform"""
        platform_name, data = platform_data
        
        if not data["enabled"]:
            return platform_name, "skipped", None
            
        url = data["url"].format(self.results['username'])
        success, result = self.make_request(url, platform_name)
        
        if success is True:
            return platform_name, "found", result
        elif success is False:
            return platform_name, "not_found", None
        else:
            return platform_name, "error", result

    def run_osint_scan(self, username):
        """Run OSINT scan with multi-threading"""
        self.results = {
            "username": username,
            "found": [],
            "not_found": [],
            "errors": [],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {}
        }
        
        print(f"\n[🔍] Starting OSINT scan for: {username}")
        print("[⚡] Using multi-threading...")
        print("[🛡️] Proxy support: " + ("ENABLED" if self.settings['proxy_enabled'] else "DISABLED"))
        print("[⏳] Please wait...\n")
        
        start_time = time.time()
        enabled_platforms = [(name, data) for name, data in self.platforms.items() if data["enabled"]]
        total_platforms = len(enabled_platforms)
        
        with ThreadPoolExecutor(max_workers=self.settings['max_threads']) as executor:
            future_to_platform = {
                executor.submit(self.check_platform, (name, data)): name 
                for name, data in enabled_platforms
            }
            
            completed = 0
            for future in as_completed(future_to_platform):
                platform_name, status, result = future.result()
                completed += 1
                
                # Progress indicator
                progress = (completed / total_platforms) * 100
                print(f"\r[📊] Progress: {completed}/{total_platforms} ({progress:.1f}%)", end="")
                
                if status == "found":
                    risk_level = self.platforms[platform_name]["risk_level"]
                    self.results["found"].append({
                        "platform": platform_name, 
                        "url": result,
                        "risk_level": risk_level
                    })
                    print(f"\n[✅] {platform_name}: Found (Risk: {risk_level.upper()})")
                elif status == "not_found":
                    self.results["not_found"].append(platform_name)
                    print(f"\n[❌] {platform_name}: Not found")
                elif status == "error":
                    self.results["errors"].append({"platform": platform_name, "error": result})
                    print(f"\n[⚠️] {platform_name}: Error - {result}")
        
        # Calculate summary
        scan_time = time.time() - start_time
        self.results["summary"] = {
            "total_platforms": total_platforms,
            "scan_duration": f"{scan_time:.2f}s",
            "success_rate": f"{(len(self.results['found']) / total_platforms) * 100:.1f}%"
        }
        
        print("\n" + "="*60)

    def display_results(self):
        """Display results in formatted way"""
        print(f"\n📊 OSINT SCAN RESULTS")
        print(f"👤 Username: {self.results['username']}")
        print(f"🕐 Timestamp: {self.results['timestamp']}")
        print(f"⏱️  Scan Duration: {self.results['summary']['scan_duration']}")
        print(f"📈 Success Rate: {self.results['summary']['success_rate']}")
        print(f"✅ Found: {len(self.results['found'])} platforms")
        print(f"❌ Not Found: {len(self.results['not_found'])} platforms")
        print(f"⚠️ Errors: {len(self.results['errors'])} platforms")
        
        if self.results['found']:
            print(f"\n🎯 ACCOUNTS FOUND:")
            # Sort by risk level
            high_risk = [item for item in self.results['found'] if item['risk_level'] == 'high']
            medium_risk = [item for item in self.results['found'] if item['risk_level'] == 'medium']
            low_risk = [item for item in self.results['found'] if item['risk_level'] == 'low']
            
            if high_risk:
                print(f"\n   🔴 HIGH RISK:")
                for item in high_risk:
                    print(f"      • {item['platform']}: {item['url']}")
            
            if medium_risk:
                print(f"\n   🟡 MEDIUM RISK:")
                for item in medium_risk:
                    print(f"      • {item['platform']}: {item['url']}")
            
            if low_risk:
                print(f"\n   🟢 LOW RISK:")
                for item in low_risk:
                    print(f"      • {item['platform']}: {item['url']}")
        
        if self.results['not_found']:
            print(f"\n🚫 NOT FOUND:")
            # Display in columns
            not_found_list = self.results['not_found']
            for i in range(0, len(not_found_list), 4):
                print(f"   {', '.join(not_found_list[i:i+4])}")
        
        if self.results['errors']:
            print(f"\n⚡ ERRORS:")
            for error in self.results['errors']:
                print(f"   • {error['platform']}: {error['error']}")

    def save_results(self):
        """Save results in multiple formats"""
        base_name = self.settings['output_file'].replace('.txt', '').replace('.json', '')
        
        if self.settings['save_format'] in ['txt', 'both']:
            txt_file = f"{base_name}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("OSINT SCAN RESULTS\n")
                f.write("="*60 + "\n\n")
                f.write(f"Username: {self.results['username']}\n")
                f.write(f"Timestamp: {self.results['timestamp']}\n")
                f.write(f"Scan Duration: {self.results['summary']['scan_duration']}\n")
                f.write(f"Success Rate: {self.results['summary']['success_rate']}\n\n")
                
                f.write("ACCOUNTS FOUND:\n")
                f.write("-" * 40 + "\n")
                for item in self.results['found']:
                    f.write(f"Platform: {item['platform']}\n")
                    f.write(f"URL: {item['url']}\n")
                    f.write(f"Risk Level: {item['risk_level'].upper()}\n")
                    f.write("-" * 40 + "\n")
                
                f.write(f"\nNot Found ({len(self.results['not_found'])}): {', '.join(self.results['not_found'])}\n")
                
                if self.results['errors']:
                    f.write(f"\nErrors:\n")
                    for error in self.results['errors']:
                        f.write(f"- {error['platform']}: {error['error']}\n")
            
            print(f"[💾] Text results saved to: {txt_file}")
        
        if self.settings['save_format'] in ['json', 'both']:
            json_file = f"{base_name}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=4, ensure_ascii=False)
            print(f"[💾] JSON results saved to: {json_file}")

    def settings_menu(self):
        """Enhanced settings menu"""
        while True:
            self.banner()
            print("SETTINGS MENU")
            print("=" * 50)
            print(f"[1] Request Timeout: {self.settings['timeout']} seconds")
            print(f"[2] Max Threads: {self.settings['max_threads']}")
            print(f"[3] Request Delay: {self.settings['delay_between_requests']}s")
            print(f"[4] Output File: {self.settings['output_file']}")
            print(f"[5] Save Format: {self.settings['save_format']}")
            print(f"[6] Proxy Settings: {'ENABLED' if self.settings['proxy_enabled'] else 'DISABLED'}")
            print(f"[7] Platform Management")
            print(f"[8] User-Agent Management")
            print(f"[9] Back to Main Menu")
            
            choice = input("\nSelect setting > ")
            
            if choice == '1':
                new_timeout = input("Enter new timeout (seconds): ")
                if new_timeout.isdigit() and int(new_timeout) > 0:
                    self.settings['timeout'] = int(new_timeout)
                    print("[✓] Timeout updated successfully")
                else:
                    print("[!] Invalid timeout value")
                time.sleep(1)
            
            elif choice == '2':
                new_threads = input("Enter max threads (1-10): ")
                if new_threads.isdigit() and 1 <= int(new_threads) <= 10:
                    self.settings['max_threads'] = int(new_threads)
                    print("[✓] Max threads updated successfully")
                else:
                    print("[!] Invalid thread count")
                time.sleep(1)
            
            elif choice == '3':
                new_delay = input("Enter request delay (seconds): ")
                try:
                    delay = float(new_delay)
                    if delay >= 0:
                        self.settings['delay_between_requests'] = delay
                        print("[✓] Request delay updated successfully")
                    else:
                        print("[!] Delay cannot be negative")
                except ValueError:
                    print("[!] Invalid delay value")
                time.sleep(1)
            
            elif choice == '4':
                new_file = input("Enter output filename: ").strip()
                if new_file:
                    self.settings['output_file'] = new_file
                    print("[✓] Output file updated successfully")
                else:
                    print("[!] Filename cannot be empty")
                time.sleep(1)
            
            elif choice == '5':
                print("\nSelect save format:")
                print("[1] TXT only")
                print("[2] JSON only") 
                print("[3] Both formats")
                format_choice = input("> ")
                formats = {'1': 'txt', '2': 'json', '3': 'both'}
                if format_choice in formats:
                    self.settings['save_format'] = formats[format_choice]
                    print("[✓] Save format updated successfully")
                else:
                    print("[!] Invalid choice")
                time.sleep(1)
            
            elif choice == '6':
                self.proxy_settings()
            
            elif choice == '7':
                self.platform_management()
            
            elif choice == '8':
                self.user_agent_management()
            
            elif choice == '9':
                self.save_config()
                break
            
            else:
                print("[!] Invalid choice")
                time.sleep(1)

    def proxy_settings(self):
        """Proxy configuration menu"""
        while True:
            self.banner()
            print("PROXY SETTINGS")
            print("=" * 50)
            print(f"[1] Proxy Status: {'ENABLED' if self.settings['proxy_enabled'] else 'DISABLED'}")
            print("[2] Configure HTTP Proxy")
            print("[3] Configure HTTPS Proxy")
            print("[4] Test Proxy Connection")
            print("[5] Back to Settings")
            
            choice = input("\nSelect option > ")
            
            if choice == '1':
                self.settings['proxy_enabled'] = not self.settings['proxy_enabled']
                status = "ENABLED" if self.settings['proxy_enabled'] else "DISABLED"
                print(f"[✓] Proxy {status}")
                time.sleep(1)
            
            elif choice == '2':
                http_proxy = input("Enter HTTP proxy (e.g., http://user:pass@host:port): ").strip()
                if http_proxy:
                    self.settings['proxies']['http'] = http_proxy
                    print("[✓] HTTP proxy configured")
                else:
                    print("[!] Proxy URL cannot be empty")
                time.sleep(1)
            
            elif choice == '3':
                https_proxy = input("Enter HTTPS proxy (e.g., https://user:pass@host:port): ").strip()
                if https_proxy:
                    self.settings['proxies']['https'] = https_proxy
                    print("[✓] HTTPS proxy configured")
                else:
                    print("[!] Proxy URL cannot be empty")
                time.sleep(1)
            
            elif choice == '4':
                if not self.settings['proxies']:
                    print("[!] No proxies configured")
                else:
                    print("[⏳] Testing proxy connection...")
                    try:
                        response = requests.get('http://httpbin.org/ip', 
                                              proxies=self.settings['proxies'],
                                              timeout=10)
                        print(f"[✓] Proxy working! Response: {response.text}")
                    except Exception as e:
                        print(f"[!] Proxy test failed: {e}")
                time.sleep(2)
            
            elif choice == '5':
                break
            
            else:
                print("[!] Invalid choice")
                time.sleep(1)

    def platform_management(self):
        """Platform management menu"""
        while True:
            self.banner()
            print("PLATFORM MANAGEMENT")
            print("=" * 50)
            
            enabled_count = sum(1 for p in self.platforms.values() if p['enabled'])
            print(f"Enabled Platforms: {enabled_count}/{len(self.platforms)}\n")
            
            # Display platforms in columns
            platforms_list = list(self.platforms.keys())
            for i in range(0, len(platforms_list), 3):
                row = platforms_list[i:i+3]
                for platform in row:
                    status = "✅" if self.platforms[platform]['enabled'] else "❌"
                    risk = self.platforms[platform]['risk_level'].upper()
                    print(f"{status} {platform:<15} ({risk})", end="  ")
                print()
            
            print(f"\n[1-{len(platforms_list)}] Toggle platform")
            print(f"[{len(platforms_list)+1}] Enable All")
            print(f"[{len(platforms_list)+2}] Disable All") 
            print(f"[{len(platforms_list)+3}] Back to Settings")
            
            try:
                choice = input("\nSelect option > ")
                
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(platforms_list):
                        platform_name = platforms_list[choice_num-1]
                        self.platforms[platform_name]['enabled'] = not self.platforms[platform_name]['enabled']
                        status = "enabled" if self.platforms[platform_name]['enabled'] else "disabled"
                        print(f"[✓] {platform_name} {status}")
                    elif choice_num == len(platforms_list) + 1:
                        for platform in self.platforms:
                            self.platforms[platform]['enabled'] = True
                        print("[✓] All platforms enabled")
                    elif choice_num == len(platforms_list) + 2:
                        for platform in self.platforms:
                            self.platforms[platform]['enabled'] = False
                        print("[✓] All platforms disabled")
                    elif choice_num == len(platforms_list) + 3:
                        break
                    else:
                        print("[!] Invalid choice")
                else:
                    print("[!] Please enter a number")
                
                time.sleep(1)
            except (ValueError, IndexError):
                print("[!] Invalid input")
                time.sleep(1)

    def user_agent_management(self):
        """User-Agent management menu"""
        while True:
            self.banner()
            print("USER-AGENT MANAGEMENT")
            print("=" * 50)
            print("Current User-Agents:\n")
            for i, ua in enumerate(self.settings['user_agents'], 1):
                print(f"[{i}] {ua[:80]}...")
            
            print(f"\n[1] Add User-Agent")
            print(f"[2] Remove User-Agent")
            print(f"[3] Reset to Default")
            print(f"[4] Back to Settings")
            
            choice = input("\nSelect option > ")
            
            if choice == '1':
                new_ua = input("Enter new User-Agent: ").strip()
                if new_ua:
                    self.settings['user_agents'].append(new_ua)
                    print("[✓] User-Agent added successfully")
                else:
                    print("[!] User-Agent cannot be empty")
                time.sleep(1)
            
            elif choice == '2':
                if len(self.settings['user_agents']) <= 1:
                    print("[!] Cannot remove all User-Agents")
                else:
                    try:
                        idx = int(input(f"Enter number to remove (1-{len(self.settings['user_agents'])}): ")) - 1
                        if 0 <= idx < len(self.settings['user_agents']):
                            removed = self.settings['user_agents'].pop(idx)
                            print(f"[✓] User-Agent removed: {removed[:50]}...")
                        else:
                            print("[!] Invalid number")
                    except ValueError:
                        print("[!] Please enter a valid number")
                time.sleep(1)
            
            elif choice == '3':
                self.settings['user_agents'] = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
                ]
                print("[✓] User-Agents reset to default")
                time.sleep(1)
            
            elif choice == '4':
                break
            
            else:
                print("[!] Invalid choice")
                time.sleep(1)

    def main_menu(self):
        """Main menu"""
        while True:
            self.banner()
            print("MAIN MENU")
            print("=" * 50)
            print("[1] Start OSINT Scan")
            print("[2] Settings")
            print("[3] View Documentation")
            print("[4] Exit")
            
            choice = input("\nSelect option > ")
            
            if choice == '1':
                username = input("Enter target username: ").strip().replace(" ", "")
                valid, message = self.validate_username(username)
                
                if valid:
                    self.run_osint_scan(username)
                    self.display_results()
                    self.save_results()
                    
                    print(f"\n[🎯] Scan completed for: {username}")
                    input("Press Enter to continue...")
                else:
                    print(f"[!] {message}")
                    time.sleep(2)
            
            elif choice == '2':
                self.settings_menu()
            
            elif choice == '3':
                self.show_documentation()
            
            elif choice == '4':
                print("\n[🚪] Thank you for using OSINT Tool v1.0!")
                print("[👋] Goodbye!")
                sys.exit(0)
            
            else:
                print("[!] Invalid choice")
                time.sleep(1)

    def show_documentation(self):
        """Show tool documentation"""
        self.banner()
        print("DOCUMENTATION")
        print("=" * 60)
        print("""
🔍 OSINT TOOL v1.0 - Enhanced Intelligence Suite

FEATURES:
✅ Multi-threaded scanning (5 threads default)
✅ 25+ supported platforms
✅ Risk level classification (High/Medium/Low)
✅ Proxy support with authentication
✅ User-Agent rotation
✅ Multiple output formats (TXT, JSON)
✅ Advanced error handling
✅ Progress tracking
✅ Configuration persistence

RISK LEVELS:
🔴 HIGH: Sensitive platforms (LinkedIn, Discord, etc.)
🟡 MEDIUM: Social media with privacy concerns
🟢 LOW: Public platforms with minimal risk

PLATFORMS SUPPORTED:
• Social Media: Facebook, Instagram, Twitter, TikTok, etc.
• Professional: LinkedIn, GitHub, GitLab, etc.
• Creative: Behance, Dribbble, DeviantArt, etc.
• Communication: Telegram, Discord, etc.

SETTINGS:
• Adjust timeout, threads, and delays
• Enable/disable specific platforms  
• Configure proxies for anonymity
• Customize User-Agents
• Choose output formats

TIPS:
• Use proxies for large-scale scanning
• Adjust delays to avoid rate limiting
• Enable only needed platforms for faster scans
• Check risk levels for sensitive investigations
        """)
        input("\nPress Enter to return to main menu...")

# Run the tool
if __name__ == "__main__":
    try:
        tool = OSINTTool()
        tool.main_menu()
    except KeyboardInterrupt:
        print("\n\n[⚠️] Program interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[💥] Critical error: {e}")
        sys.exit(1)
