"""
种子脚本：初始化平台审核规则
运行方式:
  uv run python scripts/seed_moderation_rules.py          # 追加模式（跳过已存在的）
  uv run python scripts/seed_moderation_rules.py --reset  # 重置模式（先删后插）
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.database import get_db
from models.moderation import PlatformRule
from sqlalchemy.orm import Session

# ============================================================
# 审核规则定义
# 设计原则：
#   1. 使用最短词根匹配最大范围（如 "drug" 可匹配 drugs/drugged）
#   2. 中英文双语覆盖
#   3. 覆盖常见绕词和变体（如空格分隔、符号替换）
#   4. block = 绝对拦截，warn = 警告但可人工审核后放行
# ============================================================

RULES = [
    # ==================== Amazon - 违禁商品 (block) ====================
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-毒品",
        "severity": "block",
        "keywords": json.dumps([
            # 英文（词根匹配）
            "drug", "heroin", "cocaine", "meth", "fentanyl", "narcotic",
            "opioid", "opium", "morphine", "cannabis", "marijuana",
            "weed", "lsd", "ecstasy", "mdma", "ketamine", "amphetamine",
            "steroid", "crack", "thc", "psychedelic", "hallucinogen",
            # 中文（单字+多字覆盖）
            "毒", "大麻", "鸦片", "吗啡", "海洛因", "可卡因",
            "冰毒", "摇头丸", "迷幻药", "致幻剂", "麻古", "丧尸药",
            "吸毒", "毒品", "药物滥用", "麻醉药品",
            # 绕词/变体
            "d r u g", "dr ug", "d.r.u.g", "narcotics",
            "class a drug", "controlled substance",
        ]),
        "description": "Amazon 禁售：毒品、管制药物、精神活性物质",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-武器",
        "severity": "block",
        "keywords": json.dumps([
            "weapon", "gun", "firearm", "rifle", "pistol", "shotgun",
            "ammo", "ammunition", "bullet", "explosive", "bomb",
            "dynamite", "grenade", "mine", "detonator", "taser",
            "pepper spray", "stun gun", "switchblade", "brass knuckles",
            "武器", "枪支", "手枪", "步枪", "冲锋枪", "弹药",
            "子弹", "炸弹", "爆炸物", "雷管", "弩", "弓",
            "电击器", "催泪", "军刀", "指虎",
            "arm", "armed", "militia", "insurgent", "terrorist",
        ]),
        "description": "Amazon 禁售：武器、弹药、爆炸物及配件",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-假货伪造",
        "severity": "block",
        "keywords": json.dumps([
            "counterfeit", "fake", "replica", "knockoff", "clone",
            "imitation", "copycat", "not genuine", "not authentic",
            "假", "仿", "高仿", "精仿", "A货", "B货", "超A",
            "同款不同厂", "复刻", "定制同款", "原单", "尾单",
            "fake id", "fake passport", "fake document",
            "假证", "假护照", "假身份证", "假学历", "假文凭",
            "degree for sale", "buy diploma",
        ]),
        "description": "Amazon 禁售：假冒伪劣商品、伪造证件",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-烟酒",
        "severity": "block",
        "keywords": json.dumps([
            "tobacco", "cigarette", "cigar", "vape", "e-cigarette",
            "e-liquid", "vaping", "hookah", "shisha", "nicotine",
            "烟", "香烟", "雪茄", "电子烟", "烟油", "水烟",
            "尼古丁", "烟草", "卷烟",
            "alcohol", "liquor", "whiskey", "vodka", "beer", "wine",
            "酒", "白酒", "啤酒", "红酒", "洋酒", "烈酒", "酒精",
        ]),
        "description": "Amazon 禁售：烟草制品及电子烟、酒类",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-人体器官",
        "severity": "block",
        "keywords": json.dumps([
            "organ", "kidney", "liver", "heart", "lung",
            "human trafficking", "slave", "slavery", "forced labor",
            "器官", "肾", "肝脏", "心脏", "移植",
            "人口贩卖", "贩卖人口", "强迫劳动", "奴役",
            "body part", "blood", "plasma", "sperm", "egg donor",
        ]),
        "description": "Amazon 禁售：人体器官、人口贩卖、人体组织",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-危险品",
        "severity": "block",
        "keywords": json.dumps([
            "hazardous", "toxic", "poison", "cyanide", "arsenic",
            "mercury", "asbestos", "lead", "radioactive", "uranium",
            "有毒", "毒药", "砒霜", "氰化物", "水银", "汞",
            "石棉", "放射性", "铀", "铅",
            "acid", "chemical", "flammable", "corrosive",
            "硫酸", "硝酸", "易燃", "易爆", "腐蚀",
            "pesticide", "insecticide", "herbicide", "rodenticide",
            "农药", "杀虫剂", "除草剂", "老鼠药",
        ]),
        "description": "Amazon 禁售：危险品、有毒化学品、农药",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-野生动物",
        "severity": "block",
        "keywords": json.dumps([
            "ivory", "elephant", "rhino", "tiger", "shark fin",
            "pangolin", "sea turtle", "coral", "whale",
            "象牙", "犀牛", "虎骨", "鱼翅", "穿山甲", "海龟",
            "珊瑚", "鲸", "熊胆", "麝香", "羚羊角",
            "endangered", "protected species", "wild animal product",
            "濒危", "野生动物", "保护动物", "活体动物",
            "exotic pet", "tropical bird", "monkey", "primate",
        ]),
        "description": "Amazon 禁售：濒危野生动物及其制品",
    },

    # ==================== Amazon - 药品医疗 (block) ====================
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "医疗-处方药",
        "severity": "block",
        "keywords": json.dumps([
            "prescription", "rx only", "antibiotic", "antibiotics",
            "处方", "处方药", "抗生素", "消炎药", "激素",
            "安眠药", "镇定", "抗抑郁", "抗焦虑", "精神类药物",
            "ozempic", "wegovy", "viagra", "cialis", "xanax",
            "adderall", "valium", "ambien", "codeine", "tramadol",
            "伟哥", "西力士", "减肥针", "司美格鲁肽",
            "没有处方", "无需处方", "代购处方",
            "online pharmacy", "pharmacy without prescription",
        ]),
        "description": "Amazon 禁售：处方药及无需处方的药品销售",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "医疗-虚假疗效",
        "severity": "block",
        "keywords": json.dumps([
            "cure cancer", "cure disease", "cure all", "miracle",
            "奇迹", "神药", "特效药", "包治", "根治",
            "治愈癌症", "治疗艾滋", "艾滋病治愈", "治愈新冠",
            "cancer treatment", "hiv cure", "covid cure",
            "medical breakthrough", "secret formula", "ancient remedy",
            "祖传秘方", "民间偏方", "秘方", "灵丹妙药",
            "stem cell therapy", "干细胞治疗", "基因治疗",
        ]),
        "description": "Amazon 禁售：夸大疗效的虚假医疗宣传",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "医疗-未批准器械",
        "severity": "block",
        "keywords": json.dumps([
            "medical device", "surgical", "implant", "prosthetic",
            "医疗器械", "手术器械", "植入物", "假体",
            "diagnostic test", "blood test", "covid test",
            "检测试剂", "诊断试剂", "核酸检测", "抗原检测",
            "cpap", "ventilator", "defibrillator", "pacemaker",
            "呼吸机", "除颤器", "起搏器",
            "not fda", "未经fda", "fda pending", "ce mark",
        ]),
        "description": "Amazon 禁售：未经批准的医疗器械",
    },

    # ==================== Amazon - 仇恨/歧视 (block) ====================
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违规-仇恨言论",
        "severity": "block",
        "keywords": json.dumps([
            "hate", "racist", "racism", "nazi", "kkk", "supremacist",
            "种族歧视", "种族主义", "纳粹", "白人至上",
            "genocide", "holocaust", "ethnic cleansing",
            "种族灭绝", "大屠杀", "种族清洗",
            "slur", "derogatory", "offensive",
            "歧视", "侮辱", "诽谤", "贬低",
            "terrorist", "terrorism", "isis", "al qaeda",
            "恐怖主义", "恐怖分子", "圣战",
        ]),
        "description": "Amazon 禁售：仇恨言论、种族歧视、恐怖主义相关",
    },

    # ==================== Amazon - 成人内容 (block) ====================
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违规-成人色情",
        "severity": "block",
        "keywords": json.dumps([
            "porn", "xxx", "sexual", "erotic", "explicit",
            "色情", "成人", "裸露", "裸体", "淫秽", "情色",
            "sex toy", "vibrator", "dildo", "adult toy",
            "情趣", "震动棒", "自慰", "成人用品", "性用品",
            "escort", "prostitute", "sex service", "massage parlor",
            "escort服务", "卖淫", "嫖娼", "小姐", "上门服务",
            "onlyfans", "nsfw", "nude", "naked",
        ]),
        "description": "Amazon 禁售：成人色情内容及服务",
    },

    # ==================== Amazon - 赌博 (block) ====================
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违规-赌博",
        "severity": "block",
        "keywords": json.dumps([
            "casino", "gambl", "betting", "lottery", "poker",
            "赌", "博彩", "彩票", "下注", "德州扑克",
            "slot machine", "roulette", "blackjack", "baccarat",
            "老虎机", "轮盘", "二十一点", "百家乐",
            "sports betting", "race betting", "horse racing",
            "体育博彩", "赌马", "赛马", "赌球",
            "online casino", "live casino", "dealer",
            "在线赌场", "真人赌场", "庄家",
            "gambling equipment", "marked cards", "loaded dice",
        ]),
        "description": "Amazon 禁售：赌博相关产品和服务",
    },

    # ==================== Amazon - 虚假宣传 (warn) ====================
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-绝对化用语",
        "severity": "warn",
        "keywords": json.dumps([
            "#1", "number 1", "no.1", "no 1", "world best",
            "全球第一", "世界第一", "行业第一", "第一品牌",
            "100% guarantee", "guaranteed", "risk free", "no risk",
            "百分百", "100%", "绝对", "肯定", "必然", "必定",
            "never fail", "never break", "lifetime warranty",
            "永远不会", "终身保修", "永不坏",
            "best in class", "best on market", "unbeatable",
            "最好的", "无人能敌", "无与伦比", "绝无仅有",
            "only product", "only solution", "only way",
            "唯一的", "仅有的", "独一无二",
            "scientifically proven", "clinically proven",
            "科学证明", "临床验证", "实验证明",
            "no side effect", "completely safe", "100% natural",
            "无副作用", "完全安全", "纯天然", "无毒无害",
        ]),
        "description": "风控提醒：绝对化用语可能触发平台审核或下架",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-虚假认证",
        "severity": "warn",
        "keywords": json.dumps([
            "fda approved", "fda certified", "fda registered",
            "fda认证", "fda批准", "fda注册",
            "ce certified", "ce approved", "rohs certified",
            "ce认证", "rohs认证",
            "usda organic", "gmp certified", "iso certified",
            "usda有机", "gmp认证", "iso认证",
            "organic certified", "non gmo verified",
            "有机认证", "非转基因认证",
            "dermatologist tested", "clinically tested",
            "皮肤科测试", "临床测试",
            "certified safe", "certified quality",
            "质量认证", "安全认证",
        ]),
        "description": "风控提醒：未经证实的认证声明（除非持有相应证书）",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-价格欺诈",
        "severity": "warn",
        "keywords": json.dumps([
            "free trial", "free sample", "free gift",
            "免费试用", "免费样品", "免费礼品", "免费赠送",
            "限时免费", "0元", "免费领取",
            "lowest price", "price match", "best deal",
            "最低价", "全网最低", "史上最低", "抄底价",
            "liquidation", "going out of business",
            "清仓", "破产", "倒闭", "亏本", "跳楼价",
            "buy one get", "bogo", "free shipping worldwide",
            "买一送", "买二送", "全球包邮",
        ]),
        "description": "风控提醒：价格误导或促销滥用",
    },

    # ==================== Amazon - 侵权风险 (warn) ====================
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-品牌侵权",
        "severity": "warn",
        "keywords": json.dumps([
            "仿", "高仿", "精仿", "超A", "原单", "尾单",
            "同款", "复刻", "定制款", "原版", "定制同款",
            "A货", "B货", "水货", "港版", "海外版",
            "replica", "knock off", "knockoff", "look alike",
            "inspired by", "similar to", "like nike", "like apple",
            "仿制", "山寨", "国产替代", "平替",
            "oem", "odm代工",
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
            "lego", "disney", "marvel", "star wars", "pokemon",
            "hello kitty", "snoopy", "mickey", "minions",
            "rolex", "omega", "cartier", "tiffany",
        ]),
        "description": "风控提醒：涉及知名品牌（除非持有官方授权）",
    },

    # ==================== Amazon - 违规营销 (warn) ====================
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-评论操纵",
        "severity": "warn",
        "keywords": json.dumps([
            "刷单", "刷评", "刷销量", "刷排名",
            "fake review", "paid review", "buy review",
            "虚假评论", "好评返现", "返现卡", "好评有礼",
            "5 star review", "positive review", "verified review",
            "五星好评", "五星评价", "好评", "加微信好评",
            "incentivized review", "compensated review",
            "review manipulation", "fake rating",
            "upvote", "downvote manipulation",
            "rank boosting", "listing optimization hack",
            "hijack listing", "listing劫持", "抢listing",
            "suppress negative", "remove bad review",
            "删除差评", "改差评", "删差评",
        ]),
        "description": "风控提醒：评论操纵和违规推广行为",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-导流外链",
        "severity": "warn",
        "keywords": json.dumps([
            "visit my website", "go to my store", "click link",
            "访问我的网站", "点击链接", "扫码", "微信",
            "whatsapp", "telegram", "wechat", "line",
            "添加微信", "加好友", "联系我", "私信",
            "off amazon", "outside amazon", "direct order",
            "站外", "线下", "私下交易",
            "email me", "call me", "text me",
        ]),
        "description": "风控提醒：向站外导流（Amazon 严格禁止）",
    },

    # ==================== Shopee 平台 ====================
    {
        "platform": "shopee",
        "rule_type": "keyword",
        "category": "违禁品",
        "severity": "block",
        "keywords": json.dumps([
            "drug", "heroin", "cocaine", "meth", "cannabis", "marijuana",
            "毒", "毒品", "大麻", "海洛因", "可卡因", "冰毒",
            "weapon", "gun", "firearm", "rifle", "pistol", "ammo",
            "武器", "枪支", "手枪", "步枪", "弹药", "炸弹",
            "explosive", "bomb", "counterfeit", "replica",
            "爆炸物", "假币", "假钞", "伪造",
            "tobacco", "cigarette", "vape", "e-cigarette",
            "香烟", "烟草", "电子烟", "雪茄",
            "alcohol", "liquor", "酒", "酒精",
            "porn", "sexual", "色情", "成人", "情趣",
            "casino", "gambl", "赌", "博彩",
            "endangered", "ivory", "濒危", "象牙", "野生动物",
            "prescription", "rx", "处方", "处方药",
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
            "仿", "高仿", "A货", "同款", "复刻", "原单",
            "replica", "knockoff",
            "刷单", "刷评", "fake review", "好评返现",
            "lowest price", "最低价", "全网最低",
        ]),
        "description": "Shopee 平台风控提醒",
    },

    # ==================== Lazada 平台 ====================
    {
        "platform": "lazada",
        "rule_type": "keyword",
        "category": "违禁品",
        "severity": "block",
        "keywords": json.dumps([
            "drug", "heroin", "cocaine", "meth", "cannabis", "marijuana",
            "毒", "毒品", "大麻", "海洛因", "可卡因", "冰毒",
            "weapon", "gun", "firearm", "rifle", "pistol", "ammo",
            "武器", "枪支", "手枪", "步枪", "弹药", "炸弹",
            "explosive", "bomb", "counterfeit", "replica",
            "爆炸物", "假币", "假钞", "伪造",
            "tobacco", "cigarette", "vape", "e-cigarette",
            "香烟", "烟草", "电子烟", "雪茄",
            "alcohol", "liquor", "酒", "酒精",
            "porn", "sexual", "色情", "成人", "情趣",
            "casino", "gambl", "赌", "博彩",
            "endangered", "ivory", "濒危", "象牙", "野生动物",
            "prescription", "rx", "处方", "处方药",
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
            "仿", "高仿", "A货", "同款", "复刻", "原单",
            "replica", "knockoff",
            "刷单", "刷评", "fake review", "好评返现",
            "lowest price", "最低价", "全网最低",
        ]),
        "description": "Lazada 平台风控提醒",
    },
]


def seed_rules(db: Session, reset: bool = False):
    """插入/更新默认规则"""
    if reset:
        # 清除目标平台的旧规则
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
                # 重置模式下不会走到这里（已被删除），但保留兼容
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
