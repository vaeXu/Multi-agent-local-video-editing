# 《代签》EP01 · 红果短剧验收报告

- 生成时间：2026-11-12T20:21:29+08:00
- 成片：`output/06_final/EP01.mp4`
- 综合状态：**WARN**，符合度 **75/100**
- 规则合计 32 条：通过 16 / 需人工核验 16 / 不通过 0（blocker 不通过 0）

> 说明：标 `warn` 的项目多为画面级、法律效力级判定（如画风一致性、参考图授权、AIGC 隐式标识），机器无法替代人工结论，因此**不写死通过**，逐条列出人工核验方式。打开 `console/index.html` 可边看边勾。

## 逐条验收结果

| 规则 | 类别 | 级别 | 状态 | 期望 | 实测 | 证据 |
|---|---|---|---|---|---|---|
| HG-TECH-01 竖屏 9:16 分辨率 1080×1920 | 技术规格 | blocker | pass | 1080x1920（宽×高，9:16 竖屏） | 1080x1920（期望 1080x1920） | `output/06_final/EP01.mp4` |
| HG-TECH-02 视频编码 H.264/AVC | 技术规格 | blocker | pass | h264 | 视频编码=h264 | `output/06_final/EP01.mp4` |
| HG-TECH-03 帧率 25 或 30fps（不低于 25） | 技术规格 | major | pass | 25 或 30 fps（>=25） | 帧率=30 fps | `output/06_final/EP01.mp4` |
| HG-TECH-04 视频码率不低于 4Mbps（建议 8~12Mbps） | 技术规格 | major | pass | >=4000 kb/s（建议 8000~12000 kb/s） | 码率=9180 kb/s（下限 4000） | `output/06_final/EP01.mp4` |
| HG-TECH-05 容器格式 MP4 | 技术规格 | blocker | pass | mp4 | 容器=mp4 | `output/06_final/EP01.mp4` |
| HG-TECH-06 单集时长 60~120s（上传口径 1~5 分钟） | 技术规格 | major | pass | 60~120 s（平台上传口径 60~300 s） | 时长=73.00 s（期望 60~120s，上传口径 60~300s）；落在 60~120s 为佳区间 | `output/06_final/EP01.mp4` |
| HG-TECH-07 无 alpha 通道 | 技术规格 | major | pass | 无 alpha（像素格式如 yuv420p） | 像素格式=yuv420p；无 alpha 通道 | `output/06_final/EP01.mp4` |
| HG-TECH-08 分辨率宽高均为偶数（非奇数） | 技术规格 | major | pass | width/height 均为偶数 | 1080x1920（均为偶数） | `output/06_final/EP01.mp4` |
| HG-TECH-09 音频编码 AAC | 技术规格 | major | pass | aac | 音频编码=aac | `output/06_final/EP01.mp4` |
| HG-TECH-10 音频采样率 44100Hz | 技术规格 | major | pass | 44100 Hz | 采样率=44100 Hz | `output/06_final/EP01.mp4` |
| HG-TECH-11 音频双声道（stereo） | 技术规格 | major | pass | 2 声道 / stereo | 声道数=2（stereo） | `output/06_final/EP01.mp4` |
| HG-TECH-12 连载首次投稿 ≥3 集（总时长门槛待核） | 技术规格 | minor | warn | 连载作品首次上传 >=3 集 | 需人工核验：登录短剧创作者中心核对本批次投稿集数；「总时长>20分钟」仅见第三方实操文，须向对接商务或后台当前提示核实 | `output/06_final/EP01.mp4` |
| HG-CONT-01 每集明显位置添加 AI 提示标识（含片头「AI辅助制作」） | 内容合规 | blocker | warn | 每集片头/明显位置可见 AI 提示标识；片头、封面、简介同步标注；文件元数据含隐式 AIGC 标识 | 需人工核验：每集片头/明显位置的可见 AI 提示标识、封面与简介同步标注、文件元数据隐式 AIGC 标识是否齐全且未被隐藏；本地文本线索命中 4 处：output/07_reports/compliance_report.md(AI 辅助制作)；output/07_reports/creation_chain.md(AI 辅助制作)；output/07_reports/originality_declaration.md(AIGC)；o | `output/06_final/EP01.mp4` |
| HG-CONT-02 不含《微短剧发展管理办法》第二十五条禁止内容 | 内容合规 | blocker | warn | 无第二十五条 11 项禁止内容：邪教迷信、拜金主义、淫秽赌博吸毒、渲染暴力恐怖/教唆犯罪、危害未成年人、侮辱诽谤散布隐私 | 需人工核验：人工通读 script.md 与 storyboard.json 的全部台词、画面描述、剧名，逐项对照第二十五条 11 款；本地无语义审核能力 | `input/demo/storyboard.json` |
| HG-CONT-03 受限题材自查（仅作风险提示，非平台硬规） | 内容合规 | major | warn | 规避灵异迷信/猎奇/超自然金手指/以暴制暴/畸形婚恋等方向（风险自查项） | 需人工核验：人工核对题材方向。★该「3类禁拍13类受限」清单已被红果官方明确否认发布，绝不可当作官方硬规引用；只按 [官1]§25 与广电专项治理方向做风险自查 | `input/demo/storyboard.json` |
| HG-CONT-04 角色身份锚点 ≥3 条（跨镜五官一致的数据基础） | 内容合规 | major | pass | 每个角色 identity_anchors >= 3 条 | 2 个角色 / 共 8 条锚点；每角色均 >=3 条 | `input/demo/characters.json` |
| HG-CONT-05 跨剧/跨角色不复用高度近似 AI 脸 | 内容合规 | major | warn | 不与平台已有剧集角色面部高度相似；同剧各角色形象有清晰区分度 | 需人工核验：人工用平台人脸相似度预检工具做跨剧比对，并逐帧比对本地角色主视觉；本地无跨剧人脸库，无法自动判定 | `input/demo/storyboard.json` |
| HG-CONT-06 全剧画风统一 | 内容合规 | major | warn | 全剧统一 style.name / prompt_prefix，镜头无风格漂移 | 需人工核验：全剧画风/线条/色温一致性与五官稳定性；数据层：style.name=写实国漫 · 都市冷调电影感，prompt_prefix=已配置，negative_prompt=已配置，帧 12 / 镜 12 | `input/demo/storyboard.json` |
| HG-CONT-07 单句台词 ≤24 字 | 内容合规 | minor | pass | 每个 shot 的 dialogue.text 长度 <= 24 字 | 检查 12 条非空台词（<=24 字）；全部合规 | `input/demo/storyboard.json` |
| HG-CONT-08 片头信息标注（剧名/许可证号/批准文件编号/节目编号） | 内容合规 | major | warn | 片头明显位置标注剧名，并按剧目类别标注许可证号/批准文件编号/节目编号 | 需人工核验：人工查看每集片头；三类剧须有平台节目编号，一/二类须有发行许可证号或批准文件编号；投资额≥30万或特殊题材须先走广电备案 | `input/demo/storyboard.json` |
| HG-CONT-09 整集镜头数 ≥8 | 内容合规 | minor | pass | storyboard.shots 数量 >= 8 且 shot id 唯一、形如 S\d{2} | 镜头数=12（>=8）；id 唯一=True；id 符合 S\d{2}=True | `input/demo/storyboard.json` |
| HG-CONT-10 单镜时长 3~8s | 内容合规 | minor | pass | 每个 shot 的 duration_s 在 3~8 之间 | 共 12 镜；全部在 3~8s | `input/demo/storyboard.json` |
| HG-RIGHT-01 创作链路归档完整（剧本/分镜/角色卡/参数/报告） | 版权留痕 | major | pass | output/01_script/script.md、output/01_script/storyboard.json、 | 5/5 项归档文件齐备（output/01_script/script.md, output/01_script/storyboard.json, output/02_characters/characters.json, config/project.json, output/07_reports/compliance_report.md）；内容完整性按 how_to_verify 人工核验 | `output/` |
| HG-RIGHT-02 剪辑工程文件截图（创作链路截图） | 版权留痕 | major | warn | ≥4 张不同段落的工程文件截图，含短剧画面、合理分轨与剪辑点，可见项目名 | 需人工核验：人工打开截图文件夹，核对连续时间段、项目名可见、未打码、≥4 张且与成片对应 | `output/07_reports/` |
| HG-RIGHT-03 不侵权承诺函 / 原创声明 | 版权留痕 | blocker | warn | 按平台最新模板填写并签署《不侵权承诺函》/原创声明，拍照上传后台 | 需人工核验：人工核对承诺函为后台最新模板版本、签署主体与账号认证一致、已拍照上传；法律效力无法自动判定 | `output/07_reports/` |
| HG-RIGHT-04 参考图 / 角色肖像 / 字体音效授权状态可追溯 | 版权留痕 | major | warn | characters.json 的 reference_images 与所用素材均有授权状态记录；AI 工具商用授权条款 | 需人工核验：人工逐项核对参考图、真人肖像、字体、音效、配音模型、AI 工具的授权凭证与商用范围；授权状态需写入 characters.json 与授权台账 | `output/07_reports/` |
| HG-RIGHT-05 AI 隐式标识 / 元数据溯源留痕 | 版权留痕 | major | warn | 成片文件元数据含 AIGC 隐式标识（生成服务/传播平台/唯一编号），且未被删除篡改 | 需人工核验：人工用平台/专门工具读取文件元数据中的 AIGC 字段；ffmpeg -i 不展示自定义元数据，本检查器无法自动判定 | `output/07_reports/` |
| HG-AV-01 内嵌烧录字幕（白字黑描边） | 音画质量 | major | warn | 字幕烧录进画面（非外挂软字幕），白字黑描边、字体清晰可读 | 需人工核验：字幕是否烧录进画面、白字黑描边、字体清晰且不遮挡人脸；数据层：12/12 镜头有字幕文本；未检出独立软字幕流 | `output/06_final/EP01.mp4` |
| HG-AV-02 无第三方水印 / AI 工具水印，且 AI 标识不得刻意隐藏 | 音画质量 | blocker | warn | 画面无水印；不得用颜色/透明度/边缘裁剪隐藏 AI 标识 | 需人工核验：人工全片逐段查看四角与边缘，确认无工具/平台水印、无遮挡式隐藏标识；水印无法从流信息自动判定 | `output/06_final/EP01.mp4` |
| HG-AV-03 无黑边 / 无拉伸变形 | 音画质量 | major | warn | 画面满屏 9:16，无上下/左右黑边，人物无拉伸变形 | 需人工核验：人工播放确认画面铺满、无黑边；并核对 03_frames 合成时 scale/pad 参数与 1080×1920 一致 | `output/06_final/EP01.mp4` |
| HG-AV-04 音画同步 / 口型同步 | 音画质量 | major | warn | 配音、音效、字幕与画面时间轴对齐，口型基本吻合，非全程怼脸单一特写 | 需人工核验：人工全片播放核对音画与口型、景别分布；本地无自动音画/口型比对能力 | `output/06_final/EP01.mp4` |
| HG-AV-05 封面规格（比例 + 描边剧名） | 音画质量 | major | warn | 封面 3:4（建议 1200×1600，1~5MB）或按投稿入口要求 350×500；带描边剧名、无拉伸（两来源口径不一 | 需人工核验：封面描边剧名、无拉伸变形、比例符合后台当前口径（版权中台 3:4 建议 1200×1600；另有 350×500 实操口径，二者不一致）；实测 1200x1600（约 3:4），1.00 MB | `output/06_final/cover.png` |

