"""
生成图2.7 WebSocket 通信系统流程图 (PNG)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(20, 34))
ax.set_xlim(0, 20)
ax.set_ylim(0, 34)
ax.invert_yaxis()
ax.set_aspect("equal")
ax.axis("off")

# ── 颜色 ──
C_START_END = "#e6f7ff"  # 开始/结束：浅蓝
C_PROCESS = "#e6f7ff"    # 处理步骤：浅蓝
C_DECISION = "#fff7e6"   # 判断：浅橙
C_ERROR = "#fff1f0"      # 错误/拒绝：浅红
C_DISPATCH = "#f9f0ff"   # 消息分发：浅紫
C_EDGE = "#434343"       # 边框
C_ARROW = "#595959"      # 箭头
C_TEXT = "#262626"       # 文字
FONT = "SimHei"
FONT_SIZE = 9
FONT_TITLE = 11

def box(x, y, w, h, text, color=C_PROCESS, fontsize=FONT_SIZE, bold=False):
    """圆角矩形"""
    r = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.15",
                        facecolor=color, edgecolor=C_EDGE, linewidth=1.2, zorder=2)
    ax.add_patch(r)
    weight = "bold" if bold else "normal"
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fontsize,
            fontfamily=FONT, color=C_TEXT, weight=weight, zorder=3, linespacing=1.3)

def diamond(x, y, w, h, text, color=C_DECISION, fontsize=FONT_SIZE):
    """菱形判断框"""
    cx, cy = x + w/2, y + h/2
    points = [(cx, y), (x + w, cy), (cx, y + h), (x, cy)]
    poly = Polygon(points, facecolor=color, edgecolor=C_EDGE, linewidth=1.2, zorder=2)
    ax.add_patch(poly)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize,
            fontfamily=FONT, color=C_TEXT, zorder=3, linespacing=1.3)

def arrow(x1, y1, x2, y2, label="", color=C_ARROW, lw=1.0, style="->"):
    """箭头"""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle="arc3,rad=0"), zorder=1)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.2, my - 0.25, label, fontsize=7, fontfamily=FONT,
                color="#8c8c8c", zorder=3)

def h_arrow(x1, y1, x2, y2, label="", color=C_ARROW, lw=1.0):
    """垂直箭头"""
    arrow(x1, y1, x2, y2, label, color, lw)

def side_label(x, y, text, color="#8c8c8c"):
    """侧边标注"""
    ax.text(x, y, text, fontsize=7, fontfamily=FONT, color=color, zorder=3, style="italic")

# ========================
# 节点定义 (x, y, w, h)
# ========================

# Row 0: 开始
box(7, 0.3, 6, 1.2, "前端发起 WS 连接请求\n/ws/chat?token=eyJ...",
    color=C_START_END, fontsize=FONT_TITLE, bold=True)

# Row 1: 验证 Token（判断）
diamond(6, 2.5, 8, 2.0, "后端验证 JWT Token\n是否有效？")

# 左分支: 拒绝
box(0.5, 5.5, 4, 1.0, "拒绝连接\n返回 403", color=C_ERROR)
box(0.5, 7.5, 4, 1.0, "结束", color=C_ERROR)

# 右分支（主流程）: 接受连接
box(9, 5.5, 5.5, 1.0, "接受连接 accept()\n标记用户在线 is_online=T", color=C_PROCESS)
arrow(11.75, 6.5, 11.75, 7.5)

box(9, 7.5, 5.5, 1.0, "推送上线通知\n给所有在线好友", color=C_PROCESS)
arrow(11.75, 8.5, 11.75, 9.5)

# ── 消息循环（大框）──
loop_rect = FancyBboxPatch((1, 9.5), 18, 14.5, boxstyle="round,pad=0.3",
                            facecolor="none", edgecolor="#bfbfbf", linewidth=1.5,
                            linestyle="--", zorder=0)
ax.add_patch(loop_rect)
ax.text(2, 10.0, "循环等待消息", fontsize=9, fontfamily=FONT, color="#8c8c8c", zorder=3)

# 收到消息 → 解析 type
box(7, 10.2, 6, 1.0, "收到消息，解析 type 字段", color=C_DISPATCH, fontsize=FONT_TITLE, bold=True)

# 四个分支节点
BRANCH_Y = 12.2
BRANCHES = [
    (1, "chat_message", "存储消息到数据库\n→ 查询接收方位置"),
    (6, "read_receipt", "更新消息已读状态\nis_read = TRUE"),
    (11, "typing", "转发打字状态\n给接收方"),
    (16, "ping / heartbeat", "回复 pong\n保持连接"),
]
branch_centers = []
for x, title, desc in BRANCHES:
    box(x, BRANCH_Y, 4, 1.0, f"{title}\n{desc}", color=C_PROCESS, fontsize=7.5)
    branch_centers.append((x + 2, BRANCH_Y + 0.5))

# chat_message 的后续处理（最左边那条）
box(1, 14.2, 4, 1.0, "判断接收方\n是否在本 Worker", color=C_DECISION, fontsize=7.5)

# 本机在线
box(0.2, 16.0, 3.5, 1.0, "直接 send_json\n推送给接收方", color=C_PROCESS, fontsize=8)

# 不在本机
box(4.2, 16.0, 3.5, 1.0, "Redis Pub/Sub\n转发到其他 Worker", color=C_PROCESS, fontsize=8)

# ACK
box(1, 17.8, 7, 1.0, '返回 ACK 给发送方\n前端更新消息状态为 [已发送]', color="#f6ffed")

# 接收方展示
box(1, 19.5, 7, 1.0, '接收方展示新消息, 自动发送已读回执\n发送方更新为 [已读]', color="#f6ffed")

# other branches 回到循环
for i in range(1, 4):
    bx, by = branch_centers[i]
    # small box for back-to-loop
    box(branch_centers[i][0] - 1.5, 20.0, 3, 0.7, "回到循环 ↑",
        color="#f0f0f0", fontsize=7)

# ── 断开连接 ──
box(7, 24.8, 6, 1.0, "WebSocket 连接断开\n(用户关闭页面 / 网络中断)", color=C_START_END, fontsize=FONT_TITLE, bold=True)
h_arrow(10, 24.0, 10, 24.8)

box(7, 26.5, 6, 1.0, "标记用户离线 is_online=F\n记录 last_seen_at = now()", color=C_PROCESS)
h_arrow(10, 25.8, 10, 26.5)

box(7, 28.3, 6, 1.0, "推送下线通知\n给所有在线好友", color=C_PROCESS)
h_arrow(10, 27.5, 10, 28.3)

box(7, 29.8, 6, 1.0, "结束", color=C_START_END, fontsize=FONT_TITLE, bold=True)
h_arrow(10, 29.3, 10, 29.8)

# ========================
# 箭头连接
# ========================

# 开始 → 验证
arrow(10, 1.5, 10, 2.5)
# 验证 → 拒绝 (左)
arrow(8, 3.5, 2.5, 5.5, label="无效/过期")
# 验证 → 接受 (右)
arrow(12, 3.5, 11.75, 5.5, label="有效")

# 拒绝 → 结束
arrow(2.5, 6.5, 2.5, 7.5)

# 接受 → 推送上线 → 进入循环
arrow(11.75, 8.5, 11.75, 9.5)

# 循环入口 → 解析 type
arrow(10, 9.5, 10, 10.2)

# 解析 → 四个分支
for i, (x, title, desc) in enumerate(BRANCHES):
    arrow(10, 11.2, x + 2, 12.2)

# chat_message → 判断 Worker
arrow(branch_centers[0][0], 13.2, 3, 14.2)
# 判断 → 本机
arrow(2.5, 15.2, 1.95, 16.0, label="本机")
# 判断 → Redis
arrow(3.5, 15.2, 5.95, 16.0, label="其他Worker")

# 两者 → ACK
arrow(1.95, 17.0, 4.5, 17.8)
arrow(5.95, 17.0, 4.5, 17.8)

# ACK → 接收方展示
arrow(4.5, 18.8, 4.5, 19.5)

# 接收方展示 → 回到解析
# 曲线回到顶部
ax.annotate("", xy=(10, 10.2), xytext=(4.5, 20.5),
            arrowprops=dict(arrowstyle="->", color=C_ARROW, lw=1.2,
                            connectionstyle="arc3,rad=-0.4"), zorder=1)
ax.text(0.2, 15.5, "回到循环\n继续等待", fontsize=7, fontfamily=FONT, color="#8c8c8c", zorder=3)

# read_receipt → 回到循环
ax.annotate("", xy=(10, 10.2), xytext=(branch_centers[1][0], 13.2),
            arrowprops=dict(arrowstyle="->", color=C_ARROW, lw=1.0,
                            connectionstyle="arc3,rad=0.25"), zorder=1)

# typing → 回到循环
ax.annotate("", xy=(10, 10.2), xytext=(branch_centers[2][0], 13.2),
            arrowprops=dict(arrowstyle="->", color=C_ARROW, lw=1.0,
                            connectionstyle="arc3,rad=0.25"), zorder=1)

# ping → 回到循环
ax.annotate("", xy=(17, 10.2), xytext=(branch_centers[3][0], 13.2),
            arrowprops=dict(arrowstyle="->", color=C_ARROW, lw=1.0,
                            connectionstyle="arc3,rad=0.25"), zorder=1)

# 循环结束 → 断开连接
ax.annotate("", xy=(10, 24.8), xytext=(10, 24.0),
            arrowprops=dict(arrowstyle="->", color=C_ARROW, lw=1.2,
                            connectionstyle="arc3,rad=0"), zorder=1)

# ── 图例 ──
legend_y = 32.5
leg_items = [
    (C_START_END, "开始 / 结束"),
    (C_PROCESS, "处理步骤"),
    (C_DECISION, "判断分支"),
    (C_DISPATCH, "消息分发"),
    (C_ERROR, "异常 / 拒绝"),
]
for i, (color, label) in enumerate(leg_items):
    lx = 2 + i * 3.8
    r = FancyBboxPatch((lx, legend_y), 2.8, 0.7, boxstyle="round,pad=0.1",
                        facecolor=color, edgecolor=C_EDGE, linewidth=0.8, zorder=2)
    ax.add_patch(r)
    ax.text(lx + 1.4, legend_y + 0.35, label, ha="center", va="center",
            fontsize=8, fontfamily=FONT, color=C_TEXT, zorder=3)

# ── 标题 ──
ax.text(10, -1.0, "图2.7  WebSocket 通信系统流程图", ha="center", va="center",
        fontsize=14, fontfamily=FONT, color=C_TEXT, weight="bold")

# ── 保存 ──
out = r"d:\chatzzj\chatzzj\图2.7_WebSocket通信流程图.png"
fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white", edgecolor="none")
plt.close(fig)
print(f"已保存: {out}")
