"""
种子脚本：初始化平台审核规则
运行方式:
  uv run python scripts/seed_moderation_rules.py          # 追加模式（跳过已存在的）
  uv run python scripts/seed_moderation_rules.py --reset  # 重置模式（先删后插）

设计原则：
  1. 只用明确的多字词组，禁用单字匹配（"毒"→误伤"病毒"、"核"→误伤"核心"）
  2. block = 绝对拦截（毒品/武器/色情等红线），warn = 仅告警不阻断
  3. warn 规则极简 —— AI 营销文案天然带有夸张修辞，不应拦截
  4. 子串匹配保留（"heroin" 匹配 "heroin"），但词根须足够长
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.database import get_db
from models.moderation import PlatformRule
from sqlalchemy.orm import Session

RULES = [
    # ════════════════════ Amazon - 违禁商品 BLOCK ════════════════════
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-毒品",
        "severity": "block",
        "keywords": json.dumps([
            # 英文（词根≥4字符，避免误伤）
            "heroin", "cocaine", "methamphetamine", "fentanyl", "narcotic",
            "opioid", "opium", "morphine", "cannabis", "marijuana",
            "ecstasy", "ketamine", "amphetamine", "methadone",
            "psychedelic", "hallucinogen", "lsd", "mdma",
            # 中文（多字明确词汇）
            "海洛因", "可卡因", "冰毒", "大麻", "鸦片", "吗啡",
            "摇头丸", "迷幻药", "致幻剂", "麻古", "丧尸药",
            "吸毒", "毒品", "药物滥用", "麻醉药品",
            # 绕词/变体
            "class a drug", "controlled substance",
            "d r u g", "d.r.u.g",
        ]),
        "description": "Amazon 禁售：毒品、管制药物、精神活性物质",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-武器",
        "severity": "block",
        "keywords": json.dumps([
            "firearm", "shotgun", "rifle", "pistol", "handgun",
            "ammunition", "explosive", "dynamite", "grenade",
            "detonator", "taser", "pepper spray", "stun gun",
            "switchblade", "brass knuckles",
            "枪支", "手枪", "步枪", "冲锋枪", "弹药",
            "子弹", "炸弹", "爆炸物", "雷管",
            "assault rifle", "machine gun",
            "homemade gun", "3d printed gun",
            "c4", "semtex", "塑料炸药",
        ]),
        "description": "Amazon 禁售：武器、弹药、爆炸物及配件",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-假货伪造",
        "severity": "block",
        "keywords": json.dumps([
            "counterfeit", "knockoff",
            "fake id", "fake passport", "fake document",
            "假证", "假护照", "假身份证", "假学历", "假文凭",
            "degree for sale", "buy diploma",
            "counterfeit money", "假币", "假钞",
            "passport for sale",
        ]),
        "description": "Amazon 禁售：假冒伪劣商品、伪造证件",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-烟酒",
        "severity": "block",
        "keywords": json.dumps([
            "tobacco", "cigarette", "cigar", "e-cigarette",
            "e-liquid", "vaping", "nicotine",
            "香烟", "雪茄", "电子烟", "烟草",
            "alcohol", "liquor", "whiskey", "vodka",
            "白酒", "洋酒", "烈酒",
        ]),
        "description": "Amazon 禁售：烟草制品及电子烟、酒类",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-人体器官",
        "severity": "block",
        "keywords": json.dumps([
            "human trafficking", "forced labor",
            "器官买卖", "人口贩卖", "贩卖人口", "强迫劳动",
            "代孕", "surrogacy", "surrogate mother",
            "adoption for sale", "买孩子", "卖孩子",
        ]),
        "description": "Amazon 禁售：人体器官、人口贩卖",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-危险品",
        "severity": "block",
        "keywords": json.dumps([
            "hazardous", "toxic", "poison", "cyanide", "arsenic",
            "mercury", "asbestos", "radioactive", "uranium",
            "氰化物", "砒霜", "水银", "石棉", "放射性",
            "acid", "flammable", "corrosive",
            "硫酸", "硝酸", "易燃", "易爆",
            "pesticide", "insecticide", "herbicide", "rodenticide",
            "农药", "杀虫剂", "除草剂", "老鼠药",
            "bioweapon", "化学武器", "芥子气",
            "chlorine gas", "氯气", "炭疽",
            "烟花爆竹", "鞭炮",
        ]),
        "description": "Amazon 禁售：危险品、有毒化学品、农药",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-野生动物",
        "severity": "block",
        "keywords": json.dumps([
            "ivory", "rhino", "shark fin", "pangolin", "sea turtle",
            "象牙", "犀牛", "虎骨", "鱼翅", "穿山甲",
            "endangered", "protected species", "wild animal product",
            "濒危", "野生动物制品", "穿山甲鳞片",
            "偷猎", "盗猎", "poaching",
        ]),
        "description": "Amazon 禁售：濒危野生动物及其制品",
    },

    # ════════════════ Amazon - 药品医疗 BLOCK ════════════════
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "医疗-处方药",
        "severity": "block",
        "keywords": json.dumps([
            "prescription", "rx only", "antibiotic", "antibiotics",
            "处方药", "抗生素", "精神类药物",
            "ozempic", "wegovy", "adderall", "codeine", "tramadol",
            "没有处方", "无需处方", "代购处方",
            "online pharmacy", "pharmacy without prescription",
            "药品代购", "印度仿制药", "走私药",
        ]),
        "description": "Amazon 禁售：处方药及无需处方的药品销售",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "医疗-虚假疗效",
        "severity": "block",
        "keywords": json.dumps([
            "cure cancer", "cure disease", "cure all",
            "治愈癌症", "治疗艾滋", "艾滋病治愈", "治愈新冠",
            "hiv cure", "covid cure", "cancer cure",
            "包治", "根治", "神药", "灵丹妙药",
            "保证治愈", "无效退款", "不愈包退",
        ]),
        "description": "Amazon 禁售：夸大疗效的虚假医疗宣传",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "医疗-未批准器械",
        "severity": "block",
        "keywords": json.dumps([
            "medical device", "surgical", "implant",
            "医疗器械", "手术器械", "植入物",
            "检测试剂", "诊断试剂", "核酸检测", "抗原检测",
            "cpap", "ventilator", "defibrillator", "pacemaker",
            "呼吸机", "除颤器", "起搏器",
            "not fda", "未经fda", "fda pending",
        ]),
        "description": "Amazon 禁售：未经批准的医疗器械",
    },

    # ════════════════ Amazon - 仇恨/歧视 BLOCK ════════════════
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违规-仇恨言论",
        "severity": "block",
        "keywords": json.dumps([
            "racist", "racism", "nazi", "kkk", "supremacist",
            "种族歧视", "种族主义", "纳粹", "白人至上",
            "genocide", "holocaust", "ethnic cleansing",
            "种族灭绝", "大屠杀", "种族清洗",
            "terrorist", "terrorism", "isis", "al qaeda",
            "恐怖主义", "恐怖分子", "圣战",
            "hate speech", "仇恨言论",
        ]),
        "description": "Amazon 禁售：仇恨言论、种族歧视、恐怖主义",
    },

    # ════════════════ Amazon - 成人内容 BLOCK ════════════════
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违规-成人色情",
        "severity": "block",
        "keywords": json.dumps([
            "pornography", "xxx", "explicit sexual",
            "色情", "淫秽", "情色",
            "sex toy", "vibrator", "dildo",
            "震动棒", "自慰器", "成人用品",
            "escort", "prostitute", "sex service",
            "卖淫", "嫖娼",
            "onlyfans", "nsfw",
            "充气娃娃", "催情药", "迷奸",
            "性虐待", "bdsm",
        ]),
        "description": "Amazon 禁售：成人色情内容及服务",
    },

    # ════════════════ Amazon - 赌博 BLOCK ════════════════
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违规-赌博",
        "severity": "block",
        "keywords": json.dumps([
            "casino", "gambling", "lottery", "betting",
            "博彩", "赌场", "赌局",
            "slot machine", "roulette", "online casino",
            "老虎机", "轮盘", "在线赌场",
            "sports betting", "体育博彩", "赌球",
            "gambling equipment", "marked cards",
        ]),
        "description": "Amazon 禁售：赌博相关产品和服务",
    },

    # ════════════════ Amazon - 虚假宣传 WARN ════════════════
    # 注意：AI文案天然带夸张，warn规则仅覆盖明确欺诈性表述
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-绝对化用语",
        "severity": "warn",
        "keywords": json.dumps([
            "#1", "number 1", "world best",
            "全球第一", "世界第一",
            "100% guarantee", "risk free", "no risk",
            "never fail", "lifetime warranty",
            "scientifically proven", "clinically proven",
            "科学证明", "临床验证",
            "no side effect", "完全安全", "100% natural",
            "无副作用", "纯天然", "无毒无害",
        ]),
        "description": "风控提醒：绝对化用语可能触发平台审核",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-虚假认证",
        "severity": "warn",
        "keywords": json.dumps([
            "fda approved", "fda certified", "fda registered",
            "fda认证", "fda批准", "fda注册",
            "ce certified", "ce approved",
            "ce认证",
            "usda organic", "gmp certified", "iso certified",
            "usda有机", "gmp认证", "iso认证",
            "假一赔命",
        ]),
        "description": "风控提醒：未经证实的认证声明",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-价格欺诈",
        "severity": "warn",
        "keywords": json.dumps([
            "free trial", "限时免费",
            "free shipping worldwide", "全球包邮",
            "lowest price", "price match",
            "最低价", "全网最低", "史上最低",
            "liquidation", "going out of business",
            "清仓", "破产", "倒闭",
            "below cost", "亏本卖",
        ]),
        "description": "风控提醒：价格误导或促销滥用",
    },

    # ════════════════ Amazon - 侵权风险 WARN ════════════════
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-品牌侵权",
        "severity": "warn",
        "keywords": json.dumps([
            "高仿", "精仿", "超A", "A货", "B货",
            "原单", "尾单", "定制同款",
            "replica", "knockoff", "knock off",
            "山寨", "仿制", "odm代工",
        ]),
        "description": "风控提醒：仿品/侵权暗示（除非持有品牌授权）",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-知名品牌",
        "severity": "warn",
        "keywords": json.dumps([
            "nike", "adidas", "gucci", "louis vuitton", "chanel",
            "hermes", "prada", "dior", "burberry", "versace",
            "apple watch", "airpods", "iphone case",
            "supreme", "off white", "balenciaga", "yeezy",
            "rolex", "omega", "cartier", "tiffany",
        ]),
        "description": "风控提醒：涉及知名品牌（除非持有官方授权）",
    },

    # ════════════════ Amazon - 违规营销 WARN ════════════════
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-评论操纵",
        "severity": "warn",
        "keywords": json.dumps([
            "刷单", "刷评", "刷销量", "刷排名",
            "fake review", "paid review", "buy review",
            "虚假评论", "好评返现", "好评有礼",
            "incentivized review", "compensated review",
            "review manipulation", "fake rating",
            "delete negative review", "删除差评",
            "hijack listing", "listing劫持",
            "空包网", "拍A发B",
        ]),
        "description": "风控提醒：评论操纵和违规推广行为",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-导流外链",
        "severity": "warn",
        "keywords": json.dumps([
            "visit my website", "go to my store",
            "访问我的网站",
            "off amazon", "outside amazon",
            "站外", "私下交易",
            "direct order", "线下交易",
        ]),
        "description": "风控提醒：向站外导流（Amazon 严格禁止）",
    },

    # ════════════════ Shopee 平台 ════════════════
    {
        "platform": "shopee",
        "rule_type": "keyword",
        "category": "违禁品",
        "severity": "block",
        "keywords": json.dumps([
            "heroin", "cocaine", "meth", "cannabis", "marijuana",
            "海洛因", "可卡因", "冰毒", "大麻", "毒品",
            "firearm", "rifle", "pistol", "ammo",
            "枪支", "手枪", "步枪", "弹药", "炸弹",
            "explosive", "bomb", "counterfeit",
            "爆炸物", "假币", "假钞", "伪造",
            "cigarette", "vape", "e-cigarette",
            "香烟", "烟草", "电子烟", "雪茄",
            "alcohol", "liquor",
            "porn", "sexual", "色情", "成人", "情趣",
            "casino", "gambl", "博彩",
            "endangered", "ivory", "濒危", "象牙", "野生动物",
            "prescription", "处方药",
            "dadah", "ganja", "syabu",
        ]),
        "description": "Shopee 平台禁售商品综合规则",
    },
    {
        "platform": "shopee",
        "rule_type": "keyword",
        "category": "风控-虚假宣传",
        "severity": "warn",
        "keywords": json.dumps([
            "#1", "第一", "最好", "绝对", "100%", "百分百",
            "guaranteed", "保证", "肯定有效",
            "fda certified", "fda认证", "ce认证",
            "高仿", "A货", "同款", "复刻", "原单",
            "刷单", "刷评", "fake review", "好评返现",
            "lowest price", "最低价", "全网最低",
        ]),
        "description": "Shopee 平台风控提醒",
    },

    # ════════════════ Lazada 平台 ════════════════
    {
        "platform": "lazada",
        "rule_type": "keyword",
        "category": "违禁品",
        "severity": "block",
        "keywords": json.dumps([
            "heroin", "cocaine", "meth", "cannabis", "marijuana",
            "海洛因", "可卡因", "冰毒", "大麻", "毒品",
            "firearm", "rifle", "pistol", "ammo",
            "枪支", "手枪", "步枪", "弹药", "炸弹",
            "explosive", "bomb", "counterfeit",
            "爆炸物", "假币", "假钞", "伪造",
            "cigarette", "vape", "e-cigarette",
            "香烟", "烟草", "电子烟", "雪茄",
            "alcohol", "liquor",
            "porn", "sexual", "色情", "成人", "情趣",
            "casino", "gambl", "博彩",
            "endangered", "ivory", "濒危", "象牙", "野生动物",
            "prescription", "处方药",
            "dadah", "ganja", "syabu",
        ]),
        "description": "Lazada 平台禁售商品综合规则",
    },
    {
        "platform": "lazada",
        "rule_type": "keyword",
        "category": "风控-虚假宣传",
        "severity": "warn",
        "keywords": json.dumps([
            "#1", "第一", "最好", "绝对", "100%", "百分百",
            "guaranteed", "保证", "肯定有效",
            "fda certified", "fda认证", "ce认证",
            "高仿", "A货", "同款", "复刻", "原单",
            "刷单", "刷评", "fake review", "好评返现",
            "lowest price", "最低价", "全网最低",
        ]),
        "description": "Lazada 平台风控提醒",
    },
]


def seed_rules(db: Session, reset: bool = False):
    """插入/更新默认规则"""
    if reset:
        platforms = {"amazon", "shopee", "lazada"}
        deleted = db.query(PlatformRule).filter(
            PlatformRule.platform.in_(platforms)
        ).delete(synchronize_session=False)
        db.commit()
        print(f"已清除旧规则: {deleted} 条")

    inserted = 0
    updated = 0
    skipped = 0

    for rule_data in RULES:
        existing = db.query(PlatformRule).filter(
            PlatformRule.platform == rule_data["platform"],
            PlatformRule.category == rule_data["category"],
            PlatformRule.rule_type == rule_data["rule_type"],
            PlatformRule.severity == rule_data["severity"],
        ).first()

        if existing:
            if reset:
                existing.keywords = rule_data["keywords"]
                existing.description = rule_data["description"]
                updated += 1
            else:
                skipped += 1
            continue

        rule = PlatformRule(**rule_data)
        db.add(rule)
        inserted += 1

    db.commit()
    return inserted, updated, skipped


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    db = next(get_db())
    try:
        inserted, updated, skipped = seed_rules(db, reset=reset)
        print(f"规则入库: 新增 {inserted} 条, 更新 {updated} 条, 跳过 {skipped} 条")

        print("\n=== Amazon 审核规则 ===")
        rules = db.query(PlatformRule).filter(
            PlatformRule.platform == "amazon",
            PlatformRule.is_active == True
        ).order_by(PlatformRule.severity, PlatformRule.category).all()

        block_count = warn_count = 0
        for r in rules:
            if r.severity == "block":
                block_count += 1
            else:
                warn_count += 1
            keywords = json.loads(r.keywords) if r.keywords else []
            kw_preview = ", ".join(keywords[:6])
            if len(keywords) > 6:
                kw_preview += f" ...(+{len(keywords) - 6})"
            print(f"  [{r.severity.upper():5s}] {r.category:16s} | {kw_preview}")

        total_kw = sum(len(json.loads(r.keywords)) for r in rules if r.keywords)
        print(f"\n统计: {block_count} 条 block + {warn_count} 条 warn = {len(rules)} 条规则, 共 {total_kw} 个关键词")
    finally:
        db.close()
