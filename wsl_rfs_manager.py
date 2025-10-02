#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSL RFS Manager - WSL ext4.vhdx 파일 위치를 찾는 프로그램
"""

import subprocess
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import threading

class WSLRFSManager:
    def __init__(self):
        self.root = None
        self.distributions = []
        self.vhdx_locations = []

    def run_powershell_command(self, command):
        """PowerShell 명령을 실행하고 결과를 반환"""
        try:
            result = subprocess.run(
                ['powershell', '-Command', command],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30  # 30초 타임아웃 추가
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return "", "명령 시간이 초과되었습니다 (30초)"
        except Exception as e:
            return "", str(e)

    def get_wsl_distributions(self):
        """레지스트리에서 WSL 배포판 정보를 가져옴"""
        command = '''
        Get-ItemProperty "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Lxss\\*" |
        Select-Object DistributionName, BasePath |
        ConvertTo-Json -Compress
        '''

        output, error = self.run_powershell_command(command)
        if error:
            return []

        try:
            # JSON 배열을 직접 파싱
            if output.strip():
                distributions = json.loads(output)
                if isinstance(distributions, list):
                    return [
                        {
                            'name': dist.get('DistributionName', 'Unknown'),
                            'path': dist.get('BasePath', '')
                        }
                        for dist in distributions
                    ]
                elif isinstance(distributions, dict):
                    # 단일 객체인 경우
                    return [{
                        'name': distributions.get('DistributionName', 'Unknown'),
                        'path': distributions.get('BasePath', '')
                    }]

            return []
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing distributions: {e}")
            return []

    def find_vhdx_files(self, distribution_path):
        """특정 배포판 경로에서 ext4.vhdx 파일을 찾음"""
        vhdx_files = []

        try:
            # 배포판 경로에서 직접 찾기 시도
            if distribution_path:
                # 경로 정규화 (UNC 경로 처리)
                normalized_path = distribution_path.replace('\\\\?\\', '')

                # 일반적인 vhdx 파일 위치들 검색
                search_paths = [
                    normalized_path,
                    os.path.join(normalized_path, "LocalState"),
                    os.path.expanduser(r"~\AppData\Local\Microsoft\WindowsApps"),
                ]

                for search_path in search_paths:
                    if os.path.exists(search_path):
                        # 해당 경로에서 ext4.vhdx 파일 찾기
                        for root, dirs, files in os.walk(search_path):
                            for file in files:
                                if file == "ext4.vhdx":
                                    vhdx_files.append(os.path.join(root, file))
                            # 너무 깊게 검색하지 않도록 제한
                            if root.count(os.sep) - search_path.count(os.sep) >= 3:
                                dirs.clear()

            return vhdx_files

        except Exception as e:
            print(f"Error finding vhdx files: {e}")
            return vhdx_files

    def scan_distributions(self):
        """모든 배포판을 스캔하여 vhdx 파일 위치를 찾음"""
        self.distributions = self.get_wsl_distributions()
        self.vhdx_locations = []

        for dist in self.distributions:
            vhdx_files = self.find_vhdx_files(dist['path'])
            if vhdx_files:
                self.vhdx_locations.append({
                    'distribution': dist['name'],
                    'path': dist['path'],
                    'vhdx_files': vhdx_files
                })

        return self.vhdx_locations

class WSLRFSGUI:
    def __init__(self):
        self.manager = WSLRFSManager()
        self.root = tk.Tk()
        self.root.title("WSL RFS Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.setup_ui()
        self.center_window()

    def center_window(self):
        """창을 화면 중앙에 배치"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """사용자 인터페이스 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 제목
        title_label = ttk.Label(
            main_frame,
            text="WSL ext4.vhdx 파일 위치 찾기",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        # 스캔 버튼
        self.scan_button = ttk.Button(
            button_frame,
            text="WSL 배포판 스캔",
            command=self.start_scan,
            width=20
        )
        self.scan_button.grid(row=0, column=0, padx=5)

        # 새로고침 버튼
        self.refresh_button = ttk.Button(
            button_frame,
            text="새로고침",
            command=self.refresh_results,
            width=20,
            state=tk.DISABLED
        )
        self.refresh_button.grid(row=0, column=1, padx=5)

        # 진행률 표시줄
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 결과 텍스트 영역
        result_frame = ttk.LabelFrame(main_frame, text="검색 결과", padding="5")
        result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Consolas", 10)
        )
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 상태바
        self.status_var = tk.StringVar()
        self.status_var.set("준비 완료")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 메인 프레임의 무게 배분 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

    def start_scan(self):
        """스캔 작업을 시작"""
        self.scan_button.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("스캔 중...")
        self.progress_var.set(0)

        # 백그라운드에서 스캔 실행
        scan_thread = threading.Thread(target=self.scan_worker, daemon=True)
        scan_thread.start()

    def scan_worker(self):
        """백그라운드에서 스캔 작업 수행"""
        try:
            # 진행률 업데이트 (메인 스레드에서 실행)
            self.root.after(0, lambda: self.progress_var.set(25))
            locations = self.manager.scan_distributions()

            self.root.after(0, lambda: self.progress_var.set(75))

            # 결과 표시 (메인 스레드에서 실행)
            self.root.after(0, lambda: self.display_results(locations))

            self.root.after(0, lambda: self.progress_var.set(100))

            def update_status():
                if locations:
                    self.status_var.set(f"{len(locations)}개의 배포판에서 ext4.vhdx 파일을 찾았습니다")
                else:
                    self.status_var.set("ext4.vhdx 파일을 찾을 수 없습니다")

            def update_buttons():
                self.scan_button.config(state=tk.NORMAL)
                self.refresh_button.config(state=tk.NORMAL)

            self.root.after(0, update_status)
            self.root.after(0, update_buttons)

        except Exception as e:
            def show_error():
                self.status_var.set(f"오류 발생: {str(e)}")
                messagebox.showerror("오류", f"스캔 중 오류가 발생했습니다:\n{str(e)}")
                self.scan_button.config(state=tk.NORMAL)
                self.refresh_button.config(state=tk.NORMAL)

            self.root.after(0, show_error)

    def display_results(self, locations):
        """검색 결과를 텍스트 영역에 표시"""
        self.result_text.delete(1.0, tk.END)

        if not locations:
            self.result_text.insert(tk.END, "WSL 배포판이나 ext4.vhdx 파일을 찾을 수 없습니다.\n\n")
            self.result_text.insert(tk.END, "다음 사항을 확인하세요:\n")
            self.result_text.insert(tk.END, "1. WSL이 설치되어 있는지 확인\n")
            self.result_text.insert(tk.END, "2. WSL 배포판이 설치되어 있는지 확인\n")
            self.result_text.insert(tk.END, "3. 관리자 권한으로 실행 중인지 확인\n")
            return

        for i, location in enumerate(locations, 1):
            self.result_text.insert(tk.END, f"=== 배포판 {i}: {location['distribution']} ===\n")
            self.result_text.insert(tk.END, f"설치 경로: {location['path']}\n")

            if location['vhdx_files']:
                self.result_text.insert(tk.END, "찾은 ext4.vhdx 파일:\n")
                for vhdx_file in location['vhdx_files']:
                    self.result_text.insert(tk.END, f"  • {vhdx_file}\n")
            else:
                self.result_text.insert(tk.END, "ext4.vhdx 파일을 찾을 수 없습니다.\n")

            self.result_text.insert(tk.END, "\n")

        # 결과 끝에 요약 정보 추가
        self.result_text.insert(tk.END, f"총 {len(locations)}개의 배포판을 발견했습니다.\n")

    def refresh_results(self):
        """결과를 새로고침"""
        if self.manager.vhdx_locations:
            self.display_results(self.manager.vhdx_locations)
            self.status_var.set("결과를 새로고침했습니다")
        else:
            self.status_var.set("새로고침할 결과가 없습니다. 먼저 스캔을 실행하세요.")

    def run(self):
        """애플리케이션 실행"""
        self.root.mainloop()

def main():
    """메인 함수"""
    try:
        # Windows에서만 실행 가능
        if os.name != 'nt':
            print("이 프로그램은 Windows에서만 실행할 수 있습니다.")
            return

        app = WSLRFSGUI()
        app.run()

    except Exception as e:
        messagebox.showerror("오류", f"프로그램 실행 중 오류가 발생했습니다:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()