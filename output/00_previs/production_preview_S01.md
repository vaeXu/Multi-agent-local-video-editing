# 单镜试片 · 生产预览与确认记录

- 范围：**仅 S01**，其余 11 镜不生成（零积分）
- 源任务：`JOB-C69345C8` / 全量指纹 `c69345c89071`
- 单镜指纹：`f35d6c95d7df06a5611250994827919c72b7e3200a3c60b73687c9711214ea21`
- 预计积分：**50–100**；预计耗时 1–3 分钟
- 用户确认：先试 1 镜看效果（2026-11-12 20:1x 明确选择）

## 调用参数

- image：`/Users/xujiahua/WorkBuddy/视频剪辑/shixiang-agent/output/03_frames/S01.png`（冻结起始帧）
- reference_images：`/Users/xujiahua/WorkBuddy/视频剪辑/shixiang-agent/output/02_characters/character_sheets/1_林昭.png`、`/Users/xujiahua/WorkBuddy/视频剪辑/shixiang-agent/output/02_characters/character_sheets/2_苏晴.png`
- seconds：`6` · aspect_ratio：`9:16` · enable_audio：`false`
- 输出：`/Users/xujiahua/WorkBuddy/视频剪辑/shixiang-agent/input/demo/generated_video/S01.mp4`（生成后按镜号重命名）

## 可复制提示词

> 9:16 竖屏国产悬疑冷调半写实厚涂漫画，平涂色块、清晰描线、细网点，低饱和青灰。冷白 LED 会议室，右侧落地窗阴天漫射侧光，深色胡桃木长桌。过肩近景，机位在苏晴左肩后约一米、略俯 10 度，缓慢推近 6%，低动态不晃动。起点：苏晴（齐肩栗棕内扣发、右耳单只珍珠耳钉、米白西装、左手食指素圈银戒）右手把一张 A4 签字页平拍在长桌上，食指压住签名。唯一动作：指尖压住纸面不动，纸角被气流微微掀起，她抬起视线直逼对面。终点：纸静止、视线锁定对面。景深浅、背景虚化白墙与投影幕。画面内不出现任何文字、字幕、水印、logo；不改发型服装、不加多余手指、不出现第二张正脸张嘴、不越轴、不剧烈晃动。

## 四步门

prepare → 本预览 → 用户明确确认 → run（调用 VideoGen）