## 需人工核验项与核验方式

### HG-TECH-12 连载首次投稿 ≥3 集（总时长门槛待核）
- 依据：[平台合作口径][官5] 抖音集团短剧版权中台《成品漫剧业务介绍及合作指引》连载作品首次上传至少≥3集 | http://mp.weixin.qq.com/s?__biz=MzkxMTQ5MjkzMA==&mid=2247496815&idx=4&sn=21039388f1dad31de03064f18a458895；[存疑·非官方][实1] 称 2026-06 起总时长>20分钟、保底精品总时长≥120分钟系不同模式口径，未见官方统一确认 | https://www.runmie.com/44742.html
- 核验方式：登录短剧创作者中心核对本批次投稿集数；「总时长>20分钟」仅见第三方实操文，须向对接商务或后台当前提示核实
- 实测线索：需人工核验：登录短剧创作者中心核对本批次投稿集数；「总时长>20分钟」仅见第三方实操文，须向对接商务或后台当前提示核实
- 不合规时：补齐至少 3 集成片再提交；总时长门槛以平台后台当前口径为准，勿按网传数字硬凑

### HG-CONT-01 每集明显位置添加 AI 提示标识（含片头「AI辅助制作」）
- 依据：[硬规-法规][官1] 广电总局令第16号《微短剧发展管理办法》第三十四条：每集明显位置添加提示标识 | https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html；[官2]《人工智能生成合成内容标识办法》显式+隐式标识 | https://www.cac.gov.cn/2025-03/14/c_1743654685899683.htm；[平台执行·媒体报道][实9] 红果 2026-08-03 起要求每集片头标注「AI辅助制作」| https://www.toutiao.com/a7701912782408614440；[权1] 人民网 苔花统一标识 | https://sc.people.com.cn/n2/2026/0903/c345167-41685601.html
- 核验方式：逐集播放片头 3 秒确认可见「AI辅助制作」/苔花标识；核对封面与简介同步标注；用专门工具读取文件元数据 AIGC 隐式标识。注意法规原文为「每集明显位置」，非仅片头一次
- 实测线索：需人工核验：每集片头/明显位置的可见 AI 提示标识、封面与简介同步标注、文件元数据隐式 AIGC 标识是否齐全且未被隐藏；本地文本线索命中 4 处：output/07_reports/compliance_report.md(AI 辅助制作)；output/07_reports/creation_chain.md(AI 辅助制作)；output/07_reports/originality_declaration.md(AIGC)；output/06_final/ai_label_notice.txt(AI 辅助制作)。ffmpeg -i 无法读取画面文字与自定义元数据
- 不合规时：在 06_final 片头叠加 AI 标识字幕层（每集都加，不得用透明度/边缘裁剪隐藏），并保留导出元数据，重跑导出

