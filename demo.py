#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import random
from colorama import init, Fore, Style
from tabulate import tabulate

# Khởi tạo colorama
init(autoreset=True)

def simulate_check():
    """Mô phỏng quá trình kiểm tra tài khoản Instagram"""
    # Giả lập dữ liệu
    total_accounts = 100
    live_accounts = []
    die_accounts = []
    unknown_accounts = []
    
    # Hiển thị tiêu đề
    print("Instagram Account Checker - Demo")
    print("-------------------------------")
    print("Đang kiểm tra tài khoản từ file account.txt...")
    print("Đang sử dụng proxy từ file proxy.txt...")
    
    # Mô phỏng quá trình kiểm tra
    for i in range(1, total_accounts + 1):
        # Xác định ngẫu nhiên trạng thái tài khoản
        status = random.choices(
            ["live", "die", "unknown"], 
            weights=[0.6, 0.3, 0.1], 
            k=1
        )[0]
        
        # Cập nhật danh sách
        if status == "live":
            live_accounts.append(f"account{i}")
        elif status == "die":
            die_accounts.append(f"account{i}")
        else:
            unknown_accounts.append(f"account{i}")
        
        # Hiển thị bảng thống kê
        display_stats(total_accounts, live_accounts, die_accounts)
        
        # Delay
        time.sleep(0.1)

def display_stats(total_accounts, live_accounts, die_accounts):
    """Hiển thị thống kê"""
    # Tính tỉ lệ LIVE/Tổng
    if total_accounts > 0:
        ratio = (len(live_accounts) / total_accounts) * 100
    else:
        ratio = 0
    
    # Tạo bảng thống kê
    table = [
        ["Tổng", total_accounts],
        [f"{Fore.GREEN}LIVE{Style.RESET_ALL}", f"{Fore.GREEN}{len(live_accounts)}{Style.RESET_ALL}"],
        [f"{Fore.RED}DIE{Style.RESET_ALL}", f"{Fore.RED}{len(die_accounts)}{Style.RESET_ALL}"],
        ["Tỉ lệ", f"{ratio:.2f}%"]
    ]
    
    # Xóa màn hình
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Hiển thị bảng
    print(tabulate(table, headers=["Trạng thái", "Số lượng"], tablefmt="grid"))
    
    # Hiển thị thông tin thêm
    print(f"\nĐã kiểm tra: {len(live_accounts) + len(die_accounts)}/{total_accounts}")
    print(f"UNKNOWN: {total_accounts - len(live_accounts) - len(die_accounts)}")

if __name__ == "__main__":
    simulate_check()
    
    # Hiển thị kết quả cuối cùng
    print("\nKết quả kiểm tra:")
    print("- Tài khoản LIVE đã được lưu vào LIVE.txt")
    print("- Tài khoản DIE đã được lưu vào DIE.txt")
    print("- Tài khoản UNKNOWN đã được lưu vào UNKNOWN.txt")
    print("\nCảm ơn bạn đã sử dụng tool!") 