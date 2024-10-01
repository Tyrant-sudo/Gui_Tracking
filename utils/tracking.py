import numpy as np
import mmcv
import tempfile
import mmengine
from mmtrack.apis import inference_sot, init_model
from mmtrack.utils import register_all_modules
from itertools import islice
from configparser import ConfigParser
# cfg = SafeConfigParser()
# cfg.read(config_path)
# # self.auto = cfg.getfloat('case','auto')

def tracking_all(modelconfig_path, model_path, video_path, target_fps, group_batten):
    num_batten = len(group_batten)

    register_all_modules(init_default_scope=True)
    sot_model  = init_model(modelconfig_path, model_path, device='cpu')

    imgs           = mmcv.VideoReader(video_path)
    original_fps   = imgs.fps
    frame_interval = int(original_fps / target_fps)

    circle_coord_list = {}

    for  ID in range(num_batten):

        circle_coord_list[ID] = {}
        circle_coord_list[ID]['bbox'] = []
        circle_coord_list[ID]['trace'] = []
        
        prog_bar = mmengine.ProgressBar(len(imgs))
        cur_circle_coord = tracking_onebatten(frame_interval, sot_model, prog_bar, circle_coord_list[ID], imgs, group_batten[ID])
        circle_coord_list[ID] = cur_circle_coord
    
    return circle_coord_list

def tracking_onebatten(interval,sot_model, prog_bar, imgs, cur_circle_coord, Cor_CurBatten):
    
    # for index, value in islice(enumerate(data), 0, None, interval):
    for i, img in islice(enumerate(imgs), 0, None, interval):

        result_bbox, cur_circle_coord_np, prog_bar = tracking_oneframe(i,sot_model, prog_bar, img, cur_circle_coord, Cor_CurBatten)

        # Save track point coordinates
        cur_circle_coord['bbox'].append(result_bbox)
        cur_circle_coord['trace'].append(cur_circle_coord_np)   
        prog_bar.update()
    
    return cur_circle_coord

def tracking_oneframe(frame_id, sot_model, prog_bar, img, Cor_CurBatten):
    
    result = inference_sot(sot_model, img, Cor_CurBatten, frame_id=frame_id)
    result_bbox = result._pred_track_instances.bboxes.cpu().numpy().astype('uint32')
    result_bbox = result_bbox.reshape(-1)


    
    # Get the coordinates of the center point of the rectangle
    circle_x = int((result_bbox[0] + result_bbox[2]) / 2)
    circle_y = int((result_bbox[1] + result_bbox[3]) / 2)
    
    return result_bbox, np.array([circle_x, circle_y]), prog_bar

if __name__ == "__main__":
    
    config_path = "config.ini"
    cfg = ConfigParser()
    cfg.read(config_path)
    modelconfig_path, model_path, video_path, output_path, image_path, target_fps = \
    cfg.get("Path","modelconfig_path"),\
    cfg.get("Path","model_path"),\
    cfg.get("Path","video_path"),\
    cfg.get("Path","output_path"),\
    cfg.get("Path","image_path"),\
    cfg.getint("Case","target_fps")

    register_all_modules(init_default_scope=True) 
    sot_model = init_model(modelconfig_path, model_path, device='cpu')

      
    # tracking_area = np.array([[577, 1411, 666, 1494], [895, 1350, 975, 1446]])
    # result_bbox, =  tracking_oneframe()
    # self.auto = cfg.getfloat('case','auto')