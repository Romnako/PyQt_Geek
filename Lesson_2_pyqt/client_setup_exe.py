import sys
from cx_Freeze import setup, Executable
import cx_Freeze
build_exe_options = {
    "packages": ["lib", "logs", "client"],
}
setup(
    name="mini_chat_client",
    version="1.0",
    description="mini_chat_client",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('client.py',
                            base='Win32GUI',
                            targetName='client.exe',
                            )]
)