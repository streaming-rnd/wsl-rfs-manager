# Tkinter 스레딩 및 비동기 처리

## 개요
Tkinter는 단일 스레드에서 실행되므로, 긴 작업을 수행할 때 UI가 멈추는 것을 방지하기 위해 스레딩을 사용해야 합니다. 이 프로젝트에서는 WSL 배포판 스캔과 같은 장시간 작업을 백그라운드에서 실행합니다.

## 기본 스레딩 구조

### Threading 모듈 사용
```python
import threading

class WSLRFSGUI:
    def start_scan(self):
        """스캔 작업을 시작"""
        # 백그라운드에서 스캔 실행
        scan_thread = threading.Thread(target=self.scan_worker, daemon=True)
        scan_thread.start()

    def scan_worker(self):
        """백그라운드에서 스캔 작업 수행"""
        # 실제 작업 수행
        locations = self.manager.scan_distributions()
        # 결과 업데이트 (메인 스레드에서)
        self.root.after(0, lambda: self.display_results(locations))
```

## 스레딩의 필요성

### 문제 상황
Tkinter에서 긴 작업을 메인 스레드에서 직접 실행하면 UI가 응답하지 않습니다:

```python
# ❌ 잘못된 방식 - UI가 멈춤
def bad_scan(self):
    self.status_var.set("스캔 중...")  # UI 업데이트
    time.sleep(5)  # 5초 대기 - 이 동안 UI가 응답하지 않음!
    locations = self.manager.scan_distributions()  # 오래 걸리는 작업
    self.display_results(locations)  # 결과 업데이트
```

### 해결 방법
백그라운드 스레드에서 작업을 실행하고, UI 업데이트는 메인 스레드에서 수행:

```python
# ✅ 올바른 방식 - UI가 응답성 유지
def start_scan(self):
    """스캔 작업을 시작"""
    self.status_var.set("스캔 중...")
    self.progress_var.set(0)

    # 백그라운드 스레드에서 작업 실행
    scan_thread = threading.Thread(target=self.scan_worker, daemon=True)
    scan_thread.start()

def scan_worker(self):
    """백그라운드에서 스캔 작업 수행"""
    locations = self.manager.scan_distributions()  # 오래 걸리는 작업

    # UI 업데이트는 메인 스레드에서
    self.root.after(0, lambda: self.display_results(locations))
    self.root.after(0, lambda: self.status_var.set("스캔 완료"))
```

## after 메서드 활용

### 기본 사용법
`after` 메서드는 지정된 시간 후에 함수를 메인 스레드에서 실행합니다:

```python
# 즉시 실행
self.root.after(0, lambda: self.status_var.set("완료"))

# 1초 후 실행
self.root.after(1000, lambda: self.status_var.set("준비 완료"))

# 반복 실행
self.root.after(100, self.update_progress)  # 100ms마다 업데이트
```

### 프로젝트에서의 활용 예시
```python
def scan_worker(self):
    """백그라운드에서 스캔 작업 수행"""
    try:
        # 진행률 업데이트 (단계별로)
        self.root.after(0, lambda: self.progress_var.set(25))
        locations = self.manager.scan_distributions()

        self.root.after(0, lambda: self.progress_var.set(75))

        # 결과 표시
        self.root.after(0, lambda: self.display_results(locations))

        self.root.after(0, lambda: self.progress_var.set(100))

        # 상태 및 버튼 업데이트
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
```

## 진행률 업데이트 패턴

### 단계별 진행률 표시
```python
def scan_worker(self):
    """백그라운드에서 스캔 작업 수행"""
    def update_progress(step, total=100):
        progress = (step / total) * 100
        self.root.after(0, lambda: self.progress_var.set(progress))

    try:
        # 단계 1: 배포판 정보 수집 (25%)
        update_progress(1, 4)
        distributions = self.manager.get_wsl_distributions()

        # 단계 2: 파일 시스템 검색 (50%)
        update_progress(2, 4)
        vhdx_locations = []

        # 단계 3: 결과 처리 (75%)
        update_progress(3, 4)
        for dist in distributions:
            vhdx_files = self.manager.find_vhdx_files(dist['path'])
            if vhdx_files:
                vhdx_locations.append({
                    'distribution': dist['name'],
                    'path': dist['path'],
                    'vhdx_files': vhdx_files
                })

        # 단계 4: 완료 (100%)
        update_progress(4, 4)

        # 결과 표시
        self.root.after(0, lambda: self.display_results(vhdx_locations))

    except Exception as e:
        self.root.after(0, lambda: self.handle_scan_error(e))
```

