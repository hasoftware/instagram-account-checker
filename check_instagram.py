#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from enum import Enum
import time
import random
from typing import Dict, Any, Optional

class IgApiCallStatusCode(Enum):
    """Enum định nghĩa các trạng thái có thể có của API call"""
    Success = 0
    Checkpoint = 1
    UnknownBlockType = 2
    Error = 3

class IGApiQueryResult:
    """Lớp chứa kết quả trả về từ API Instagram"""
    def __init__(self):
        self.ig_status_code: IgApiCallStatusCode = IgApiCallStatusCode.Error
        self.data: Optional[Dict[str, Any]] = None
    
    @property
    def is_success(self) -> bool:
        return self.ig_status_code == IgApiCallStatusCode.Success

class InstagramAPI:
    """API để kiểm tra trạng thái tài khoản Instagram"""
    
    def __init__(self, proxy: Optional[str] = None, timeout: int = 10, fast_mode: bool = False, preferred_method: int = 0):
        """
        Khởi tạo Instagram API
        
        Args:
            proxy: Proxy để sử dụng (định dạng: "http://user:pass@host:port" hoặc "http://host:port")
            timeout: Thời gian chờ tối đa cho mỗi request (giây)
            fast_mode: Chế độ kiểm tra nhanh (chỉ dùng 1 phương thức)
            preferred_method: Phương thức API ưu tiên (0: tự động, 1: API Web, 2: API Mobile, 3: Kiểm tra trực tiếp trang profile)
        """
        # User-Agent của thiết bị Samsung (tương tự như trong code C#)
        self._samsung_ua = "Instagram 361.0.0.0.84 Android (28/9; 480dpi; 1080x1920; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 673256705)"
        self._desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        # Cấu hình proxy
        self._proxies = None
        if proxy:
            self._proxies = {
                "http": proxy,
                "https": proxy
            }
        
        # Cấu hình timeout và chế độ nhanh
        self._timeout = timeout
        self._fast_mode = fast_mode
        self._preferred_method = preferred_method
        
        # Session để tái sử dụng kết nối
        self._session = requests.Session()
    
    def query_account_info(self, account_id: str) -> IGApiQueryResult:
        """
        Kiểm tra thông tin tài khoản Instagram bằng ID
        
        Args:
            account_id: ID của tài khoản Instagram cần kiểm tra
            
        Returns:
            IGApiQueryResult: Kết quả kiểm tra
        """
        result = IGApiQueryResult()
        
        headers = {
            "User-Agent": self._samsung_ua,
            "Accept": "*/*",
            "Accept-Language": "en-US",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        try:
            response = self._session.get(
                f"https://i.instagram.com/api/v1/users/{account_id}/info/",
                headers=headers,
                proxies=self._proxies,
                timeout=self._timeout
            )
            
            response_text = response.text
            
            # Phân tích phản hồi để xác định trạng thái tài khoản
            if "username\":" in response_text or "profile_pic_url\":" in response_text:
                result.ig_status_code = IgApiCallStatusCode.Success
                result.data = response.json()
            elif "user_not_found\"" in response_text:
                result.ig_status_code = IgApiCallStatusCode.Checkpoint
            else:
                result.ig_status_code = IgApiCallStatusCode.UnknownBlockType
                
        except Exception as e:
            print(f"Error: {str(e)}")
            result.ig_status_code = IgApiCallStatusCode.Error
            
        return result

    def query_account_by_username(self, username: str) -> IGApiQueryResult:
        """
        Kiểm tra thông tin tài khoản Instagram bằng username
        
        Args:
            username: Tên người dùng Instagram cần kiểm tra
            
        Returns:
            IGApiQueryResult: Kết quả kiểm tra
        """
        result = IGApiQueryResult()
        
        if self._fast_mode:
            if self._preferred_method == 1:
                return self._check_method_1(username)
            elif self._preferred_method == 2:
                return self._check_method_2(username)
            else:
                return self._check_method_3(username)
        
        methods_to_try = [1, 2, 3]
        
        if self._preferred_method > 0:
            methods_to_try.remove(self._preferred_method)
            methods_to_try.insert(0, self._preferred_method)
        
        for method in methods_to_try:
            try:
                if method == 1:
                    method_result = self._check_method_1(username)
                elif method == 2:
                    method_result = self._check_method_2(username)
                else:
                    method_result = self._check_method_3(username)
                
                if method_result.ig_status_code != IgApiCallStatusCode.UnknownBlockType:
                    return method_result
            except:
                pass
        
        result.ig_status_code = IgApiCallStatusCode.UnknownBlockType
        return result
    
    def _check_method_1(self, username: str) -> IGApiQueryResult:
        """Phương thức 1: Sử dụng API web"""
        result = IGApiQueryResult()
        
        headers = {
            "User-Agent": self._samsung_ua,
            "Accept": "*/*",
            "Accept-Language": "en-US",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        response = self._session.get(
            f"https://www.instagram.com/{username}/?__a=1&__d=dis",
            headers=headers,
            proxies=self._proxies,
            timeout=self._timeout
        )
        
        # Kiểm tra phản hồi
        if response.status_code == 200 and len(response.text) > 50:
            # Tài khoản tồn tại
            try:
                result.data = response.json()
                result.ig_status_code = IgApiCallStatusCode.Success
                return result
            except:
                pass
        
        if response.status_code == 404 or "user not found" in response.text.lower():
            result.ig_status_code = IgApiCallStatusCode.Checkpoint
        else:
            result.ig_status_code = IgApiCallStatusCode.UnknownBlockType
        
        return result
    
    def _check_method_2(self, username: str) -> IGApiQueryResult:
        """Phương thức 2: Sử dụng API mobile"""
        result = IGApiQueryResult()
        
        headers = {
            "User-Agent": self._samsung_ua,
            "Accept": "*/*",
            "X-IG-App-ID": "936619743392459",
            "X-ASBD-ID": "198387",
            "X-IG-WWW-Claim": "0",
            "Accept-Language": "en-US",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        response = self._session.get(
            f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
            headers=headers,
            proxies=self._proxies,
            timeout=self._timeout
        )
        
        if response.status_code == 200:
            result.ig_status_code = IgApiCallStatusCode.Success
            result.data = response.json()
        elif response.status_code == 404 or "user not found" in response.text.lower():
            result.ig_status_code = IgApiCallStatusCode.Checkpoint
        else:
            result.ig_status_code = IgApiCallStatusCode.UnknownBlockType
        
        return result
    
    def _check_method_3(self, username: str) -> IGApiQueryResult:
        """Phương thức 3: Kiểm tra trực tiếp trang profile"""
        result = IGApiQueryResult()
        
        headers = {
            "User-Agent": self._desktop_ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        response = self._session.get(
            f"https://www.instagram.com/{username}/",
            headers=headers,
            proxies=self._proxies,
            timeout=self._timeout
        )
        
        if response.status_code == 200 and ("profile picture" in response.text.lower() or "profile_pic_url" in response.text):
            result.ig_status_code = IgApiCallStatusCode.Success
            # Không có dữ liệu JSON, nhưng tài khoản tồn tại
        elif response.status_code == 404 or "sorry, this page isn't available" in response.text.lower():
            result.ig_status_code = IgApiCallStatusCode.Checkpoint
        else:
            result.ig_status_code = IgApiCallStatusCode.UnknownBlockType
        
        return result

def main():
    """Hàm chính để chạy tool"""
    print("Instagram Account Checker")
    print("------------------------")
    print("Developed by HoangAnhDev")
    print("Telegram: @HoangAnhDev")
    print("------------------------")
    
    # Hỏi người dùng có muốn dùng chế độ nhanh không
    fast_choice = input("Bật chế độ kiểm tra nhanh? (y/n): ").lower()
    fast_mode = fast_choice == 'y' or fast_choice == 'yes'
    
    print("\nChọn phương thức API ưu tiên:")
    print("0. Tự động (thử tất cả các phương thức)")
    print("1. API Web (?__a=1&__d=dis)")
    print("2. API Mobile (web_profile_info)")
    print("3. Kiểm tra trực tiếp trang profile")
    
    method_choice = input("Lựa chọn của bạn (0/1/2/3): ")
    preferred_method = 0
    
    if method_choice in ["1", "2", "3"]:
        preferred_method = int(method_choice)
    
    # Khởi tạo API
    api = InstagramAPI(fast_mode=fast_mode, preferred_method=preferred_method)
    
    while True:
        print("\nChọn chế độ kiểm tra:")
        print("1. Kiểm tra bằng ID tài khoản")
        print("2. Kiểm tra bằng tên người dùng")
        print("3. Thoát")
        
        choice = input("Lựa chọn của bạn: ")
        
        if choice == "1":
            account_id = input("Nhập ID tài khoản Instagram: ")
            result = api.query_account_info(account_id)
            
            if result.is_success:
                print(f"Tài khoản tồn tại!")
                if result.data and 'user' in result.data:
                    user_data = result.data['user']
                    print(f"Username: {user_data.get('username', 'N/A')}")
                    print(f"Full name: {user_data.get('full_name', 'N/A')}")
                    print(f"Followers: {user_data.get('follower_count', 'N/A')}")
                    print(f"Following: {user_data.get('following_count', 'N/A')}")
            else:
                print(f"Trạng thái: {result.ig_status_code.name}")
                
        elif choice == "2":
            username = input("Nhập tên người dùng Instagram: ")
            result = api.query_account_by_username(username)
            
            if result.is_success:
                print(f"Tài khoản tồn tại!")
                if result.data:
                    try:
                        if 'graphql' in result.data:
                            user_data = result.data.get('graphql', {}).get('user', {})
                            print(f"Username: {user_data.get('username', 'N/A')}")
                            print(f"Full name: {user_data.get('full_name', 'N/A')}")
                            print(f"Followers: {user_data.get('edge_followed_by', {}).get('count', 'N/A')}")
                            print(f"Following: {user_data.get('edge_follow', {}).get('count', 'N/A')}")
                        elif 'data' in result.data:
                            user_data = result.data.get('data', {}).get('user', {})
                            print(f"Username: {user_data.get('username', 'N/A')}")
                            print(f"Full name: {user_data.get('full_name', 'N/A')}")
                            print(f"Followers: {user_data.get('edge_followed_by', {}).get('count', 'N/A')}")
                            print(f"Following: {user_data.get('edge_follow', {}).get('count', 'N/A')}")
                    except:
                        print("Không thể phân tích dữ liệu người dùng")
            else:
                print(f"Trạng thái: {result.ig_status_code.name}")
                
        elif choice == "3":
            break
        else:
            print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main() 