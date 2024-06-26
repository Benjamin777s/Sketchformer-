import os
import time
import json
import utils
from utils.util import mkdir
try:
    from tensorboardX import SummaryWriter
except ImportError as error:
    print('tensorboard X not installed, visualizing wont be available')
    SummaryWriter = None

class Writer:
    def __init__(self, opt):
        #self.name = opt.class_name
        self.opt = opt
        self.save_dir = os.path.join(opt.checkpoints_dir, opt.dataset, opt.timestamp)
        self.log_name = os.path.join(self.save_dir, 'loss_log.txt')
        self.testacc_log = os.path.join(self.save_dir, 'testacc_log.txt')
        #self.train_record_json = os.path.join(opt.checkpoints_dir, opt.dataset, 'record.ndjson')
        self.latest_macro_f = 0
        self.latest_micro = 0
        self.start_logs()

        if opt.is_train  and SummaryWriter is not None:
            self.display = SummaryWriter(logdir=os.path.join("runs", opt.dataset, opt.timestamp))
        else:
            self.display = None 
 
    def start_logs(self):
        """ 
        creates test / train log files 
        """
        mkdir(self.save_dir)
        if self.opt.is_train:
            with open(self.log_name, "a") as log_file:
                now = time.strftime("%c")
                log_file.write('================ Training (%s) ================\n' % now)
        else:
            with open(self.testacc_log, "a") as log_file:
                now = time.strftime("%c")
                log_file.write('================ Testing  (%s) ================\n' % now)

    def print_train_loss(self, epoch, i, loss):
        """ 
        prints train loss to terminal / file 
        """
        message = '(time: %s, epoch: %d, iters: %d) loss: %.3f ' \
                  % (time.strftime("%X %x"), epoch, i, loss.item())
        print(message)

        with open(self.log_name, "a") as log_file:
            log_file.write('%s\n' % message)

    def plot_train_loss(self, loss, iters):
        # iters = i + epoch * n
        if self.display:
            self.display.add_scalar('data/train_loss', loss, iters)

    def print_test_loss(self, epoch, i, loss):
        """ 
        prints test loss to terminal / file 
        """
        epoch = 0 if not epoch else epoch
        message = 'test (time: %s, epoch: %d, iters: %d) loss: %.3f ' \
                  % (time.strftime("%X %x"), epoch, i, loss.item())
        print(message)
        with open(self.log_name, "a") as log_file:
            log_file.write('%s\n' % message)


    def plot_test_loss(self, loss, epoch):
        if self.display:
            self.display.add_scalar('data/test_loss', loss, epoch)

    def plot_model_wts(self, model, epoch):
        if self.opt.is_train and self.display:
            for name, param in model.net.named_parameters():
                self.display.add_histogram(name, param.clone().cpu().data.numpy(), epoch)

    

    def close(self):
        if self.display is not None:
            self.display.close()
