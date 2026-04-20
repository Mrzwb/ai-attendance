import abc
import os
import getpass
from abc import ABC

from openai import OpenAI

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

if "ZWB_FREE_API_KEY" not in os.environ:
    os.environ["ZWB_DP_API_KEY"] = getpass.getpass(
        prompt="请输入你的AI密钥: "
    )


def init_model(use_unicom_model: bool = False):
    API_KEY = os.getenv("ZWB_FREE_API_KEY")
    BASE_URL = os.getenv("ZWB_FREE_API_URL")
    if use_unicom_model:
        API_KEY = os.getenv("ZWB_UNICOM_API_KEY")
        BASE_URL = os.getenv("ZWB_UNICOM_API_URL")

    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def generate_prompt(message: str | list[str]) -> list:
    return [
        {"role": "system", "content": """
            你是一名数据分析专家，对于输入的文件进行统计分析、预测分析、趋势分析、表头分析是否符合模版要求，最后给出一次性结论
        """},
        {"role": "assistant", "content": """
            你是一名数据分析助手，提醒用户模版表头格式为：
              1) 考勤报表的模版表头为("日期", "姓名", "所属项目组", "迟到", "早退", "旷工", "申诉", "备注")
              2) 财务报表的模版标图为("日期", "所属项目组", "报账单量", "退单量", "退单率", "审计", "备注")
        """},
        {"role": "user", "content": message}
    ]


class BaseClient(ABC):

    def __init__(self, use_unicom_model: bool = False):
        self.client = init_model(use_unicom_model)

    @abc.abstractmethod
    def response_with_raw(self, message: str | list[str]):
        pass

    @abc.abstractmethod
    def response_with_stream(self, message: str | list[str]):
        pass

    def close(self):
        try:
            self.client.close()
        except Exception as e:
            pass

    def is_closed(self):
        return self.client.is_closed()


class FreeClient(BaseClient):

    def __init__(self):
        super().__init__()
        self.__model = "free:Qwen3-30B-A3B"

    def response_with_raw(self, message: str | list[str]):
        if self.is_closed():
            self.__init__()
        response = self.client.chat.completions.create(
            model = self.__model,
            messages = generate_prompt(message),
        )
        return response.choices[0].message.content

    def response_with_stream(self, message: str | list[str]):
        if self.is_closed():
            self.__init__()
        response = self.client.chat.completions.create(
            model = self.__model,
            messages = generate_prompt(message),
            stream=True,
        )
        return response


class InnerClient(BaseClient):

    def __init__(self):
        super().__init__(True)

    def response_with_raw(self, message: str | list[str]):
        pass

    def response_with_stream(self, message: str | list[str]):
        pass


__all__ = ["FreeClient", "InnerClient", "BaseClient"]
