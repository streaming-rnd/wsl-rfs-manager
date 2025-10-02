# Tkinter 이벤트 처리

## 개요
이벤트 처리는 Tkinter GUI 애플리케이션의 핵심입니다. 사용자의 행동(버튼 클릭, 키 입력 등)에 응답하여 적절한 기능을 실행합니다.

## 기본 이벤트 처리

### 버튼 클릭 이벤트
가장 일반적인 이벤트 처리 방식은 버튼 클릭입니다:

```python
def setup_ui(self):
    """사용자 인터페이스 설정"""
    # 스캔 버튼
    self.scan_button = ttk.Button(
        button_frame,
        text="WSL 배포판 스캔",
        command=self.start_scan,  # 클릭 시 실행할 메서드
        width=20
    )
    self.scan_button.grid(row=0, column=0, padx=5)

    # 새로고침 버튼
    self.refresh_button = ttk.Button(
        button_frame,
        text="새로고침",
        command=self.refresh_results,  # 클릭 시 실행할 메서드
        width=20,
        state=tk.DISABLED  # 초기 상태는 비활성화
    )
    self.refresh_button.grid(row=0, column=1, padx=5)
```

## 이벤트 핸들러 메서드들

### 1. 스캔 시작 이벤트
```python
def start_scan(self):
    """스캔 작업을 시작"""
    # 버튼 상태 변경 (재클릭 방지)
    self.scan_button.config(state=tk.DISABLED)
    self.refresh_button.config(state=tk.DISABLED)

    # UI 초기화
    self.result_text.delete(1.0, tk.END)
    self.status_var.set("스캔 중...")
    self.progress_var.set(0)

    # 백그라운드에서 스캔 실행
    scan_thread = threading.Thread(target=self.scan_worker, daemon=True)
    scan_thread.start()
```

### 2. 결과 새로고침 이벤트
```python
def refresh_results(self):
    """결과를 새로고침"""
    if self.manager.vhdx_locations:
        self.display_results(self.manager.vhdx_locations)
        self.status_var.set("결과를 새로고침했습니다")
    else:
        self.status_var.set("새로고침할 결과가 없습니다. 먼저 스캔을 실행하세요.")
```

## 이벤트 처리의 주요 패턴

### 1. 즉시 실행 vs 지연 실행
Tkinter는 단일 스레드에서 실행되므로, 긴 작업은 백그라운드에서 실행하고 결과를 메인 스레드에서 업데이트해야 합니다:

```python
def scan_worker(self):
    """백그라운드에서 스캔 작업 수행"""
    try:
        # 작업 진행률 업데이트 (메인 스레드에서 실행)
        self.root.after(0, lambda: self.progress_var.set(25))
        locations = self.manager.scan_distributions()

        self.root.after(0, lambda: self.progress_var.set(75))

        # 결과 표시 (메인 스레드에서 실행)
        self.root.after(0, lambda: self.display_results(locations))

        # ... 상태 업데이트도 메인 스레드에서
        self.root.after(0, update_status)
        self.root.after(0, update_buttons)

    except Exception as e:
        # 오류 처리도 메인 스레드에서
        self.root.after(0, lambda: show_error())
```

### 2. `after` 메서드 활용
`after` 메서드는 지정된 시간 후에 함수를 실행합니다:

```python
# 1초 후에 상태 메시지 업데이트
self.root.after(1000, lambda: self.status_var.set("준비 완료"))

# 일정 시간마다 반복 실행 (예: 진행률 업데이트)
self.root.after(100, self.update_progress)  # 100ms마다 업데이트
```

## 상태 기반 이벤트 처리

### 버튼 상태 관리
작업 중에는 버튼을 비활성화하여 중복 실행을 방지합니다:

```python
def start_scan(self):
    """스캔 작업을 시작"""
    # 작업 시작 전 버튼 비활성화
    self.scan_button.config(state=tk.DISABLED)
    self.refresh_button.config(state=tk.DISABLED)
    # ... 작업 수행 ...

def scan_worker(self):
    """백그라운드에서 스캔 작업 수행"""
    try:
        # ... 작업 수행 ...
    finally:
        # 작업 완료 후 버튼 활성화 (항상 실행)
        def update_buttons():
            self.scan_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)
        self.root.after(0, update_buttons)
```

