# Pygameライブラリのインポート（ゲーム開発用）
import pygame

# Pygameの定数を明示的にインポート（イベントやキーコード用）
from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_SPACE,
    K_q,
    K_r,
    K_LEFT,
    K_RIGHT,
    K_UP,
    K_DOWN,
    K_w,
    K_a,
    K_s,
    K_d,
)

# システム終了用
import sys

# 非同期処理用
import asyncio

import js  # pygbag環境でのみ有効

# スプライト関連クラスのインポート
from sprites import Background, Majo, Dragon, Beam, Bomb, Explosion, Point, HPBarSprite

# ユーティリティ関数・定数のインポート
from utils import (
    load_image,
    load_sound,
    SCREEN,
    Score,
    Counter,
    calculate_score_and_rank,
    TimerSprite,
)


# =============================
# 衝突判定関数（ゲーム内の当たり判定をまとめて管理）
# =============================
def collision_detection(majo, dragon, beam_g, bomb_g):
    """
    ゲーム内の各種衝突判定を行う関数。
    - ビームとドラゴン
    - ビームと爆弾
    - 魔女と爆弾
    それぞれの衝突時にエフェクトやスコア・ライフの更新を行う。
    """
    # --- ビームとドラゴンの衝突判定 ---
    beam_collided = pygame.sprite.spritecollide(
        dragon, beam_g, True
    )  # ドラゴンに当たったビームを取得
    if beam_collided:
        # 爆発エフェクト生成
        Explosion(
            Beam.exp_images,
            beam_collided[0].rect.center,
            (Beam.EXP_IMAGE_WIDTH, Beam.EXP_IMAGE_HEIGHT),
            Beam.EXP_IMAGE_OFFSET,
            Beam.EXP_ANIME_COUNT,
            Beam.exp_sound,
        )
        Beam.counter.val -= 1  # ビーム発射数を減らす
        Point(Dragon.MINUS_POINT, dragon.rect.center)  # 得点表示
        dragon.hp -= Dragon.MINUS_POINT  # ドラゴンスコア減少

    # --- ビームと爆弾の衝突判定 ---
    group_collided = pygame.sprite.groupcollide(
        bomb_g, beam_g, True, True
    )  # 爆弾とビームの衝突
    # group_collided: {爆弾: [当たったビーム, ...], ...}
    if group_collided:
        for bomb, beams in group_collided.items():
            for beam in beams:
                # 爆発エフェクト生成
                Explosion(
                    Beam.exp_images,
                    bomb.rect.center,
                    (Beam.EXP_IMAGE_WIDTH, Beam.EXP_IMAGE_HEIGHT),
                    Beam.EXP_IMAGE_OFFSET,
                    Beam.EXP_ANIME_COUNT,
                    Beam.exp_sound,
                )
        Beam.counter.val -= 1  # ビーム発射数を減らす

    # --- 魔女と爆弾の衝突判定 ---
    bomb_collided = pygame.sprite.spritecollide(
        majo, bomb_g, True
    )  # 魔女に当たった爆弾
    if bomb_collided:
        # 爆発エフェクト生成
        Explosion(
            Bomb.exp_images,
            majo.rect.center,
            (Bomb.EXP_IMAGE_WIDTH, Bomb.EXP_IMAGE_HEIGHT),
            Bomb.EXP_IMAGE_OFFSET,
            Bomb.EXP_ANIME_COUNT,
            Bomb.exp_sound,
        )
        Majo.life.val -= Majo.MINUS_LIFE  # ライフ減少
        Point(Majo.MINUS_LIFE, majo.rect.center)  # ライフ減少表示
        if Majo.life.val == 0:
            majo.kill()  # ライフ0で魔女消滅


def stop_all_sounds(opening_sound, play_sound):
    """全てのSoundインスタンスを停止する関数

    Args:
        opening_sound (_type_): オープニングBGM
        play_sound (_type_): プレイ中BGM
    """
    pygame.mixer.music.stop()
    opening_sound.stop()
    play_sound.stop()
    Beam.sound.stop()
    Beam.exp_sound.stop()
    Dragon.exp_sound.stop()
    Bomb.exp_sound.stop()
    pygame.mixer.stop()


