import os
import subprocess
import sys


class _EnhancedSeleniumBuilder:
    def start(self, n=1, *, never_stop=False):
        for _ in range(n):
            pid = os.fork()
            if pid == 0:
                return

        if not never_stop:
            for _ in range(n):
                os.wait()

        else:
            while True:
                os.wait()
                pid = os.fork()
                if pid == 0:
                    return

    def build(self, file_path: str, dist_path="."):
        """
        builder.build(__file__)
        Only working in development environment
        """

        # pyinstaller로 패키징된 실행 파일에서 실행되는지 확인
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            print(
                "This is a packaged executable. The build process will not proceed."
            )
            return

        try:
            # pyinstaller 명령 실행, --distpath 옵션 추가
            subprocess.run(
                [
                    "pyinstaller",
                    "--onefile",
                    "--distpath",
                    dist_path,
                    file_path,
                ],
                check=True,
            )
            print(f"Build completed successfully for {file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}", file=sys.stderr)


builder = _EnhancedSeleniumBuilder()
