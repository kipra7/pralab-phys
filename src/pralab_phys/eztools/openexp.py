import tkinter as tk
from tkinter import filedialog

from typing import Union
import time


def openpath(multichoice:bool = False) -> Union[str, tuple[str, ...]]:
    """It returns path(s) of (a) file(s) that you select on filedialog.

    Args:
        multichoice (bool, optional): Selecting multiple files. Defaults to False.

    Returns:
        Union[str, tuple[str, ...]]: file path(s)
    """
    root = tk.Tk()
    root.withdraw()
    # ファイルダイアログを開いてファイルを選択
    root.lift() # ウィンドウを最前面に表示する
    root.attributes('-topmost', True) # ウィンドウを常に最前面に表示する
    path = filedialog.askopenfilename(parent=root, multiple=multichoice)
    # ルートウィンドウを閉じる
    root.attributes('-topmost', False) # 最前面表示を解除
    root.destroy()
    return path


def opendir() -> str:
    """It returns a directory path that you select on filedialog.

    Returns:
        str: a directory path
    """
    root = tk.Tk()
    root.withdraw()
    # ディレクトリ選択ダイアログを開く
    root.lift()  # ウィンドウを最前面に表示する
    root.attributes('-topmost', True)  # ウィンドウを常に最前面に表示する
    directory = filedialog.askdirectory(parent=root)
    # ルートウィンドウを閉じる
    root.attributes('-topmost', False)  # 最前面表示を解除
    root.destroy()
    return directory


def opendir_safety() -> str:
    """It returns a directory path that you select on filedialog.

    Returns:
        str: a directory path
    """
    # tk.Tk() インスタンスの作成と管理をすべて削除します。
    # filedialog.askdirectory() が暗黙的にウィンドウを処理します。
    directory = filedialog.askdirectory()
    return directory