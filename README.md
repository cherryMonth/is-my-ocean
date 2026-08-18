# Cyber Kitty 电子玫瑰

一个零依赖、手机优先的七夕告白页面。直接打开 `index.html` 即可预览，也可以部署到任意静态网站托管服务。

## 修改名字和文案

编辑 `script.js` 顶部的 `CONFIG`：

```js
const CONFIG = {
  to: "她的名字",
  from: "你的名字",
  message: "你想对她说的话",
};
```

也可以不改代码，直接通过网址参数临时定制：

```text
index.html?to=她的名字&from=你的名字&msg=你的告白
```

中文和空格较多时，建议用浏览器或在线工具对参数进行 URL 编码。

## 使用

推荐用静态服务器预览：

```bash
cd electronic-rose
python3 -m http.server 8080
```

然后访问 `http://localhost:8080`。

点击“启动心动核心”时会同步播放约 21 秒的原创七夕电子配乐。右上角声音按钮可以随时暂停或重新播放。

配乐文件位于 `assets/qixi-love-core.mp3`，无损母带位于
`assets/qixi-love-core.wav`。如需重新生成，可运行：

```bash
python3 tools/generate_qixi_soundtrack.py
ffmpeg -y -i assets/qixi-love-core.wav \
  -af "loudnorm=I=-16:TP=-1.5:LRA=8" \
  -codec:a libmp3lame -b:a 192k assets/qixi-love-core.mp3
```
