#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import re
import socket
from typing import List, Dict, Tuple, Optional
from colorama import init, Fore, Style
from tabulate import tabulate

# Thêm đường dẫn hiện tại vào sys.path để có thể import các module trong cùng thư mục
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from check_instagram import InstagramAPI, IgApiCallStatusCode
except ModuleNotFoundError:
    print("Không tìm thấy module check_instagram. Đảm bảo file check_instagram.py nằm trong cùng thư mục.")
    sys.exit(1)

# Khởi tạo colorama
init(autoreset=True)

class ProxyManager:
    """Quản lý danh sách proxy"""
    
    def __init__(self, proxy_file: str):
        """
        Khởi tạo proxy manager
        
        Args:
            proxy_file: Đường dẫn đến file chứa danh sách proxy
        """
        self.proxies = []
        self.current_index = 0
        
        # Đọc danh sách proxy từ file
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                for line in f:
                    proxy = line.strip()
                    if proxy:
                        self.proxies.append(proxy)
            
            print(f"Đã tải {len(self.proxies)} proxy từ file {proxy_file}")
        else:
            print(f"Không tìm thấy file proxy {proxy_file}")
    
    def detect_proxy_type(self, proxy: str) -> str:
        """
        Phát hiện loại proxy (SOCKS5 hay HTTP)
        
        Args:
            proxy: Proxy cần phát hiện loại
            
        Returns:
            str: Proxy với prefix đúng loại
        """
        # Nếu đã có prefix, giữ nguyên
        if proxy.startswith('socks5://') or proxy.startswith('http://'):
            return proxy
        
        # Kiểm tra xem có phải là SOCKS5 không
        if ':' in proxy:
            host, port_str = proxy.split(':')
            try:
                port = int(port_str)
                # Thử kết nối SOCKS5
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    sock.connect((host, port))
                    # Gửi SOCKS5 handshake
                    sock.sendall(b'\x05\x01\x00')
                    response = sock.recv(2)
                    sock.close()
                    if response[0] == 5:  # SOCKS5 protocol version
                        return f"socks5://{proxy}"
                except:
                    # Nếu không phải SOCKS5, mặc định là HTTP
                    return f"http://{proxy}"
            except:
                pass
        
        # Mặc định là HTTP nếu không xác định được
        if ':' in proxy:
            return f"http://{proxy}"
        return None
    
    def get_next_proxy(self) -> Optional[str]:
        """
        Lấy proxy tiếp theo trong danh sách
        
        Returns:
            str: Proxy tiếp theo hoặc None nếu không có proxy nào
        """
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        # Xác định loại proxy (HTTP hay SOCKS5)
        return self.detect_proxy_type(proxy)
    
