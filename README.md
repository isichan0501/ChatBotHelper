* 雑談用の自動応答関数を作成

1. ユーザー毎にチャットルームがあるので識別情報として
uid = sitename + '_' + 自分のuserid + 相手のuserid
conv_id = chatbot.conversation_id
parent_id = chatbot.message_id
をjsonを保存しておく。

2. 会話のタイトルでユーザーを特定できるように変更
chatbot.change_title(convo_id: str, title: str)

3. conversationのjson構造
conversation_ids = chatbot.get_conversations()

#msg履歴,['title', 'create_time', 'mapping', 'moderation_results', 'current_node']

4. messageのjson構造
"""msg_his = chatbot.get_msg_history(convo_id=conversation_ids[0]['id'], encoding='utf-8')
msg_his['mapping'].keys() に msg_idのリスト.
msg_his['mapping'][msg_id].keys() = ['id', 'message', 'parent', 'children']
msg_his['mapping'][msg_id]['message'].keys() = ['id', 'author', 'create_time', 'content', 'end_turn', 'weight', 'metadata', 'recipient']
msg_his['mapping'][msg_id]['message']['content'].keys() = ['content_type', 'parts']
msg_his['mapping'][msg_id]['message']['content']['parts']は \n1 ,,, \n2 など \n{数字}で改行されている。
"""

5. uidを渡すと個別チャットを取得して、チャット毎に毎回conv_idとpar_idをsave

6. マッチング用のプロンプト取得
自分プロフと相手のプロフからユーザー情報を取得してget_promptに渡す