### HG-CONT-02 不含《微短剧发展管理办法》第二十五条禁止内容
- 依据：[硬规-法规][官1] 国家广播电视总局令第16号 第二十五条（全文 11 款）| https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html
- 核验方式：人工通读 script.md 与 storyboard.json 的全部台词、画面描述、剧名，逐项对照第二十五条 11 款；本地无语义审核能力
- 实测线索：需人工核验：人工通读 script.md 与 storyboard.json 的全部台词、画面描述、剧名，逐项对照第二十五条 11 款；本地无语义审核能力
- 不合规时：删除/改写命中条款的桥段与台词，从 01_script 起重跑受影响环节

### HG-CONT-03 受限题材自查（仅作风险提示，非平台硬规）
- 依据：[存疑·非官方][权6] 环球网科技《红果3类短剧禁拍13类受限》| https://new.qq.com/rain/a/20260606A031QE00；★[官方辟谣][权5] 新京报/腾讯网《红果短剧回应：从未发布过类似审核标准》(2026-06-06) | https://new.qq.com/rain/a/20260606A082OE00；[监管方向][权4] 广电总局 2026-06-01 专项治理 8 类重点问题 | https://www.zhitongcaijing.com/content/detail/1522062.html；[实3] 夜雨聆风备案避坑指南 | https://e.yeyulingfeng.com/a/478803.html
- 核验方式：人工核对题材方向。★该「3类禁拍13类受限」清单已被红果官方明确否认发布，绝不可当作官方硬规引用；只按 [官1]§25 与广电专项治理方向做风险自查
- 实测线索：需人工核验：人工核对题材方向。★该「3类禁拍13类受限」清单已被红果官方明确否认发布，绝不可当作官方硬规引用；只按 [官1]§25 与广电专项治理方向做风险自查
- 不合规时：若命中高危方向，把超自然能力改为可解释的专业本领、以暴制暴改为交由公安依法处置，重跑 01_script

