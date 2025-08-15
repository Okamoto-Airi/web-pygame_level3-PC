# ランダム値生成用
import random
import math

# Pygameライブラリ
import pygame

# 画像読み込み・画面サイズ定数
from utils import load_image, SCREEN


# =============================
# 登場する人物/物/背景のクラス定義
# =============================


class Background:
    """
    ゲーム画面の背景を管理するクラス。
    ・空の画像を読み込み、描画する。

    """

    def __init__(self, majo):
        # self.majo = majo  # 魔女インスタンス。魔女の位置に応じて山の表示を動かす。
        self.sky_image = load_image(
            "bg_natural_sky.jpg", SCREEN.size
        )  # 空の画像を画面サイズで読み込み
        # self.mount_image = load_image(
        #     "bg_natural_mount_800x800.png"
        # )  # 山の画像を読み込み
        # self.mount_rect = (
        #     self.mount_image.get_rect()
        # )  # 山画像の矩形情報（幅・高さなど）
        # self.ground_image = pygame.Surface(
        #     (SCREEN.width, 20)
        # )  # 地面用のサーフェス（矩形画像）を生成
        # self.ground_image.fill((0, 128, 64))  # 地面の色を緑色(RGB)で塗りつぶす
        # self.ground_rect = self.ground_image.get_rect()  # 地面の矩形情報
        # self.ground_rect.bottom = SCREEN.bottom  # 地面を画面下端に配置（y座標調整）

    # def update(self):
    #     # 魔女のx座標に応じて山の表示位置を計算し、パララックス効果を演出
    #     # 画面幅を超える山画像を、魔女の移動に合わせて左右にスクロールさせる
    #     self.mount_image_x = (
    #         (self.mount_rect.width - SCREEN.width)
    #         / SCREEN.width
    #         * self.majo.rect.centerx
    #     )

    def draw(self, screen):
        # 背景（空・山・地面）を画面に描画する
        # 空は常に画面全体に描画
        screen.blit(self.sky_image, SCREEN)  # 空
        # # 山は魔女の位置に応じて左右にスクロール
        # screen.blit(self.mount_image, (-self.mount_image_x, -118))  # 山
        # # 地面は画面下端に固定して描画
        # screen.blit(self.ground_image, self.ground_rect)  # 地面


