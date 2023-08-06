import numpy as np

def normalize_hist(img,process=True):
    # histogram normalization
    assert img.dtype in ['float64' , 'float32']
    if process:
        img_m = np.mean(img,axis=-1)
        img_ms = np.sort(img_m.flatten())
        n_pxs = len(img_ms)
        lb = img_ms[int(np.ceil(n_pxs*0.05))]
        ub = img_ms[int(np.floor(n_pxs*0.95))]
        img_p = (img-lb)/(ub-lb) * 150/255.
        img_p = np.clip(img_p,0,1)
    else:
        raise RuntimeError
    # img_p = img_p.astype('uint8')

    return img_p
def gray_world(img):
    for i in range(img.shape[-1]):
        img[...,i] = img[...,i]/np.mean(img[...,i])*0.5

        img = np.clip(img,0,1)
    return img
def illumination_norm(img):
    return (img-img.min())/(img.max()-img.min())
    # return np.clip(img/img.mean(),0,1)