### HG-CONT-05 跨剧/跨角色不复用高度近似 AI 脸
- 依据：[平台公告][官6] 南方+ 红果治理「高频AI脸」| https://www.nfnews.com/content/voAp8L5Y6R.html；[官7] 中国新闻出版广电报 2026-10-27 公告「多人同脸」「跨剧撞脸」| https://epaper.chinaxwcb.com/epaper/2026-11/04/content_99886689.html；[权2] 澎湃新闻 | https://m.thepaper.cn/newsDetail_forward_34388675；[权3] 百度百科 AI短剧词条（2026-08 公告）| https://baike.baidu.com/item/AI微短剧/67248821；[实9] 平台人脸相似度比对系统 | https://www.toutiao.com/a7701912782408614440
- 核验方式：人工用平台人脸相似度预检工具做跨剧比对，并逐帧比对本地角色主视觉；本地无跨剧人脸库，无法自动判定
- 实测线索：需人工核验：人工用平台人脸相似度预检工具做跨剧比对，并逐帧比对本地角色主视觉；本地无跨剧人脸库，无法自动判定
- 不合规时：为每个角色单独调参渲染，建立差异化「视觉指纹」（骨相五官+服饰造型），重跑 02_characters/03_frames

### HG-CONT-06 全剧画风统一
- 依据：[平台执行·行业整理][实10] 红果公告要求全剧画风统一 | https://www.toutiao.com/a7706135472770155050；[官7] 中国新闻出版广电报：治理剧情结构/视听表达要素同质化与低质 | https://epaper.chinaxwcb.com/epaper/2026-11/04/content_99886689.html；[项目契约] SPEC §2.1/§6
- 核验方式：人工连续播放全片检查画风、色温、线条风格是否一致；并核对所有镜头共用同一 prompt_prefix 与 negative_prompt（本项仅自动校验配置与帧齐备性）
- 实测线索：需人工核验：全剧画风/线条/色温一致性与五官稳定性；数据层：style.name=写实国漫 · 都市冷调电影感，prompt_prefix=已配置，negative_prompt=已配置，帧 12 / 镜 12
- 不合规时：统一 style.prompt_prefix / negative_prompt，剔除风格异常镜头后重跑 03_frames