# =============================
# メイン関数（ゲームのエントリーポイント）
# =============================
async def main():
    """
    ゲームの初期設定とメインループを管理する関数。
    画面初期化、スプライト登録、BGM設定、イベント処理、描画、衝突判定など全体の流れを制御。
    """
    # 画面の初期設定
    pygame.init()  # Pygameの初期化
    screen = pygame.display.set_mode(SCREEN.size)  # 画面サイズの設定
    pygame.display.set_caption("Animation")  # ウィンドウタイトルの設定

    # ゲームステータスの定数定義
    INIT, PLAY, CLEAR, GAMEOVER = 1, 2, 3, 4  # ゲーム状態の定数
    game_status = INIT  # ゲーム開始時は初期状態

    # 時間管理用クロックの作成
    clock = pygame.time.Clock()  # FPS制御用

    # Spriteグループの登録
    group = pygame.sprite.RenderUpdates()  # 描画更新用グループ
    bomb_g = pygame.sprite.Group()  # 爆弾グループ
    beam_g = pygame.sprite.Group()  # ビームグループ
    Majo.containers = group  # 魔女スプライトの所属グループ
    Beam.containers = group, beam_g  # ビームスプライトの所属グループ
    Dragon.containers = group  # ドラゴンスプライトの所属グループ
    Bomb.containers = group, bomb_g  # 爆弾スプライトの所属グループ
    Explosion.containers = group  # 爆発エフェクトの所属グループ
    Point.containers = group  # 得点表示の所属グループ
    Score.containers = group  # スコア表示の所属グループ
    TimerSprite.containers = group  # タイマーの所属グループ
    HPBarSprite.containers = group  # ドラゴンHPバーの所属グループ

    # 制限時間
    TIME_LIMIT = 60  # 制限時間（秒）
    # time_left = TIME_LIMIT  # 残り時間
    # time_font = pygame.font.SysFont(None, 32)  # 残り時間表示用フォント
    timer_sprite = TimerSprite(TIME_LIMIT, pos=(SCREEN.left + 10, 10))

    # 各種画像・サウンドの読み込みと設定
    Beam.sound = load_sound("se_maoudamashii_se_ignition01.ogg")  # ビーム発射音
    Beam.sound.set_volume(0.03)  # ビーム発射音の音量調整（0.0～1.0）
    # Beam.image = load_image("majo_beam_right.png")  # ビーム画像
    Beam.images = {
        (1, 0): load_image("majo_beam_right.png"),
        (-1, 0): load_image("majo_beam_left.png"),
        (0, -1): load_image("majo_beam_up.png"),
        (0, 1): load_image("majo_beam_down.png"),
    }
    # Dragon.images = load_image("dragon_small.png", (128, 128))  # UFO画像
    Dragon.exp_images = load_image("ufo_fire.png", (320, 960))  # UFO爆発画像
    Dragon.exp_sound = load_sound("se_maoudamashii_explosion08.ogg")  # UFO爆発音
    Dragon.exp_sound.set_volume(0.03)  # UFO爆発音の音量調整（0.0～1.0）
    # Bomb.images = load_image("ufo_bomb_left.png")  # 爆弾画像
    Bomb.exp_images = load_image("bomb_fire.png")  # 爆弾爆発画像
    Bomb.exp_sound = load_sound("se_maoudamashii_explosion05.ogg")  # 爆弾爆発音
    Bomb.exp_sound.set_volume(0.03)  # 爆弾爆発音の音量調整（0.0～1.0）
    Beam.exp_images = load_image("beam_fire.png")  # ビーム爆発画像
    Beam.exp_sound = load_sound("se_maoudamashii_explosion04.ogg")  # ビーム爆発音
    Beam.exp_sound.set_volume(0.03)  # ビーム爆発音の音量調整（0.0～1.0）

    # # タイトル・ゲームオーバー・クリア画面用画像の辞書
    # title_msg = {
    #     INIT: load_image("opening-logo.png"),  # タイトル画像
    #     GAMEOVER: load_image("gameover.png"),  # ゲームオーバー画像
    #     CLEAR: load_image("gameclear.png"),  # クリア画像
    # }
    title_msg = load_image("opening-logo.png")  # タイトル画像
    opening_sound = load_sound("bgm_maoudamashii_healing08.ogg")  # タイトルBGM
    opening_sound.set_volume(0.03)  # 音量調整
    opening_sound.play(-1)  # ループ再生
    play_sound = load_sound("bgm_maoudamashii_fantasy15.ogg")  # プレイ中BGM
    play_sound.set_volume(0.03)  # 音量調整
    gameclear_sound = load_sound("clear.ogg")
    # gameclear_sound.set_volume(0.03)  # クリア音の音量調整
    gameover_sound = load_sound("gameover.ogg")
    # gameover_sound.set_volume(0.15)  # ゲームオーバー

    # スコア・ライフなどの初期化
    Majo.life = Score(
        initval=3,  # 初期ライフ
        maxval=3,  # 最大ライフ
        pos=(SCREEN.right - 165, 5),  # 表示位置
        color=Score.RED,  # 色
        font="ipaexg.ttf",  # フォント
        form="Player HP: #",  # 表示フォーマット
        pat="●○",  # ライフ表示パターン
    )

    Beam.counter = Counter(initval=0, maxval=2)  # ビーム発射回数カウンタ

    # 魔女・背景のインスタンス生成
    majo = Majo()  # 魔女キャラクター生成
    bg_img = Background(majo)  # 背景生成（魔女の参照渡し）
    dragon = None  # ドラゴンはゲーム開始時に生成するため、初期値はNone

    start_ticks = pygame.time.get_ticks()  # ゲーム開始時の時刻（ミリ秒）

    BEAM_COOLDOWN = 300  # 発射間隔（ミリ秒）
    BEAM_BURST_LIMIT = 2  # 連続発射数
    BEAM_BURST_COOLDOWN = 1000  # 2発撃った後のクールタイム（ミリ秒）

    last_beam_time = 0  # 直近の発射時刻
    burst_count = 0
    burst_cooldown_start = 0

    while True:
        # 画面を白でクリア
        screen.fill((255, 255, 255))  # 背景色を白に設定

        # 背景・スプライトの位置情報を更新
        # bg_img.update()  # 背景の更新
        group.update()  # 全スプライトの更新

        # 衝突判定（ゲームプレイ中かつドラゴンが存在する場合のみ）
        if game_status == PLAY and dragon is not None:
            collision_detection(majo, dragon, beam_g, bomb_g)  # 衝突判定処理

        # 背景・スプライトを画面に描画
        bg_img.draw(screen)  # 背景描画
        group.draw(screen)  # スプライト描画

        # # 敵のHPバー描画（ドラゴンがいる場合のみ）
        # if dragon and game_status == PLAY:
        #     draw_hp_bar(screen, dragon, pos=(SCREEN.centerx - 100, 8))

        # 制限時間の計算と表示
        if game_status == PLAY:
            elapsed_sec = (pygame.time.get_ticks() - start_ticks) // 1000  # 経過秒数
            time_left = max(0, TIME_LIMIT - elapsed_sec)  # 残り時間
            # 残り時間を画面左上に表示
            # timer_img = time_font.render(f"TIME: {time_left}", True, (0, 0, 0))
            # screen.blit(timer_img, (SCREEN.left + 10, 10))
            timer_sprite.val = time_left  # 残り秒数を更新

            # # 時間切れでゲームオーバー
            # if time_left == 0:
            #     game_status = GAMEOVER
            #     play_sound.stop()
            #     # opening_sound.play(-1)
            #     gameover_sound.play()  # ゲームオーバー音再生

        # クリア時はスコアを表示
        if game_status == CLEAR:
            font = pygame.font.Font("font/Bungee-Regular.ttf", 60)  # フォント設定
            game_msg = font.render("GAME CLEAR!", True, (255, 0, 0))
            screen.blit(game_msg, (SCREEN.centerx - 200, SCREEN.centery - 100))
            calculate_score_and_rank(
                screen, time_left, Majo.life.val, pygame.font.SysFont(None, 48)
            )
            rq_font = pygame.font.SysFont(None, 48)
            text1 = rq_font.render("Restart (R) / Exit Game (Q)", True, (0, 0, 0))
            screen.blit(text1, (SCREEN.centerx - 200, SCREEN.centery + 100))
        elif game_status == GAMEOVER:
            font = pygame.font.Font("font/Bungee-Regular.ttf", 60)  # フォント設定
            game_msg = font.render("GAME OVER", True, (0, 0, 255))
            screen.blit(game_msg, (SCREEN.centerx - 180, SCREEN.centery - 100))
            # # ゲームオーバー時はスコアを表示
            # calculate_score_and_rank(
            #     screen, time_left, Majo.life.val, pygame.font.SysFont(None, 48)
            # )
            rq_font = pygame.font.SysFont(None, 48)
            text1 = rq_font.render("Restart (R) / Exit Game (Q)", True, (0, 0, 0))
            screen.blit(text1, (SCREEN.centerx - 200, SCREEN.centery))

        # タイトル時はメッセージ画像を表示
        elif game_status == INIT:
            screen.blit(title_msg, (100, 150))  # メッセージ画像描画

        # 画面の内容を更新（ダブルバッファリング）
        pygame.display.update()  # 画面更新

        # ゲームステータスの変更判定
        # 魔女のライフが0か、時間切れになったらゲームオーバー
        if game_status == PLAY and (Majo.life.val == 0 or time_left == 0):
            game_status = GAMEOVER  # ゲームオーバー状態へ
            play_sound.stop()  # プレイBGM停止
            # opening_sound.play(-1)  # タイトルBGM再生
            gameover_sound.play()  # ゲームオーバー音再生
        # ドラゴンスコアが0になったらクリア
        if game_status == PLAY and dragon.hp == 0:
            game_status = CLEAR  # クリア状態へ
            play_sound.stop()  # プレイBGM停止
            # opening_sound.play(-1)  # タイトルBGM再生
            gameclear_sound.play()  # クリア音再生

        # イベント処理（キー入力・ウィンドウ操作など）
        for event in pygame.event.get():
            if event.type == QUIT:
                # pygame.mixer.music.stop()
                stop_all_sounds(opening_sound, play_sound)
                pygame.quit()  # Pygame終了
                await asyncio.sleep(0.1)  # 0.1秒待つ（音停止の反映待ち
                # sys.exit()  # プログラム終了
                # js.eval("window.close()")
            elif event.type == KEYDOWN:

                # # プレイ中にスペースキーでビーム発射
                # if event.key == K_SPACE and game_status == PLAY:
                #     if Beam.counter.val < Beam.counter.maxval and (fire_dx != 0 or fire_dy != 0):
                #         Beam(majo, fire_dx, fire_dy)
                # タイトル画面でスペースキーでゲーム開始
                if event.key == K_SPACE and game_status == INIT:
                    game_status = PLAY  # プレイ状態へ
                    dragon = Dragon()  # ドラゴン生成
                    # ドラゴンのHPバー用スプライト
                    hp_bar_sprite = HPBarSprite(dragon)
                    hp_bar_sprite.update()
                    opening_sound.stop()  # タイトルBGM停止
                    play_sound.play(-1)  # プレイBGM再生
                    start_ticks = pygame.time.get_ticks()  # タイマーリセット
                # ゲームクリア・ゲームオーバー画面でRキーでリトライ
                elif event.key == K_r and game_status in (GAMEOVER, CLEAR):
                    game_status = PLAY  # プレイ状態へ
                    dragon.kill()  # 既存ドラゴン削除
                    majo.kill()  # 既存魔女削除
                    hp_bar_sprite.kill()  # 既存HPバー削除
                    dragon = Dragon()  # 新ドラゴン生成
                    hp_bar_sprite = HPBarSprite(dragon)
                    hp_bar_sprite.update()  # HPバー更新
                    majo = Majo()  # 新魔女生成
                    Majo.life.reset()  # ライフリセット
                    # opening_sound.stop()  # タイトルBGM停止
                    gameclear_sound.stop()  # クリア音停止
                    gameover_sound.stop()  # ゲームオーバー音停止
                    play_sound.play(-1)  # プレイBGM再生
                    bg_img = Background(majo)  # 背景再生成
                    start_ticks = pygame.time.get_ticks()  # タイマーリセット
                # ゲームオーバー・クリア画面でQキーでゲーム終了
                elif event.key == K_q and game_status in (GAMEOVER, CLEAR):
                    # pygame.mixer.music.stop()
                    stop_all_sounds(opening_sound, play_sound)
                    pygame.quit()  # Pygame終了
                    await asyncio.sleep(0.1)  # 0.1秒待つ（音停止の反映待ち）
                    # sys.exit()  # プログラム終了
                    # タブを閉じる
                    # js.eval("window.onbeforeunload = null")
                    js.eval("window.close()")
                    # または前のページに戻る
                    js.eval("window.history.back()")
        # 障害物リスト
        obstacles = [dragon]  # [dragon, enemy1, enemy2, wall1, ...]

        # 発射方向の決定
        fire_dx, fire_dy = 0, 0

        now = pygame.time.get_ticks()  # 現在時刻（ミリ秒）

        # クールタイム中かどうか判定
        in_burst_cooldown = (
            burst_cooldown_start > 0
            and now - burst_cooldown_start < BEAM_BURST_COOLDOWN
        )
        if in_burst_cooldown and (now - burst_cooldown_start >= BEAM_BURST_COOLDOWN):
            # クールタイム終了
            burst_count = 0
            burst_cooldown_start = 0

        # キー入力による魔女の移動処理
        pressed_keys = pygame.key.get_pressed()  # 押されているキー取得
        if pressed_keys[K_DOWN]:  # 下キー
            majo.move_down(obstacles)  # 魔女を下に移動
        elif pressed_keys[K_UP]:  # 上キー
            majo.move_up(obstacles)  # 魔女を上に移動
        elif pressed_keys[K_LEFT]:
            majo.move_left(obstacles)
        elif pressed_keys[K_RIGHT]:
            majo.move_right(obstacles)

        # WASDで発射方向を決定
        if pressed_keys[K_w]:
            fire_dx, fire_dy = 0, -1
        elif pressed_keys[K_s]:
            fire_dx, fire_dy = 0, 1
        elif pressed_keys[K_a]:
            fire_dx, fire_dy = -1, 0
        elif pressed_keys[K_d]:
            fire_dx, fire_dy = 1, 0
        # スペースキーでビーム発射
        if (
            pressed_keys[K_SPACE]
            and game_status == PLAY
            and Beam.counter.val < Beam.counter.maxval
            and (fire_dx != 0 or fire_dy != 0)
            and not in_burst_cooldown
            and now - last_beam_time > BEAM_COOLDOWN
        ):
            Beam(majo, fire_dx, fire_dy)
            last_beam_time = now
            burst_count += 1

            if burst_count >= BEAM_BURST_LIMIT:
                burst_cooldown_start = now  # クールタイム開始
                burst_count = 0

        # FPS制御（描画スピード調整）
        clock.tick(60)  # 60FPSでループ
        await asyncio.sleep(0)  # 非同期処理のためのスリープ


if __name__ == "__main__":
    # エントリーポイント：main関数を非同期で実行
    asyncio.run(main())
