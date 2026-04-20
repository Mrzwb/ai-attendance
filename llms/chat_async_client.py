import threading
from typing import Union, final

from PySide6 import QtCore
from PySide6.QtGui import QTextCursor, Qt
from PySide6.QtWidgets import QTextBrowser, QApplication

from data import date_now
from llms.chat_client import BaseClient


def invoke_model(sentences: Union[str|list], text_browser: QTextBrowser, client: BaseClient) -> None:

    try:
        stream = client.response_with_stream(sentences)
        for s in stream:
            text = s.choices[0].delta.content
            point_size = text_browser.font().pointSize()
            if text == '<think>':
                text = "深度思考\U0001f30d:"
                text_browser.setTextColor(Qt.GlobalColor.darkGray)
                text_browser.setFontPointSize(point_size - 1)
            if text == '</think>':
                text = ""
                text_browser.setTextColor(Qt.GlobalColor.black)
                text_browser.setFontPointSize(point_size)
            text_browser.insertPlainText(text)
            text_browser.moveCursor(QTextCursor.MoveOperation.End)
            QApplication.processEvents(QtCore.QEventLoop.ProcessEventsFlag.AllEvents)
    except Exception as e:
        print(e)


def strat_chat_thread(*args) -> threading.Thread:
    thread = threading.Thread(target=invoke_model, args=args, name= date_now('%H%M%S.%f')[:-3])
    return thread

__all__ = ["strat_chat_thread"]
