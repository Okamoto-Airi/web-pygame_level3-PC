# Pygameライブラリのインポート
import pygame  # ゲーム用ライブラリ

# OSパス操作用
import os  # ファイルパス結合などに使用


# ゲーム画面のサイズ（左上x, 左上y, 幅, 高さ）
SCREEN = pygame.Rect((0, 0, 640, 480))  # 画面サイズを矩形で定義


def draw_hp_bar(screen, dragon, pos=(100, 50), size=(200, 20), font=None):
    """
    敵のHPゲージを描画（文字付き）
    :param screen: 描画先
    :param dragon: HP情報を持つ敵（例：Dragonクラスのインスタンス）
    :param pos: 描画位置 (x, y)
    :param size: バーサイズ (width, height)
    :param font: pygame.font.Font オブジェクト（省略時は自動生成）
    """
    x, y = pos
    w, h = size

    # 背景（灰色）
    pygame.draw.rect(screen, (180, 180, 180), (x, y, w, h))

    # HP比率に応じた色（段階的）
    hp_ratio = max(0, dragon.hp / dragon.MAX_HP)
    if hp_ratio > 0.5:
        bar_color = (0, 255, 0)  # 緑
    elif hp_ratio > 0.2:
        bar_color = (240, 240, 0)  # 黄
    else:
        bar_color = (255, 0, 0)  # 赤
    pygame.draw.rect(screen, bar_color, (x, y, int(w * hp_ratio), h))

    # 枠線（黒）
    pygame.draw.rect(screen, (0, 0, 0), (x, y, w, h), 2)

    # HP数値の文字（中央に描画）
    if font is None:
        font = pygame.font.SysFont(None, 20)
    hp_text = font.render(f"Dragon HP: {dragon.hp}/{dragon.MAX_HP}", True, (0, 0, 0))
    text_rect = hp_text.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(hp_text, text_rect)


def calculate_score_and_rank(screen, time_left, life_val, font):
    """
    残り時間とライフからスコアとランクを計算し、スコア画像・ランク画像を返す。
    screen: 描画先のPygame画面
    game_status: ゲームの状態（例：CLEAR, GAME_OVERなど）
    :param time_left: 残り秒数（int）
    :param life_val: ライフの残り値（int）
    :param font: Pygameフォントオブジェクト
    :return: (スコア画像Surface, ランク画像Surface)
    """

    # スコア計算
    time_score = time_left * 10
    life_score = life_val * 100
    final_score = time_score + life_score

    if final_score >= 500:
        rank = "GOLD"
    elif final_score >= 300:
        rank = "SILVER"
    elif final_score >= 100:
        rank = "BRONZE"
    else:
        rank = "NONE"

    score_img = font.render(f"FINAL SCORE: {final_score}", True, (245, 127, 23))
    rank_img = font.render(f"RANK: {rank}", True, (245, 127, 23))
    screen.blit(score_img, (SCREEN.centerx - 150, SCREEN.centery - 10))
    screen.blit(rank_img, (SCREEN.centerx - 100, SCREEN.centery + 20))

    text1 = font.render("Restart (R) / Exit Game (Q)", True, (0, 0, 0))
    screen.blit(text1, (SCREEN.centerx - 200, SCREEN.centery + 100))


def load_image(fname, size=None):
    """
    画像ファイルを読み込んでSurfaceオブジェクトとして返す関数。
    Args:
        fname: ファイル名（pictureフォルダ内）
        size: 指定時はそのサイズにリサイズ
    Returns:
        pygame.Surface: 読み込んだ画像（必要に応じてリサイズ済み）
    """
    picture_path = os.path.join("picture", fname)  # pictureフォルダ内のパスを作成
    tmp = pygame.image.load(
        picture_path
    ).convert_alpha()  # 画像をアルファ付きで読み込み
    return (
        tmp if size is None else pygame.transform.scale(tmp, size)
    )  # リサイズ有無で返す


def load_sound(sound):
    """
    サウンドファイルを読み込んでSoundオブジェクトとして返す関数。
    Args:
        sound: ファイル名（musicフォルダ内）
    Returns:
        pygame.mixer.Sound: 読み込んだサウンド
    """
    sound_path = os.path.join("music", sound)  # musicディレクトリとファイル名を結合
    return pygame.mixer.Sound(sound_path)  # サウンドファイルを読み込んで返す


class Counter:
    """
    汎用カウンタクラス。
    ・値の加減算、リセット、最大値制御などを提供。
    ・スコアやビーム発射数など様々な用途で利用。
    """

    def __init__(self, initval, maxval=None):
        self.init_val = initval  # カウンタの初期値
        self._val = initval  # 現在値
        if maxval:  # 最大値が指定されていれば
            self._maxval = maxval  # 最大値をセット

    @property
    def val(self):
        # 現在値を取得
        return self._val

    @val.setter
    def val(self, val):
        # 現在値をセット（0未満は0に補正）
        self._val = val if val >= 0 else 0

    def reset(self):
        # カウンタを初期値にリセット
        self._val = self.init_val

    @property
    def maxval(self):
        # 最大値を取得
        return self._maxval


class Score(Counter, pygame.sprite.Sprite):
    """
    スコアやライフなどの数値を画面に表示するスプライトクラス。
    Counter（値管理）とpygame.sprite.Sprite（描画）を多重継承。
    数字やパターン（●○など）で表示可能。
    """

    FONT_SIZE = 28  # フォントサイズ
    BLUE = (0, 0, 255)  # 青色（デフォルト）
    RED = (255, 0, 0)  # 赤色

    def __init__(
        self,
        initval=0,  # 初期値
        maxval=None,  # 最大値
        pos=(0, 0),  # 表示位置
        color=BLUE,  # 色指定
        font=None,  # フォント指定（既定値：システム）
        form="#",  # 表示形式指定
        pat=None,  # 表示パターン（pat="●○"のように指定）
    ):
        Counter.__init__(self, initval, maxval)  # Counterの初期化
        pygame.sprite.Sprite.__init__(self, self.containers)  # Spriteの初期化
        if font is None:  # フォント指定がなければシステムデフォルト
            self.font = pygame.font.SysFont(None, Score.FONT_SIZE)
        else:  # 指定があればfontディレクトリから読み込む
            font_path = os.path.join("font", font)
            self.font = pygame.font.Font(font_path, 20)
        self.color = color  # 表示色
        self.pos = pos  # 表示位置
        self.pat = pat  # パターン表示用（例: "●○"）
        # 表示形式の設定
        if self.pat:  # パターン表示の場合
            self.form = form.replace("#", "{}")  # #を{}に置換
            text_img = self.form.format(self.pat[0] * self._val)  # ●の数だけ表示
        else:  # 数値表示の場合
            self.form = form.replace("#", "{:0>5d}")  # #をゼロ埋め5桁に置換
            text_img = self.form.format(self._val)  # 数値を表示
        self.image = self.font.render(text_img, False, self.color)  # テキスト画像生成
        self.rect = self.image.get_rect().move(self.pos)  # 画像の位置をセット

    def update(self):
        # スコアやライフの値が変化したときに呼ばれる
        # パターン表示（例: ●○）の場合
        if self.pat:
            text_img = self.form.format(
                self.pat[0] * self._val + self.pat[1] * (self._maxval - self._val)
            )  # ●の数と○の数を合成
        else:  # 数値表示の場合
            text_img = self.form.format(self._val)
        self.image = self.font.render(
            text_img, False, self.color
        )  # テキスト画像を再生成
        self.rect = self.image.get_rect().move(self.pos)  # 画像の位置も再設定
