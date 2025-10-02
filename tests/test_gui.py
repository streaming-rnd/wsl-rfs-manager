#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 테스트 GUI - PowerShell 명령 테스트용
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import threading

class SimpleTestGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PowerShell 테스트")
        self.root.geometry("600x400")

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 버튼
        test_button = ttk.Button(
            main_frame,
            text="PowerShell 명령 테스트",
            command=self.test_powershell
        )
        test_button.grid(row=0, column=0, pady=10)

        # 결과 텍스트
        self.result_text = tk.Text(main_frame, height=15, width=60)
        self.result_text.grid(row=1, column=0, pady=10)

        # 상태 라벨
        self.status_var = tk.StringVar()
        self.status_var.set("준비 완료")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0)

        # 스크롤바
        scrollbar = ttk.Scrollbar(main_frame, command=self.result_text.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.result_text.config(yscrollcommand=scrollbar.set)

    def run_powershell_command(self, command):
        """PowerShell 명령 실행"""
        try:
            result = subprocess.run(
                ['powershell', '-Command', command],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return "", "명령 시간이 초과되었습니다"
        except Exception as e:
            return "", str(e)

    def test_powershell(self):
        """PowerShell 명령 테스트"""
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("테스트 중...")

        def run_test():
            try:
                # WSL 배포판 정보 가져오기
                command = '''
                Get-ItemProperty "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Lxss\\*" |
                Select-Object DistributionName, BasePath |
                ConvertTo-Json -Compress
                '''

                output, error = self.run_powershell_command(command)

                if error:
                    self.root.after(0, lambda: self.show_error(error))
                    return

                if output:
                    try:
                        distributions = json.loads(output)
                        result = f"성공! {len(distributions)}개의 배포판을 찾았습니다:\n\n"
                        for i, dist in enumerate(distributions, 1):
                            result += f"{i}. {dist.get('DistributionName', 'Unknown')}\n"
                            result += f"   경로: {dist.get('BasePath', '')}\n\n"

                        self.root.after(0, lambda: self.show_result(result))
                    except json.JSONDecodeError as e:
                        self.root.after(0, lambda: self.show_error(f"JSON 파싱 오류: {e}\n출력: {output}"))
                else:
                    self.root.after(0, lambda: self.show_error("출력이 없습니다"))

            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"오류: {str(e)}"))

        # 백그라운드에서 실행
        test_thread = threading.Thread(target=run_test, daemon=True)
        test_thread.start()

    def show_result(self, result):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, result)
        self.status_var.set("테스트 완료")

    def show_error(self, error):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, f"오류 발생:\n{error}")
        self.status_var.set("테스트 실패")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleTestGUI()
    app.run()