### HG-CONT-08 片头信息标注（剧名/许可证号/批准文件编号/节目编号）
- 依据：[硬规-法规][官1]《微短剧发展管理办法》第二十七条（片头明显位置标注剧名、许可证号、批准文件编号、节目编号）、第十七条/第三十三条（三类由平台审核并标注节目编号）| https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html；[权1] 人民网 微短剧统一标识与备案号 | https://sc.people.com.cn/n2/2026/0903/c345167-41685601.html
- 核验方式：人工查看每集片头；三类剧须有平台节目编号，一/二类须有发行许可证号或批准文件编号；投资额≥30万或特殊题材须先走广电备案
- 实测线索：需人工核验：人工查看每集片头；三类剧须有平台节目编号，一/二类须有发行许可证号或批准文件编号；投资额≥30万或特殊题材须先走广电备案
- 不合规时：在片头模板加入剧名与编号占位，取得编号后回填，重跑 06_final；编号未取得前不得上架

### HG-RIGHT-02 剪辑工程文件截图（创作链路截图）
- 依据：[平台要求][实4] 引《短剧版权证明文件提交指南》：至少 4 张不同段落展示图片，含短剧画面及合理分轨和剪辑点 | http://mp.weixin.qq.com/s?__biz=Mzk0NTYwNTAyMg==&mid=2247492686&idx=1&sn=7a9058ee9cfbdf7df752522146bf64da；[实5] 2026-06-12 起工程文件截图为多渠道分发必要条件 | https://duanju007.com/?p=27372；[实1] 剧本创作记录/剪映工程/即梦或 Liblib 生成截图 | https://www.runmie.com/44742.html
- 核验方式：人工打开截图文件夹，核对连续时间段、项目名可见、未打码、≥4 张且与成片对应
- 实测线索：需人工核验：人工打开截图文件夹，核对连续时间段、项目名可见、未打码、≥4 张且与成片对应
- 不合规时：在剪辑软件中拉动时间轴连续截图，归入 output/07_reports/ 后随片重新提交

### HG-RIGHT-03 不侵权承诺函 / 原创声明
- 依据：[平台要求][实4] 平台给模板，必填必拍照上传，签后对版权负责 | http://mp.weixin.qq.com/s?__biz=Mzk0NTYwNTAyMg==&mid=2247492686&idx=1&sn=7a9058ee9cfbdf7df752522146bf64da；[实2] 上传版权证明文件：创作链路截图、不侵权承诺函 | https://e.yeyulingfeng.com/a/481272.html；[实5] 2026-06-12 更新《承诺函》模板 | https://duanju007.com/?p=27372；[实3] 原创声明函/AI 工具商用授权 | https://e.yeyulingfeng.com/a/478803.html
- 核验方式：人工核对承诺函为后台最新模板版本、签署主体与账号认证一致、已拍照上传；法律效力无法自动判定
- 实测线索：需人工核验：人工核对承诺函为后台最新模板版本、签署主体与账号认证一致、已拍照上传；法律效力无法自动判定
- 不合规时：从创作者中心后台下载最新模板，填写签署后重新上传

