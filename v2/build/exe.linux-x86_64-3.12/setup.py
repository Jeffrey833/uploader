from cx_Freeze import setup, Executable

setup(
    name="d.py",
    version="0.1",
    description="A brief description of d.py",
    executables=[Executable("d.py")],
)