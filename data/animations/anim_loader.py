import os, json
import pygame
import sys

pygame.init()

ANIMATION_PATH = "."

def load_img(path, colorkey=None):
    img = pygame.image.load(path).convert()
    if colorkey : img.set_colorkey(colorkey)
    return img

class AnimationData:
    def __init__(self, path, colorkey=None):
        # print(path)
        self.id = path.split("/")[-1]
        self.image_list = []
        if len(path.split("/")[-1].split(".")) == 1 and path != "__pycache__":
            for img in os.listdir(path):
                if img.split(".")[-1] == "png": # Checking if img type is equal to png or not
                    i = [int(img.split(".")[0].split("_")[-1]), load_img(path + "/" + img, colorkey)]
                    self.image_list.append(i)
            try:
                file = open(path + "/config.json", 'r')
                self.config = json.loads(file.read())
                file.close()
            except FileNotFoundError:
                self.config = {
                    "frames" : [5 for i in range(len(self.image_list))],
                    "loop" : True,
                    "speed" : 1.0,
                    "centered" : False,
                    "paused" : False,
                    "outline" : None,
                    "offset" : [0, 0]
                }
                file = open(path + "/config.json", "w")
                file.write(json.dumps(self.config))
                file.close()

            self.image_list.sort()
            self.image_list = [img_data[1] for img_data in self.image_list]
            self.frame_surfs = []
            total = 0
            for i, frame in enumerate(self.config["frames"]):
                total += frame
                self.frame_surfs.append([total, self.image_list[i]])
        

     # it is same as a variable line duration = sum(self.config["frames"]) just it provides getter, setter and deleter functionality
    @property
    def duration(self):
        return sum(self.config["frames"])



class Animation:
    def __init__(self, animation_data):
        self.data = animation_data
        self.frame = 0
        self.paused = self.data.config["paused"]
        self.img = None
        self.calc_img()
        self.rotation = 0
        self.just_looped = False
    
    def render(self, surf, pos, offset = (0, 0)):
        img = self.img
        rot_offset = [0, 0]
        if self.rotation:
            orig_size = self.img.get_size()
            img = pygame.transform.rotate(self.img, self.rotation)
            if not self.data.config["centered"]:
                rot_offset = [(img.get_width() - orig_size[0] // 2, img.get_height() - orig_size[1] // 2)]
        
        if self.data.config["outline"]:
            pass
        if self.data.config["centered"]:
            pos_x = pos[0] - offset[0] - img.get_width() // 2
            pos_y = pos[1] - offset[1] - img.get_height() // 2
            surf.blit(img, (pos_x, pos_y))
        else:
            pos_x = pos[0] - offset[0] + rot_offset[0]
            pos_y = pos[1] - offset[1] + rot_offset[1]
            surf.blit(img, (pos_x, pos_y))


    def calc_img(self):
        for frame in self.data.frame_surfs:
            if frame[0] > self.frame:
                self.img = frame[1]
                break
            if self.data.frame_surfs[-1][0] < self.frame:
                self.img = self.data.frame_surfs[-1][1]
    


    def set_speed(self, speed):
        self.data.config["speed"] = speed
    
    def set_loop(self, value):
        self.data.config["loop"] = value
    
    def set_frame_index(self, idx):
        self.frame = self.data.frame_surfs[idx][0]
    
    def play(self, dt):
        self.just_looped = False
        if not self.paused:
            self.frame += dt * 60 * self.data.config["speed"]
        if self.data.config["loop"]:
            while self.frame > self.data.duration:
                self.frame -= self.data.duration
                self.just_looped = True
        self.calc_img()
  
    
    def rewind(self):
        self.frame = 0
    
    
    def pause(self):
        self.paused = True
    
    def resume(self):
        self.paused = False
    
    def render_animation(self, surf, pos = (0, 0), offset=(0, 0)):
        offset = list(offset)
        surf.blit(self.img, pos)
    
    def render_at_screen_center(self, display, img):
        pos = ((display.get_width() - img.get_width())//2, (display.get_height() - img.get_height())//2)
        display.blit(self.img, pos)

class AnimationManager:
    def __init__(self, anim_folder_path, colorkey = None):
        self.animations = {}
        for anim in os.listdir(anim_folder_path):
            self.animations[anim] = AnimationData(anim_folder_path + '/' + anim, colorkey)
        self.anim = None
    
    def load_animation(self, anim_name):
        self.anim = Animation(self.animations[anim_name])
        return self.anim