### HG-RIGHT-04 参考图 / 角色肖像 / 字体音效授权状态可追溯
- 依据：[平台要求][实4] AI 生成需提供平台用户协议版权归属条款截图，改编须有正式授权 | http://mp.weixin.qq.com/s?__biz=Mzk0NTYwNTAyMg==&mid=2247492686&idx=1&sn=7a9058ee9cfbdf7df752522146bf64da；[官5] 非取得合法授权严禁蹭 IP 名称、版权归属清晰 | http://mp.weixin.qq.com/s?__biz=MzkxMTQ5MjkzMA==&mid=2247496815&idx=4&sn=21039388f1dad31de03064f18a458895；[权3] 2026-09-02「融像」「融声」座谈会：须取得权利人明确授权 | https://baike.baidu.com/item/AI微短剧/67248821；[实8] 五证合一（角色肖像模型合规来源证明、全商业字体音效授权）| https://www.tahou.com/article/221745076397698053
- 核验方式：人工逐项核对参考图、真人肖像、字体、音效、配音模型、AI 工具的授权凭证与商用范围；授权状态需写入 characters.json 与授权台账
- 实测线索：需人工核验：人工逐项核对参考图、真人肖像、字体、音效、配音模型、AI 工具的授权凭证与商用范围；授权状态需写入 characters.json 与授权台账
- 不合规时：补齐授权凭证，把授权状态写入 characters.json 并在 output/07_reports/ 建立授权台账

### HG-RIGHT-05 AI 隐式标识 / 元数据溯源留痕
- 依据：[硬规-法规][官2]《人工智能生成合成内容标识办法》：文件元数据添加隐式标识、不得恶意删除篡改隐匿 | https://www.cac.gov.cn/2025-03/14/c_1743654685899683.htm；[官3] 中国政府网解读 | https://www.gov.cn/zhengce/202503/content_7014281.htm；[官1] 第16号令第三十四条 | https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html；[实12] 中国经济网 元数据字段名含 AIGC 标识符号 | https://www.ce.cn/cysc//newmain/yc/jsxw/202510/t20251024_2535313.shtml
- 核验方式：人工用平台/专门工具读取文件元数据中的 AIGC 字段；ffmpeg -i 不展示自定义元数据，本检查器无法自动判定
- 实测线索：需人工核验：人工用平台/专门工具读取文件元数据中的 AIGC 字段；ffmpeg -i 不展示自定义元数据，本检查器无法自动判定
- 不合规时：导出时保留 AIGC 元数据，禁止二次转码丢失；必要时用平台标识工具补写

### HG-AV-01 内嵌烧录字幕（白字黑描边）
- 依据：[硬规-上传口径][实6] 内嵌字幕 | https://developer.aliyun.com/article/1774060；[项目契约] SPEC §6（白字黑描边，思源黑体/微软雅黑级别）；[官1] 第二十六条 剧名台词字幕须符合国家通用语言文字规范 | https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html
- 核验方式：人工逐镜播放确认字幕已烧录进画面、描边清晰、不遮挡人脸；本项仅自动校验 storyboard 字幕文本齐备与是否存在独立软字幕流
- 实测线索：需人工核验：字幕是否烧录进画面、白字黑描边、字体清晰且不遮挡人脸；数据层：12/12 镜头有字幕文本；未检出独立软字幕流
- 不合规时：用 drawtext 烧录字幕（白字+黑描边），重跑 06_final

