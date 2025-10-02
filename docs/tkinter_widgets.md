# Tkinter 위젯 사용법

## 개요
이 프로젝트에서는 다양한 Tkinter 위젯을 활용하여 사용자 친화적인 인터페이스를 구현합니다. 주요 위젯들과 그 사용법을 살펴보겠습니다.

## 주요 위젯들

### 1. Label (라벨)
텍스트나 이미지를 표시하는 기본 위젯입니다.

```python
# 제목 라벨
title_label = ttk.Label(
    main_frame,
    text="WSL ext4.vhdx 파일 위치 찾기",
    font=("Helvetica", 16, "bold")
)
title_label.grid(row=0, column=0, columnspan=2, pady=10)
```

**주요 옵션:**
- `text`: 표시할 텍스트
- `font`: 폰트 설정 (글꼴, 크기, 스타일)
- `justify`: 텍스트 정렬 (LEFT, CENTER, RIGHT)

### 2. Button (버튼)
사용자 클릭 이벤트를 처리하는 위젯입니다.

```python
# 스캔 버튼
self.scan_button = ttk.Button(
    button_frame,
    text="WSL 배포판 스캔",
    command=self.start_scan,  # 클릭 시 실행할 함수
    width=20
)
self.scan_button.grid(row=0, column=0, padx=5)

# 상태에 따른 버튼 활성화/비활성화
self.scan_button.config(state=tk.DISABLED)  # 비활성화
self.scan_button.config(state=tk.NORMAL)   # 활성화
```

**주요 옵션:**
- `text`: 버튼에 표시할 텍스트
- `command`: 클릭 시 실행할 함수 (이벤트 핸들러)
- `width`: 버튼 너비
- `state`: 버튼 상태 (NORMAL, DISABLED, ACTIVE)

### 3. Progressbar (진행률 표시줄)
작업 진행률을 시각적으로 표시합니다.

```python
self.progress_var = tk.DoubleVar()
self.progress_bar = ttk.Progressbar(
    main_frame,
    variable=self.progress_var,  # 연결할 변수
    maximum=100  # 최대값
)
self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

# 진행률 업데이트
self.progress_var.set(25)  # 25%로 설정
```

**사용법:**
- `DoubleVar`와 연결하여 동적으로 업데이트
- `maximum`: 진행률 최대값 설정
- `mode`: 'determinate' (정확한 진행률) 또는 'indeterminate' (불확실한 진행률)

### 4. Text & ScrolledText (텍스트 영역)
다양한 양의 텍스트를 표시하고 편집할 수 있는 위젯입니다.

```python
from tkinter import scrolledtext

self.result_text = scrolledtext.ScrolledText(
    result_frame,
    wrap=tk.WORD,  # 단어 단위로 줄바꿈
    width=80,
    height=20,
    font=("Consolas", 10)  # 고정폭 폰트 사용
)
self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# 텍스트 추가
self.result_text.insert(tk.END, "새로운 텍스트\n")
self.result_text.delete(1.0, tk.END)  # 전체 삭제
```

**주요 메서드:**
- `insert(index, text)`: 지정 위치에 텍스트 삽입
- `delete(start, end)`: 텍스트 삭제
- `get(start, end)`: 텍스트 가져오기

**스크롤 기능:**
- `ScrolledText`: 자동 스크롤바 제공
- `tk.Scrollbar`와 함께 사용 가능

### 5. Frame (프레임)
다른 위젯들을 그룹화하는 컨테이너입니다.

```python
# 메인 프레임
main_frame = ttk.Frame(self.root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# 버튼 프레임 (버튼들을 그룹화)
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=1, column=0, columnspan=2, pady=10)

# 결과 프레임 (결과 영역을 그룹화)
result_frame = ttk.LabelFrame(main_frame, text="검색 결과", padding="5")
result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
```

**프레임 종류:**
- `tk.Frame`: 기본 프레임
- `ttk.Frame`: 스타일이 적용된 프레임
- `ttk.LabelFrame`: 제목이 있는 프레임

### 6. LabelFrame (제목이 있는 프레임)
그룹화와 함께 제목을 표시할 수 있는 프레임입니다.

```python
result_frame = ttk.LabelFrame(main_frame, text="검색 결과", padding="5")
```

**주요 옵션:**
- `text`: 프레임 제목
- `padding`: 내부 여백

## 변수와 위젯 연결

### StringVar, DoubleVar 활용
Tkinter에서는 특별한 변수 클래스를 사용하여 위젯과 값을 동기화할 수 있습니다.

```python
# 문자열 변수 (상태 메시지용)
self.status_var = tk.StringVar()
self.status_var.set("준비 완료")

status_bar = ttk.Label(
    main_frame,
    textvariable=self.status_var,  # 변수와 연결
    relief=tk.SUNKEN,
    anchor=tk.W
)

# 숫자 변수 (진행률용)
self.progress_var = tk.DoubleVar()
self.progress_bar = ttk.Progressbar(
    main_frame,
    variable=self.progress_var,
    maximum=100
)

# 값 업데이트는 변수의 set() 메서드로
self.status_var.set("스캔 중...")
self.progress_var.set(75)
```

## 실전 예제: 결과 표시 함수

```python
def display_results(self, locations):
    """검색 결과를 텍스트 영역에 표시"""
    self.result_text.delete(1.0, tk.END)  # 기존 내용 삭제

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
```

## 핵심 포인트

1. **위젯 선택**: 용도에 맞는 적절한 위젯 선택
2. **옵션 활용**: 각 위젯의 다양한 옵션을 활용하여 기능 구현
3. **변수 연결**: StringVar, DoubleVar 등을 통한 동적 업데이트
4. **그룹화**: Frame과 LabelFrame을 활용한 논리적 그룹화
5. **사용자 경험**: 적절한 피드백과 상태 표시