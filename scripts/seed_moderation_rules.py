"""
种子脚本：初始化平台审核规则
运行方式:
  uv run python scripts/seed_moderation_rules.py          # 追加模式（跳过已存在的）
  uv run python scripts/seed_moderation_rules.py --reset  # 重置模式（先删后插）

匹配引擎（services/rule_engine.py）已升级：
  - ASCII 关键词 → \b 词边界匹配（drug 不命中 drugstore）
  - CJK 单字 → 自动跳过（"核"不命中"核心"）
  - 含空格变体 → 规范化后匹配（"d r u g" → "drug"）
  - CJK 多字 → 子串匹配（中文无英文式复合词问题）
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.database import get_db
from models.moderation import PlatformRule
from sqlalchemy.orm import Session

RULES = [
    # ════════════════ Amazon - 违禁商品 BLOCK ════════════════
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-毒品",
        "severity": "block",
        "keywords": json.dumps([
            "heroin", "cocaine", "meth", "fentanyl", "narcotic",
            "opioid", "opium", "morphine", "cannabis", "marijuana",
            "weed", "lsd", "ecstasy", "mdma", "ketamine", "amphetamine",
            "steroid", "crack", "thc", "psychedelic", "hallucinogen",
            "海洛因", "可卡因", "冰毒", "大麻", "鸦片", "吗啡",
            "摇头丸", "迷幻药", "致幻剂", "麻古", "丧尸药",
            "吸毒", "毒品", "药物滥用", "麻醉药品",
            "d r u g", "d.r.u.g", "controlled substance", "class a drug",
            "coke", "dope", "hashish", "kush",
            "溜冰", "煲猪肉", "白粉", "k粉", "神仙水", "笑气",
            "嗑药", "溜粉", "追龙", "吹泡泡",
            "上头电子烟", "电子烟油上头",
            "迷魂药", "听话水", "乖乖水", "迷情水", "失身酒",
            "kratom", "迷幻蘑菇", "magic mushroom",
            "毒邮票", "贴纸毒品", "开心粉", "奶茶粉",
            "一粒眠", "蓝精灵", "犀牛液",
            "上瘾", "成瘾", "戒毒", "毒瘾",
        ]),
        "description": "Amazon 禁售：毒品、管制药物、精神活性物质",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-武器",
        "severity": "block",
        "keywords": json.dumps([
            "gun", "firearm", "rifle", "pistol", "shotgun",
            "ammo", "ammunition", "bullet", "explosive", "bomb",
            "dynamite", "grenade", "mine", "detonator", "taser",
            "pepper spray", "stun gun", "switchblade", "brass knuckles",
            "枪支", "手枪", "步枪", "冲锋枪", "弹药",
            "子弹", "炸弹", "爆炸物", "雷管", "弩", "弓",
            "电击器", "催泪", "军刀", "指虎",
            "armed", "militia", "insurgent", "terrorist",
            "machete", "flamethrower", "silencer", "suppressor",
            "消音器", "砍刀", "军火", "枪械", "枪支配件",
            "airsoft", "bb gun", "pellet gun", "弹弓",
            "assault rifle", "machine gun", "机关枪",
            "homemade gun", "3d printed gun", "自制枪",
            "c4", "semtex", "塑料炸药",
            "管制刀具", "仿真枪", "电棍", "电击棒", "狼牙棒",
            "双节棍", "三棱刀", "弹簧刀", "蝴蝶刀",
            "军刺", "刺刀", "匕首",
            "防身喷雾", "防狼喷雾", "辣椒水",
            "手铐", "脚镣", "警用", "警械",
            "枪模", "打火机枪", "钥匙扣枪",
            "气枪", "铅弹", "气罐", "高压气瓶",
            "弓弩", "复合弓", "反曲弓", "十字弓",
            "火狗", "气狗",
        ]),
        "description": "Amazon 禁售：武器、弹药、爆炸物及配件",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-假货伪造",
        "severity": "block",
        "keywords": json.dumps([
            "counterfeit", "knockoff", "clone",
            "imitation", "copycat", "not genuine", "not authentic",
            "高仿", "精仿", "A货", "B货", "超A",
            "同款不同厂", "复刻", "定制同款", "原单", "尾单",
            "fake id", "fake passport", "fake document",
            "假证", "假护照", "假身份证", "假学历", "假文凭",
            "degree for sale", "buy diploma",
            "假币", "假钞", "假发票", "假合同",
            "counterfeit money", "prop money",
            "unlicensed", "未授权", "无授权", "非官方",
            "莆田货", "白云皮具", "华强北", "档口货",
            "仿冒", "冒牌", "假货", "赝品",
            "山寨版", "山寨货", "1:1", "一比一",
            "精工", "顶级复刻", "原版复刻",
            "出入专柜", "专柜验货", "过验", "过鉴定",
            "裸鞋", "裸包", "原盒", "配盒",
            "顶级版本", "完美版本", "市面最高",
            "办证", "刻章", "印章", "证照制作",
            "广东货", "浙江货", "河北货",
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
            "e-liquid", "vaping", "hookah", "nicotine",
            "香烟", "雪茄", "电子烟", "烟油", "水烟",
            "尼古丁", "烟草", "卷烟",
            "alcohol", "liquor", "whiskey", "vodka", "beer", "wine",
            "白酒", "啤酒", "红酒", "洋酒", "烈酒", "酒精",
            "大麻烟", "电子雾化器", "iqos", "加热不燃烧",
            "嚼烟", "鼻烟", "烟丝", "烟斗", "手卷烟",
            "moonshine", "自酿酒", "homebrew", "蒸馏酒",
            "absinthe", "苦艾酒", "高度酒", "原浆酒",
            "juul", "puff bar", "disposable vape", "一次性电子烟",
            "散烟", "拆烟", "烟弹", "电子烟弹",
            "外烟", "韩免", "日免",
            "爆珠", "薄荷烟", "果味烟",
            "自酿", "散装酒", "桶装酒",
        ]),
        "description": "Amazon 禁售：烟草制品及电子烟、酒类",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "违禁品-人体器官",
        "severity": "block",
        "keywords": json.dumps([
            "human trafficking", "slave", "slavery", "forced labor",
            "器官", "人口贩卖", "贩卖人口", "强迫劳动", "奴役",
            "organ trafficking", "器官买卖",
            "卖血", "卖肾", "卖身",
            "surrogacy", "surrogate mother",
            "代孕", "代孕妈妈",
            "捐卵", "供卵",
            "adoption for sale", "买孩子", "卖孩子", "婴儿贩卖",
            "地下代孕", "非法代孕", "有偿捐卵",
            "黑市器官",
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
            "mercury", "asbestos", "radioactive", "uranium",
            "氰化物", "砒霜", "水银", "汞", "石棉", "放射性", "铀",
            "acid", "flammable", "corrosive",
            "硫酸", "硝酸", "易燃", "易爆", "腐蚀",
            "pesticide", "insecticide", "herbicide", "rodenticide",
            "农药", "杀虫剂", "除草剂", "老鼠药",
            "bioweapon", "化学武器", "芥子气",
            "vx", "sarin", "神经毒剂",
            "chlorine gas", "氯气", "炭疽",
            "烟花爆竹", "鞭炮", "礼花",
            "汽油", "柴油", "煤油", "液化气",
            "剧毒", "放射", "辐射", "nuclear",
            "毒鼠强", "百草枯", "敌敌畏", "甲胺磷",
            "呋喃丹", "磷化铝", "磷化锌",
            "强酸", "强碱", "烧碱", "火碱",
            "香蕉水", "天那水", "有机溶剂",
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
            "coral", "whale",
            "象牙", "犀牛", "虎骨", "鱼翅", "穿山甲", "海龟",
            "珊瑚", "鲸", "熊胆", "麝香", "羚羊角",
            "endangered", "protected species", "wild animal product",
            "濒危", "野生动物", "野生动物制品",
            "穿山甲鳞片", "虎鞭", "熊掌",
            "冬虫夏草", "雪蛤", "鹿茸", "藏羚羊",
            "鲨鱼", "海马", "玳瑁", "tortoise",
            "蛇胆", "蛇皮", "鳄鱼皮",
            "动物标本", "taxidermy",
            "禁猎", "偷猎", "盗猎", "poaching",
            "野味", "吃野味", "野货",
            "穿山甲肉", "果子狸", "猴脑",
            "娃娃鱼", "大鲵", "中华鲟", "刀鱼",
            "天鹅", "丹顶鹤", "朱鹮", "金丝猴", "大熊猫",
            "活体", "活体快递", "活体运输",
            "斗狗", "斗鸡", "斗牛", "动物搏斗",
            "捕兽夹", "捕鸟网", "猎套",
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
            "prescription", "rx only", "antibiotic",
            "处方药", "抗生素", "消炎药", "安眠药",
            "精神类药物", "抗抑郁", "抗焦虑",
            "ozempic", "wegovy", "adderall", "codeine", "tramadol",
            "xanax", "valium", "ambien", "viagra", "cialis",
            "oxycontin", "oxycodone", "percocet", "fentanyl patch",
            "伟哥", "西力士", "司美格鲁肽", "芬太尼贴",
            "没有处方", "无需处方", "代购处方",
            "online pharmacy", "pharmacy without prescription",
            "买药", "卖药", "药品代购", "印度仿制药", "走私药",
            "医院代开", "代开处方", "套取处方",
            "印度直邮", "土耳其直邮", "泰国代购药",
            "疫苗代购", "hpv疫苗代购", "九价代购",
            "肉毒素", "玻尿酸", "水光针", "溶脂针",
            "童颜针", "美白针", "瘦脸针",
            "人血白蛋白", "免疫球蛋白",
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
            "治愈癌症", "治疗艾滋", "艾滋病治愈", "治愈新冠",
            "hiv cure", "covid cure", "cancer cure",
            "包治", "根治", "神药", "灵丹妙药",
            "祖传秘方", "民间偏方", "秘方",
            "stem cell therapy", "干细胞治疗", "基因治疗",
            "保证治愈", "无效退款", "不愈包退", "包治好",
            "药到病除", "治百病", "立竿见影",
            "magic pill", "神奇药丸", "万能药", "仙丹",
            "排毒", "清肠", "净化", "酸碱体质",
            "神油", "印度神油", "增大", "增粗", "延时",
            "老军医", "中医世家", "祖传", "御医秘方",
            "藏药", "苗药", "彝药", "蒙药", "傣药",
            "辟谷", "断食", "生酮抗癌", "饥饿疗法",
            "碱性体质", "酸性体质", "排酸",
            "磁疗", "频谱", "太赫兹",
            "量子医学", "量子检测", "量子植入",
            "能量石", "能量手环", "能量项链",
            "保健酒", "药酒", "壮阳酒", "补肾酒",
            "增高药", "增高贴",
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
            "not fda", "未经fda", "fda pending",
            "假肢", "义肢", "助听器", "hearing aid",
            "注射器", "syringe", "needle",
            "血糖仪", "血压计", "血氧仪",
            "手术刀", "手术钳", "手术缝线",
            "输液器", "输液管", "catheter", "导尿管",
            "美容仪", "激光脱毛", "ipl", "射频美容",
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
            "slur", "derogatory", "offensive",
            "歧视", "侮辱", "诽谤", "贬低",
            "terrorist", "terrorism", "isis", "al qaeda",
            "恐怖主义", "恐怖分子", "圣战",
            "hate speech", "仇恨言论",
            "swastika", "万字旗", "卐",
            "white power", "black power supremacy",
            "种族清洗", "种族隔离", "apartheid",
            "支那", "蝗虫", "白皮猪", "黑鬼",
            "小日本", "棒子", "毛子", "越南猴子",
            "台独", "藏独", "疆独", "港独",
            "法轮", "falun", "大法",
            "六四", "天安门", "吃人血馒头",
            "地域黑", "井盖", "外地的",
            "屌丝", "loser",
            "homophobic", "transphobic",
            "xenophobic", "islamophobic",
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
            "porn", "xxx", "sexual", "erotic", "explicit",
            "色情", "淫秽", "情色", "成人", "裸露", "裸体",
            "sex toy", "vibrator", "dildo",
            "情趣", "震动棒", "自慰器", "成人用品", "性用品",
            "escort", "prostitute", "sex service",
            "卖淫", "嫖娼", "小姐", "上门服务",
            "onlyfans", "nsfw", "nude", "naked",
            "裸照", "露点", "走光", "偷拍", "偷窥",
            "voyeur", "upskirt", "hidden camera",
            "hentai", "里番", "福利姬", "福利视频",
            "约炮", "援交", "sugar daddy", "sugar baby",
            "一夜情", "hookup", "dating for sex",
            "sex doll", "充气娃娃", "实体娃娃",
            "催情药", "迷奸", "春药", "aphrodisiac",
            "性虐待", "bdsm", "捆绑", "鞭打",
            "外围女", "商务伴游",
            "楼凤", "大保健", "全套", "包夜",
            "黄片", "毛片", "av", "无码", "中出",
            "制服诱惑", "巨乳", "爆乳",
            "大尺度", "限制级", "禁播",
            "色图", "福利图", "套图", "私房照",
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
            "casino", "gambl", "betting", "lottery", "poker",
            "博彩", "赌场", "彩票", "下注", "德州扑克",
            "slot machine", "roulette", "blackjack", "baccarat",
            "老虎机", "轮盘", "二十一点", "百家乐",
            "sports betting", "race betting", "horse racing",
            "体育博彩", "赌马", "赌球",
            "online casino", "live casino",
            "在线赌场", "真人赌场",
            "gambling equipment", "marked cards", "loaded dice",
            "六合彩", "时时彩", "北京赛车", "pk10",
            "骰子", "骰宝", "竞猜", "押注", "盘口", "赔率",
            "棋牌", "电玩城", "捕鱼",
            "变相赌博", "赌资", "赌金",
            "信用网", "现金网", "投注网",
            "菠菜", "网投", "电投",
            "现金棋牌", "真金棋牌", "捕鱼游戏",
        ]),
        "description": "Amazon 禁售：赌博相关产品和服务",
    },

    # ════════════════ Amazon - 虚假宣传 WARN ════════════════
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-绝对化用语",
        "severity": "warn",
        "keywords": json.dumps([
            "#1", "number 1", "world best",
            "全球第一", "世界第一", "行业第一",
            "100% guarantee", "risk free", "no risk",
            "百分百", "绝对", "肯定", "必然",
            "never fail", "never break", "lifetime warranty",
            "终身保修", "永不坏",
            "best in class", "unbeatable",
            "无人能敌", "无与伦比", "绝无仅有",
            "only product", "only solution", "only way",
            "科学证明", "临床验证", "实验证明",
            "no side effect", "completely safe", "100% natural",
            "无副作用", "完全安全", "纯天然", "无毒无害",
            "零风险", "零失败", "万无一失",
            "一劳永逸", "包满意",
            "秒杀一切", "吊打同行",
            "永久有效", "永久免费", "终生免费",
            "治愈", "根治", "永不复发",
            "不含任何化学成分", "零添加",
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
            "ce认证", "rohs认证",
            "usda organic", "gmp certified", "iso certified",
            "usda有机", "gmp认证", "iso认证",
            "organic certified", "non gmo verified",
            "有机认证", "非转基因认证",
            "certified safe", "certified quality",
            "质量认证", "安全认证",
            "假一赔十", "假一赔命",
            "官方认证", "正品保证", "原装正品",
            "支持专柜验", "支持验货",
            "进口报关", "海关进口", "报关单",
        ]),
        "description": "风控提醒：未经证实的认证声明",
    },
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-价格欺诈",
        "severity": "warn",
        "keywords": json.dumps([
            "free trial", "free sample", "free gift",
            "免费试用", "免费样品", "免费礼品", "免费赠送",
            "lowest price", "price match", "best deal",
            "最低价", "全网最低", "史上最低",
            "liquidation", "going out of business",
            "清仓", "破产", "倒闭", "亏本", "跳楼价",
            "free shipping worldwide", "全球包邮",
            "买一送", "买二送",
            "血亏", "吐血", "甩卖", "抛售",
            "厂家直销", "工厂价", "出厂价", "批发价",
            "内部价", "关系价", "员工价",
            "bug价", "漏洞价",
            "亏本冲量", "引流价", "福利单",
            "亏钱冲销量", "只为好评",
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
            "原单", "尾单", "定制同款", "同款不同厂",
            "replica", "knock off", "knockoff", "look alike",
            "inspired by", "similar to", "like nike", "like apple",
            "仿制", "山寨", "国产替代", "平替",
            "oem", "odm代工",
            "仿冒", "冒牌", "假货", "赝品",
            "山寨版", "山寨货",
            "代购", "海淘", "原厂",
            "出口转内销", "外贸原单",
            "工厂尾单", "品牌尾货", "跟单",
            "老鼠货", "试产货",
            "剪标", "去标", "换标",
            "致敬款", "复刻致敬", "一比一复刻",
            "平价款", "平价替代", "大牌平替",
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

    # ════════════════ Amazon - 违规营销 WARN ════════════════
    {
        "platform": "amazon",
        "rule_type": "keyword",
        "category": "风控-评论操纵",
        "severity": "warn",
        "keywords": json.dumps([
            "刷单", "刷评", "刷销量", "刷排名",
            "fake review", "paid review", "buy review",
            "虚假评论", "好评返现", "返现卡", "好评有礼",
            "incentivized review", "compensated review",
            "review manipulation", "fake rating",
            "赞", "downvote manipulation",
            "rank boosting", "listing optimization hack",
            "hijack listing", "listing劫持", "抢listing",
            "suppress negative", "remove bad review",
            "删除差评", "改差评", "删差评",
            "好评返", "五星返", "现金返", "红包",
            "有偿好评", "shua单", "s单", "空包", "礼品单",
            "review exchange", "互评",
            "僵尸评论", "机刷", "免评",
            "合并listing", "merge listing", "变体合并",
            "feedback manipulation", "feedback removal",
            "买号", "买家号", "白号", "养号",
            "放单", "接单", "做单", "佣金单",
            "拍A发B", "空包网", "代发空包", "礼品网",
            "留评", "点星", "上星", "qa操纵",
            "刷单团队", "佣金任务",
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
            "访问我的网站", "点击链接",
            "whatsapp", "telegram", "wechat", "line",
            "添加微信", "加好友", "联系我", "私信",
            "off amazon", "outside amazon", "direct order",
            "站外", "私下交易",
            "email me", "call me", "text me",
            "加v", "加q", "qq", "微信支付", "支付宝",
            "私聊", "面交", "当面交易",
            "薇信", "vx", "v信",
            "instagram", "facebook", "messenger",
            "tiktok", "抖音", "小红书", "快手",
            "discord", "skype", "snapchat",
            "独立站", "官方网站", "官网下单",
            "线下门店", "实体店", "上门自取",
            "扫码加", "扫一扫", "二维码",
            "私信拿链接", "私信有优惠",
            "评论区找我", "评论区有惊喜",
            "有兴趣的私", "有意私聊",
            "拼多多", "淘宝", "天猫", "京东",
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
            "casino", "gambl", "博彩", "赌场",
            "endangered", "ivory", "濒危", "象牙", "野生动物",
            "prescription", "处方药",
            "dadah", "ganja", "syabu", "pil kuda",
            "senjata api", "senjata tajam",
            "minuman keras", "minuman beralkohol",
            "obat keras", "obat tanpa resep",
            "barang tiruan", "barang kw",
            "rokok elektronik", "vapor",
        ]),
        "description": "Shopee 平台禁售商品综合规则（含东南亚口语）",
    },
    {
        "platform": "shopee",
        "rule_type": "keyword",
        "category": "风控-虚假宣传",
        "severity": "warn",
        "keywords": json.dumps([
            "#1", "第一", "绝对", "100%", "百分百",
            "guaranteed", "保证", "肯定有效",
            "fda certified", "fda认证", "ce认证",
            "高仿", "A货", "复刻", "原单",
            "刷单", "刷评", "fake review", "好评返现",
            "最低价", "全网最低",
            "no.1", "terbaik", "paling murah",
            "无效退款", "不满意退款",
        ]),
        "description": "Shopee 平台风控提醒（含东南亚口语）",
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
            "casino", "gambl", "博彩", "赌场",
            "endangered", "ivory", "濒危", "象牙", "野生动物",
            "prescription", "处方药",
            "dadah", "ganja", "syabu",
            "senjata api", "peluru",
            "minuman keras", "minuman beralkohol",
            "obat keras", "obat tanpa resep",
            "barang tiruan", "barang kw",
            "rokok elektronik", "vapor",
        ]),
        "description": "Lazada 平台禁售商品综合规则（含东南亚口语）",
    },
    {
        "platform": "lazada",
        "rule_type": "keyword",
        "category": "风控-虚假宣传",
        "severity": "warn",
        "keywords": json.dumps([
            "#1", "第一", "绝对", "100%", "百分百",
            "guaranteed", "保证", "肯定有效",
            "fda certified", "fda认证", "ce认证",
            "高仿", "A货", "复刻", "原单",
            "刷单", "刷评", "fake review", "好评返现",
            "最低价", "全网最低",
            "no.1", "terbaik", "paling murah",
            "无效退款",
        ]),
        "description": "Lazada 平台风控提醒（含东南亚口语）",
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
