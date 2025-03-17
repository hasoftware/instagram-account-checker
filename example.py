#!/usr/bin/env python
# -*- coding: utf-8 -*-

from check_instagram import InstagramAPI, IgApiCallStatusCode

def check_by_id():
    """Kiểm tra tài khoản bằng ID"""
    account_id = input("Nhập ID tài khoản Instagram: ")
    
    # Khởi tạo API
    api = InstagramAPI()
    
    # Kiểm tra tài khoản
    print(f"Đang kiểm tra ID: {account_id}...")
    result = api.query_account_info(account_id)
    
    if result.is_success:
        print("✅ Tài khoản tồn tại!")
        if result.data and 'user' in result.data:
            user_data = result.data['user']
            print(f"Username: {user_data.get('username', 'N/A')}")
            print(f"Full name: {user_data.get('full_name', 'N/A')}")
            print(f"Followers: {user_data.get('follower_count', 'N/A')}")
            print(f"Following: {user_data.get('following_count', 'N/A')}")
            print(f"Biography: {user_data.get('biography', 'N/A')}")
            print(f"Profile pic URL: {user_data.get('profile_pic_url', 'N/A')}")
    else:
        print(f"❌ Trạng thái: {result.ig_status_code.name}")

def check_by_username():
    """Kiểm tra tài khoản bằng username"""
    username = input("Nhập tên người dùng Instagram: ")
    
    # Khởi tạo API
    api = InstagramAPI()
    
    # Kiểm tra tài khoản
    print(f"Đang kiểm tra username: {username}...")
    result = api.query_account_by_username(username)
    
    if result.is_success:
        print("✅ Tài khoản tồn tại!")
        if result.data:
            try:
                user_data = result.data.get('graphql', {}).get('user', {})
                print(f"Username: {user_data.get('username', 'N/A')}")
                print(f"Full name: {user_data.get('full_name', 'N/A')}")
                print(f"Followers: {user_data.get('edge_followed_by', {}).get('count', 'N/A')}")
                print(f"Following: {user_data.get('edge_follow', {}).get('count', 'N/A')}")
                print(f"Biography: {user_data.get('biography', 'N/A')}")
                print(f"Profile pic URL: {user_data.get('profile_pic_url', 'N/A')}")
            except:
                print("Không thể phân tích dữ liệu người dùng")
    else:
        print(f"❌ Trạng thái: {result.ig_status_code.name}")

def check_multiple_accounts():
    """Kiểm tra nhiều tài khoản từ file"""
    filename = input("Nhập tên file chứa danh sách username (mỗi username một dòng): ")
    
    try:
        with open(filename, 'r') as f:
            usernames = [line.strip() for line in f if line.strip()]
    except:
        print(f"Không thể đọc file {filename}")
        return
    
    print(f"Đã tìm thấy {len(usernames)} tài khoản để kiểm tra")
    
    # Khởi tạo API
    api = InstagramAPI()
    
    # Kết quả
    results = {
        "success": [],
        "failed": []
    }
    
    # Kiểm tra từng tài khoản
    for i, username in enumerate(usernames, 1):
        print(f"[{i}/{len(usernames)}] Đang kiểm tra: {username}...")
        result = api.query_account_by_username(username)
        
        if result.is_success:
            print(f"✅ {username}: Tồn tại")
            results["success"].append(username)
        else:
            print(f"❌ {username}: {result.ig_status_code.name}")
            results["failed"].append(username)
    
    # Tổng kết
    print("\n--- Kết quả ---")
    print(f"Tổng số tài khoản: {len(usernames)}")
    print(f"Tồn tại: {len(results['success'])}")
    print(f"Không tồn tại: {len(results['failed'])}")

def main():
    """Hàm chính"""
    print("Instagram Account Checker - Ví dụ")
    print("----------------------------------")
    
    while True:
        print("\nChọn chức năng:")
        print("1. Kiểm tra bằng ID tài khoản")
        print("2. Kiểm tra bằng tên người dùng")
        print("3. Kiểm tra nhiều tài khoản từ file")
        print("4. Thoát")
        
        choice = input("Lựa chọn của bạn: ")
        
        if choice == "1":
            check_by_id()
        elif choice == "2":
            check_by_username()
        elif choice == "3":
            check_multiple_accounts()
        elif choice == "4":
            break
        else:
            print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main() 