from cone_commands.contrib.dingtalk import DingTalkCommand
from cone_commands.contrib.stock.base import Receiver, BaseReceiver


@Receiver.register()
class DingTalkReceiver(BaseReceiver):

    def on_received(self, trigger, current, histories):
        DingTalkCommand().send_msg(current)
