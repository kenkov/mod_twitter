#! /usr/bin/env python
# coding:utf-8


from mod import Mod
from textfilter import TwitterPreprocess
import re
from datetime import datetime
import numpy as np


class PrePostProcessing:
    def __init__(self, logger=None):
        Mod.__init__(self, logger)
        self.twpre = TwitterPreprocess()

    def preprocess(self, text) -> str:
        return self.twpre.sub(text)

    def postprocess(self, message, answer, master) -> (float, str, str):
        prob, text, source, info = answer

        if self.is_reply_needed(message, master):
            mod_text = self.convert2reply(message, text)
            info["in_reply_to_status_id"] = message["id"]
        else:
            mod_text = text

        return (prob, mod_text, source, info)

    def convert2reply(self, message, text) -> str:
        # リプライ用に修正する
        return "@{} {}".format(
            message["user"]["screen_name"],
            text
        )

    def is_reply_needed(self, message, master) -> bool:
        """
        リプライする必要があるか判定する
        """
        reply_flag = bool(re.search(
            r'^@{} '.format(master["screen_name"]),
            message["text"]
        ))
        return reply_flag


class ModTwitter(Mod):
    def __init__(self, logger=None):
        Mod.__init__(self, logger)

        self.processing = PrePostProcessing()
        self.basetime = datetime.now()
        self.modules = []

    def add_module(self, module):
        self.modules.append(module)
        self.logger.info("add module to {}: {}".format(self, module))

    def is_fire(self, message, master) -> bool:
        """
        900秒以上ツイートしていないかリプライだったらツイートする
        """
        # flags
        now = datetime.now()
        time_diff = (now - self.basetime).seconds
        time_flag = time_diff > 900

        if time_flag:
            # basetime の更新
            self.basetime = now
            self.logger.debug("time passed")

        return self.processing.is_reply_needed(message, master) or time_flag

    def random_prob(self, answer):
        """
        確率を0.1前後うごかす
        """
        prob, text, source, info = answer
        delta = np.random.dirichlet((18, 2), 1)[0].min()
        return (
            max(0.0, prob - delta),
            text,
            source,
            info
        )

    def reses(self, message, master):
        _message = {
            "id": message["id"],
            "text": self.processing.preprocess(message["text"]),
            "user": {
                "name": message["user"]["name"],
                "screen_name": message["user"]["screen_name"]
            }
        }
        answers = []
        for module in self.modules:
            answers.extend(module.reses(_message, master))

        return [
            self.random_prob(
                self.processing.postprocess(message, answer, master)
            )
            for answer in answers
        ]
