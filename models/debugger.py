import os
import subprocess
import sys


class _EnhancedSeleniumDebugger:
    QUIT_CODE = 2

    def run(self, path: str):
        """
        debugger.run(__file__)
        """

        if os.environ.get("ES_DEBUG") == "1":
            return

        os.environ["ES_DEBUG"] = "1"
        while True:
            process = subprocess.Popen(
                [sys.executable, path],
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            process.wait()

            if process.returncode != 0:
                print("The ES Debugger has terminated.")
                sys.exit(0)

    def breakpoint(self):
        user_input = input(
            "ES Debugger: Breakpoint reached. [C]ontinue / [R]etry / [Q]uit: "
        )
        while user_input.lower() not in ["c", "r", "q"]:
            user_input = input()
        user_input = user_input.lower()
        if user_input == "c":
            return
        elif user_input == "r":
            sys.exit(0)
        elif user_input == "q":
            sys.exit(self.QUIT_CODE)

    def close(self):
        user_input = input("ES Debugger: End of the script. [R]etry / [Q]uit: ")
        while user_input.lower() not in ["r", "q"]:
            user_input = input()
        user_input = user_input.lower()
        if user_input == "r":
            sys.exit(0)
        elif user_input == "q":
            sys.exit(self.QUIT_CODE)


debugger = _EnhancedSeleniumDebugger()