class Majo(pygame.sprite.Sprite):
    """
    魔女キャラクターのスプライトクラス。
    ・上下移動、アニメーション、画面端制御を担当。
    ・ライフや得点などの定数もここで管理。
    継承: pygame.sprite.Sprite
    """

    IMAGE_WIDTH, IMAGE_HEIGHT = (32, 32)  # 1コマの幅・高さ（ピクセル）
    # LEFT, RIGHT = (1, 2)  # 向き（左:1, 右:2）
    SPEED = 5  # 移動速度（ピクセル/フレーム）
    # IMAGE_NUMS = 3  # アニメーションコマ数
    MINUS_LIFE = 1  # 爆弾被弾時のライフ減少量

    def __init__(self):
        # スプライトの初期化（所属グループに登録）
        # self.containersはmain.pyでSpriteグループとしてセットされる
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = load_image(
            "majo_level2_small.png"
        )  # 魔女のスプライト画像（複数コマ）
        # self.image_dir = Majo.LEFT  # 初期向き（左）
        # self.image_off = 0  # アニメーション用のコマ番号
        # # 初期画像（左向き・最初のコマ）を切り出し
        # self.image = self.images.subsurface((0, 0, Majo.IMAGE_WIDTH, Majo.IMAGE_HEIGHT))
        # 位置情報（pygame.Rect）を初期化
        self.rect = pygame.Rect((0, 0, Majo.IMAGE_WIDTH, Majo.IMAGE_HEIGHT))
        self.rect.left = SCREEN.left  # 画面左に配置
        # 画面真ん中に配置
        self.rect.centery = SCREEN.centery  # y座標は画面中央
        # self.rect.bottom = SCREEN.bottom - 20  # 画面下から20px上に配置

    def move_left(self, obstacles):
        # 左キーが押されたときの移動処理
        # self.rect.move_ip(-Majo.SPEED, 0)  # x座標を左に移動
        # self.image_dir = Majo.LEFT  # 向きを左に
        self.move(obstacles, -Majo.SPEED, 0)  # 画像（アニメーション）更新

    def move_right(self, obstacles):
        # 右キーが押されたときの移動処理
        # self.rect.move_ip(Majo.SPEED, 0)  # x座標を右に移動
        # self.image_dir = Majo.RIGHT  # 向きを右に
        self.move(obstacles, Majo.SPEED, 0)  # 画像（アニメーション）更新

    def move_up(self, obstacles):
        # 上キーが押されたときの移動処理
        # self.rect.move_ip(0, -Majo.SPEED)  # y座標を上に移動
        self.move(obstacles, 0, -Majo.SPEED)  # 画像（アニメーション）更新

    def move_down(self, obstacles):
        # 下キーが押されたときの移動処理
        # self.rect.move_ip(0, Majo.SPEED)  # y座標を下に移動
        self.move(obstacles, 0, Majo.SPEED)  # 画像（アニメーション）更新

    def move(self, obstacles, x_speed, y_speed):
        # 移動後の仮位置を作成
        new_rect = self.rect.move(x_speed, y_speed)

        # 画面外に出ないように制限
        screen_rect = pygame.Rect((0, 40, 640, 440))
        new_rect.clamp_ip(screen_rect)

        # 衝突判定
        collision = False
        for obs in obstacles:
            if new_rect.colliderect(obs.rect):
                collision = True
                break

        # 衝突していなければ移動
        if not collision:
            self.rect = new_rect
        # # アニメーション用の画像切り替え（歩く動作）
        # self.image_off = (self.image_off + 1) % Majo.IMAGE_NUMS  # コマ番号を進める
        # # 向きは一定（例: 左向き）で固定
        # self.image = self.images.subsurface(
        #     (
        #         self.image_off * Majo.IMAGE_WIDTH,
        #         Majo.LEFT * Majo.IMAGE_HEIGHT,  # 常に左向き
        #         Majo.IMAGE_WIDTH,
        #         Majo.IMAGE_HEIGHT,
        #     )
        # )

    def update(self):
        # 魔女の自動更新処理（現状は何もしない。将来拡張用）
        pass


class Beam(pygame.sprite.Sprite):
    """
    魔女が発射するビームのスプライトクラス。
    ・ビームの発射、移動、画面外での消滅、発射数カウントを担当。
    ・ビームの爆発アニメ用定数もここで管理。
    継承: pygame.sprite.Sprite
    """

    SPEED = 5  # ビームの移動速度（ピクセル/フレーム）
    counter = 0  # 発射中のビーム数（最大2発まで）
    EXP_IMAGE_WIDTH, EXP_IMAGE_HEIGHT = (
        120,
        120,
    )  # 爆発画像の1コマの幅・高さ（ピクセル）
    EXP_IMAGE_OFFSET = 5  # 爆発アニメのコマ数
    EXP_ANIME_COUNT = 5  # 爆発アニメの繰り返し回数

    def __init__(self, majo, dx, dy):
        # スプライトの初期化（所属グループに登録）
        # majo: 発射元の魔女インスタンス
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.majo = majo  # 発射元の魔女
        self.dx = dx
        self.dy = dy
        # 方向に応じて画像を選択
        self.image = Beam.images.get((dx, dy), Beam.images[(1, 0)])
        self.rect = self.image.get_rect()  # ビーム画像の矩形情報
        self.rect.center = self.majo.rect.center
        Beam.counter.val += 1  # 発射中ビーム数をカウント（最大2発まで）
        Beam.sound.play()  # 発射音再生

    def update(self):
        self.rect.move_ip(self.dx * Beam.SPEED, self.dy * Beam.SPEED)
        # 画面外に出たら消滅し、カウンタも減らす
        if (
            self.rect.right < 0
            or self.rect.left > SCREEN.right
            or self.rect.bottom < 0
            or self.rect.top > SCREEN.bottom
        ):
            Beam.counter.val -= 1  # 画面外でカウンタ減少
            self.kill()  # ビーム消滅


