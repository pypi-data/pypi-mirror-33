from pathlib import Path


def get_setting_path() -> Path:
    global_path = Path("/etc/dashbase/")
    user_path = Path("~/.dashbase/").expanduser()
    if global_path.exists():
        return global_path

    if not user_path.exists():
        user_path.mkdir(exist_ok=True)

    return user_path