class AccountChecker:
    """Kiểm tra danh sách tài khoản Instagram"""
    
    def __init__(self, account_file: str, proxy_file: str):
        """
        Khởi tạo account checker
        
        Args:
            account_file: Đường dẫn đến file chứa danh sách tài khoản
            proxy_file: Đường dẫn đến file chứa danh sách proxy
        """
        self.account_file = account_file
        self.proxy_manager = ProxyManager(proxy_file)
        
        # Thống kê
        self.total_accounts = 0
        self.live_accounts = []
        self.die_accounts = []
        self.unknown_accounts = []
        
        # Cấu hình debug và tốc độ
        self.debug_mode = False
        self.speed_mode = 1  # 1: Chậm, 2: Trung bình, 3: Nhanh
        self.preferred_method = 0
    
    def load_accounts(self) -> List[str]:
        """
        Tải danh sách tài khoản từ file
        
        Returns:
            List[str]: Danh sách tài khoản
        """
        accounts = []
        
        if os.path.exists(self.account_file):
            with open(self.account_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        accounts.append(line)
            
            print(f"Đã tải {len(accounts)} tài khoản từ file {self.account_file}")
        else:
            print(f"Không tìm thấy file tài khoản {self.account_file}")
        
        return accounts
    
    def check_accounts(self):
        """Kiểm tra danh sách tài khoản"""
        accounts = self.load_accounts()
        self.total_accounts = len(accounts)
        
        if not accounts:
            print("Không có tài khoản nào để kiểm tra")
            return
        
        # Xác định timeout và chế độ nhanh dựa trên speed_mode
        timeout = 10
        fast_mode = False
        
        if self.speed_mode == 2:  # Trung bình
            timeout = 7
            fast_mode = False
        elif self.speed_mode == 3:  # Nhanh
            timeout = 5
            fast_mode = True
        
        # Tạo các file kết quả
        with open('LIVE.txt', 'w', encoding='utf-8') as live_file, \
             open('DIE.txt', 'w', encoding='utf-8') as die_file, \
             open('UNKNOWN.txt', 'w', encoding='utf-8') as unknown_file:
            
            for i, account_line in enumerate(accounts, 1):
                # Lấy username từ dòng tài khoản (phần đầu tiên trước dấu |)
                parts = account_line.split('|')
                if not parts:
                    continue
                
                username = parts[0].strip()
                
                # Hiển thị thông tin đang kiểm tra
                if not self.debug_mode:
                    self.display_stats()
                print(f"Đang kiểm tra [{i}/{self.total_accounts}]: {username}")
                
                # Lấy proxy
                proxy = self.proxy_manager.get_next_proxy()
                if proxy:
                    print(f"Sử dụng proxy: {proxy}")
                
                # Khởi tạo API với proxy
                api = InstagramAPI(proxy=proxy, timeout=timeout, fast_mode=fast_mode, preferred_method=self.preferred_method)
                
                # Kiểm tra tài khoản
                result = api.query_account_by_username(username)
                
                # Xử lý kết quả
                if result.is_success:
                    self.live_accounts.append(account_line)
                    live_file.write(f"{account_line}\n")
                    live_file.flush()
                    print(f"{Fore.GREEN}✓ LIVE: {username}{Style.RESET_ALL}")
                elif result.ig_status_code == IgApiCallStatusCode.Checkpoint:
                    self.die_accounts.append(account_line)
                    die_file.write(f"{account_line}\n")
                    die_file.flush()
                    print(f"{Fore.RED}✗ DIE: {username}{Style.RESET_ALL}")
                else:
                    self.unknown_accounts.append(account_line)
                    unknown_file.write(f"{account_line}\n")
                    unknown_file.flush()
                    print(f"{Fore.YELLOW}? UNKNOWN: {username}{Style.RESET_ALL}")
                
                # Hiển thị bảng thống kê
                if not self.debug_mode:
                    # Delay tùy theo chế độ tốc độ
                    if self.speed_mode == 1:  # Chậm
                        time.sleep(random.uniform(1, 3))
                    elif self.speed_mode == 2:  # Trung bình
                        time.sleep(random.uniform(0.5, 1.5))
                    else:  # Nhanh
                        time.sleep(random.uniform(0.1, 0.5))
                else:
                    # Không xóa màn hình trong chế độ debug
                    self.display_stats(clear_screen=False)
                    time.sleep(0.2)
    
    def display_stats(self, clear_screen=True):
        """
        Hiển thị thống kê
        
        Args:
            clear_screen: Có xóa màn hình hay không
        """
        # Tính tỉ lệ LIVE/Tổng
        if self.total_accounts > 0:
            ratio = (len(self.live_accounts) / self.total_accounts) * 100
        else:
            ratio = 0
        
        # Tạo bảng thống kê
        table = [
            ["Tổng", self.total_accounts],
            [f"{Fore.GREEN}LIVE{Style.RESET_ALL}", f"{Fore.GREEN}{len(self.live_accounts)}{Style.RESET_ALL}"],
            [f"{Fore.RED}DIE{Style.RESET_ALL}", f"{Fore.RED}{len(self.die_accounts)}{Style.RESET_ALL}"],
            ["Tỉ lệ", f"{ratio:.2f}%"]
        ]
        
        # Xóa màn hình
        if clear_screen:
            os.system('cls' if os.name == 'nt' else 'clear')
        
        # Hiển thị bảng
        print(tabulate(table, headers=["Trạng thái", "Số lượng"], tablefmt="grid"))
        
        # Hiển thị thông tin thêm
        checked = len(self.live_accounts) + len(self.die_accounts) + len(self.unknown_accounts)
        print(f"\nĐã kiểm tra: {checked}/{self.total_accounts}")
        print(f"UNKNOWN: {len(self.unknown_accounts)}")
        
        # Hiển thị chế độ tốc độ
        speed_text = "Chậm" if self.speed_mode == 1 else "Trung bình" if self.speed_mode == 2 else "Nhanh"
        print(f"Tốc độ: {speed_text}")
        
        method_text = "Tự động" if self.preferred_method == 0 else f"Phương thức {self.preferred_method}"
        print(f"Phương thức API: {method_text}")

def main():
    """Hàm chính"""
    print("Instagram Account Checker")
    print("------------------------")
    print("Developed by HoangAnhDev")
    print("Telegram: @HoangAnhDev")
    print("------------------------")
    
    # Kiểm tra file account.txt và proxy.txt
    account_file = "account.txt"
    proxy_file = "proxy.txt"
    
    if not os.path.exists(account_file):
        print(f"Không tìm thấy file {account_file}")
        return
    
    if not os.path.exists(proxy_file):
        print(f"Không tìm thấy file {proxy_file}, sẽ kiểm tra không dùng proxy")
    
    # Hỏi người dùng có muốn bật chế độ debug không
    debug_choice = input("Bật chế độ debug? (y/n): ").lower()
    debug_mode = debug_choice == 'y' or debug_choice == 'yes'
    
    # Hỏi người dùng chọn tốc độ kiểm tra
    print("\nChọn tốc độ kiểm tra:")
    print("1. Chậm (an toàn nhất, ít bị chặn)")
    print("2. Trung bình")
    print("3. Nhanh (có thể bị chặn IP)")
    
    speed_choice = input("Lựa chọn của bạn (1/2/3): ")
    speed_mode = 1  # Mặc định là chậm
    
    if speed_choice == "2":
        speed_mode = 2
    elif speed_choice == "3":
        speed_mode = 3
    
    print("\nChọn phương thức API ưu tiên:")
    print("0. Tự động (thử tất cả các phương thức)")
    print("1. API Web (?__a=1&__d=dis)")
    print("2. API Mobile (web_profile_info)")
    print("3. Kiểm tra trực tiếp trang profile")
    
    method_choice = input("Lựa chọn của bạn (0/1/2/3): ")
    preferred_method = 0
    
    if method_choice in ["1", "2", "3"]:
        preferred_method = int(method_choice)
    
    # Khởi tạo account checker
    checker = AccountChecker(account_file, proxy_file)
    checker.debug_mode = debug_mode
    checker.speed_mode = speed_mode
    checker.preferred_method = preferred_method
    
    # Kiểm tra tài khoản
    checker.check_accounts()
    
    print("\nKết quả kiểm tra:")
    print(f"- Tài khoản LIVE: {len(checker.live_accounts)} (đã lưu vào LIVE.txt)")
    print(f"- Tài khoản DIE: {len(checker.die_accounts)} (đã lưu vào DIE.txt)")
    print(f"- Tài khoản UNKNOWN: {len(checker.unknown_accounts)} (đã lưu vào UNKNOWN.txt)")

if __name__ == "__main__":
    main() 