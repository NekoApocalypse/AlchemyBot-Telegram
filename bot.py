import requests
import json
import time

# file that contains bot token and master_id
TOKEN_FILE = './private/bot_token.json'
# file that contains command phrase and response information
CONVERSATION_FILE = './private/conversation.json'


class TelegramBot(object):
    def __init__(self, token_file, conversation_file, proxies=None):
        with open(token_file) as f:
            info = json.load(f)
            self.token = info['token']
            self.master_id = info['master_id']
        with open(conversation_file) as f:
            self.command_dict = json.load(f)
        self.url = 'https://api.telegram.org/bot{}/'.format(self.token)
        self.timeout = 3
        self.connect_timeout = 3
        self.read_timeout = 40
        self.last_id = 0
        if proxies is None:
            self.proxies = {'http': 'socks5://localhost:1080',
                            'https': 'socks5h://localhost:1080'}
        else:
            self.proxies = proxies
        self.hello_message = 'Alchemy bot V0.1, at your service!'
        self.init_script()
        # self.event_loop()

    def init_script(self):
        content = self.get_update({'timeout': '5'})
        result = json.loads(content)['result']
        if len(result) > 0:
            self.last_id = result[-1]['update_id']
        else:
            self.last_id = 0
        print('id of last message:', self.last_id, '\n')
        print('Bot started.\n')
        self.send_msg(self.hello_message, self.master_id)

    def get_update(self, params=None):
        url = self.url + 'getUpdates'
        r = requests.get(
            url=url,
            proxies=self.proxies,
            timeout=(self.connect_timeout, self.read_timeout),
            params=params
        )
        return r.content.decode('utf-8')

    def send_msg(self, text, chat_id):
        url = self.url + 'sendMessage'
        payload = {'text': text, 'chat_id': chat_id}
        requests.get(
            url, proxies=self.proxies, timeout=self.timeout, params=payload)

    def start_event_loop(self):
        def event_handler(text, chat_id):
            if text not in self.command_dict:
                text = 'unk'
            event_type = self.command_dict[text][0]
            event_param = self.command_dict[text][1]
            if event_type == 'msg':
                self.send_msg(event_param, chat_id)

        get_params = {
            'timeout': '30',
            'offset': str(self.last_id + 1)
        }

        while True:
            try:
                content = self.get_update(params=get_params)
            except Exception as e:
                print(e)
                exit(1)
            result = json.loads(content)['result']
            if len(result) > 0:
                self.last_id = result[-1]['update_id']
                get_params['offset'] = str(self.last_id + 1)
            for msg in result:
                text = msg['message']['text']
                chat_id = msg['message']['chat']['id']
                event_handler(text, chat_id)


def main():
    new_bot = TelegramBot(TOKEN_FILE, CONVERSATION_FILE)
    new_bot.start_event_loop()


if __name__ == '__main__':
    main()