class Demon(pygame.sprite.Sprite):
    """
    魔王のスプライトクラス。
    ・上下移動、炎投下、爆発アニメ、スコア管理を担当。
    ・爆弾の投下確率や爆発アニメの定数もここで管理。
    継承: pygame.sprite.Sprite
    """

    IMAGE_WIDTH, IMAGE_HEIGHT = 64, 28  # 魔王画像の1コマの幅・高さ（ピクセル）
    SPEED = 5  # 移動速度（ピクセル/フレーム）
    # LEFT, RIGHT = 0, 1  # 向き（左:0, 右:1）
    BOMB_PROB = 0.05  # 爆弾投下確率（5%）
    MINUS_POINT = 5  # 魔王撃破時の減点
    MAX_HP = 100  # 魔王の最大HP

    RADIUS = 60  # 円運動の半径（ピクセル）
    ANGLE_SPEED = 0.05  # 1フレームあたりの角度変化（ラジアン）

    # 爆発アニメ
    EXP_IMAGE_WIDTH, EXP_IMAGE_HEIGHT = (
        320,
        120,
    )  # 爆発画像の1コマの幅・高さ（ピクセル）
    EXP_IMAGE_OFFSET = 8  # 爆発アニメのコマ数
    EXP_ANIME_COUNT = 10  # 爆発アニメの繰り返し回数

    def __init__(self):
        # スプライトの初期化（所属グループに登録）
        # self.containersはmain.pyでSpriteグループとしてセットされる
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = load_image("demon-king_small.png")
        self.rect = self.image.get_rect()  # 位置情報
        self.center = SCREEN.center  # 初期位置（画面中央）
        self.angle = 0  # 現在の角度（ラジアン）
        self.radius = Demon.RADIUS  # 円運動の半径
        self.speed = Demon.SPEED  # 移動速度
        # self.dir = Demon.LEFT  # 初期向き
        self.hp = Demon.MAX_HP  # 初期HP（最大値）

    def update(self):
        # # 毎フレーム上下に移動
        # self.rect.move_ip(0, self.speed)
        # # 画面端に到達したら進行方向を反転
        # if self.rect.top <= SCREEN.top or self.rect.bottom >= SCREEN.bottom:
        #     self.speed = -self.speed  # 方向転換
        # self.rect.clamp_ip(SCREEN)  # 画面外に出ないよう制限
        # # 画像の向きは一定（例: 左向き）で固定
        # self.image = Dragon.images.subsurface(
        #     0, 0, Dragon.IMAGE_WIDTH, Dragon.IMAGE_HEIGHT
        # )

        # # 一定確率で爆弾を投下（BOMB_PROBで制御）
        # if random.random() < Dragon.BOMB_PROB:
        #     # # ステージが進むと爆弾の横方向速度もランダムで増加
        #     # dx = (
        #     #     0 if Majo.stage.val <= 2 else (random.random() * 2.0 - 1.0) * self.speed
        #     # )
        #     dx = 0  # 横方向の移動量（ステージ1は固定）
        #     Bomb(self, dx)  # 爆弾生成

        # 角度を少しずつ増やす（時計回り）
        self.angle += Demon.ANGLE_SPEED
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi

        # 円運動の座標計算
        x = self.center[0] + self.radius * math.cos(self.angle)
        y = self.center[1] + self.radius * math.sin(self.angle)

        # rectの中心を更新
        self.rect.center = (int(x), int(y))

        # 魔王は中央に固定（移動なし）
        # 四方八方に爆弾を投下
        if random.random() < Demon.BOMB_PROB:
            # 8方向ベクトル
            directions = [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
                (-1, -1),
                (1, -1),
                (-1, 1),
                (1, 1),
            ]
            dx, dy = random.choice(directions)
            Bomb(self, dx * Bomb.SPEED, dy * Bomb.SPEED)
        elif random.random() < Demon.BOMB_PROB:
            # 30%の確率で無敵爆弾
            invincible = random.random() < 0.3
            # Bomb(self, invincible=invincible)
            directions = [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
                (-1, -1),
                (1, -1),
                (-1, 1),
                (1, 1),
            ]
            dx, dy = random.choice(directions)
            Bomb(self, dx * Bomb.SPEED, dy * Bomb.SPEED, invincible=invincible)

        # 魔王の爆破シーン（スコア0で爆発アニメ＆消滅）
        if self.hp == 0:
            Explosion(
                Demon.exp_images,
                self.rect.center,
                (Demon.EXP_IMAGE_WIDTH, Demon.EXP_IMAGE_HEIGHT),
                Demon.EXP_IMAGE_OFFSET,
                Demon.EXP_ANIME_COUNT,
                Demon.exp_sound,
            )
            self.kill()
            return


