
from basicsr.models import create_model
from basicsr.utils import img2tensor as _img2tensor, tensor2img, imwrite
from basicsr.utils.options import parse
import numpy as np
import cv2


HD = (1280, 720)




def imread(img_path):
  img = cv2.imread(img_path)
  img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  return img


def img2tensor(img, bgr2rgb=False, float32=True):
    img = img.astype(np.float32) / 255.
    return _img2tensor(img, bgr2rgb=bgr2rgb, float32=float32)

def split_into_blocks(img):
    """ Takes an image as input splits it into 4 blocks and returns these blocks"""
    h, w = img.shape[:2]

    block_1 = img[0:h//2, 0:w//2]
    block_2 = img[0:h//2, w//2:w]
    block_3 = img[h//2:h, 0:w//2]
    block_4 = img[h//2:h, w//2:w]

    return (block_1, block_2, block_3, block_4)


def glue_blocks(blocks, img):

    my_image = np.zeros_like(img)
    h, w = my_image.shape[:2]

    my_image[0:h//2, 0:w//2] = blocks[0]
    my_image[0:h//2, w//2:w] = blocks[1]
    my_image[h//2:h, 0:w//2] = blocks[2]
    my_image[h//2:h, w//2:w] = blocks[3]

    return my_image




def single_image_inference(model, img, save_path, save):
    model.feed_data(data={'lq': img.unsqueeze(dim=0)})

    if model.opt['val'].get('grids', False):
        model.grids()

    model.test()

    if model.opt['val'].get('grids', False):
        model.grids_inverse()

    visuals = model.get_current_visuals()
    sr_img = tensor2img([visuals['result']])
    if(save):
        imwrite(sr_img, save_path)
    else:
        return sr_img


def main(input, output, action):

    # create the model
    if action == "denoise":
        opt_path = 'options/test/SIDD/NAFNet-width64.yml'
    elif action == "deblur":
        opt_path = 'options/test/REDS/NAFNet-width64.yml'
    
    opt = parse(opt_path, is_train=False)
    opt['dist'] = False
    NAFNet = create_model(opt)

    # treatment
    img_input = imread(input)

    # croping into 4 blocks
    if(img_input.shape[:2] > HD):

        # image is too big crop into 4 blocks
        # ask user for opinion 
        blocks = split_into_blocks(img_input)
        blocks_deblurred = []
        for i in range(4):
            inp = img2tensor(blocks[i])
            blocks_deblurred.append(single_image_inference(NAFNet, inp, output, False))
        
        blocks_deblurred = tuple(blocks_deblurred)
        my_image = glue_blocks(blocks_deblurred, img_input)

        imwrite(my_image, output)

    else:
        # normal treatement
        inp = img2tensor(img_input)
        single_image_inference(NAFNet, inp, output, True)






if __name__ == "__main__":
    main()
