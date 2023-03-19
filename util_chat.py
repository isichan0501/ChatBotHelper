from revChatGPT.V1 import Chatbot
import json
import logging
from typing import Optional
import pandas as pd
from pprint import pprint
import re
#db
from tinydb import TinyDB, where, Query

#---logger--------

def get_logger(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers = []
    
    # ファイルへ出力するハンドラーを定義
    log_file_path = 'revChatGPT_debug.log'
    file_handler = logging.FileHandler(filename=log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)
    return logger


v1_logger = get_logger("revChatGPT.V1")



def parse_log_txt(log_file_path):
    # ログファイルを読み込む
    with open(log_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 各行を辞書型に変換する
    logs = []
    for line in lines:
        record = {}
        #時間表現ではじまるか
        mtc = re.match(r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}", line)
        if not mtc:
            continue

        asctime = mtc.group()
        record['asctime'] = asctime
        line.replace(asctime, 'asctime')
        parts = line.split(' - ')
        record['name'] = parts[1]
        record['levelname'] = parts[2]
        record['funcName'] = parts[3]
        # messageの改行を削除して格納する
        record['message'] = parts[4].replace('\n', '')
        logs.append(record)

    # 辞書型のリストをpandasデータフレームに変換する
    df = pd.DataFrame.from_dict(logs)
    return df


class ChatbotUtil:
    """uid=Noneならconv_idとpar_idもNone
    dbのsaveとloadも無効化
    """
    def __init__(self, uid=None):
        self.uid = uid
        self.usertb = self._get_usertb()
        self.new_msg = ""
        self.chat_dict = self.load_chat_ids(uid=uid)
        
        self.chatbot = self.get_chatbot(conv_id=self.chat_dict['conv_id'], par_id=self.chat_dict['par_id'])
        #新規チャットでuid有りならタイトル作成
        if (uid != None) and (self.chat_dict['conv_id'] == None):
            self._set_chat_title()
            
    def _set_chat_title(self):
        self.chatbot.change_title(convo_id=self._get_conv_id(), title=self.uid)
        

    def get_chatbot(self, conv_id=None, par_id=None, collect_dt=True):
        with open('config.json') as f:
            config = json.loads(f.read())
        chatbot = Chatbot(config=config, conversation_id=conv_id, parent_id=par_id, collect_data=collect_dt)
        return chatbot


    def ask_quetion(self, prompt):
        # print('Welcome to ChatGPT CLI')
        response = ""
        for data in self.chatbot.ask(
                prompt
        ):
            response = data["message"]

        print(response)
        return response
            
    @staticmethod
    def read_txtfile(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = f.read()
            return data


    #会話ループ
    def start_chat(self):
        print('Welcome to ChatGPT CLI')
        while True:
            sentence = input("You (qで終了): ")
            if sentence.endswith('.txt'):
                sentence = ChatbotUtil.read_txtfile(sentence)
            stripped = sentence.strip()
            if not stripped:
                continue
            if stripped.lower() == "q":
                break

            print()
            print("Chatbot: ")
            prev_text = ""
            for data in self.chatbot.ask(stripped):
                message = data["message"][len(prev_text):]
                print(message, end="", flush=True)
                prev_text = data["message"]
            print()


    def ask_chat(self, prompt):
        prev_text = ""
        try:
            for data in self.chatbot.ask(prompt):
                message = data["message"][len(prev_text):]
                print(message, end="", flush=True)
                prev_text = data["message"]
        except Exception as e:
            print('ask_chat error')

        finally:
            self.save_chat_ids(uid=self.uid)
            return prev_text 


    def _get_conv_id(self):
        return self.chatbot.conversation_id

    def _get_par_id(self):
        return self.chatbot.parent_id

    def _get_usertb(self):
        return TinyDB('chat.json').table('user_chat')
    
    def save_chat_ids(self, uid):
        if not uid:
            return None
        user_dict = {'uid': uid, 'conv_id': self._get_conv_id(), 'par_id': self._get_par_id()}
        self.usertb.upsert(user_dict, where('uid') == uid)
        
    # @staticmethod
    def load_chat_ids(self,uid):
        #uid = Noneならリターン
        if not uid:
            {'uid': None, 'conv_id': None, 'par_id': None}
        user_dict_list = self.usertb.search(where('uid') == uid)
        if len(user_dict_list) > 0:
            return user_dict_list[0]
        return {'uid': uid, 'conv_id': None, 'par_id': None}

    
    def gen_prompt_for_tinder(self, my_info="", my_prof="", my_tone="", user_info="", user_prof="", chat_command=""):
        
        prompt = "@前提事項: あなたはマッチングアプリで出会いを求めるユーザーとして振舞ってください。。対話相手があなたに好意を持つような返答を心がけてください。 \n"
        prompt += "#あなたの基本情報 \n" + my_info + "\n"
        prompt += "#あなたのプロフィール \n" + my_prof + "\n"
        prompt += "#あなたの口調の例 \n" + my_tone + "\n"
        prompt += "#あいての基本情報 \n" + user_info + "\n"
        prompt += "#あなたのプロフィール \n" + user_prof + "\n"
        if not chat_command:
            chat_command = "あいてへ最初に送るメッセージを作成してください。また顔文字や絵文字なども適宜使用してください。"
        prompt += "@命令書 \n" + chat_command

        return prompt





if __name__ == "__main__":
    # start_chat()

    userid = 'happymail_193732783'
    cb = ChatbotUtil(uid=userid)
    # cb.start_chat()

    
    prompt = cb.read_txtfile(filepath='prompt.txt')
    res = cb.ask_chat(prompt)
    import pdb;pdb.set_trace()
    cb.chatbot.change_title(convo_id=cb._get_conv_id(), title=cb.uid)
    
    prompt = "４文字熟語を３つ挙げてください"
    res = cb.ask_chat(prompt)
    # res = ask_quetion(prompt)
    # df = parse_log_txt(log_file_path)
    import pdb;pdb.set_trace()
    #会話IDのリスト id, title, create_time
    conversation_ids = cb.chatbot.get_conversations()

    #msg履歴,['title', 'create_time', 'mapping', 'moderation_results', 'current_node']