# 周りを周回する敵
class EdgeRunner(pygame.sprite.Sprite):
    def __init__(self, speed=3, clockwise=True):
        super().__init__(self.containers)
        self.image = load_image("sub-demon_small.png")
        self.rect = self.image.get_rect()  # 位置情報

        self.speed = speed
        self.clockwise = clockwise

        # 初期位置（左下から反時計回り）
        self.rect.topleft = (0, 440)
        self.state = 1  # 0=右, 1=下, 2=左, 3=上

    def update(self):
        screen_rect = pygame.Rect((0, 40, 640, 440))

        # 移動
        if self.state == 0:  # 右
            self.rect.x += self.speed
            if self.rect.right >= screen_rect.right:
                self.rect.right = screen_rect.right
                self.state = (self.state + (1 if self.clockwise else -1)) % 4
        elif self.state == 1:  # 下
            self.rect.y += self.speed
            if self.rect.bottom >= screen_rect.bottom:
                self.rect.bottom = screen_rect.bottom
                self.state = (self.state + (1 if self.clockwise else -1)) % 4
        elif self.state == 2:  # 左
            self.rect.x -= self.speed
            if self.rect.left <= screen_rect.left:
                self.rect.left = screen_rect.left
                self.state = (self.state + (1 if self.clockwise else -1)) % 4
        elif self.state == 3:  # 上
            self.rect.y -= self.speed
            if self.rect.top <= screen_rect.top:
                self.rect.top = screen_rect.top
                self.state = (self.state + (1 if self.clockwise else -1)) % 4


class Explosion(pygame.sprite.Sprite):
    """
    爆発アニメーションのスプライトクラス。
    ・爆発画像のコマ切り替え、消滅処理、効果音再生を担当。
    ・横長画像/縦長画像どちらにも対応。
    継承: pygame.sprite.Sprite
    Args:
        images: 爆発アニメ画像
        start_pos: 爆発の中心座標
        image_size: 1コマのサイズ
        max_offset: コマ数
        max_anime_count: アニメ繰り返し数
        exp_sound: 爆発音
    """

    def __init__(
        self, images, start_pos, image_size, max_offset, max_anime_count, exp_sound
    ):
        # スプライトの初期化（所属グループに登録）
        # images: 爆発アニメ画像（横長 or 縦長）
        # start_pos: 爆発の中心座標
        # image_size: 1コマの幅・高さ
        # max_offset: コマ数
        # max_anime_count: アニメ繰り返し数
        # exp_sound: 爆発音
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = images  # 爆発画像
        self.images_rect = self.images.get_rect()  # 画像全体の矩形
        self.max_offset = max_offset  # 爆発コマ数
        self.offset = 0  # 現在のコマ番号
        self.max_anime_count = max_anime_count  # アニメーション繰り返し数
        self.anime_count = 0  # 現在のアニメカウント
        self.sizex, self.sizey = image_size  # 1コマのサイズ
        # 横長画像か縦長画像かで切り出し方法を変える
        if self.images_rect.width > self.images_rect.height:
            # 横長画像の場合（横方向にコマが並ぶ）
            self.image = self.images.subsurface(
                (self.offset * self.sizex, 0, self.sizex, self.sizey)
            )
        else:
            # 縦長画像の場合（縦方向にコマが並ぶ）
            self.image = self.images.subsurface(
                (0, self.offset * self.sizey, self.sizex, self.sizey)
            )

        self.rect = self.image.get_rect()  # 爆発の位置
        self.rect.center = start_pos  # 爆発の中心座標
        exp_sound.play()  # 爆発音再生

    def update(self):
        # 毎フレーム呼ばれる。アニメーションカウントを進める
        self.anime_count = (self.anime_count + 1) % self.max_anime_count
        if self.anime_count == 0:
            self.offset += 1  # コマを進める
            if self.offset == self.max_offset:
                self.offset = 0  # コマリセット
                self.kill()  # 爆発スプライトを消滅させる
                return
        # 横長画像か縦長画像かで切り出し方法を変える
        if self.images_rect.width > self.images_rect.height:
            # 横長画像の場合
            self.image = self.images.subsurface(
                (self.offset * self.sizex, 0, self.sizex, self.sizey)
            )
        else:
            # 縦長画像の場合
            self.image = self.images.subsurface(
                (0, self.offset * self.sizey, self.sizex, self.sizey)
            )


