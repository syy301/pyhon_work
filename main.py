import time
import math
import random
import pygame
from pygame.constants import *

pygame.init()

""" 背景图片 """
class Background(pygame.sprite.Sprite):

    def __init__(self, window, x, y, image_path):
        pygame.sprite.Sprite.__init__(self)
        self.window = window
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.window.blit(self.image, self.rect)


""" 被抛出的水果类 """
class ThrowFruit(pygame.sprite.Sprite):

    def __init__(self, window, image_path, speed, turn_angel, flag):
        pygame.sprite.Sprite.__init__(self)

        # 游戏窗口
        self.window = window

        # 导入水果图像并获取其矩形区域
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

        # 水果抛出时x坐标取随机数
        self.rect.x = random.randint(0, Manager.WIDTH - 10)

        # 水果初始y坐标
        self.rect.y = Manager.HEIGHT

        # 抛出时速度
        self.speed = speed

        # 旋转速度
        self.turn_angel = turn_angel

        # 水果抛出时与窗口下水平线的夹角弧度，因为要用到随机函数, 所以取整数， 使用时除以100
        self.throw_angel = 157

        # 水果抛出后所经历的时间, 初始化为0
        self.fruit_t = 0

        # 旋转的总角度
        self.v_angel = 0

        # 水果抛出时的初速度
        self.v0 = 6

        # 水果标记
        self.flag = flag

    def update(self):
        """ 水果运动状态更新 """

        # 在弧度制中，一个完整的圆周对应的角度是360度，对应的弧度是2π（即360度 = 2π弧度）。
        # 因此，可以通过以下公式将角度转换为弧度： 弧度 = 角度 × π / 180
        # 当角度为90度时，根据上述公式，可以计算出对应的弧度为： 90度 × π / 180 = 0.5π = 1.57（约）

        # 如果水果的初始X坐标位于窗口左边区域, 取抛出时弧度在70度至90度之间
        if self.rect.x <= Manager.WIDTH / 2:
            self.throw_angel = random.randint(140, 157)

        # 如果水果的初始X坐标位于窗口右侧区域, 取抛出时弧度在90度至110度之间
        elif self.rect.x >= Manager.WIDTH / 2:
            self.throw_angel = random.randint(157, 175)

        # 水果旋转后的新图像
        new_fruit = pygame.transform.rotate(self.image, self.v_angel)

        self.window.blit(new_fruit, (self.rect.x + self.rect.width / 2 - new_fruit.get_width() / 2,
                                     self.rect.y + self.rect.height / 2 - new_fruit.get_height() / 2))

        # 如果水果落出屏幕，没有被切，经典模式 X 加一，并销毁水果对象
        if self.rect.y >= Manager.HEIGHT + self.rect.height:
            if self.flag != 5:
                Manager.classic_miss += 1
            self.kill()

        # 水果抛出后的运动时水平匀速运动以及竖直向上的变速运动到达最高点时下落, 所以可以判断水果做的是斜上抛运动
        # 可以利用重力加速度来求出每隔一段时间水果运动后的y坐标
        # 公式: v0 * t * sin(α) - g * t^2 / 2
        self.rect.y -= self.v0 * self.fruit_t * math.sin(self.throw_angel / 100) - (Manager.G *
                                                                                    self.fruit_t ** 2 / 10) / 2

        # 计算水果在水平方向的匀速运动位移之后的X坐标
        # 公式: v0 * t * cos(α)
        self.rect.x += self.v0 * self.fruit_t * math.cos(self.throw_angel / 100)

        # 累加经过的时间
        self.fruit_t += 0.1

        # 累加旋转总角度
        self.v_angel += self.turn_angel


""" 水果切片类 """
class HalfFruit(pygame.sprite.Sprite):

    def __init__(self, window, image_path, x, y, turn_angel, v_angel, v0):
        pygame.sprite.Sprite.__init__(self)
        self.window = window
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.turn_angel = turn_angel
        self.fruit_t = 0
        self.v_angel = v_angel
        self.v0 = v0

    def update(self):
        """ 水果运动状态更新 """

        # 水果旋转后的新图像
        new_fruit = pygame.transform.rotate(self.image, self.v_angel)

        # 将旋转后的新图像贴入游戏窗口, 注意, 旋转后的图像尺寸以及像素都不一样了(尺寸变大了), 所以坐标需要进行适当处理
        #                               在原先图片矩形的中心位置绘制
        self.window.blit(new_fruit, (self.rect.x + self.rect.width / 2 - new_fruit.get_width() / 2,
                                     self.rect.y + self.rect.height / 2 - new_fruit.get_height() / 2))

        if self.rect.y >= Manager.HEIGHT:
            self.kill()
        self.rect.y += Manager.G * self.fruit_t ** 2 / 2

        self.rect.x += self.v0 * self.fruit_t

        self.fruit_t += 0.01

        self.v_angel += self.turn_angel


