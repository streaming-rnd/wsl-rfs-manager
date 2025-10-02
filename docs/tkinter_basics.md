# Tkinter 기본 사용법

## 개요
이 프로젝트에서는 Tkinter를 사용하여 WSL 배포판과 ext4.vhdx 파일 위치를 찾는 그래픽 사용자 인터페이스(GUI)를 구현합니다.

## 기본 윈도우 생성

```python
import tkinter as tk
from tkinter import ttk

class WSLRFSGUI:
    def __init__(self):
        self.root = tk.Tk()  # 기본 윈도우 생성
        self.root.title("WSL RFS Manager")  # 윈도우 제목 설정
        self.root.geometry("800x600")  # 윈도우 크기 설정
        self.root.resizable(True, True)  # 창 크기 조절 가능하도록 설정
```

## 주요 구성 요소

### 1. Tkinter 기본 요소들
- `tk.Tk()`: 기본 윈도우 생성
- `tk.Frame`: 컨테이너 위젯 (다른 위젯들을 그룹화)
- `ttk.Label`: 텍스트 라벨
- `ttk.Button`: 버튼
- `ttk.Progressbar`: 진행률 표시줄

### 2. 프로젝트에서 사용되는 주요 모듈들

```python
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import threading
```

- `tkinter`: 기본 Tkinter 모듈
- `ttk`: Themed Tkinter (더 나은 스타일의 위젯들)
- `messagebox`: 메시지박스 (알림, 오류 등)
- `scrolledtext`: 스크롤 가능한 텍스트 영역
- `threading`: 백그라운드 작업을 위한 스레딩

## 창 관리 기법

### 창 중앙 배치
```python
def center_window(self):
    """창을 화면 중앙에 배치"""
    self.root.update_idletasks()
    width = self.root.winfo_width()
    height = self.root.winfo_height()
    x = (self.root.winfo_screenwidth() // 2) - (width // 2)
    y = (self.root.winfo_screenheight() // 2) - (height // 2)
    self.root.geometry(f'{width}x{height}+{x}+{y}')
```

### 창 크기 및 위치 정보 얻기
- `winfo_screenwidth()` / `winfo_screenheight()`: 화면 크기
- `winfo_width()` / `winfo_height()`: 현재 창 크기
- `winfo_x()` / `winfo_y()`: 창 위치

## 상태 관리

### StringVar를 사용한 동적 텍스트 업데이트
```python
# 상태바 설정
self.status_var = tk.StringVar()
self.status_var.set("준비 완료")

status_bar = ttk.Label(
    main_frame,
    textvariable=self.status_var,  # StringVar 연결
    relief=tk.SUNKEN,
    anchor=tk.W
)
```

### 진행률 표시줄
```python
self.progress_var = tk.DoubleVar()
self.progress_bar = ttk.Progressbar(
    main_frame,
    variable=self.progress_var,
    maximum=100
)
```

## 메시지박스 활용

```python
from tkinter import messagebox

# 오류 메시지 표시
messagebox.showerror("오류", f"스캔 중 오류가 발생했습니다:\n{str(e)}")

# 정보 메시지 표시
messagebox.showinfo("정보", "스캔이 완료되었습니다.")
```

## 프로젝트 실행 구조

```python
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
```

## 핵심 포인트

1. **메인 윈도우**: `tk.Tk()`로 생성하며, 애플리케이션의 기본 창
2. **위젯 구성**: `ttk` 모듈을 사용하여 더 나은 스타일의 위젯 사용
3. **동적 업데이트**: `StringVar`, `DoubleVar` 등을 사용하여 실시간 업데이트
4. **사용자 피드백**: 메시지박스와 상태바를 통한 사용자 정보 제공
5. **오류 처리**: 적절한 예외 처리와 사용자 친화적 오류 메시지