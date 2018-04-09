import json

command_list = {
    '卖萌': 'be_moe',
    '测试': 'test',
    '开始炼丹': 'start_training'
}


def parse_command(msg):
    if msg in command_list:
        return command_list[msg]
    else:
        return 'unknown'