## 키보드 이벤트 처리

### Enter 키 이벤트 처리 예시
```python
# 엔터 키로 스캔 실행 (선택적 기능)
self.root.bind('<Return>', lambda e: self.start_scan() if self.scan_button['state'] == tk.NORMAL else None)
```

## 마우스 이벤트 처리

### 버튼 호버 효과 (선택적)
```python
def setup_ui(self):
    """사용자 인터페이스 설정"""
    # 마우스 호버 이벤트 바인딩
    self.scan_button.bind('<Enter>', lambda e: self.scan_button.config(style='Hover.TButton'))
    self.scan_button.bind('<Leave>', lambda e: self.scan_button.config(style='TButton'))
```

## 이벤트 처리 시 주의사항

### 1. 예외 처리
이벤트 핸들러에서는 적절한 예외 처리가 중요합니다:

```python
def start_scan(self):
    """스캔 작업을 시작"""
    try:
        # 버튼 상태 변경
        self.scan_button.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)

        # ... 작업 수행 ...

    except Exception as e:
        # 오류 발생 시 사용자에게 알림
        self.status_var.set(f"오류 발생: {str(e)}")
        messagebox.showerror("오류", f"스캔 중 오류가 발생했습니다:\n{str(e)}")

        # 버튼 상태 복원
        self.scan_button.config(state=tk.NORMAL)
        self.refresh_button.config(state=tk.NORMAL)
```

### 2. UI 업데이트는 메인 스레드에서
백그라운드 스레드에서는 UI를 직접 업데이트할 수 없습니다:

```python
# ❌ 잘못된 방식 (백그라운드 스레드에서 직접 UI 업데이트)
# self.progress_var.set(50)  # 오류 발생 가능

# ✅ 올바른 방식 (메인 스레드에서 업데이트)
self.root.after(0, lambda: self.progress_var.set(50))
```

## 실전 예제: 복잡한 이벤트 처리

### 작업 완료 후 일련의 이벤트 처리
```python
def scan_worker(self):
    """백그라운드에서 스캔 작업 수행"""
    try:
        # 진행률 업데이트
        self.root.after(0, lambda: self.progress_var.set(25))
        locations = self.manager.scan_distributions()

        self.root.after(0, lambda: self.progress_var.set(75))

        # 결과 표시
        self.root.after(0, lambda: self.display_results(locations))

        self.root.after(0, lambda: self.progress_var.set(100))

        # 상태 업데이트 함수들 정의
        def update_status():
            if locations:
                self.status_var.set(f"{len(locations)}개의 배포판에서 ext4.vhdx 파일을 찾았습니다")
            else:
                self.status_var.set("ext4.vhdx 파일을 찾을 수 없습니다")

        def update_buttons():
            self.scan_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)

        # 순차적으로 실행
        self.root.after(0, update_status)
        self.root.after(0, update_buttons)

    except Exception as e:
        def show_error():
            self.status_var.set(f"오류 발생: {str(e)}")
            messagebox.showerror("오류", f"스캔 중 오류가 발생했습니다:\n{str(e)}")
            self.scan_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)

        self.root.after(0, show_error)
```

## 이벤트 처리 원칙

1. **단순함**: 각 이벤트 핸들러는 하나의 명확한 기능을 수행
2. **안전성**: 적절한 예외 처리와 오류 복구
3. **사용자 피드백**: 작업 상태를 실시간으로 사용자에게 알림
4. **상태 관리**: 버튼 활성화/비활성화로 사용자 행동 제어
5. **스레드 안전성**: UI 업데이트는 메인 스레드에서만 수행

이러한 이벤트 처리 방식을 통해 응답성 좋고 사용자 친화적인 GUI 애플리케이션을 만들 수 있습니다.