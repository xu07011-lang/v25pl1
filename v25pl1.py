import base64
import hashlib
import json
import os
import platform
import random
import re
import string
import subprocess
import sys
import time
import urllib.parse
import uuid
from datetime import datetime, timedelta, timezone
from time import sleep

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    import pytz
    import requests
except ImportError:
    print('__Đang cài đặt các thư viện cần thiết, vui lòng chờ...__')
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "colorama", "pytz"])
    print('__Cài đặt hoàn tất, vui lòng chạy lại Tool__')
    sys.exit()

FREE_CACHE_FILE = 'free_key_cache.json'
VIP_CACHE_FILE = 'vip_cache.json'
HANOI_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
VIP_KEY_URL = "https://raw.githubusercontent.com/DUONGKP2401/keyxworkdf/main/keyxworkdf.txt"

def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

xnhac = "\033[1;36m"
do = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
xduong = "\033[1;34m"
hong = "\033[1;35m"
trang = "\033[1;39m"
end = '\033[0m'

def authentication_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner_text = f"""
████████╗██████╗░██╗░░██╗
╚══██╔══╝██╔══██╗██║░██╔╝
░░░██║░░░██║░░██║█████═╝░
░░░██║░░░██║░░██║██╔═██╗░
░░░██║░░░██████╔╝██║░╚██╗
░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝
══════════════════════════
Admin: DUONG phung
Tool xworld VTD
TIKTOK: @tdktool
══════════════════════════
"""
    for char in banner_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.0001)

def get_device_id():
    system = platform.system()
    try:
        if system == "Windows":
            cpu_info = subprocess.check_output('wmic cpu get ProcessorId', shell=True, text=True, stderr=subprocess.DEVNULL)
            cpu_info = ''.join(line.strip() for line in cpu_info.splitlines() if line.strip() and "ProcessorId" not in line)
        else:
            try:
                cpu_info = subprocess.check_output("cat /proc/cpuinfo", shell=True, text=True)
            except:
                cpu_info = platform.processor()
        if not cpu_info:
            cpu_info = platform.processor()
    except Exception:
        cpu_info = "Unknown"

    hash_hex = hashlib.sha256(cpu_info.encode()).hexdigest()
    only_digits = re.sub(r'\D', '', hash_hex)
    if len(only_digits) < 16:
        only_digits = (only_digits * 3)[:16]

    return f"DEVICE-{only_digits[:16]}"

def get_ip_address():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_data = response.json()
        return ip_data.get('ip')
    except Exception as e:
        print(f"{do}Lỗi khi lấy địa chỉ IP: {e}{trang}")
        return None

def display_machine_info(ip_address, device_id):
    authentication_banner()
    if ip_address:
        print(f"{trang}[{do}<>{trang}] {do}Địa chỉ IP: {vang}{ip_address}{trang}")
    else:
        print(f"{do}Không thể lấy địa chỉ IP của thiết bị.{trang}")

    if device_id:
        print(f"{trang}[{do}<>{trang}] {do}Mã Máy: {vang}{device_id}{trang}")
    else:
        print(f"{do}Không thể lấy Mã Máy của thiết bị.{trang}")

def save_vip_key_info(device_id, key, expiration_date_str):
    data = {'device_id': device_id, 'key': key, 'expiration_date': expiration_date_str}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(VIP_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)
    print(f"{luc}Đã lưu thông tin Key VIP cho lần đăng nhập sau.{trang}")

def load_vip_key_info():
    try:
        with open(VIP_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return None

def display_remaining_time(expiry_date_str):
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
        now = datetime.now()

        if expiry_date > now:
            delta = expiry_date - now
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"{xnhac}Key VIP của bạn còn lại: {luc}{days} ngày, {hours} giờ, {minutes} phút.{trang}")
        else:
            print(f"{do}Key VIP của bạn đã hết hạn.{trang}")
    except ValueError:
        print(f"{vang}Không thể xác định ngày hết hạn của key.{trang}")

def check_vip_key(machine_id, user_key):
    print(f"{vang}Đang kiểm tra Key VIP...{trang}")
    try:
        response = requests.get(VIP_KEY_URL, timeout=10)
        if response.status_code != 200:
            print(f"{do}Lỗi: Không thể tải danh sách key (Status code: {response.status_code}).{trang}")
            return 'error', None

        key_list = response.text.strip().split('\n')
        for line in key_list:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                key_ma_may, key_value, _, key_ngay_het_han = parts

                if key_ma_may == machine_id and key_value == user_key:
                    try:
                        expiry_date = datetime.strptime(key_ngay_het_han, '%d/%m/%Y')
                        if expiry_date.date() >= datetime.now().date():
                            return 'valid', key_ngay_het_han
                        else:
                            return 'expired', None
                    except ValueError:
                        continue
        return 'not_found', None
    except requests.exceptions.RequestException as e:
        print(f"{do}Lỗi kết nối đến server key: {e}{trang}")
        return 'error', None
        