## 동시성 제어

### 작업 취소 기능 (선택적)
```python
class WSLRFSGUI:
    def __init__(self):
        self.scan_cancelled = False
        self.current_scan_thread = None

    def start_scan(self):
        """스캔 작업을 시작"""
        self.scan_cancelled = False
        self.scan_button.config(text="취소", command=self.cancel_scan)
        self.current_scan_thread = threading.Thread(target=self.scan_worker, daemon=True)
        self.current_scan_thread.start()

    def cancel_scan(self):
        """스캔 작업 취소"""
        self.scan_cancelled = True
        self.status_var.set("취소 중...")
        self.scan_button.config(state=tk.DISABLED)

    def scan_worker(self):
        """백그라운드에서 스캔 작업 수행"""
        try:
            # 주기적으로 취소 확인
            if self.scan_cancelled:
                self.root.after(0, lambda: self.status_var.set("취소됨"))
                return

            locations = self.manager.scan_distributions()

            if self.scan_cancelled:
                self.root.after(0, lambda: self.status_var.set("취소됨"))
                return

            self.root.after(0, lambda: self.display_results(locations))

        except Exception as e:
            if not self.scan_cancelled:
                self.root.after(0, lambda: self.handle_scan_error(e))
        finally:
            # 버튼 상태 복원
            def restore_button():
                self.scan_button.config(text="WSL 배포판 스캔", command=self.start_scan)
                if not self.scan_cancelled:
                    self.scan_button.config(state=tk.NORMAL)
                    self.refresh_button.config(state=tk.NORMAL)

            self.root.after(0, restore_button)
```

## 타이머와 반복 작업

### 정기적 업데이트 예시
```python
class WSLRFSGUI:
    def __init__(self):
        self.auto_refresh_timer = None

    def start_auto_refresh(self):
        """자동 새로고침 시작"""
        self.check_for_updates()
        # 30초마다 자동 새로고침
        self.auto_refresh_timer = self.root.after(30000, self.start_auto_refresh)

    def stop_auto_refresh(self):
        """자동 새로고침 중지"""
        if self.auto_refresh_timer:
            self.root.after_cancel(self.auto_refresh_timer)
            self.auto_refresh_timer = None

    def check_for_updates(self):
        """업데이트 확인"""
        # 실제 업데이트 확인 로직
        pass
```

## 스레드 간 통신 패턴

### 작업 완료 콜백
```python
def scan_worker_with_callback(self, callback=None):
    """콜백을 지원하는 스캔 작업"""
    try:
        locations = self.manager.scan_distributions()

        def complete_scan():
            if callback:
                callback(locations)
            else:
                self.display_results(locations)

        self.root.after(0, complete_scan)

    except Exception as e:
        def handle_error():
            if callback:
                callback(None, e)
            else:
                self.handle_scan_error(e)

        self.root.after(0, handle_error)

# 사용 예시
def start_scan_with_progress(self):
    """진행률이 포함된 스캔 시작"""
    def progress_callback(current, total):
        progress = (current / total) * 100
        self.root.after(0, lambda: self.progress_var.set(progress))

    def completion_callback(result, error=None):
        if error:
            self.root.after(0, lambda: self.handle_scan_error(error))
        else:
            self.root.after(0, lambda: self.display_results(result))

    scan_thread = threading.Thread(
        target=self.scan_worker_with_progress,
        args=(progress_callback, completion_callback),
        daemon=True
    )
    scan_thread.start()
```

## 비동기 작업의 설계 원칙

### 1. 작업 분리
- UI 업데이트와 실제 작업을 명확히 분리
- 백그라운드 작업은 데이터를 준비만 하고 UI 업데이트는 메인 스레드에서

### 2. 오류 처리
- 백그라운드 작업과 UI 업데이트 모두에서 적절한 예외 처리
- 사용자가 작업 상태를 항상 파악할 수 있도록 함

### 3. 사용자 피드백
- 진행률 표시로 작업 상태를 시각적으로 제공
- 취소 기능으로 사용자 제어권 보장

### 4. 자원 관리
- 불필요한 스레드 생성 방지
- 타이머와 같은 자원은 적절히 정리

이러한 스레딩 기법을 통해 응답성이 뛰어난 Tkinter 애플리케이션을 만들 수 있습니다.