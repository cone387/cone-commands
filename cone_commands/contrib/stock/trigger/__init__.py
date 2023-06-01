from cone_commands.contrib.stock.base import Trigger, BaseTrigger


class TargetPriceTrigger(BaseTrigger):
    name = 'up-to'
    description = 'target price trigger'

    def triggerable(self, current, histories) -> bool:
        return current.close >= self.receiver
