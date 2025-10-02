# Tkinter 레이아웃 관리

## 개요
Tkinter에서 위젯을 배치하는 방법에는 여러 가지가 있지만, 이 프로젝트에서는 주로 `grid` 레이아웃 관리자를 사용합니다. Grid는 표 형식으로 위젯을 배치할 수 있어 복잡한 UI를 구성하기에 적합합니다.

## Grid 레이아웃 관리자

### 기본 개념
Grid는 행(row)과 열(column)을 사용하여 위젯을 배치합니다:

```python
# 위젯 배치 기본 구조
widget.grid(row=0, column=0)  # 첫 번째 행, 첫 번째 열
```

### 프로젝트에서 사용되는 주요 Grid 옵션들

#### 1. 기본 위치 설정
```python
def setup_ui(self):
    """사용자 인터페이스 설정"""
    # 메인 프레임
    main_frame = ttk.Frame(self.root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # 제목 (0행, 0~1열 차지)
    title_label = ttk.Label(
        main_frame,
        text="WSL ext4.vhdx 파일 위치 찾기",
        font=("Helvetica", 16, "bold")
    )
    title_label.grid(row=0, column=0, columnspan=2, pady=10)
```

#### 2. sticky 옵션 활용
`sticky` 옵션은 위젯이 할당된 공간에서 어떻게 확장될지 결정합니다:

```python
# 모든 방향으로 확장
widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# 가로 방향만 확장
widget.grid(row=0, column=0, sticky=(tk.W, tk.E))

# 세로 방향만 확장
widget.grid(row=0, column=0, sticky=(tk.N, tk.S))
```

**sticky 방향:**
- `tk.W`: 왼쪽 (West)
- `tk.E`: 오른쪽 (East)
- `tk.N`: 위쪽 (North)
- `tk.S`: 아래쪽 (South)

#### 3. 여백 설정 (padx, pady, padding)
```python
# 버튼 프레임에 여백 추가
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=1, column=0, columnspan=2, pady=10)  # 세로 여백

# 버튼 사이에 가로 여백 추가
self.scan_button.grid(row=0, column=0, padx=5)  # 가로 여백
self.refresh_button.grid(row=0, column=1, padx=5)  # 가로 여백

# 프레임 자체에 내부 여백 추가
main_frame = ttk.Frame(self.root, padding="10")  # 모든 방향 10픽셀 여백
```

#### 4. columnspan과 rowspan
여러 행이나 열을 차지하도록 설정:

```python
# 제목: 2개 열 차지
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# 진행률바: 2개 열 차지
self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

# 결과 프레임: 2개 열 차지
result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
```

## 무게 배분 (weight) 설정

### 행과 열의 상대적 크기 조절
```python
# 메인 프레임의 무게 배분 설정
self.root.columnconfigure(0, weight=1)
self.root.rowconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(3, weight=1)  # 결과 영역이 더 크게
result_frame.columnconfigure(0, weight=1)
result_frame.rowconfigure(0, weight=1)
```

**무게 배분 원리:**
- `weight=1`: 창 크기 변경 시 해당 행/열이 확장됨
- `weight=0` (기본값): 창 크기 변경 시 크기 고정
- 숫자가 클수록 더 많은 공간을 차지

## 복잡한 레이아웃 예제

### 전체 UI 레이아웃 구조

```python
def setup_ui(self):
    """사용자 인터페이스 설정"""
    # 1. 메인 프레임 (전체 영역 차지)
    main_frame = ttk.Frame(self.root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # 2. 제목 행 (0행, 모든 열 차지)
    title_label = ttk.Label(
        main_frame,
        text="WSL ext4.vhdx 파일 위치 찾기",
        font=("Helvetica", 16, "bold")
    )
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # 3. 버튼 행 (1행, 모든 열 차지)
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=0, columnspan=2, pady=10)

    # 4. 진행률바 행 (2행, 모든 열 차지)
    self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

    # 5. 결과 영역 (3행, 모든 열 차지, 나머지 공간 모두 사용)
    result_frame = ttk.LabelFrame(main_frame, text="검색 결과", padding="5")
    result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

    # 6. 상태바 행 (4행, 모든 열 차지)
    status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

    # 7. 무게 배분 설정 (중요!)
    self.root.columnconfigure(0, weight=1)
    self.root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(3, weight=1)  # 결과 영역 우선 확장
    result_frame.columnconfigure(0, weight=1)
    result_frame.rowconfigure(0, weight=1)
```

## 레이아웃 디버깅 팁

### 1. 색상으로 영역 확인
```python
# 프레임에 배경색을 주어 영역 확인 (개발 시 유용)
main_frame = ttk.Frame(self.root, padding="10", relief="solid")
result_frame = ttk.LabelFrame(main_frame, text="검색 결과", padding="5", relief="solid")
```

### 2. Grid 정보 출력 (개발 시 유용)
```python
# 특정 위젯의 grid 정보 확인
print(f"Title label grid info: {title_label.grid_info()}")
print(f"Progress bar grid info: {self.progress_bar.grid_info()}")

# 모든 grid 슬레이브 확인
print(f"Main frame slaves: {main_frame.grid_slaves()}")
```

## 레이아웃 설계 원칙

### 1. 일관된 구조 사용
- 상단: 제목과 버튼들
- 중간: 진행률 표시
- 하단: 결과 영역 (가장 큰 공간 할당)
- 최하단: 상태 표시

### 2. 적절한 여백 사용
- 관련 위젯들 간: 작은 여백 (padx=5, pady=5)
- 주요 섹션 간: 큰 여백 (pady=10)
- 프레임 자체: 내부 여백 (padding="10")

### 3. 반응형 설계
- `sticky` 옵션으로 창 크기 변경에 대응
- `weight` 설정으로 공간 배분 제어
- 결과 영역과 같이 내용이 많은 곳에 더 많은 공간 할당

## 실제 프로젝트 레이아웃 분석

프로젝트의 레이아웃은 다음과 같은 그리드 구조를 가집니다:

```
행 0: 제목 (columnspan=2)
행 1: 버튼 프레임 (columnspan=2)
행 2: 진행률바 (columnspan=2)
행 3: 결과 프레임 (columnspan=2, 나머지 공간 모두 사용)
행 4: 상태바 (columnspan=2)

열 0: 모든 위젯의 시작점
열 1: 모든 위젯의 끝점 (여유 공간)
```

이 구조는 간단하면서도 기능적이며, 창 크기 변경에도 잘 대응합니다.