""" 水果刀光类 """
class Knife(object):

    def __init__(self, window):
        self.window = window
        self.apple_flash = pygame.image.load("./images/apple_flash.png")
        self.banana_flash = pygame.image.load("./images/banana_flash.png")
        self.peach_flash = pygame.image.load("./images/peach_flash.png")
        self.watermelon_flash = pygame.image.load("./images/watermelon_flash.png")
        self.strawberry_flash = pygame.image.load("./images/strawberry_flash.png")

    def show_apple_flash(self, x, y):
        self.window.blit(self.apple_flash, (x, y))

    def show_banana_flash(self, x, y):
        self.window.blit(self.banana_flash, (x, y))

    def show_peach_flash(self, x, y):
        self.window.blit(self.peach_flash, (x, y))

    def show_watermelon_flash(self, x, y):
        self.window.blit(self.watermelon_flash, (x, y))

    def show_strawberry_flash(self, x, y):
        self.window.blit(self.strawberry_flash, (x, y))


""" 模式选项类 """
class OptionMode(pygame.sprite.Sprite):

    def __init__(self, window, x, y, image_path, turn_angel, flag):
        pygame.sprite.Sprite.__init__(self)
        self.window = window
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.turn_angel = turn_angel
        self.v_angel = 0
        self.flag = flag

    def update(self):
        new_image = pygame.transform.rotate(self.image, -self.v_angel)
        self.window.blit(new_image, (self.rect.x + self.rect.width / 2 - new_image.get_width() / 2,
                                     self.rect.y + self.rect.height / 2 - new_image.get_height() / 2))
        self.v_angel += self.turn_angel


""" 游戏音乐类 """
class Bgm(object):

    def __init__(self):
        pygame.mixer.init()

    def play_menu(self):
        pygame.mixer.music.load("./sound/menu.mp3")
        pygame.mixer.music.play(-1, 0)

    def play_classic(self):
        pygame.mixer.music.load("./sound/start.mp3")
        pygame.mixer.music.play(1, 0)

    def play_throw(self):
        pygame.mixer.music.load("./sound/throw.mp3")
        pygame.mixer.music.play(1, 0)

    def play_splatter(self):
        pygame.mixer.music.load("./sound/splatter.mp3")
        pygame.mixer.music.play(1, 0)

    def play_over(self):
        pygame.mixer.music.load("./sound/over.mp3")
        pygame.mixer.music.play(1, 0)

    def play_boom(self):
        pygame.mixer.music.load("./sound/boom.mp3")
        pygame.mixer.music.play(1, 0)


