"""
Dungeon Toolkit API 集成测试
运行方式：python unittest/test_api.py
依赖：pip install requests
"""
import sys
import json
import requests

BASE_URL = "http://localhost/api"

# 测试账号（会自动注册，若已存在则直接登录）
TEST_EMAIL = "test_runner@dungeon-toolkit.local"
TEST_PASSWORD = "TestPass1234"
TEST_USERNAME = "test_runner"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def ok(msg):
    print(f"  {Colors.GREEN}✓{Colors.RESET} {msg}")


def fail(msg):
    print(f"  {Colors.RED}✗ {msg}{Colors.RESET}")


def info(msg):
    print(f"\n{Colors.CYAN}{Colors.BOLD}▶ {msg}{Colors.RESET}")


def warn(msg):
    print(f"  {Colors.YELLOW}⚠ {msg}{Colors.RESET}")


passed = 0
failed = 0


def check(condition, success_msg, fail_msg, detail=None):
    global passed, failed
    if condition:
        ok(success_msg)
        passed += 1
    else:
        fail(fail_msg)
        if detail:
            print(f"    └─ {detail}")
        failed += 1


# ─────────────────────────────────────────
# 1. 健康检查
# ─────────────────────────────────────────
info("健康检查")
try:
    r = requests.get(f"{BASE_URL}/health/", timeout=5)
    check(r.status_code == 200, "服务响应正常 (200)", f"服务无响应 ({r.status_code})")
    check(r.json().get("status") == "ok", "返回 status: ok", "返回内容异常", r.text)
except Exception as e:
    fail(f"无法连接到服务：{e}")
    print(f"\n{Colors.RED}服务未启动，请先执行 docker-compose up -d{Colors.RESET}")
    sys.exit(1)


# ─────────────────────────────────────────
# 2. 用户认证
# ─────────────────────────────────────────
info("用户认证")

# 注册（允许已存在）
r = requests.post(f"{BASE_URL}/auth/register/", json={
    "email": TEST_EMAIL,
    "username": TEST_USERNAME,
    "password": TEST_PASSWORD,
})
if r.status_code == 201:
    ok("注册新账号成功 (201)")
    passed += 1
elif r.status_code == 400 and "already" in r.text.lower() or "存在" in r.text or "unique" in r.text.lower():
    warn("账号已存在，跳过注册")
else:
    check(False, "", f"注册失败 ({r.status_code})", r.text)

# 登录（后端接受 identifier 字段，支持邮箱或用户名）
r = requests.post(f"{BASE_URL}/auth/login/", json={
    "identifier": TEST_EMAIL,
    "password": TEST_PASSWORD,
})
check(r.status_code == 200, "登录成功 (200)", f"登录失败 ({r.status_code})", r.text)

token = None
if r.status_code == 200:
    data = r.json()
    token = data.get("access")
    check(bool(token), "获取到 access token", "响应中无 access token", str(data))
    check(bool(data.get("refresh")), "获取到 refresh token", "响应中无 refresh token")

if not token:
    fail("无法获取 token，后续测试终止")
    sys.exit(1)

auth = {"Authorization": f"Bearer {token}"}

# 获取当前用户信息
r = requests.get(f"{BASE_URL}/auth/me/", headers=auth)
check(r.status_code == 200, "GET /auth/me/ 返回 200", f"GET /auth/me/ 失败 ({r.status_code})")
if r.status_code == 200:
    me = r.json()
    check(me.get("email") == TEST_EMAIL, f"用户邮箱正确 ({me.get('email')})", "用户邮箱不符")

# 未授权访问
r = requests.get(f"{BASE_URL}/auth/me/")
check(r.status_code == 401, "未授权访问返回 401", f"未授权访问未被拦截 ({r.status_code})")


# ─────────────────────────────────────────
# 3. 游戏数据 - 规则集
# ─────────────────────────────────────────
info("游戏数据 - 规则集")

r = requests.get(f"{BASE_URL}/gamedata/rulesets/", headers=auth)
check(r.status_code == 200, "GET /gamedata/rulesets/ 返回 200", f"请求失败 ({r.status_code})", r.text)

