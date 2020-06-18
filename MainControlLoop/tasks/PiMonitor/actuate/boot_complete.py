import os


class BootCompleteActuateTask:

    FILE_PATH = os.path.join(os.environ["HOME"], 'first_boot')

    def __init__(self):
        self.run = False

    def execute(self):
        if not self.run:
            return

        self.run = False
        
        file = open(self.FILE_PATH, "w")
        file.close()
