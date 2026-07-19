import re

t = open(
    r"D:\grok-cli\workspace\jcc-controller-work\jadx\sources\a\q1.java",
    encoding="utf-8",
    errors="ignore",
).read()
for m in re.finditer(r'y1\.f\("([^"]+)"', t):
    print("SET", m.group(1))
for m in re.finditer(r'y1\.e\("([^"]+)"', t):
    print("GET", m.group(1))
for m in re.finditer(r'y1\.c\("([^"]+)"', t):
    print("DO", m.group(1))

t2 = open(
    r"D:\grok-cli\workspace\jcc-controller-work\jadx\sources\com\jcc\controller\FloatingService.java",
    encoding="utf-8",
    errors="ignore",
).read()
idx = t2.find("handlePush")
print("handlePush at", idx)
if idx >= 0:
    print(t2[idx : idx + 3000])

t3 = open(
    r"D:\grok-cli\workspace\jcc-controller-work\jadx\sources\com\jcc\controller\BattleOverlayView.java",
    encoding="utf-8",
    errors="ignore",
).read()
idx = t3.find("lambda$startPolling")
print("poll at", idx)
if idx >= 0:
    print(t3[idx : idx + 1500])