rulesets = []
if r.status_code == 200:
    data = r.json()
    rulesets = data.get("results", data) if isinstance(data, dict) else data
    check(len(rulesets) > 0, f"规则集数量: {len(rulesets)}", "规则集为空，请先运行导入脚本")
    if rulesets:
        slugs = [rs["slug"] for rs in rulesets]
        check("dnd5e_2014" in slugs, "dnd5e_2014 规则集存在", "dnd5e_2014 规则集未找到", f"现有: {slugs}")


# ─────────────────────────────────────────
# 4. 游戏数据 - 种族
# ─────────────────────────────────────────
info("游戏数据 - 种族")

r = requests.get(f"{BASE_URL}/gamedata/races/?ruleset__slug=dnd5e_2014", headers=auth)
check(r.status_code == 200, "GET /gamedata/races/ 返回 200", f"请求失败 ({r.status_code})", r.text)

races = []
if r.status_code == 200:
    data = r.json()
    races = data.get("results", data) if isinstance(data, dict) else data
    check(len(races) >= 9, f"种族数量: {len(races)}（应≥9）", f"种族数量不足: {len(races)}")

    expected_races = ["human", "elf", "dwarf", "halfling", "gnome", "half-elf", "half-orc", "tiefling", "dragonborn"]
    existing_slugs = [r["slug"] for r in races]
    for slug in expected_races:
        check(slug in existing_slugs, f"种族存在: {slug}", f"种族缺失: {slug}")

    # 验证有亚种族的种族
    elf = next((r for r in races if r["slug"] == "elf"), None)
    if elf:
        check(elf.get("has_subraces") == True, "精灵标记有亚种族", "精灵未标记亚种族")

# 种族详情（含亚种族）
r = requests.get(f"{BASE_URL}/gamedata/races/", headers=auth)
if r.status_code == 200:
    all_races = r.json()
    results = all_races.get("results", all_races) if isinstance(all_races, dict) else all_races
    elf_obj = next((r for r in results if r["slug"] == "elf"), None)
    if elf_obj:
        elf_id = elf_obj["id"]
        r2 = requests.get(f"{BASE_URL}/gamedata/races/{elf_id}/", headers=auth)
        check(r2.status_code == 200, "种族详情接口正常", f"种族详情失败 ({r2.status_code})")
        if r2.status_code == 200:
            elf_detail = r2.json()
            subraces = elf_detail.get("subraces", [])
            check(len(subraces) >= 2, f"精灵亚种族数量: {len(subraces)}（应≥2）", "精灵亚种族为空")


# ─────────────────────────────────────────
# 5. 游戏数据 - 职业
# ─────────────────────────────────────────
info("游戏数据 - 职业")

r = requests.get(f"{BASE_URL}/gamedata/classes/?ruleset__slug=dnd5e_2014", headers=auth)
check(r.status_code == 200, "GET /gamedata/classes/ 返回 200", f"请求失败 ({r.status_code})", r.text)

if r.status_code == 200:
    data = r.json()
    classes = data.get("results", data) if isinstance(data, dict) else data
    if len(classes) == 0:
        warn("职业数据为空（classes.json 尚未创建，属预期情况）")
    else:
        check(len(classes) >= 1, f"职业数量: {len(classes)}", "职业为空")
        spellcasters = [c for c in classes if c.get("is_spellcaster")]
        check(len(spellcasters) > 0, f"施法职业数量: {len(spellcasters)}", "没有施法职业")


# ─────────────────────────────────────────
# 6. 游戏数据 - 背景
# ─────────────────────────────────────────
info("游戏数据 - 背景")

r = requests.get(f"{BASE_URL}/gamedata/backgrounds/?ruleset__slug=dnd5e_2014", headers=auth)
check(r.status_code == 200, "GET /gamedata/backgrounds/ 返回 200", f"请求失败 ({r.status_code})", r.text)

if r.status_code == 200:
    data = r.json()
    backgrounds = data.get("results", data) if isinstance(data, dict) else data
    if len(backgrounds) == 0:
        warn("背景数据为空（backgrounds.json 尚未创建，属预期情况）")
    else:
        check(len(backgrounds) >= 1, f"背景数量: {len(backgrounds)}", "背景为空")


# ─────────────────────────────────────────
# 7. 角色管理
# ─────────────────────────────────────────
info("角色管理")

