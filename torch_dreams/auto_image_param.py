import torch.nn as nn
import torch
import numpy as np

from .utils import init_image_param, image_buf_to_rgb
import torchvision.transforms as transforms

class BaseImageParam():
    def __init__(self):
        self.height = None
        self.width = None
        self.param = None
        self.optimizer = None
        
    def fetch_optimizer(self, params_list, optimizer = None, lr = 1e-3, weight_decay = 0.):
        if optimizer is not None:
            optimizer = optimizer(params_list, lr = lr, weight_decay = weight_decay)
        else:
            optimizer = torch.optim.AdamW(params_list, lr=lr, weight_decay=weight_decay)
        return optimizer

    def get_optimizer(self, lr, weight_decay):

        self.optimizer = self.fetch_optimizer(
                                    params_list = [self.param],
                                    lr = lr,
                                    weight_decay= weight_decay
                                    )
    
    def clip_grads(self, grad_clip = 1.):
        torch.nn.utils.clip_grad_norm_(self.param,grad_clip)

    def to_hwc_tensor(self, device = 'cpu'):
        rgb = image_buf_to_rgb(h = self.height, w = self.width, img_buf = self.param , device= device).permute(1,2,0).to(device = device, dtype = torch.float32)
        return rgb

    def to_chw_tensor(self, device = 'cpu'):
        t = image_buf_to_rgb(h = self.height, w = self.width, img_buf = self.param , device= device)
        return t

    def __array__(self):
        return self.to_hwc_tensor().numpy()

    def save(self, filename):
        """Save an image_param as an image. Uses PIL to save the image

        usage:
            
            image_param.save(filename = 'my_image.jpg')
            

        Args:
            filename (str): image.jpg
        """
        ten = self.to_chw_tensor()
        im = transforms.ToPILImage()(ten)
        im.save(filename)


class auto_image_param(BaseImageParam):
    def __init__(self, height, width, device, standard_deviation):
        super().__init__()
        self.height = height
        self.width = width
        self.param = init_image_param(height = height, width = width, sd = standard_deviation, device = device)
        self.param.requires_grad_()
        self.optimizer = None

    