### HG-AV-02 无第三方水印 / AI 工具水印，且 AI 标识不得刻意隐藏
- 依据：[硬规-上传口径][实1] 无水印无黑边 | https://www.runmie.com/44742.html；[实8] 严禁利用文字颜色、透明度或边缘裁剪刻意隐藏 AI 水印 | https://www.tahou.com/article/221745076397698053；[官2] 不得恶意删除、篡改、伪造、隐匿生成合成内容标识 | https://www.cac.gov.cn/2025-03/14/c_1743654685899683.htm
- 核验方式：人工全片逐段查看四角与边缘，确认无工具/平台水印、无遮挡式隐藏标识；水印无法从流信息自动判定
- 实测线索：需人工核验：人工全片逐段查看四角与边缘，确认无工具/平台水印、无遮挡式隐藏标识；水印无法从流信息自动判定
- 不合规时：改用有商用授权的生成与剪辑工具，去除素材水印后重跑 03_frames/06_final

### HG-AV-03 无黑边 / 无拉伸变形
- 依据：[硬规-上传口径][实1] 无水印无黑边 | https://www.runmie.com/44742.html；[官5] 书壳封面不能拉伸、人物不得拉伸变形（同一审核口径延伸至正片）| http://mp.weixin.qq.com/s?__biz=MzkxMTQ5MjkzMA==&mid=2247496815&idx=4&sn=21039388f1dad31de03064f18a458895
- 核验方式：人工播放确认画面铺满、无黑边；并核对 03_frames 合成时 scale/pad 参数与 1080×1920 一致
- 实测线索：需人工核验：人工播放确认画面铺满、无黑边；并核对 03_frames 合成时 scale/pad 参数与 1080×1920 一致
- 不合规时：统一按 1080×1920 居中裁剪/填充，重跑 03_frames/06_final

### HG-AV-04 音画同步 / 口型同步
- 依据：[平台执行·行业整理][实10] 红果公告要求口型同步、别全程怼脸 | https://www.toutiao.com/a7706135472770155050；[项目契约] SPEC §5（05_audio 配音 / 06_final 合成）
- 核验方式：人工全片播放核对音画与口型、景别分布；本地无自动音画/口型比对能力
- 实测线索：需人工核验：人工全片播放核对音画与口型、景别分布；本地无自动音画/口型比对能力
- 不合规时：调整 05_audio 时间轴与 06_final 合成偏移，重跑 05_audio/06_final

### HG-AV-05 封面规格（比例 + 描边剧名）
- 依据：[平台合作口径][官5] 版权中台：动态漫书壳封面必须 3:4、1-5MB、建议 1200×1600、不得拉伸变形 | http://mp.weixin.qq.com/s?__biz=MzkxMTQ5MjkzMA==&mid=2247496815&idx=4&sn=21039388f1dad31de03064f18a458895；[创作者实操][实1] 封面 350×500 且必须带描边剧名，否则驳回 | https://www.runmie.com/44742.html。★两者比例口径不一致，已标注差异
- 核验方式：人工打开封面确认比例、描边剧名、无拉伸，并核对文件大小；本项仅自动读取封面图片像素尺寸
- 实测线索：需人工核验：封面描边剧名、无拉伸变形、比例符合后台当前口径（版权中台 3:4 建议 1200×1600；另有 350×500 实操口径，二者不一致）；实测 1200x1600（约 3:4），1.00 MB
- 不合规时：按后台当前要求重做封面，剧名加描边，另存到投稿目录；不同季不得复用同一张封面


## 小云雀导演台 · 确定性质量门

- 结果：PASS 100.0/100；20 门中通过 20 / 待确认 0 / 不通过 0
- 明细：`output/00_previs/director_gates.json`；预演：`output/00_previs/previs.md`
- 生产预览与指纹：`output/00_previs/production_preview.md`（未确认不产生费用）

