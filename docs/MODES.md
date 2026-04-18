# Saddle 协作模式（Modes）

使用 **Claude Code / OpenClaw 插件** 对接 HTTP 时的 Memory API 约定见 **[`PLUGIN_HTTP.md`](./PLUGIN_HTTP.md)**。

**协作原语与 `collaboration_config`（分组、原语、简写、示例）**：[中文](./COLLABORATION_CONFIG.zh.md) · [English](./COLLABORATION_CONFIG.md)

Saddle 支持低认知成本的协作模式配置：

- 文件配置：`.saddle/modes/*.yaml`
- CLI 临时覆盖：`--mode` + `--set key=value`

默认执行链路（无额外配置）：

`spec -> design -> develop`

## 快速使用

```bash
saddle run "实现带审计日志的订单系统"
```

使用内置 fast 模式：

```bash
saddle run "实现带审计日志的订单系统" --mode fast
```

临时覆盖配置（不改文件）：

```bash
saddle run "实现带审计日志的订单系统" \
  --mode default \
  --set design.deep_loop=true \
  --set develop.max_iters=20 \
  --set agent_selection.strategy=balanced
```

## 最常用 5 个配置键

- `pipeline.order`：阶段顺序，默认 `['spec','design','develop']`
- `design.deep_loop`：是否启用 design 深循环
- `design.max_iters`：design 深循环最大轮次
- `develop.deep_loop`：是否启用 develop 深循环
- `agent_selection.strategy`：角色选择策略（`minimal|balanced|custom`）

## 模式模板

- `default.yaml`：零配置默认，适合一般任务
- `fast.yaml`：快速交付，偏少轮次 + compact prompt
- `deep.yaml`：高要求协作，默认开启 deep loop

## 查看与诊断（`saddle mode`）

若未将 `saddle` 控制台脚本所在目录加入 `PATH`，可使用 **`python -m saddle`**（与 `saddle` 等价），例如：`python -m saddle mode list`。请用 **`python -m pip install -e .`** 与 **`python -m saddle`** 保持同一解释器；仓库根目录的 shim 支持在上级目录执行 `python -m saddle` 时仍能加载 `src/saddle`。

```bash
# 列出 .saddle/modes/ 下可用的模式名
saddle mode list

# 打印合并后的完整配置（默认 cwd、模式 default）
saddle mode show fast --project /path/to/repo

# 校验配置；有错误时退出码为 1
saddle mode validate default --set pipeline.order=[spec,design,develop]
```

列表类字段在 `--set` 中需写成方括号形式，例如 `pipeline.order=[spec,develop]`。

## 可视化配置面板（Saddle Studio）

`saddle/studio` 提供 Stripe 风格的可视化配置面板，支持：

- Welcome 页（品牌介绍、协作链路说明）
- 基础模式配置（`spec/design/develop`、`pipeline.order`）
- 专业配置（角色思维模型、工具策略、阈值）
- JSON/YAML 实时预览
- 服务端校验与保存（写回 `.saddle/modes/*.yaml`）

启动：

**开发（Vite 热更新，默认端口 4173）：**

```bash
cd saddle/studio
npm install
npm run dev
```

**发布（构建后由 `saddle serve` 托管，与 API 同端口）：**

```bash
cd saddle/studio
npm install
npm run build
cd ..
saddle serve
# 打开 http://127.0.0.1:1995/ （或你指定的 host/port）
```

自定义构建输出目录：`saddle serve --studio-dir /path/to/dist` 或设置环境变量 `SADDLE_STUDIO_DIR`。