class Bomb(pygame.sprite.Sprite):
    """
    魔王が落とす爆弾のスプライトクラス。
    ・爆弾の落下、爆発、アニメーションを担当。
    ・爆弾の色やアニメコマ数もここで管理。
    継承: pygame.sprite.Sprite
    Args:
        demon: 爆弾を落とす魔王インスタンス
    """

    IMAGE_COLORS, IMAGE_OFFSET = 4, 3  # 爆弾の色数とアニメコマ数
    # IMAGE_WIDTH, IMAGE_HEIGHT = 112, 64  # 1コマの幅・高さ（ピクセル）
    SPEED = 5  # 爆弾の落下速度（ピクセル/フレーム）
    # 爆発アニメ
    EXP_IMAGE_WIDTH, EXP_IMAGE_HEIGHT = (
        120,
        120,
    )  # 爆発画像の1コマの幅・高さ（ピクセル）
    EXP_IMAGE_OFFSET = 7  # 爆発アニメのコマ数
    EXP_ANIME_COUNT = 5  # 爆発アニメの繰り返し回数

    # 8方向の画像ファイル名対応表(通常爆弾)
    DIRECTION_IMAGES = {
        (-1, 0): ("ufo_bomb_left.png", 112, 64),
        (1, 0): ("ufo_bomb_right.png", 112, 64),
        (0, -1): ("ufo_bomb_up.png", 64, 112),
        (0, 1): ("ufo_bomb_down.png", 64, 112),
        # (-1, -1): ("ufo_bomb_up-left.png",),
        # (1, -1): ("ufo_bomb_up-right.png",),
        # (-1, 1): ("ufo_bomb_down-left.png",),
        # (1, 1): ("ufo_bomb_down-right.png",)
    }
    # 無敵爆弾の画像セット
    INVINCIBLE_DIRECTION_IMAGES = {
        (-1, 0): ("demon_beam_small_left.png", 111, 55),
        (1, 0): ("demon_beam_small_right.png", 111, 55),
        (0, -1): ("demon_beam_small_up.png", 55, 111),
        (0, 1): ("demon_beam_small_down.png", 55, 111),
    }
    # 画像キャッシュ
    direction_images_cache = {}
    invincible_images_cache = {}

    def __init__(self, demon, dx, dy, invincible=False):
        # スプライトの初期化（所属グループに登録）
        # demon: 爆弾を落とす魔王インスタンス
        # dx, dy: 爆弾の移動量（上下方向）
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.invincible = invincible  # 無敵爆弾フラグ
        self.dx = dx
        self.dy = dy
        # 爆弾の色をランダムで決定（4色）
        self.image_color = int(random.random() * Bomb.IMAGE_COLORS)
        self.image_off = 0  # アニメーション用オフセット

        # 方向に応じて画像を選択
        key = (self._sign(dx), self._sign(dy))
        # if key not in Bomb.direction_images_cache:
        #     fname = Bomb.DIRECTION_IMAGES.get(key, "ufo_bomb_down.png")
        #     Bomb.direction_images_cache[key] = load_image(fname)
        # base_image = Bomb.direction_images_cache[key]
        self.frames = self._load_direction_image(key, invincible=self.invincible)
        self.image = self.frames[self.image_off]
        self.rect = self.image.get_rect(center=demon.rect.center)

        # # 爆弾画像（色・コマ番号で切り出し）
        # self.image = base_image.subsurface(
        #     (
        #         self.image_color * Bomb.IMAGE_WIDTH,
        #         self.image_off * Bomb.IMAGE_HEIGHT,
        #         Bomb.IMAGE_WIDTH,
        #         Bomb.IMAGE_HEIGHT,
        #     )
        # )
        # self.rect = self.image.get_rect()  # 位置情報
        # self.rect.center = demon.rect.center  # 魔王中央から発射
        # self.dx = dx  # 上下方向の移動量
        # self.dy = dy

    def _sign(self, v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def _load_direction_image(self, key, invincible=False):
        # キャッシュ対象と画像セットを切り替える
        if invincible:
            cache = Bomb.invincible_images_cache
            img_set = Bomb.INVINCIBLE_DIRECTION_IMAGES
        else:
            cache = Bomb.direction_images_cache
            img_set = Bomb.DIRECTION_IMAGES
        # すでにキャッシュ済みならそれを返す
        # if key in Bomb.direction_images_cache:
        #     return Bomb.direction_images_cache[key]
        if key in cache:
            return cache[key]

        # 上下左右：画像からそのまま分割して返す
        if key in img_set:
            fname, w, h = img_set[key]
            sheet = load_image(fname)
            # frames = [
            #     sheet.subsurface((i * w, 0, w, h))  # 横並び前提
            #     for i in range(Bomb.IMAGE_OFFSET)
            # ]
            frames = []
            if invincible:
                # 無敵爆弾はアニメーションしないので画像を1枚だけ返す（フレームリストとして）
                frames.append(sheet)  # 画像まるごと
                cache[key] = frames
                return frames
            # 横長画像（左右方向）はX方向、縦長画像（上下方向）はY方向で切り出す
            if w >= h:
                # 横長（左右方向）
                for i in range(Bomb.IMAGE_OFFSET):
                    frames.append(sheet.subsurface((0, i * h, w, h)))
            else:
                # 縦長（上下方向）
                for i in range(Bomb.IMAGE_OFFSET):
                    frames.append(sheet.subsurface((i * w, 0, w, h)))

            cache[key] = frames
            return frames

        # 斜め方向：上下左右の画像を回転して作る
        base_key = self._get_nearest_base_direction(key)
        base_frames = self._load_direction_image(base_key, invincible)  # 再帰的に取得

        angle = self._get_rotation_angle(base_key, key)
        rotated_frames = [
            pygame.transform.rotate(frame, angle) for frame in base_frames
        ]

        cache[key] = rotated_frames
        return rotated_frames

    def _get_nearest_base_direction(self, key):
        # 斜め→左右（dx!=0）優先、なければ上下
        dx, dy = key
        if dx != 0 and dy != 0:
            return (dx, 0)  # 横ベース（←→）を使う
        return key

    def _get_rotation_angle(self, from_dir, to_dir):
        """回転角度を返す（反時計回り）"""
        # (from_dir) → (to_dir) に回す角度
        angle_map = {
            ((-1, 0), (-1, -1)): -45,  # ← → ↖
            ((-1, 0), (-1, 1)): 45,  # ← → ↙
            ((1, 0), (1, -1)): 45,  # → → ↗
            ((1, 0), (1, 1)): -45,  # → → ↘
            ((0, -1), (-1, -1)): 45,  # ↑ → ↖
            ((0, -1), (1, -1)): -45,  # ↑ → ↗
            ((0, 1), (-1, 1)): -45,  # ↓ → ↙
            ((0, 1), (1, 1)): 45,  # ↓ → ↘
        }
        return angle_map.get((from_dir, to_dir), 0)

    # def _get_frame(self):
    #     w, h = self.frame_size
    #     x = self.image_color * w
    #     y = self.image_off * h
    #     return self.base_image.subsurface((x, y, w, h))

    def update(self):
        # 毎フレーム四方八方に攻撃
        self.rect.move_ip(self.dx, self.dy)
        # 画面外に出たら爆発
        if (
            self.rect.left < SCREEN.left
            or self.rect.right > SCREEN.right
            or self.rect.top < SCREEN.top
            or self.rect.bottom > SCREEN.bottom
        ):
            Explosion(
                Bomb.exp_images,
                self.rect.center,
                (Bomb.EXP_IMAGE_WIDTH, Bomb.EXP_IMAGE_HEIGHT),
                Bomb.EXP_IMAGE_OFFSET,
                Bomb.EXP_ANIME_COUNT,
                Bomb.exp_sound,
            )
            self.kill()
            return
        # # アニメーション用の画像切り替え（コマ番号を進める）
        # self.image_off = (self.image_off + 1) % Bomb.IMAGE_OFFSET
        # key = (self._sign(self.dx), self._sign(self.dy))
        # base_image = Bomb.direction_images_cache[key]
        # self.image = base_image.subsurface(
        #     (
        #         self.image_color * Bomb.IMAGE_WIDTH,
        #         self.image_off * Bomb.IMAGE_HEIGHT,
        #         Bomb.IMAGE_WIDTH,
        #         Bomb.IMAGE_HEIGHT,
        #     )
        # )
        # 無敵爆弾はアニメーションしない
        if not self.invincible:
            self.image_off = (self.image_off + 1) % Bomb.IMAGE_OFFSET
            self.image = self.frames[self.image_off]
            self.rect = self.image.get_rect(center=self.rect.center)


class Point(pygame.sprite.Sprite):
    """
    得点やライフ減少などのポイント表示用スプライトクラス。
    ・画面上に一時的に数値を表示し、一定時間後に自動で消滅。
    ・主に衝突時の得点やライフ減少の視覚的フィードバックに使用。
    継承: pygame.sprite.Sprite
    Args:
        point: 表示する数値
        start_pos: 表示開始位置
    """

    FONT_SIZE = 32
    RED = (255, 0, 0)
    MAX_ANIME_COUNT = 50

    def __init__(self, point, start_pos):
        # スプライトの初期化（所属グループに登録）
        # point: 表示する数値
        # start_pos: 表示開始位置（x, y）
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.point = point  # 表示するポイント値（例: -1, -5, +10など）
        self.font = pygame.font.SysFont(
            None, Point.FONT_SIZE
        )  # フォント設定（デフォルト）
        # 数値を赤色で画像化（例: "-5"）
        self.image = self.font.render("-" + str(self.point), False, Point.RED)
        self.rect = self.image.get_rect()  # 画像の矩形情報
        self.rect.center = start_pos  # 表示位置（中心座標）
        self.anime_count = 0  # アニメーションカウント（表示経過フレーム数）

    def update(self):
        # 毎フレーム呼ばれる。一定時間経過で自動消滅
        self.anime_count += 1
        if self.anime_count == Point.MAX_ANIME_COUNT:
            self.kill()  # スプライトを消滅させる
            return


class HPBarSprite(pygame.sprite.Sprite):
    def __init__(self, demon, pos=(SCREEN.centerx - 100, 8), size=(200, 20)):
        super().__init__(self.containers)
        self.demon = demon
        self.pos = pos
        self.size = size
        self.font = pygame.font.SysFont(None, 20)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        self.update()

    def update(self):
        x, y = 0, 0
        w, h = self.size
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, (180, 180, 180), (x, y, w, h))
        hp_ratio = max(0, self.demon.hp / self.demon.MAX_HP)
        if hp_ratio > 0.5:
            bar_color = (0, 255, 0)
        elif hp_ratio > 0.2:
            bar_color = (240, 240, 0)
        else:
            bar_color = (255, 0, 0)
        pygame.draw.rect(self.image, bar_color, (x, y, int(w * hp_ratio), h))
        pygame.draw.rect(self.image, (0, 0, 0), (x, y, w, h), 2)
        hp_text = self.font.render(
            f"Demon HP: {self.demon.hp}/{self.demon.MAX_HP}", True, (0, 0, 0)
        )
        text_rect = hp_text.get_rect(center=(w // 2, h // 2))
        self.image.blit(hp_text, text_rect)