| 门 | 名称 | 级别 | 状态 | 实测 |
|---|---|---|---|---|
| D01 | 五份创作文档齐全 | blocker | pass | 齐备 5/5 |
| D02 | SHOT↔MOTION↔CUT 一一对应 | blocker | pass | SHOT 12 / MOTION 12 / CUT 12 / 分镜 12 |
| D03 | 分镜/视频提示词/剪辑单时长逐字一致 | blocker | pass | 漂移镜 无；剪辑单时长条目 12 |
| D04 | 集长等于可见镜头时长之和 | blocker | pass | 镜头合计 73.00s / 目标 73s |
| D05 | 对白发声窗口预算（4.1 字/秒） | blocker | pass | 超载镜 无；最紧窗口占用 52% |
| D06 | 字幕与台词逐字对齐且能在剧本中找到原文 | blocker | pass | 偏离镜 无 |
| D07 | 连续性锁锁面原样传播到生效镜头 | blocker | pass | 缺失 无；锁 4 把 |
| D08 | REF 槽位顺序/用途/控制域/文件真实性 | blocker | pass | 问题 0；12 张起始帧 |
| D09 | 相邻镜景别/角度/人物关系至少改变一项 | craft | pass | 重复相邻 无 |
| D10 | 正反打不越轴，越轴须声明过渡 | craft | pass | 未声明越轴 无 |
| D11 | 运镜幅度 ≤30% 且速率 0.1–10%/秒 | craft | pass | 越界 无 |
| D12 | 每镜单一戏剧目的且不重复 | craft | pass | 唯一目的 12/12 |
| D13 | 起点→唯一动作→终点三态完整 | blocker | pass | 缺失 无 |
| D14 | 前 3 秒强冲突钩子 | craft | pass | 前 3 秒抛出代签指控，把冲突直接摆上桌 |
| D15 | 集尾留悬念引导下一集 | craft | pass | 留悬念引导下一集，机位穿轴重建空间 / 这页，只是第一份。 |
| D16 | 付费生产前预览 + 指纹明确确认 | blocker | pass | job=JOB-C69345C8 fp=c69345c89071 任务=12；确认=有效 |
| D17 | 画幅帧率一致且宽高为偶数 | blocker | pass | 1080×1920 @ 30fps |
| D18 | 对白镜 ≥1.2s、静帧段 ≥0.50s | craft | pass | 过短镜 无；最短 5.00s |
| D19 | 同框说话人绑定（不说话正脸须闭嘴） | craft | pass | 需人工复核镜 无 |
| D20 | 剪辑单出点−入点==时长 | blocker | pass | 记录 12 段，算术异常 0 |

## 逐镜质检与重拍清单

- 合计 12 镜：通过 12 / 提示 0 / 不通过 0
- 真动态视频 1 镜 / 本地视差 11 镜
- 建议重拍：`无`
- 逐镜测量：帧间运动量、黑边、字幕高亮像素、跨镜重复度、接镜亮度跳变、时长与音画漂移
- 明细：`output/07_reports/shot_qc.json`；抽帧证据：`output/07_reports/qc_frames/`
- 重拍方式：替换 `input/<项目>/generated_video/<Sxx>.mp4` 后执行 `python3 src/pipeline.py --input input/demo --retake Sxx --from 04_clips`

| 镜 | 通道 | 状态 | 运动量 | 问题 | 建议 |
|---|---|---|---|---|---|
| S01 | generated_video | pass | 8.921 | — | 无需返工 |
| S02 | local_parallax | pass | 5.493 | — | 无需返工 |
| S03 | local_parallax | pass | 1.859 | — | 无需返工 |
| S04 | local_parallax | pass | 4.75 | — | 无需返工 |
| S05 | local_parallax | pass | 1.156 | — | 无需返工 |
| S06 | local_parallax | pass | 4.445 | — | 无需返工 |
| S07 | local_parallax | pass | 2.007 | — | 无需返工 |
| S08 | local_parallax | pass | 1.325 | — | 无需返工 |
| S09 | local_parallax | pass | 5.531 | — | 无需返工 |
| S10 | local_parallax | pass | 6.0 | — | 无需返工 |
| S11 | local_parallax | pass | 11.128 | — | 无需返工 |
| S12 | local_parallax | pass | 4.597 | — | 无需返工 |
## 人工确认门

- G1 剧本与分镜确认：**approved** 演示模式自动通过，仍需人工复核
- G2 角色定妆与一致性锁定：**approved** 演示模式自动通过，仍需人工复核
- G3 真人转绘帧验收：**approved** 演示模式自动通过，仍需人工复核
- G4 配音与音画同步预检：**approved** 演示模式自动通过，仍需人工复核
- G5 成片终审（人工）：**approved** 演示模式自动通过，仍需人工复核

## 创作链路与版权留痕

- `output/07_reports/creation_chain.md`：逐环节输入/命令/产物
- `output/07_reports/generation_params.json`：全部生成参数
- `output/07_reports/asset_licenses.csv`：参考图来源与授权状态
- `output/07_reports/originality_declaration.md`：原创声明模板（待人工签署）

本片标识：AI 辅助制作
