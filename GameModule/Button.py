import pygame as pg

class Button:
    def __init__(self, image:pg.Surface = None, pos:tuple = (0, 0), scale:float = 1.0, content:str = None, ret:str = None):
        self.ret = ret
        self.scale = scale
        self.image = pg.transform.scale_by(image, scale)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        
        if content != None:
            img_size = self.image.get_size()
            font = pg.font.Font("resource/Fonts/XiaolaiMonoSC-Regular.ttf", 100)
            text = font.render(content, True, "black")
            text_size = text.get_size()

            text = pg.transform.scale_by(text, img_size[0]*0.65/text_size[0])
            text_size = text.get_size()
            if text_size[1] > img_size[1]*0.65:
                text = pg.transform.scale_by(text, img_size[1]*0.65/text_size[1])
                
            
            text_rect = text.get_rect()
            text_rect.center = (img_size[0]//2, img_size[1]//2)
            self.image.blit(text, text_rect.topleft)
            
    def move_to(self, pos:tuple, ref:str = "tl"):
        if ref == "tl": self.rect.topleft = pos
        elif ref == "c": self.rect.center = pos
        
    def draw(self, screen:pg.Surface):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            temp = pg.transform.scale_by(self.image, 1.1)
            t_rect = temp.get_rect()
            t_rect.center = self.rect.center
            screen.blit(temp, t_rect.topleft)
        else:
            screen.blit(self.image, self.rect.topleft)
            
    def click_test(self, events:list):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN:
                    return event
        return False