def seeded_shuffle_js_equivalent(array, seed):
    seed_value = 0
    for i, char in enumerate(seed):
        seed_value = (seed_value + ord(char) * (i + 1)) % 1_000_000_000
    def custom_random():
        nonlocal seed_value
        seed_value = (seed_value * 9301 + 49297) % 233280
        return seed_value / 233280.0
    shuffled_array = array[:]
    current_index = len(shuffled_array)
    while current_index != 0:
        random_index = int(custom_random() * current_index)
        current_index -= 1
        shuffled_array[current_index], shuffled_array[random_index] = shuffled_array[random_index], shuffled_array[current_index]
    return shuffled_array

def save_free_key_info(device_id, key, expiration_date):
    data = {device_id: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open(FREE_CACHE_FILE, 'w') as file:
        file.write(encrypted_data)

def load_free_key_info():
    try:
        with open(FREE_CACHE_FILE, 'r') as file:
            encrypted_data = file.read()
        return json.loads(decrypt_data(encrypted_data))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def check_saved_free_key(device_id):
    data = load_free_key_info()
    if data and device_id in data:
        try:
            expiration_date = datetime.fromisoformat(data[device_id]['expiration_date'])
            if expiration_date > datetime.now(HANOI_TZ):
                return data[device_id]['key']
        except (ValueError, KeyError):
            return None
    return None

def generate_free_key_and_url(device_id):
    today_str = datetime.now(HANOI_TZ).strftime('%Y-%m-%d')
    seed_str = f"TDK_FREE_KEY_{device_id}_{today_str}"
    hashed_seed = hashlib.sha256(seed_str.encode()).hexdigest()
    digits = [d for d in hashed_seed if d.isdigit()][:10]
    letters = [l for l in hashed_seed if 'a' <= l <= 'f'][:5]
    while len(digits) < 10:
        digits.extend(random.choices(string.digits))
    while len(letters) < 5:
        letters.extend(random.choices(string.ascii_lowercase))
    key_list = digits + letters
    shuffled_list = seeded_shuffle_js_equivalent(key_list, hashed_seed)
    key = "".join(shuffled_list)
    now_hanoi = datetime.now(HANOI_TZ)
    expiration_date = now_hanoi.replace(hour=21, minute=0, second=0, microsecond=0)
    url = f'https://tdkbumxkey.blogspot.com/2025/10/lay-link.html?m={key}'
    return url, key, expiration_date

def get_shortened_link_phu(url):
    try:
        token = "6725c7b50c661e3428736919"
        api_url = f"https://link4m.co/api-shorten/v2?api={token}&url={urllib.parse.quote(url)}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": f"Lỗi {response.status_code}: Không thể kết nối đến dịch vụ rút gọn URL."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi rút gọn URL: {e}"}

def process_free_key(device_id):
    if datetime.now(HANOI_TZ).hour >= 21:
        print(f"{do}Đã qua 21:00 giờ Việt Nam, key miễn phí cho hôm nay đã hết hạn.{trang}")
        print(f"{vang}Vui lòng quay lại vào ngày mai để nhận key mới.{trang}")
        time.sleep(3)
        return False

    url, key, expiration_date = generate_free_key_and_url(device_id)
    shortened_data = get_shortened_link_phu(url)

    if shortened_data and shortened_data.get('status') == "error":
        print(f"{do}{shortened_data.get('message')}{trang}")
        return False

    link_key_shortened = shortened_data.get('shortenedUrl')
    if not link_key_shortened:
        print(f"{do}Không thể tạo link rút gọn. Vui lòng thử lại.{trang}")
        return False

    print(f'{trang}[{do}<>{trang}] {hong}Vui Lòng Vượt Link Để Lấy Key Free (Hết hạn 21:00 hàng ngày).{trang}')
    print(f'{trang}[{do}<>{trang}] {hong}Link Để Vượt Key Là {xnhac}: {link_key_shortened}{trang}')

    while True:
        keynhap = input(f'{trang}[{do}<>{trang}] {vang}Key Đã Vượt Là: {luc}')
        if keynhap == key:
            print(f'{luc}Key Đúng! Mời Bạn Dùng Tool{trang}')
            if datetime.now(HANOI_TZ) >= expiration_date:
                print(f"{do}Rất tiếc, key này đã hết hạn vào lúc 21:00. Vui lòng quay lại vào ngày mai.{trang}")
                return False
            time.sleep(2)
            save_free_key_info(device_id, keynhap, expiration_date)
            return True
        else:
            print(f'{trang}[{do}<>{trang}] {hong}Key Sai! Vui Lòng Vượt Lại Link {xnhac}: {link_key_shortened}{trang}')

def main_authentication():
    ip_address = get_ip_address()
    device_id = get_device_id()
    display_machine_info(ip_address, device_id)

    if not device_id:
        print(f"{do}Không thể lấy thông tin Mã Máy. Vui lòng kiểm tra lại thiết bị.{trang}")
        return False

    cached_vip_info = load_vip_key_info()
    if cached_vip_info and cached_vip_info.get('device_id') == device_id:
        try:
            expiry_date = datetime.strptime(cached_vip_info['expiration_date'], '%d/%m/%Y')
            if expiry_date.date() >= datetime.now().date():
                print(f"{luc}Đã tìm thấy Key VIP hợp lệ, tự động đăng nhập...{trang}")
                display_remaining_time(cached_vip_info['expiration_date'])
                sleep(3)
                return True
            else:
                print(f"{vang}Key VIP đã lưu đã hết hạn. Vui lòng lấy hoặc nhập key mới.{trang}")
        except (ValueError, KeyError):
            print(f"{do}Lỗi file lưu key VIP. Vui lòng nhập lại key.{trang}")

    if check_saved_free_key(device_id):
        expiry_str = f"21:00 ngày {datetime.now(HANOI_TZ).strftime('%d/%m/%Y')}"
        print(f"{trang}[{do}<>{trang}] {hong}Key free hôm nay vẫn còn hạn (Hết hạn lúc {expiry_str}). Mời bạn dùng tool...{trang}")
        time.sleep(2)
        return True

    while True:
        print(f"{trang}========== {vang}MENU LỰA CHỌN{trang} ==========")
        print(f"{trang}[{luc}1{trang}] {xduong}Nhập Key VIP{trang}")
        print(f"{trang}[{luc}2{trang}] {xduong}Lấy Key Free (Hết hạn 21:00 hàng ngày){trang}")
        print(f"{trang}======================================")

        try:
            choice = input(f"{trang}[{do}<>{trang}] {xduong}Nhập lựa chọn của bạn: {trang}")
            print(f"{trang}═══════════════════════════════════")

            if choice == '1':
                vip_key_input = input(f'{trang}[{do}<>{trang}] {vang}Vui lòng nhập Key VIP: {luc}')
                status, expiry_date_str = check_vip_key(device_id, vip_key_input)

                if status == 'valid':
                    print(f"{luc}Xác thực Key VIP thành công!{trang}")
                    save_vip_key_info(device_id, vip_key_input, expiry_date_str)
                    display_remaining_time(expiry_date_str)
                    sleep(3)
                    return True
                elif status == 'expired':
                    print(f"{do}Key VIP của bạn đã hết hạn. Vui lòng liên hệ admin.{trang}")
                elif status == 'not_found':
                    print(f"{do}Key VIP không hợp lệ hoặc không tồn tại cho mã máy này.{trang}")
                else:
                    print(f"{do}Đã xảy ra lỗi trong quá trình xác thực. Vui lòng thử lại.{trang}")
                sleep(2)

            elif choice == '2':
                return process_free_key(device_id)

            else:
                print(f"{vang}Lựa chọn không hợp lệ, vui lòng nhập 1 hoặc 2.{trang}")

        except KeyboardInterrupt:
            print(f"\n{trang}[{do}<>{trang}] {do}Cảm ơn bạn đã dùng Tool !!!{trang}")
            sys.exit()

from urllib.parse import urlparse, parse_qs
from collections import Counter, defaultdict
import requests
import time

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.style import Style
    from rich.text import Text
except ImportError:
    print("Thư viện 'rich' chưa được cài đặt. Vui lòng cài đặt: pip install rich")
    sys.exit(1)

console = Console()
STYLE_SUCCESS, STYLE_ERROR, STYLE_WARNING, STYLE_INFO, STYLE_HEADER, STYLE_VALUE = \
    Style(color="green"), Style(color="red"), Style(color="yellow"), Style(color="cyan"), \
    Style(color="magenta", bold=True), Style(color="blue", bold=True)

def clear_console(): os.system("cls" if os.name == "nt" else "clear")
def show_header():
    header = Text("Tool Xworld Vua thoát hiểm V2.5PLUS- admin: DUONG PHUNG nhóm zalo: https://zalo.me/g/ddxsyp497  telegram: @tankeko12 -Lưu ý : Hãy quản lí vốn thật tốt; không tham lam, biết điểm dừng. Chúc bạn dùng tool vui vẻ!!", style=STYLE_HEADER, justify="center")
    console.print(Panel(header, border_style="magenta", expand=False)); console.print()

CONFIG_FILE = "config.json"
def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        if console.input(f"🔎 Đã tìm thấy file config. Dùng lại? ([bold green]Y[/bold green]/n): ").strip().lower() in ["y", "yes", ""]:
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if all(k in config for k in ["stop_profit", "stop_loss", "max_lose_streak", "play_rounds", "pause_rounds"]):
                        return config
            except (json.JSONDecodeError, KeyError):
                console.print("⚠️ File config bị lỗi hoặc không hợp lệ. Vui lòng tạo mới.", style=STYLE_WARNING)

    console.print("⚠️ Không tìm thấy config hoặc config cũ. Vui lòng tạo mới.", style=STYLE_WARNING)
    config = {
        "url_game": console.input(f"[{STYLE_INFO}]Nhập Link Game:[/] ").strip(),
        "bet_type": console.input(f"[{STYLE_INFO}]Nhập Loại Tiền cược (BUILD/USDT/WORLD):[/] ").strip().upper(),
        "base_bet": float(console.input(f"[{STYLE_INFO}]Nhập Số Tiền Cược cơ bản:[/] ").strip()),
        "multiplier": float(console.input(f"[{STYLE_INFO}]Nhập Cấp số nhân sau khi thua:[/] ").strip()),
        "max_lose_streak": int(console.input(f"[{STYLE_WARNING}]Nhập Giới hạn chuỗi thua để DỪNG/RESET (ví dụ: 5):[/] ").strip()),
        "stop_profit": float(console.input(f"[{STYLE_SUCCESS}]Nhập Số LÃI mục tiêu để DỪNG (ví dụ: 50):[/] ").strip()),
        "stop_loss": float(console.input(f"[{STYLE_ERROR}]Nhập Mức LỖ tối đa để DỪNG (ví dụ: 100):[/] ").strip())
    }

    while True:
        try:
            config["play_rounds"] = int(console.input(f"[{STYLE_INFO}]Nhập số ván muốn chơi trước khi tạm nghỉ (nhập 0 để chơi liên tục):[/] ").strip())
            config["pause_rounds"] = int(console.input(f"[{STYLE_INFO}]Nhập số ván muốn nghỉ sau mỗi phiên:[/] ").strip())
            if config["play_rounds"] > 0 and config["pause_rounds"] <= 0:
                console.print("🔥 Nếu đã cài số ván chơi, số ván nghỉ phải lớn hơn 0. Vui lòng nhập lại.", style=STYLE_WARNING)
                continue
            if config["play_rounds"] < 0 or config["pause_rounds"] < 0:
                 console.print("🔥 Vui lòng nhập số dương.", style=STYLE_WARNING)
                 continue
            break
        except ValueError:
            console.print("🔥 Vui lòng nhập một số hợp lệ.", style=STYLE_ERROR)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(config, f, indent=4)
    console.print(f"✅ Đã lưu config vào file [bold cyan]{CONFIG_FILE}[/bold cyan]", style=STYLE_SUCCESS)
    return config

def choose_safe_room(recent_100, lose_streak=0, last_win_room=None, user_id=None, issue_id=None):
    try:
        full_history = [int(r["killed_room_id"]) for r in recent_100 if "killed_room_id" in r] if isinstance(recent_100, list) else []
        if len(full_history) < 25:
            return random.randint(1, 8), "Lịch sử không đủ"

        DEFENSIVE_MODE = lose_streak >= 2
        
        unthinkable_rooms = set()
        last_killed = full_history[0]
        unthinkable_rooms.add(last_killed)
        if last_win_room:
            unthinkable_rooms.add(last_win_room)
        
        if len(full_history) > 1 and full_history[0] == full_history[1]:
            unthinkable_rooms.add(full_history[0])

        fire_counts = Counter(full_history[:12])
        for room, count in fire_counts.items():
            if count >= 3:
                unthinkable_rooms.add(room)

        risky_rooms = defaultdict(set)
        
        hot_counts_15 = Counter(full_history[:15])
        for room, count in hot_counts_15.items():
            if count >= 2: risky_rooms["hot"].add(room)
        
        gaps = {r: full_history.index(r) if r in full_history else len(full_history) for r in range(1, 9)}
        coldest_room = max(gaps, key=gaps.get)
        if gaps[coldest_room] > 25:
            risky_rooms["cold"].add(coldest_room)
            
        transitions = defaultdict(Counter)
        for i in range(len(full_history) - 1):
            transitions[full_history[i+1]][full_history[i]] += 1
        if last_killed in transitions and transitions[last_killed]:
            most_likely_next = transitions[last_killed].most_common(1)[0][0]
            risky_rooms["transition"].add(most_likely_next)

        risky_rooms["position"].add((last_killed % 8) + 1)
        risky_rooms["position"].add((last_killed - 2 + 8) % 8 + 1)
        opposites = {1: 5, 5: 1, 2: 6, 6: 2, 3: 7, 7: 3, 4: 8, 8: 4}
        if opposites.get(last_killed):
            risky_rooms["position"].add(opposites.get(last_killed))
            
        if len(full_history) > 2 and full_history[0] == full_history[2]:
            risky_rooms["ping_pong"].add(full_history[1])

        recent_4_parity = [r % 2 for r in full_history[:4]]
        if len(set(recent_4_parity)) == 1:
            target_parity = 1 - recent_4_parity[0]
            for r in range(1, 9):
                if r % 2 != target_parity:
                    risky_rooms["parity"].add(r)


        candidate_pool = set(range(1, 9)) - unthinkable_rooms
        all_risks = set().union(*risky_rooms.values())

        tier1_safe_pool = [r for r in candidate_pool if r not in all_risks]
        
        if DEFENSIVE_MODE:
            if not tier1_safe_pool:
                return None, "Bỏ qua (Phòng thủ)"
            final_pool = tier1_safe_pool
            status = "Bậc 1 (Phòng thủ)"
        else:
            tier2_safe_pool = [r for r in candidate_pool if sum(1 for risk_set in risky_rooms.values() if r in risk_set) == 1]
            if tier1_safe_pool:
                final_pool = tier1_safe_pool
                status = "Bậc 1 (Tối ưu)"
            elif tier2_safe_pool:
                final_pool = tier2_safe_pool
                status = "Bậc 2 (Khá tốt)"
            else:
                final_pool = list(candidate_pool) if candidate_pool else list(set(range(1, 9)) - {last_killed})
                status = "Dự phòng"
            
        if not final_pool:
            return random.randint(1, 8), "Dự phòng khẩn cấp"

        final_pool.sort()
        if not user_id or not issue_id:
            return random.choice(final_pool), status + " (Ngẫu nhiên)"
        try:
            choice_index = (int(user_id) + int(issue_id)) % len(final_pool)
            return final_pool[choice_index], status
        except (ValueError, TypeError):
            return random.choice(final_pool), status + " (Lỗi ID)"

    except Exception:
        return random.randint(1, 8), "Lỗi ngoại lệ"

def make_api_request(session, method, url, max_retries=3, **kwargs):
    base_delay = 1
    for attempt in range(max_retries):
        time.sleep(random.uniform(0.3, 0.8))
        try:
            response = session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1: return None
            time.sleep((base_delay * 2 ** attempt) + random.uniform(0.5, 1.5))
    return None

def get_wallet_balance(session, url, bet_type):
    resp = make_api_request(session, "GET", url)
    if not resp or resp.get("code") not in [0, 200]: return None
    wallet = resp.get("data", {}).get("cwallet")
    if wallet is None: return None
    key_map = {"USDT": "ctoken_kusdt", "WORLD": "ctoken_kther", "BUILD": "ctoken_contribute"}
    balance_str = wallet.get(key_map.get(bet_type))
    return float(balance_str) if balance_str is not None else None

def display_summary(session_state, round_data, config, room_names_map):
    BET_TYPE, MAX_LOSE_STREAK = config["bet_type"], config["max_lose_streak"]
    win_rate = (session_state['wins'] / (session_state['wins'] + session_state['losses']) * 100) if (session_state['wins'] + session_state['losses']) > 0 else 0
    
    summary_table = Table(title=f"[bold]Tóm Tắt Vòng {session_state['round']}[/]", show_header=True, header_style="bold magenta")
    summary_table.add_column("Chỉ số", width=15); summary_table.add_column("Thống Kê")
    summary_table.add_row("Ván đấu", f"#{round_data.get('issue_id', 'N/A')}")
    summary_table.add_row("Hành động", round_data.get('action', Text("---")))
    if round_data.get('result'):
        killed_room_id = round_data['result'].get('killed_room_id', 'N/A')
        killed_room_name = room_names_map.get(str(killed_room_id), '?')
        summary_table.add_row("Phòng Sát Thủ", f"{killed_room_id} ({killed_room_name})")
    
    if round_data.get('final_balance') is not None:
        summary_table.add_row("Số dư Hiện tại", f"{round_data.get('final_balance', 0):.4f} {BET_TYPE}")

    summary_table.add_row("Kết quả", round_data.get('outcome', Text("---")))
    summary_table.add_row("Tiền cược", f"{round_data.get('bet_amount', 0):.4f} {BET_TYPE}")
    profit_text = Text(f"{round_data.get('round_profit', 0):+.4f}", style=STYLE_SUCCESS if round_data.get('round_profit', 0) >= 0 else STYLE_ERROR)
    summary_table.add_row("Lời/Lỗ Vòng", profit_text)
    total_profit_text = Text(f"{session_state.get('cumulative_profit', 0):+.4f}", style=STYLE_SUCCESS if session_state.get('cumulative_profit', 0) >= 0 else STYLE_ERROR)
    summary_table.add_row("Tổng Lời/Lỗ", total_profit_text)
    summary_table.add_row("Thắng/Thua", f"{session_state['wins']}/{session_state['losses']} ({win_rate:.2f}%)")
    summary_table.add_row("Chuỗi thắng", f"{session_state['win_streak']} (Max: {session_state['max_win_streak']})")
    summary_table.add_row("Chuỗi thua", f"[red]{session_state['lose_streak']}[/red]/{MAX_LOSE_STREAK}")
    console.print(summary_table); console.print("-" * 60)

def main():
        
    clear_console(); show_header(); config = load_or_create_config()
    try:
        params = parse_qs(urlparse(config["url_game"]).query)
        user_id, secret_key = params.get("userId", [None])[0], params.get("secretKey", [None])[0]
        if not user_id or not secret_key: raise ValueError("Invalid Link")
    except (ValueError, IndexError, TypeError):
        console.print("[red]LỖI: Link game không hợp lệ.[/red]"); return

    BET_TYPE, BASE_BET, MULTIPLIER, STOP_PROFIT, STOP_LOSS, MAX_LOSE_STREAK, PLAY_ROUNDS, PAUSE_ROUNDS = \
        config["bet_type"], config["base_bet"], config["multiplier"], \
        config["stop_profit"], config["stop_loss"], config["max_lose_streak"], \
        config["play_rounds"], config["pause_rounds"]
    
    ROOM_NAMES = {"1":"Nhà Kho", "2":"Phòng Họp", "3":"PhGĐ", "4":"PhTròChuyện", "5":"PhGiámSát", "6":"VănPhòng", "7":"PhTàiVụ", "8":"PhNhânSự"}

    API_BASE = "https://api.escapemaster.net/escape_game"
    URL_USER_INFO = "https://user.3games.io/user/regist?is_cwallet=1"
    URL_BET = f"{API_BASE}/bet"
    URL_RECENT_10 = f"{API_BASE}/recent_10_issues?asset={BET_TYPE}"
    URL_RECENT_100 = f"{API_BASE}/recent_issues?limit=100&asset={BET_TYPE}"
    
    title = "[bold cyan]Cấu Hình Hoạt Động[/]"
    play_pause_text = f"Chơi {PLAY_ROUNDS} ván, nghỉ {PAUSE_ROUNDS} ván" if PLAY_ROUNDS > 0 else "Chơi liên tục"
    text = (f"Loại Tiền Cược : {BET_TYPE}\nCược Cơ Bản    : {BASE_BET}\nCấp số nhân    : x{MULTIPLIER}\n"
            f"Chế độ chơi     : {play_pause_text}\n"
            f"[yellow]Giới hạn thua   : {MAX_LOSE_STREAK} ván[/yellow]\n"
            f"[green]Mục tiêu Lãi   : +{STOP_PROFIT}[/green]\n[red]Ngưỡng Cắt Lỗ  : -{STOP_LOSS}[/red]")
    console.print(Panel(Text(text, style="white"), title=title, border_style="cyan", expand=False))

    api_session = requests.Session()
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    ]
    api_session.headers.update({"user-id": user_id, "user-secret-key": secret_key, "user-agent": random.choice(USER_AGENTS)})
    
    console.print("🔄 [italic]Đang quét số dư ban đầu làm mốc...[/italic]")
    initial_balance = get_wallet_balance(api_session, URL_USER_INFO, BET_TYPE)
    if initial_balance is None:
        console.print("❌ [red]Không thể lấy số dư ban đầu. Vui lòng kiểm tra lại Link Game và kết nối.[/red]"); return
    console.print(f"✅ [green]Số dư ban đầu được ghi nhận: [bold]{initial_balance:.4f} {BET_TYPE}[/bold][/green]\n")
    
    session_state = { "round": 0, "wins": 0, "losses": 0, "cumulative_profit": 0.0, "lose_streak": 0, "win_streak": 0, "max_win_streak": 0, "last_known_issue_id": None, "last_bet_on": None, "balance_before_bet": initial_balance, "initial_balance": initial_balance, "rounds_played_this_session": 0, "rounds_to_skip": 0, "last_win_room": None, "attempted_bet_for_issue": None }

    while True:
        try:
            resp10 = make_api_request(api_session, "GET", URL_RECENT_10)
            if not resp10 or not resp10.get("data"):
                console.print("[yellow]Không thể lấy lịch sử 10 ván, đang chờ...[/yellow]", end="\r"); time.sleep(5); continue
            
            latest_result = resp10["data"][0]
            latest_issue_id = str(latest_result.get("issue_id"))

            if latest_issue_id != session_state["last_known_issue_id"]:
                session_state["round"] += 1
                console.print(f"\n--- Vòng {session_state['round']}: Xử lý kết quả ván #{latest_issue_id} ---", style="bold yellow")
                
                round_data = {"issue_id": latest_issue_id, "bet_amount": 0, "round_profit": 0, "result": latest_result, "action": Text("---"), "outcome": Text("Không cược", style="dim")}
                last_bet = session_state.get("last_bet_on")
                
                if last_bet and str(last_bet["issue_id"]) == latest_issue_id:
                    if PLAY_ROUNDS > 0: session_state["rounds_played_this_session"] += 1
                    killed_room_id = latest_result.get("killed_room_id")
                    bet_room, bet_amount, balance_before = last_bet['room'], last_bet['amount'], session_state['balance_before_bet']

                    console.print("[cyan]... Đang đồng bộ số dư từ máy chủ ...[/cyan]", end="\r"); time.sleep(random.uniform(8, 12))
                    final_balance = get_wallet_balance(api_session, URL_USER_INFO, BET_TYPE)
                    console.print(" " * 60, end="\r")
                    
                    is_win = (killed_room_id is not None and int(killed_room_id) != int(bet_room))
                    
                    if is_win:
                        round_data["outcome"] = Text("THẮNG", style=STYLE_SUCCESS)
                        session_state["wins"] += 1
                        session_state["lose_streak"] = 0
                        session_state["win_streak"] += 1
                        session_state["last_win_room"] = bet_room
                        session_state["max_win_streak"] = max(session_state["max_win_streak"], session_state["win_streak"])
                        round_profit = (final_balance - balance_before) if final_balance is not None and balance_before is not None else bet_amount * 0.95
                    else:
                        round_data["outcome"] = Text("THUA", style=STYLE_ERROR)
                        session_state["losses"] += 1
                        session_state["lose_streak"] += 1
                        session_state["win_streak"] = 0
                        round_profit = -bet_amount
                    
                    session_state["cumulative_profit"] = (final_balance - session_state["initial_balance"]) if final_balance is not None else session_state["cumulative_profit"] + round_profit
                    
                    bet_room_name = ROOM_NAMES.get(str(bet_room), '?')
                    action_text = Text(f"Đã cược Phòng {bet_room} ({bet_room_name})", style=STYLE_INFO)
                    round_data.update({ "bet_amount": bet_amount, "action": action_text, "round_profit": round_profit, "final_balance": final_balance })
                
                if session_state["round"] > 1 or (session_state["round"] == 1 and last_bet): display_summary(session_state, round_data, config, ROOM_NAMES)
                
                if 0 < MAX_LOSE_STREAK <= session_state['lose_streak']:
                    console.print(Panel(f"BẠN ĐÃ THUA LIÊN TIẾP {session_state['lose_streak']} VÁN!", title="[bold yellow]ĐẠT GIỚI HẠN CHUỖI THUA[/bold yellow]", border_style="yellow"))
                    choice = console.input("Bạn muốn [bold green]Chơi tiếp[/bold green] (reset tiền cược) hay [bold red]Nghỉ[/bold red]? (mặc định là Chơi tiếp) [C/N]: ").strip().lower()
                    if choice in ['n', 'nghi']: console.print("[yellow]Bot đã dừng theo yêu cầu của người dùng.[/yellow]"); return
                    else: session_state['lose_streak'] = 0; console.print("[green]Đã reset tiền cược về mức ban đầu. Tiếp tục chơi...[/green]\n")

                if session_state['cumulative_profit'] >= STOP_PROFIT: console.print(Panel(f"✅ ĐÃ ĐẠT MỤC TIÊU LỢI NHUẬN! (Tổng lãi: {session_state['cumulative_profit']:.4f} {BET_TYPE})", title="[bold green]DỪNG TOOL[/bold green]", border_style="green")); return
                if session_state['cumulative_profit'] <= -STOP_LOSS: console.print(Panel(f"❌ ĐÃ CHẠM NGƯỠNG CẮT LỖ! (Tổng lỗ: {session_state['cumulative_profit']:.4f} {BET_TYPE})", title="[bold red]DỪNG TOOL[/bold red]", border_style="red")); return

                session_state["last_known_issue_id"] = latest_issue_id
                next_round_id = int(latest_issue_id) + 1
                
                if session_state['round'] <= 2:
                    console.print(f"👋 [yellow]Bỏ qua ván #{session_state['round']} theo cài đặt (bắt đầu từ ván 3).[/yellow]")
                    session_state["last_bet_on"] = None
                    time.sleep(3)
                    continue

                if session_state['attempted_bet_for_issue'] == next_round_id:
                    time.sleep(3)
                    continue
                session_state['attempted_bet_for_issue'] = next_round_id

                if PLAY_ROUNDS > 0 and session_state["rounds_played_this_session"] >= PLAY_ROUNDS:
                    console.print(Panel(f"Đã hoàn thành {session_state['rounds_played_this_session']} ván. Bắt đầu nghỉ {PAUSE_ROUNDS} ván.", title="[bold cyan]TẠM NGHỈ[/bold cyan]", border_style="cyan"))
                    session_state["rounds_to_skip"] = PAUSE_ROUNDS; session_state["rounds_played_this_session"] = 0

                if session_state["rounds_to_skip"] > 0:
                    console.print(f"😴 [yellow]Đang trong thời gian nghỉ, bỏ qua cược. Còn lại [bold]{session_state['rounds_to_skip']}[/bold] ván nghỉ...[/yellow]")
                    session_state["rounds_to_skip"] -= 1; session_state["last_bet_on"] = None; time.sleep(5); continue
                
                current_balance = get_wallet_balance(api_session, URL_USER_INFO, BET_TYPE)
                if current_balance is None:
                    console.print(f"⚠️ Không thể xác minh số dư, tạm bỏ qua ván #{next_round_id} để đảm bảo an toàn.", style=STYLE_WARNING); session_state["last_bet_on"] = None; time.sleep(10); continue
                
                session_state['balance_before_bet'] = current_balance
                console.print(f"💰 Số dư hiện tại: [bold green]{current_balance:.4f} {BET_TYPE}[/bold green] | Chuẩn bị cho ván: [bold]#{next_round_id}[/bold]")
                
                resp100 = make_api_request(api_session, "GET", URL_RECENT_100)
                recent_100_hist = resp100.get("data") if resp100 and resp100.get("data") else []
                
                console.print(f"⏳ [italic]Chờ một chút trước khi phân tích...[/italic]", end="\r")
                time.sleep(random.uniform(3, 5))
                console.print(" " * 60, end="\r")

                if session_state['lose_streak'] >= 2:
                    console.print(f"🛡️ [bold yellow]CHUỖI THUA = {session_state['lose_streak']}. Kích hoạt Chế Độ Phòng Thủ...[/bold yellow]")
                else:
                    console.print(f"🤖 [italic]BOT V2.5PLUS đang phân tích ván #{next_round_id}...[/italic]")

                predicted_room, status = choose_safe_room(recent_100_hist, session_state['lose_streak'], session_state['last_win_room'], user_id, next_round_id)
                
                if predicted_room is None:
                    console.print(f"🛡️ [yellow]Phân tích hoàn tất: {status}. Không có phòng nào đủ an toàn. Bỏ qua ván này để bảo toàn vốn.[/yellow]")
                    session_state["last_bet_on"] = None
                    time.sleep(5)
                    continue

                if status != "Lịch sử không đủ":
                    console.print(f"🧠 Phân tích hoàn tất. Lựa chọn từ nhóm: [bold cyan]{status}[/bold cyan]")
                
                base_bet_amount = round(BASE_BET * (MULTIPLIER ** session_state["lose_streak"]), 4)
                bet_amount = round(base_bet_amount, 4)
                
                if bet_amount > current_balance:
                    console.print(f"⚠️ Không đủ số dư ({current_balance:.4f}). Cần {bet_amount:.4f}. Bỏ qua ván.", style=STYLE_WARNING); session_state["last_bet_on"] = None
                else:
                    predicted_room_name = ROOM_NAMES.get(str(predicted_room), "?")
                    console.print(f"✅ Cược [bold blue]{bet_amount:.4f} {BET_TYPE}[/bold blue] vào phòng [bold blue]{predicted_room} ({predicted_room_name})[/bold blue] cho ván [bold]#{next_round_id}[/bold]...")
                    
                    bet_payload = { "asset_type": BET_TYPE, "user_id": int(user_id), "room_id": predicted_room, "bet_amount": bet_amount }
                    bet_response = make_api_request(api_session, "POST", URL_BET, json=bet_payload)

                    if bet_response and bet_response.get("code") == 0:
                        session_state["last_bet_on"] = {"issue_id": next_round_id, "room": predicted_room, "amount": bet_amount}
                        console.print("✅ Đặt cược thành công!", style="green")
                    else:
                        console.print(f"❌ Đặt cược thất bại! Phản hồi: {bet_response}", style="red"); session_state["last_bet_on"] = None
            else:
                console.print(f"[yellow]... Chờ kết quả ván #{int(latest_issue_id) + 1} ...[/yellow]", end="\r")
                time.sleep(3)
        except Exception as e:
            console.print(f"\n[red]Gặp lỗi trong vòng lặp chính: {e}. Đang thử lại sau 10 giây...[/red]"); time.sleep(10)

if __name__ == "__main__":
    if main_authentication():
        try:
            main()
        except KeyboardInterrupt:
            console.print("\n\nBot đã dừng bởi người dùng.", style="bold yellow")
        except Exception as e:
            console.print(f"\nĐã xảy ra lỗi không mong muốn:", style=STYLE_ERROR)
            console.print_exception(show_locals=False)