""" 游戏逻辑类 """
class Manager(object):
    # 窗口尺寸
    WIDTH = 640
    HEIGHT = 480

    # 游戏中的定时器常量
    THROWFRUITTIME = pygame.USEREVENT
    pygame.time.set_timer(THROWFRUITTIME, 3000)

    # 根据窗口大小，选取随机整数重力加速度, 水果下落更有层次感，使用时除以10
    G = random.randint(19, 21)

    # 经典模式miss掉的水果数
    classic_miss = 0

    # 打开文本文件
    with open('best.txt', 'r') as file:
        # 逐行读取文件内容
        for line in file:
            if 'zen_mode' in line:
                zen_best = int(line.split(':')[-1].strip())
            if 'classic_mode' in line:
                classic_best = int(line.split(':')[-1].strip())

    def __init__(self):
        # 生成游戏窗口
        self.window = pygame.display.set_mode((Manager.WIDTH, Manager.HEIGHT))
        self.window_icon = pygame.image.load("./images/score.png")
        pygame.display.set_icon(self.window_icon)
        pygame.display.set_caption("FruitNinja")

        # 创建游戏中用到的的精灵组
        self.background_list = pygame.sprite.Group()
        self.circle_option = pygame.sprite.Group()
        self.option_fruit_list = pygame.sprite.Group()
        self.fruit_half_list = pygame.sprite.Group()
        self.throw_fruit_list = pygame.sprite.Group()

        # 导入背景图像并添加入背景精灵组
        self.background = Background(self.window, 0, 0, "./images/background.jpg")
        self.home_mask = Background(self.window, 0, 0, "./images/home-mask.png")
        self.logo = Background(self.window, 20, 10, "./images/logo.png")
        self.ninja = Background(self.window, Manager.WIDTH - 320, 45, "./images/ninja.png")
        self.home_desc = Background(self.window, 20, 135, "./images/home-desc.png")
        self.zen_new = Background(self.window, 175, 215, "./images/new.png")

        self.background_list.add(self.background)
        self.background_list.add(self.home_mask)
        self.background_list.add(self.logo)
        self.background_list.add(self.ninja)
        self.background_list.add(self.home_desc)
        self.background_list.add(self.zen_new)

        # 创建旋转的圈并添加进精灵组
        self.dojo = OptionMode(self.window, Manager.WIDTH - 600, Manager.HEIGHT - 250,
                               "./images/dojo.png", 1, None)
        self.new_game = OptionMode(self.window, Manager.WIDTH - 405, Manager.HEIGHT - 250,
                                   "./images/new-game.png", 1, None)
        self.game_quit = OptionMode(self.window, Manager.WIDTH - 160, Manager.HEIGHT - 150,
                                    "./images/quit.png", -1, None)
        self.circle_option.add(self.dojo)
        self.circle_option.add(self.new_game)
        self.circle_option.add(self.game_quit)

        # 创建主菜单界面旋转的水果并添加进精灵组
        self.home_peach = OptionMode(self.window, Manager.WIDTH - 600 + self.dojo.rect.width / 2 - 31,
                                     Manager.HEIGHT - 250 + self.dojo.rect.height / 2 - 59 / 2,
                                     "./images/peach.png", -1, "option_peach")
        self.home_watermelon = OptionMode(self.window, Manager.WIDTH - 405 + self.new_game.rect.width / 2 - 49,
                                          Manager.HEIGHT - 250 + self.new_game.rect.height / 2 - 85 / 2,
                                          "./images/watermelon.png", -1, "option_watermelon")
        self.home_boom = OptionMode(self.window, Manager.WIDTH - 160 + self.game_quit.rect.width / 2 - 66 / 2,
                                    Manager.HEIGHT - 150 + self.game_quit.rect.height / 2 - 68 / 2,
                                    "./images/boom.png", 1, "option_boom")
        self.option_fruit_list.add(self.home_peach)
        self.option_fruit_list.add(self.home_watermelon)
        self.option_fruit_list.add(self.home_boom)

        # 设置定时器
        self.clock = pygame.time.Clock()

        # 模式标记
        self.mode_flag = 0

        # 音效
        self.bgm = Bgm()

        # 刀光
        self.knife = Knife(self.window)

        # 游戏分数
        self.classic_score = 0
        self.zen_score = 0

    def create_fruit(self):
        """ 创建水果 """
        if self.mode_flag == 1:
            boom_prob = random.randint(4, 6)
            if boom_prob == 5:
                self.bgm.play_throw()
                boom = ThrowFruit(self.window, "./images/boom.png", None, 5, 5)
                self.throw_fruit_list.add(boom)

        fruit_image_path = ["./images/apple.png", "./images/banana.png", "./images/peach.png",
                            "./images/watermelon.png", "./images/strawberry.png"]
        fruit_number = random.randint(1, 4)
        for n in range(fruit_number):
            rand_fruit_index = random.randint(0, len(fruit_image_path) - 1)
            self.bgm.play_throw()
            fruit = ThrowFruit(self.window, fruit_image_path[rand_fruit_index], None, 5,
                               rand_fruit_index)
            self.throw_fruit_list.add(fruit)

    def create_fruit_half(self, fruit_flag, fruit_x, fruit_y, turn_angel, v_angel):
        if fruit_flag == "option_peach":
            """ 禅宗模式的桃子被切开 """
            fruit_left = HalfFruit(self.window, "./images/peach-1.png", fruit_x - 50,
                                   fruit_y, turn_angel, v_angel, -5)
            fruit_right = HalfFruit(self.window, "./images/peach-2.png", fruit_x + 50,
                                    fruit_y, -turn_angel, v_angel, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == "option_watermelon":
            """ 经典模式西瓜被切开 """
            fruit_left = HalfFruit(self.window, "./images/watermelon-1.png", fruit_x - 50,
                                   fruit_y, turn_angel, v_angel, -5)
            fruit_right = HalfFruit(self.window, "./images/watermelon-2.png", fruit_x + 50,
                                    fruit_y, -turn_angel, v_angel, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == 0:
            """ 苹果被切开 """
            fruit_left = HalfFruit(self.window, "./images/apple-1.png", fruit_x - 50,
                                   fruit_y, turn_angel, v_angel, -5)
            fruit_right = HalfFruit(self.window, "./images/apple-2.png", fruit_x + 50,
                                    fruit_y, -turn_angel, v_angel, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == 1:
            """ 香蕉被切开 """
            fruit_left = HalfFruit(self.window, "./images/banana-1.png", fruit_x - 50,
                                   fruit_y, turn_angel, v_angel, -5)
            fruit_right = HalfFruit(self.window, "./images/banana-2.png", fruit_x + 50,
                                    fruit_y, -turn_angel, v_angel, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == 2:
            """ 梨被切开 """
            fruit_left = HalfFruit(self.window, "./images/peach-1.png", fruit_x - 50,
                                   fruit_y, turn_angel, v_angel, -5)
            fruit_right = HalfFruit(self.window, "./images/peach-2.png", fruit_x + 50,
                                    fruit_y, -turn_angel, v_angel, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == 3:
            """ 西瓜被切开 """
            fruit_left = HalfFruit(self.window, "./images/watermelon-1.png", fruit_x - 50,
                                   fruit_y, turn_angel, v_angel, -5)
            fruit_right = HalfFruit(self.window, "./images/watermelon-2.png", fruit_x + 50,
                                    fruit_y, -turn_angel, v_angel, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == 4:
            """ 草莓被切开 """
            fruit_left = HalfFruit(self.window, "./images/strawberry-1.png", fruit_x - 50,
                                   fruit_y, turn_angel, v_angel, -5)
            fruit_right = HalfFruit(self.window, "./images/strawberry-2.png", fruit_x + 50,
                                    fruit_y, -turn_angel, v_angel, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

    def impact_check(self):
        """ 碰撞检测 """
        for item in self.option_fruit_list:
            """ 主页的模式选择 """
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] > item.rect.left and mouse_pos[0] < item.rect.right \
                    and mouse_pos[1] > item.rect.top and mouse_pos[1] < item.rect.bottom:
                self.bgm.play_splatter()
                self.create_fruit_half(item.flag, item.rect.x, item.rect.y, item.turn_angel, item.v_angel)
                self.option_fruit_list.remove_internal(item)
                if item.flag == "option_peach":
                    self.mode_flag = 1
                    return 1
                elif item.flag == "option_watermelon":
                    self.mode_flag = 2
                    return 2
                elif item.flag == "option_boom":
                    return 0

        for item in self.throw_fruit_list:
            """ 游戏开始后判断水果是否被切到 """
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] > item.rect.left and mouse_pos[0] < item.rect.right \
                    and mouse_pos[1] > item.rect.top and mouse_pos[1] < item.rect.bottom:
                if item.flag == 0:
                    self.knife.show_apple_flash(item.rect.x, item.rect.y)
                if item.flag == 1:
                    self.knife.show_banana_flash(item.rect.x, item.rect.y)
                if item.flag == 2:
                    self.knife.show_peach_flash(item.rect.x, item.rect.y)
                if item.flag == 3:
                    self.knife.show_watermelon_flash(item.rect.x, item.rect.y)
                if item.flag == 4:
                    self.knife.show_strawberry_flash(item.rect.x, item.rect.y)

                if self.mode_flag == 1:
                    self.zen_score += 2
                if self.mode_flag == 2:
                    self.classic_score += 2
                if item.flag != 5:
                    self.bgm.play_splatter()

                self.create_fruit_half(item.flag, item.rect.x, item.rect.y, item.turn_angel, item.v_angel)
                self.throw_fruit_list.remove_internal(item)
                if item.flag == 5:
                    self.bgm.play_boom()
                    time.sleep(0.4)
                    return 3

    def check_key(self):
        """ 监听事件 """
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == Manager.THROWFRUITTIME and self.mode_flag == 1:
                self.create_fruit()
            elif event.type == Manager.THROWFRUITTIME and self.mode_flag == 2:
                self.create_fruit()

    def zen_mode(self):
        """ 禅宗模式 """
        self.bgm.play_classic()
        score_image = Background(self.window, 10, 5, "./images/score.png")
        text = pygame.font.Font("./images/simhei.ttf", 30)  # 设置分数显示的字体
        best = pygame.font.Font("./images/simhei.ttf", 20)  # 设置历史最好分数显示的字体

        # 禅宗模式游戏时间
        record_time = 3600

        while True:
            # 设置游戏帧率
            self.clock.tick(60)
            self.check_key()
            self.background_list.sprites()[0].update()
            score_image.update()

            text_score = text.render("%d" % self.zen_score, 1, (255, 213, 156))
            self.window.blit(text_score, (50, 8))
            best_score = best.render("BEST %d" % self.zen_best, 1, (255, 179, 78))
            self.window.blit(best_score, (10, 40))

            game_time = text.render("Time:%d" % (record_time / 60), 1, (178, 34, 34))
            self.window.blit(game_time, (510, 12))

            temp_flag = self.impact_check()

            self.throw_fruit_list.update()
            self.fruit_half_list.update()
            pygame.display.update()

            record_time -= 1

            # 禅宗模式更新最高历史记录
            if record_time == 0 or temp_flag == 3:
                if self.zen_score > self.zen_best:
                    file_path = 'best.txt'
                    with open(file_path, 'r') as file:
                        content = file.read()
                        content = content.replace(str(self.zen_best), str(self.zen_score))
                        with open(file_path, 'w') as file:
                            file.write(content)
                return

    def classic_mode(self):
        """ 经典模式 """
        pygame.font.init()
        self.bgm.play_classic()
        score_image = Background(self.window, 10, 5, "./images/score.png")
        text = pygame.font.Font("./images/simhei.ttf", 30)  # 设置分数显示的字体
        best = pygame.font.Font("./images/simhei.ttf", 20)  # 设置历史最好分数显示的字体

        x_nums = pygame.sprite.Group()
        miss_times = pygame.sprite.Group()
        xxx = Background(self.window, Manager.WIDTH - 30, 5, "./images/xxx.png")
        xx = Background(self.window, Manager.WIDTH - 60, 5, "./images/xx.png")
        x = Background(self.window, Manager.WIDTH - 90, 5, "./images/x.png")
        x_nums.add(xxx)
        x_nums.add(xx)
        x_nums.add(x)

        while True:
            # 设置游戏帧率
            self.clock.tick(60)
            pygame.display.update()
            self.check_key()
            self.background_list.sprites()[0].update()
            score_image.update()

            text_score = text.render("%d" % self.classic_score, 1, (255, 213, 156))
            self.window.blit(text_score, (50, 8))
            best_score = best.render("BEST %d" % self.classic_best, 1, (255, 179, 78))
            self.window.blit(best_score, (10, 40))

            x_nums.update()
            miss_times.update()
            temp_flag = self.impact_check()
            if temp_flag == 3:
                # 经典模式炸弹结束游戏更新历史最高记录
                if self.classic_score > self.classic_best:
                    file_path = 'best.txt'
                    with open(file_path, 'r') as file:
                        content = file.read()
                        content = content.replace(str(self.classic_best), str(self.classic_score))
                        with open(file_path, 'w') as file:
                            file.write(content)
                self.bgm.play_boom()
                time.sleep(0.4)
                return

            self.throw_fruit_list.update()
            self.fruit_half_list.update()
            if Manager.classic_miss == 1:
                xf = Background(self.window, Manager.WIDTH - 90, 5, "./images/xf.png")
                miss_times.add(xf)
            elif Manager.classic_miss == 2:
                xf = Background(self.window, Manager.WIDTH - 90, 5, "./images/xf.png")
                miss_times.add(xf)
                xxf = Background(self.window, Manager.WIDTH - 60, 5, "./images/xxf.png")
                miss_times.add(xxf)
            elif Manager.classic_miss >= 3:
                # 经典模式正常结束更新历史最高记录
                if self.classic_score > self.classic_best:
                    file_path = 'best.txt'
                    with open(file_path, 'r') as file:
                        content = file.read()
                        content = content.replace(str(self.classic_best), str(self.classic_score))
                        with open(file_path, 'w') as file:
                            file.write(content)
                self.bgm.play_over()
                time.sleep(0.4)
                Manager.classic_miss = 0
                return

    def main(self):
        """ 主页 """
        self.bgm.play_menu()
        while True:
            # 设置游戏帧率
            self.clock.tick(60)
            self.background_list.update()
            self.circle_option.update()
            self.option_fruit_list.update()
            self.fruit_half_list.update()
            temp_flag = self.impact_check()
            pygame.display.update()

            if temp_flag == 1:
                self.zen_mode()
                self.__init__()
                self.bgm.play_over()
                self.bgm.play_menu()

            if temp_flag == 2:
                self.classic_mode()
                self.__init__()
                self.bgm.play_over()
                self.bgm.play_menu()

            elif temp_flag == 0:
                self.bgm.play_over()
                time.sleep(0.3)
                pygame.quit()
                exit()
            elif temp_flag == 3:
                self.__init__()
                self.bgm.play_menu()
            self.check_key()


if __name__ == '__main__':
    manager = Manager()
    manager.main()