# 创建角色
char_payload = {
    "name": "测试角色_Aldric",
    "gender": "male",
    "age": 25,
    "appearance": "金发碧眼，高挑身材",
    "ruleset_slug": "dnd5e_2014",
    "race_slug": "elf",
    "subrace_slug": "high-elf",
    "class_slug": "wizard",
    "background_slug": "sage",
    "ability_method": "standard_array",
    "strength": 8,
    "dexterity": 14,
    "constitution": 13,
    "intelligence": 15,
    "wisdom": 12,
    "charisma": 10,
    "skill_proficiencies": ["arcana", "history"],
    "personality_trait": "我对一切未知事物充满好奇。",
    "ideal": "知识是力量的源泉。",
    "bond": "我的导师将我引入魔法的世界。",
    "flaw": "我常常沉溺于书本，忽视周围的危险。",
    "known_spells": [{"slug": "fire-bolt", "name": "火焰冲击"}],
    "inventory": [{"name": "法师法典", "quantity": 1}],
}
r = requests.post(f"{BASE_URL}/characters/", json=char_payload, headers=auth)
check(r.status_code == 201, "创建角色成功 (201)", f"创建角色失败 ({r.status_code})", r.text)

char_id = None
if r.status_code == 201:
    char_id = r.json().get("id")
    check(bool(char_id), f"角色 ID: {char_id}", "响应中无角色 ID")

# 角色列表
r = requests.get(f"{BASE_URL}/characters/", headers=auth)
check(r.status_code == 200, "GET /characters/ 返回 200", f"角色列表失败 ({r.status_code})")
if r.status_code == 200:
    data = r.json()
    chars = data.get("results", data) if isinstance(data, dict) else data
    check(len(chars) >= 1, f"角色列表数量: {len(chars)}", "角色列表为空")

# 角色详情
if char_id:
    r = requests.get(f"{BASE_URL}/characters/{char_id}/", headers=auth)
    check(r.status_code == 200, "角色详情返回 200", f"角色详情失败 ({r.status_code})")
    if r.status_code == 200:
        char = r.json()
        check(char.get("name") == "测试角色_Aldric", "角色名称正确", f"角色名称异常: {char.get('name')}")
        check(char.get("race_slug") == "elf", "种族 slug 正确", f"种族 slug 异常: {char.get('race_slug')}")
        check(char.get("intelligence") == 15, "智力值正确 (15)", f"智力值异常: {char.get('intelligence')}")

    # 更新角色
    r = requests.patch(f"{BASE_URL}/characters/{char_id}/", json={"level": 2}, headers=auth)
    check(r.status_code == 200, "更新角色成功 (200)", f"更新角色失败 ({r.status_code})")
    if r.status_code == 200:
        check(r.json().get("level") == 2, "等级更新为 2", "等级更新失败")

    # 切换分享
    r = requests.post(f"{BASE_URL}/characters/{char_id}/share/", headers=auth)
    check(r.status_code == 200, "切换分享状态成功", f"切换分享失败 ({r.status_code})", r.text)
    share_token = None
    if r.status_code == 200:
        share_data = r.json()
        check(share_data.get("is_public") == True, "角色已设为公开", "公开状态未变更")
        share_token = share_data.get("share_token")

    # 公开分享页（无需 token）
    if share_token:
        r = requests.get(f"{BASE_URL}/characters/public/{share_token}/")
        check(r.status_code == 200, f"公开分享页可访问 (token={share_token[:8]}...)", f"公开分享页失败 ({r.status_code})", r.text)

    # 权限隔离：其他用户无法访问
    r = requests.get(f"{BASE_URL}/characters/{char_id}/")
    check(r.status_code == 401, "未授权访问角色返回 401", f"权限控制异常 ({r.status_code})")

    # 删除角色（清理测试数据）
    r = requests.delete(f"{BASE_URL}/characters/{char_id}/", headers=auth)
    check(r.status_code == 204, "删除角色成功 (204)", f"删除角色失败 ({r.status_code})")


# ─────────────────────────────────────────
# 汇总
# ─────────────────────────────────────────
total = passed + failed
print(f"\n{'─'*50}")
print(f"{Colors.BOLD}测试结果：{Colors.RESET}", end="")
if failed == 0:
    print(f"{Colors.GREEN}{Colors.BOLD}全部通过 ✓{Colors.RESET}")
else:
    print(f"{Colors.GREEN}{passed} 通过{Colors.RESET}  {Colors.RED}{failed} 失败{Colors.RESET}")
print(f"{'─'*50}\n")

sys.exit(0 if failed == 0 else 1)
