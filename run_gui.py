import traceback


def main() -> None:
    from app import pcie_ch7_gui as gui

    gui.run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        # Keep the console window open so the user can see the error
        input("Press Enter to exit...")
