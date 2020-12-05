import cv2 
import tqdm
import torch
import numpy as np
from tqdm import tqdm 

from .utils import load_image
from .utils import preprocess_numpy_img
from .utils import pytorch_input_adapter
from .utils import pytorch_output_adapter
from .utils import post_process_numpy_image

from .constants import default_config
from .dreamer_utils import default_func_norm
from .dreamer_utils import make_octave_sizes

from .octave_utils import dream_on_octave_with_masks
from .octave_utils import dream_on_octave

from .image_transforms import transform_to_tensor


class dreamer():

    """
    Main class definition for torch-dreams:

    model = Any PyTorch deep-learning model
    preprocess_func = Set of torch transforms required for the model wrapped into a function. See torch_dreams.utils for examples
    deprocess_func <optional> = set of reverse transforms, to be applied before converting the image back to numpy
    device = checks for a GPU, uses the GPU for tensor operations if available
    """

    def __init__(self, model):
        self.model = model
        self.model = self.model.eval()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(self.device) ## model moves to GPU if available
        self.config = default_config.copy()  # possible fix to: https://github.com/Mayukhdeb/torch-dreams/issues/9

        self.default_func = default_func_norm
        self.dream_on_octave = dream_on_octave
        self.dream_on_octave_with_masks = dream_on_octave_with_masks


        print("dreamer init on: ", self.device)


    def deep_dream(self, config):


        for key in list(config.keys()):
            self.config[key] = config[key]

        image_path = self.config["image_path"]
        layers =  self.config["layers"]
        octave_scale = self.config["octave_scale"]
        num_octaves = self.config["num_octaves"]
        iterations = self.config["iterations"]
        lr = self.config["lr"]
        custom_func = self.config["custom_func"]
        max_rotation = self.config["max_rotation"]
        grayscale = self.config["grayscale"]
        gradient_smoothing_coeff = self.config["gradient_smoothing_coeff"]
        gradient_smoothing_kernel_size = self.config["gradient_smoothing_kernel_size"]

        octave_count = 0

        original_image = load_image(image_path, grayscale=grayscale)
        image_np = preprocess_numpy_img(original_image, grayscale=grayscale)
        if grayscale is True:
            image_np = np.expand_dims(image_np, axis = -1)

        original_size = image_np.shape[:-1]

        octave_sizes = make_octave_sizes(original_size = original_size, num_octaves = num_octaves, octave_scale = octave_scale)

        for new_size in tqdm(octave_sizes):

            image_np = cv2.resize(image_np, new_size)
            if grayscale is True:
                image_np = np.expand_dims(image_np, axis = -1)

            image_np = self.dream_on_octave(model = self.model, image_np  = image_np, layers = layers, iterations = iterations, lr = lr, custom_func = custom_func, max_rotation= max_rotation, gradient_smoothing_coeff= gradient_smoothing_coeff, gradient_smoothing_kernel_size=gradient_smoothing_kernel_size, grayscale=grayscale, default_func= self.default_func, device = self.device)
            
            octave_count += 1
        image_np = post_process_numpy_image(image_np)
        return image_np

    def deep_dream_with_masks(self, config):


        for key in list(config.keys()):
                    self.config[key] = config[key]

        image_path = self.config["image_path"]
        layers =  self.config["layers"]
        octave_scale = self.config["octave_scale"]
        num_octaves = self.config["num_octaves"]
        iterations = self.config["iterations"]
        lr = self.config["lr"]
        custom_funcs = self.config["custom_func"]
        max_rotation = self.config["max_rotation"]
        grayscale = self.config["grayscale"]
        gradient_smoothing_coeff = self.config["gradient_smoothing_coeff"]
        gradient_smoothing_kernel_size = self.config["gradient_smoothing_kernel_size"]
        grad_mask = self.config["grad_mask"]



        original_image = load_image(image_path, grayscale=grayscale)
        image_np = preprocess_numpy_img(original_image, grayscale=grayscale)

        if grayscale is True:
            image_np = np.expand_dims(image_np, axis = -1)

        original_size = image_np.shape[:-1]

        octave_sizes = make_octave_sizes(original_size = original_size, num_octaves = num_octaves, octave_scale = octave_scale)

        for new_size in tqdm(octave_sizes):

            image_np = cv2.resize(image_np, new_size)
            if grayscale is True:
                image_np = np.expand_dims(image_np, axis = -1)
            
            if grad_mask is not None:
                grad_mask = [cv2.resize(g, new_size) for g in grad_mask]
            image_np = self.dream_on_octave_with_masks(model = self.model, image_np  = image_np, layers = layers, iterations = iterations, lr = lr, custom_funcs = custom_funcs, max_rotation= max_rotation, gradient_smoothing_coeff= gradient_smoothing_coeff, gradient_smoothing_kernel_size=gradient_smoothing_kernel_size, grad_mask= grad_mask, grayscale=grayscale, device = self.device, default_func= self.default_func )
        image_np = post_process_numpy_image(image_np)
        return image_np