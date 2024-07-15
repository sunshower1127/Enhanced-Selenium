import os
import subprocess
import sys


class _EnhancedSeleniumDebugger:
    def run(self, path: str):
        """
        debugger.run(__file__)
        """

        if os.environ.get("ES_DEBUG") == "1":
            return

        os.environ["ES_DEBUG"] = "1"
        print("OK")
        while True:
            process = subprocess.Popen(
                [sys.executable, path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                sys.exit(1)

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
            sys.exit(1)

    def close(self):
        user_input = input("ES Debugger: End of the script. [R]etry / [Q]uit: ")
        while user_input.lower() not in ["r", "q"]:
            user_input = input()
        user_input = user_input.lower()
        if user_input == "r":
            sys.exit(0)
        elif user_input == "q":
            sys.exit(1)


debugger = _EnhancedSeleniumDebugger()
