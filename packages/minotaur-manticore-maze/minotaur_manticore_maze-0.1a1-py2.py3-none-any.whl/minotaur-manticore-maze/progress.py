from tqdm import tqdm
import time


class Progress():

    def bar(self, secs, prefix):
        self.secs = secs
        self.prefix = prefix
        with tqdm(total=100,
                  ncols=75,
                  bar_format='{l_bar}{bar}|',
                  desc=prefix) as pbar:
            for i in range(100):
                pbar.update(1)
                time.sleep(secs)
