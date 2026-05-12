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
#   2. 中英文双语覆盖 + 口语化/俚语补充
#   3. 覆盖常见绕词和变体（如空格分隔、符号替换、谐音）
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
            # --- 新增：口语化/俚语 ---
            "coke", "blow", "snow", "dope", "hashish", "skunk",
            "kush", "shatter", "dabs", "wax", "edibles",
            "叶子", "飞叶子", "溜冰", "煲猪肉", "白粉", "k粉",
            "神仙水", "开心水", "跳跳糖", "浴盐", "笑气",
            "popper", "rush", "nangs", "nos",
            "上瘾", "成瘾", "毒瘾", "戒毒",
            "chemical high", "getting high", "tripping",
            # ── 中文口语 / 黑话 / 谐音 ──
            "冰", "麻", "麻叶", "面面", "四号", "黄皮", "料子",
            "嗑药", "飞", "嗨", "溜粉", "追龙", "吹泡泡",
            "壶", "冰壶", "锡纸", "吸管", "打火机+锡纸",
            "上头", "电子烟油上头", "上头电子烟",
            "失身酒", "迷魂药", "听话水", "乖乖水", "迷情水",
            "阿拉伯茶", "恰特草", "卡痛", "kratom",
            "蘑菇", "迷幻蘑菇", "magic mushroom", "shrooms",
            "邮票", "贴纸毒品", "毒邮票",
            "一粒眠", "红冰", "开心粉", "奶茶粉", "咖啡粉", "巧克力粉",
            "小树枝", "蓝精灵", "犀牛液", "咔哇", "kawa",
            "飞仔", "high野", "飘飘", "上太空", "晕晕",
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
            # --- 新增：口语化/俚语 ---
            "shank", "shiv", "machete", "katana", "flamethrower",
            "silencer", "suppressor", "high capacity", "magazine",
            "口径", "消音器", "砍刀", "军火", "枪械", "枪支配件",
            "airsoft", "bb gun", "pellet gun", "弹弓", "钢珠",
            "assault rifle", "machine gun", "机关枪", "半自动",
            "homemade gun", "3d printed gun", "自制枪",
            "c4", "semtex", "塑料炸药",
            # ── 中文口语 ──
            "管制刀具", "仿真枪", "电棍", "电击棒", "狼牙棒",
            "双节棍", "三棱刀", "弹簧刀", "蝴蝶刀", "爪刀",
            "狗腿刀", "尼泊尔", "军刺", "刺刀", "匕首", "飞镖",
            "防身喷雾", "防狼喷雾", "辣椒水", "防身器",
            "手铐", "脚镣", "警用", "警械", "警具",
            "枪模", "模型枪", "打火机枪", "钥匙扣枪",
            "气枪", "铅弹", "气罐", "高压气瓶",
            "弓弩", "复合弓", "反曲弓", "十字弓", "箭矢",
            "火狗", "狗", "短狗", "长狗", "气狗", "鸡",
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
            # --- 新增：口语化/俚语 ---
            "copy", "dupe", "mirror image", "reproduction",
            "仿冒", "冒牌", "假货", "赝品", "克隆",
            "山寨版", "山寨货", "1:1", "一比一", "对版",
            "fake docs", "novelty id", "passport for sale",
            "假币", "假钞", "假发票", "假合同",
            "fake money", "counterfeit money", "prop money",
            "unlicensed", "未授权", "无授权", "非官方",
            # ── 中文口语 ──
            "莆田", "莆田货", "白云皮具", "华强北", "档口货",
            "做货", "拿货", "工厂拿货", "原厂拿货",
            "精工", "顶级复刻", "原版复刻", "正品对比",
            "出入专柜", "专柜验货", "过验", "过毒", "过鉴定",
            "裸鞋", "裸包", "无盒", "原盒", "配盒",
            "版本", "顶级版本", "完美版本", "市面最高",
            "广东货", "浙江货", "河北货", "产地直发",
            "办证", "刻章", "印章", "证照制作", "毕业证",
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
            # --- 新增：口语化/俚语 ---
            "大麻烟", "电子雾化器", "iqos", "加热不燃烧",
            "嚼烟", "鼻烟", "烟丝", "烟斗", "手卷烟",
            "moonshine", "自酿酒", "homebrew", "蒸馏酒",
            "absinthe", "苦艾酒", "高度酒", "原浆酒",
            "卖酒", "代购酒", "酒类代购", "免税烟酒",
            "juul", "puff bar", "disposable vape", "一次性电子烟",
            # ── 中文口语 ──
            "散烟", "拆烟", "分装烟", "烟弹", "电子烟弹",
            "免关税烟", "机场代购烟", "海南免税烟",
            "外烟", "韩免", "日免", "俄版", "哈萨克版",
            "铁盒烟", "细支", "爆珠", "薄荷烟", "果味烟",
            "自酿", "散装酒", "桶装酒", "原液", "酒曲",
            "酿酒设备", "蒸馏器", "发酵桶",
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
            # --- 新增：口语化/俚语 ---
            "器官买卖", "卖血", "卖肾", "卖身",
            "代孕", "surrogacy", "surrogate mother", "womb",
            "子宫", "卵子", "捐卵", "试管婴儿",
            "人体组织", "眼角膜", "骨髓",
            "cornea", "bone marrow", "tissue",
            "adoption for sale", "买孩子", "卖孩子", "婴儿贩卖",
            # ── 中文口语 ──
            "卖器官", "黑市器官", "找肾源", "找肝源", "配型",
            "捐卵", "供卵", "找代孕", "代孕妈妈", "借腹",
            "找孕母", "求子", "求卵", "求精",
            "地下代孕", "非法代孕", "助孕", "有偿捐卵",
            "试药", "药物试验", "人体试验", "临床招募",
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
            # --- 新增：口语化/俚语 ---
            "剧毒", "放射", "核", "nuclear", "辐射",
            "生化", "bioweapon", "化学武器", "芥子气",
            "vx", "sarin", "神经毒剂", "mustard gas",
            "chlorine", "chlorine gas", "氯气", "光气",
            "ricin", "蓖麻毒素", "anthrax", "炭疽",
            "汽油", "柴油", "煤油", "液化气", "丙烷",
            "propane", "gasoline", "diesel",
            # ── 中文口语 ──
            "老鼠药", "蟑螂药", "蚂蚁药", "毒鼠强", "三步倒",
            "百草枯", "敌敌畏", "乐果", "甲胺磷", "毒死蜱",
            "呋喃丹", "克百威", "涕灭威", "氧乐果",
            "磷化铝", "磷化锌", "溴鼠灵", "溴敌隆",
            "自制毒药", "毒物制作", "制毒配方", "毒药配方",
            "强酸", "强碱", "烧碱", "火碱", "片碱",
            "香蕉水", "天那水", "稀释剂", "有机溶剂",
            "烟花爆竹", "鞭炮", "礼花", "烟花", "擦炮", "摔炮",
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
            # --- 新增：口语化/俚语 ---
            "穿山甲鳞片", "虎鞭", "熊掌", "燕窝",
            "冬虫夏草", "雪蛤", "鹿茸", "藏羚羊", "藏羚",
            "鲨鱼", "海马", "玳瑁", "tortoise", "turtle shell",
            "蛇胆", "蛇皮", "鳄鱼皮", "蜥蜴",
            "python skin", "crocodile", "alligator",
            "动物标本", "taxidermy", "蝴蝶标本",
            "野生动物制品", "禁猎", "偷猎", "盗猎", "poaching",
            # ── 中文口语 ──
            "野味", "吃野味", "野货", "山货野味",
            "穿山甲肉", "竹鼠", "果子狸", "猴脑", "蛇肉",
            "娃娃鱼", "大鲵", "中华鲟", "刀鱼", "河豚",
            "天鹅", "丹顶鹤", "朱鹮", "金丝猴", "大熊猫",
            "活体", "活体快递", "活体运输", "宠物托运活体",
            "斗狗", "斗鸡", "斗牛", "斗鸟", "动物搏斗",
            "兽夹", "捕兽夹", "捕鸟网", "粘网", "猎套",
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
            # --- 新增：口语化/俚语 ---
            "减肥药", "催情", "迷药", "麻醉", "镇静剂", "兴奋剂",
            "聪明药", "modafinil", "ritalin", "concerta",
            "成长激素", "hgh", "睾酮", "testosterone",
            "止痛药", "镇痛", "oxycontin", "oxycodone", "percocet",
            "morphine sulfate", "fentanyl patch", "芬太尼贴",
            "sleeping pills", "安眠", "褪黑素滥用",
            "买药", "卖药", "药品代购", "印度仿制药",
            "repatha", "humira", "keytruda", "opdivo",
            # ── 中文口语 ──
            "医院代开", "代开处方", "套取处方", "处方外流",
            "印度直邮", "土耳其直邮", "泰国代购药",
            "走私药", "水货药", "拆零卖药", "分装药",
            "疫苗代购", "hpv疫苗代购", "九价代购", "四价代购",
            "肉毒", "肉毒素", "玻尿酸", "水光针", "溶脂针",
            "童颜针", "婴儿针", "美白针", "瘦脸针",
            "人血白蛋白", "静丙", "免疫球蛋白",
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
            # --- 新增：口语化/俚语 ---
            "偏方", "土方", "老中医配方", "治百病", "药到病除",
            "立竿见影", "herbal cure", "天然疗法", "natural cure",
            "magic pill", "神奇药丸", "万能药", "仙丹",
            "energy healing", "灵气治疗", "crystal healing", "水晶治疗",
            "homeopathic cure", "顺势疗法", "detox cure",
            "排毒", "清肠", "净化", "酸碱体质",
            "神油", "印度神油", "增大", "增粗", "延时",
            "保证治愈", "无效退款", "不愈包退", "包治好",
            # ── 中文口语 ──
            "老军医", "中医世家", "祖传", "御医秘方", "宫廷秘方",
            "藏药", "苗药", "彝药", "蒙药", "傣药",
            "艾灸治百病", "刮痧治百病", "拔罐治百病",
            "辟谷", "断食", "生酮抗癌", "饥饿疗法",
            "碱性体质", "酸性体质", "排酸", "酸碱平衡",
            "负离子", "远红外", "磁疗", "频谱", "太赫兹",
            "量子", "量子医学", "量子检测", "量子植入",
            "能量石", "能量手环", "能量项链", "能量贴",
            "保健酒", "药酒", "泡酒料", "壮阳酒", "补肾酒",
            "增高", "长高", "增高药", "增高贴", "增高鞋垫",
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
            # --- 新增：口语化/俚语 ---
            "假肢", "义肢", "助听器", "hearing aid", "轮椅",
            "矫正器", "隐形眼镜", "注射器", "syringe", "needle",
            "未批准", "无证", "无资质", "三无",
            "血糖仪", "血压计", "血氧仪", "体温计",
            "blood glucose", "blood pressure monitor",
            "手术刀", "手术钳", "手术缝线", "surgical suture",
            "输液器", "输液管", "iv set", "catheter", "导尿管",
            "美容仪", "激光脱毛", "ipl", "射频美容",
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
            # --- 新增：口语化/俚语 ---
            "排外", "仇外", "xenophobic", "islamophobic",
            "仇恨言论", "hate speech", "homophobic", "transphobic",
            "厌女", "misogyny", "incel",
            "swastika", "万字旗", "卐", "卍",
            "white power", "black power supremacy",
            "种族清洗", "种族隔离", "apartheid",
            "gender discrimination", "性别歧视", "地域歧视",
            "disabled discrimination", "残疾歧视",
            "body shaming", "身材羞辱", "外貌攻击",
            # ── 中文口语 ──
            "台独", "藏独", "疆独", "港独", "分裂",
            "支那", "蝗虫", "白皮猪", "黑鬼", "阿三",
            "小日本", "棒子", "毛子", "越南猴子", "菲佣",
            "轮子", "法轮", "falun", "大法",
            "六四", "天安门", "64事件", "1989",
            "吃人血馒头", "五毛", "美分", "带路党",
            "地域黑", "河南偷", "东北狗", "井盖", "外地的",
            "农民工", "乡下人", "洗脚婢", "屌丝", "loser",
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
            # --- 新增：口语化/俚语 ---
            "裸照", "露点", "走光", "偷拍", "偷窥",
            "voyeur", "upskirt", "hidden camera",
            "hentai", "里番", "本子", "福利姬", "福利视频",
            "约炮", "援交", "sugar daddy", "sugar baby",
            "一夜情", "ons", "hookup", "dating for sex",
            "sex doll", "充气娃娃", "实体娃娃",
            "催情药", "迷奸", "春药", "aphrodisiac",
            "性虐待", "sm", "bdsm", "捆绑", "鞭打",
            "wet t shirt", "hot girl", "sexy video",
            # ── 中文口语 ──
            "外围", "外围女", "商务", "商务伴游", "空降",
            "楼凤", "凤楼", "洗浴", "桑拿", "养生会所",
            "大保健", "全套", "半套", "快餐", "包夜",
            "qm", "lf", "sn", "bt", "qt",
            "黄片", "毛片", "岛国片", "av", "无码", "中出",
            "制服诱惑", "丝袜诱惑", "巨乳", "爆乳", "童颜巨乳",
            "大尺度", "超尺", "限制级", "禁播", "未删减",
            "色图", "福利图", "套图", "写真", "私房照",
            "PUA", "把妹", "泡妞", "搭讪艺术家",
            "换妻", "群交", "多人运动", "伦理", "乱伦",
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
            # --- 新增：口语化/俚语 ---
            "赌场", "赌局", "赌注", "六合彩", "时时彩",
            "北京赛车", "pk10", "快3", "骰子", "骰宝",
            "dice game", "竞猜", "押注", "盘口", "赔率",
            "odds", "parlay", "handicap", "让球",
            "棋牌", "电玩城", "捕鱼", "打鱼",
            "推币机", "娃娃机赌博", "变相赌博",
            "赌资", "赌金", "抽水", "返水", "洗码",
            "信用网", "现金网", "投注网", "盘",
            # ── 中文口语 ──
            "赌狗", "烂赌", "戒赌", "上岸", "下水",
            "买码", "报码", "特码", "平码", "波色", "单双",
            "时时彩", "分分彩", "飞艇", "赛车", "快开",
            "计划群", "跟单", "带单", "导师带队", "包赔",
            "刷水", "对刷", "套利", "刷流水", "打流水",
            "菠菜", "bc", "qs", "cp", "网投", "电投",
            "现金棋牌", "真金棋牌", "捕鱼游戏", "街机",
            "退水", "佣金", "代理线", "下级", "拉人",
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
            # --- 新增：口语化/俚语 ---
            "史上最", "天下第一", "顶级", "至尊",
            "无敌", "完美", "极好", "超级",
            "最好用", "最棒", "最强", "最牛",
            "ultimate", "premium", "elite", "supreme",
            "零风险", "零差评", "零失败", "万无一失",
            "永久有效", "一劳永逸", "包满意", "包好用",
            "秒杀一切", "吊打同行", "碾压级别",
            "限时永久", "永久免费", "终生免费",
            # ── 中文口语 ──
            "逆天", "炸裂", "封神", "天花板", "神器", "黑科技",
            "国货之光", "国产之光", "良心", "平价之王",
            "老司机推荐", "闭眼入", "无脑入", "冲就完了",
            "价格打下来了", "骨折价", "打到地板价", "把价格打穿",
            "卖爆了", "爆单", "爆款", "断货王", "抢疯了",
            "无限回购", "用过的都说好", "回头客", "老顾客",
            "不含任何化学成分", "零添加", "绝对零添加",
            "温和不刺激", "敏感肌可用", "孕妇可用", "婴儿可用",
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
            # --- 新增：口语化/俚语 ---
            "官方认证", "正品保证", "原装正品", "正品授权",
            "品牌授权", "授权经销商", "authorized dealer",
            "官方授权", "特许经营", "指定代理",
            "检测合格", "质检报告", "通过检测",
            "hypoallergenic", "低致敏", "无刺激",
            "dermatologist recommended", "皮肤科推荐",
            "doctor recommended", "医生推荐", "专家推荐",
            "patented", "专利", "专利技术", "独家专利",
            "sgs认证", "tuv认证", "ul认证",
            # ── 中文口语 ──
            "国标", "国标认证", "行业标准", "达标", "合格品",
            "防伪", "防伪查询", "可查防伪", "扫码验真",
            "专柜正品", "海淘正品", "人肉背回", "留学生代购",
            "支持验货", "支持专柜验", "假一赔十", "假一赔命",
            "进口报关", "海关进口", "报关单", "卫检证明",
            "双检", "双重检测", "三方检测", "送检报告",
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
            # --- 新增：口语化/俚语 ---
            "血亏", "吐血", "甩卖", "抛售", "清仓甩卖",
            "厂家直销", "工厂价", "出厂价", "批发价",
            "限时抢购", "限量发售", "最后一天", "最后一批",
            "暴利", "割韭菜", "智商税", "冤大头",
            "内部价", "关系价", "员工价", "家属价",
            "price error", "标错价", "bug价", "漏洞价",
            "below cost", "亏本卖", "赔本", "不赚钱",
            "半价", "一折", "白菜价", "白菜",
            # ── 中文口语 ──
            "骨折", "打骨折", "打下来了", "打到谷底",
            "亏本冲量", "刷量价", "引流价", "福利单",
            "拼单", "凑单", "团购价", "阶梯价", "量大从优",
            "不赚钱交个朋友", "亏钱冲销量", "只为好评",
            "成本价", "成本价出售", "透明价", "公开成本",
            "对半砍", "砍价", "大砍刀", "屠龙刀",
            "手慢无", "错过等一年", "双十一价", "618价",
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
            # --- 新增：口语化/俚语 ---
            "代购", "海淘", "代工厂", "尾货", "原厂",
            "出口转内销", "外贸", "外贸原单",
            "工厂尾单", "品牌尾货", "余单", "跟单",
            "渠道货", "私单", "老鼠货", "试产货",
            "打版", "开版", "复刻版", "致敬款",
            "同厂", "同工", "同料", "同源", "源头货",
            "平价款", "平价替代", "大牌平替", "轻奢同款",
            # ── 中文口语 ──
            "致敬", "复刻致敬", "一比一复刻", "1:1复刻",
            "同厂同工", "同一产线", "同一工厂", "同一车间",
            "尾货清仓", "剪标", "去标", "换标", "无标",
            "海关罚没", "海关扣留", "海关走私", "水客",
            "样品", "样板货", "打版货", "查货", "QC货",
            "二等品", "瑕疵品", "次品", "B品", "残次",
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
            # --- 新增：口语化/俚语 ---
            "samsung", "sony", "lg", "panasonic",
            "toyota", "honda", "ferrari", "lamborghini", "porsche",
            "harley davidson", "宝马", "奔驰", "奥迪", "宾利",
            "coca cola", "pepsi", "starbucks", "mcdonalds", "kfc",
            "北面", "north face", "patagonia", "始祖鸟", "arcteryx",
            "the north face", "canada goose", "moncler",
            "costco", "ikea", "宜家", "无印良品", "muji",
            "amazon basics", "amazon branded",
            # ── 中文品牌 ──
            "华为", "小米", "oppo", "vivo", "荣耀", "一加",
            "李宁", "安踏", "特步", "鸿星尔克", "回力",
            "老干妈", "茅台", "五粮液", "泸州老窖", "剑南春",
            "格力", "美的", "海尔", "海信", "tcl",
            "比亚迪", "蔚来", "小鹏", "理想", "极氪",
            "大疆", "宇树", "讯飞", "商汤", "旷视",
            "椰树", "娃哈哈", "康师傅", "统一", "旺旺",
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
            # --- 新增：口语化/俚语 ---
            "好评返", "五星返", "现金返", "红包", "red包",
            "有偿好评", "shua单", "s单", "空包", "礼品单",
            "测评", "种草", "软文", "推广任务",
            "review club", "review exchange", "互评",
            "vine voice manipulation", "vine abuse",
            "僵尸评论", "机刷", "真人测评", "免评",
            "合并listing", "merge listing", "变体合并",
            "僵尸链接", "跟卖", "挂靠", "截流",
            "feedback manipulation", "feedback removal",
            "买号", "买家号", "白号", "养号",
            # ── 中文口语 ──
            "放单", "接单", "做单", "任务单", "佣金单",
            "拍A发B", "空包网", "代发空包", "礼品网",
            "留评", "免评", "rating", "点星", "上星",
            "qa操纵", "问答刷", "点赞", "点踩", "nohelp",
            "店铺排名", "店铺提升", "销量提升", "权重提升",
            "关联流量", "截流", "关联截流", "强关联",
            "申诉", "账号申诉", "listing申诉", "封号解封",
            "服务商", "刷单团队", "佣金任务", "宝妈兼职刷",
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
            # --- 新增：口语化/俚语 ---
            "加v", "加q", "qq", "微信支付", "支付宝",
            "私下", "私聊", "面交", "当面交易",
            "加微", "➕微", "薇信", "vx", "v信",
            "ins", "instagram", "facebook", "fb", "messenger",
            "tiktok", "抖音", "小红书", "快手",
            "discord", "skype", "signal", "snapchat",
            "官方网站", "官网下单", "官方商城", "独立站",
            "线下门店", "实体店", "到店", "上门自取",
            "扫码加", "扫一扫", "二维码", "qr code",
            # ── 中文口语 ──
            "了解更多", "详情咨询", "了解更多加微", "了解加v",
            "关注我", "点关注", "主页有惊喜", "看主页",
            "私信拿链接", "私信有优惠", "私信有惊喜",
            "评论区找我", "评论区有惊喜", "看评论", "看第一条评论",
            "兴趣的私", "需要的私", "有意私聊", "有需要滴滴",
            "互粉", "关注互关", "涨粉", "吸粉",
            "链接在主页", "链接在签名", "店铺链接在主页",
            "拼多多", "淘宝", "天猫", "京东", "小红书店铺",
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
            # --- 新增：Shopee 东南亚口语化 ---
            "dadah", "ganja", "syabu", "pil kuda", "ubat",
            "senjata", "peluru", "pisau", "parang",
            "arak", "bir", "minuman keras", "minuman beralkohol",
            "judi", "togel", "taruhan", "pertaruhan",
            "obat keras", "obat resep", "tanpa resep",
            "rokok", "tembakau", "rokok elektronik", "vapor",
            "逃跑", "滥用", "迷幻", "k粉", "摇头",
            "barang tiruan", "barang kw", "barang replika",
            "senjata api rakitan", "senjata tajam",
            "makcik bawang", "haram", "haram dijual",
            # ── 中文口语 ──
            "药丸", "胶囊", "白面", "溜", "壶", "冰",
            "火机", "火石", "仿品", "仿货", "冒牌", "山寨",
            "散装", "私酿", "自制", "三无产品", "违禁品",
            "黑货", "水货", "走私", "海淘", "代购",
        ]),
        "description": "Shopee 平台禁售商品综合规则（含东南亚口语）",
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
            # --- 新增：Shopee 口语化 ---
            "no.1", "terbaik", "paling murah", "harga termurah",
            "mesti beli", "wajib beli", "rugi tak beli",
            "berkesan", "paling berkesan", "jaminan",
            "cod", "cash on delivery only",
            "like new", "macam baru", "oripun", "original punya",
            "barang syurga", "barang rare", "limited stock",
            "murah gila", "murah giler", "separuh harga",
            "卖家保证", "卖家承诺", "无效退款", "不满意退款",
            "全场最低", "全Shopee最低",
            # ── 中文口语 ──
            "神", "神器", "好用到哭", "好用到爆", "一定要买",
            "不买后悔", "买了不亏", "闭眼入", "懒人必备",
            "明星同款", "网红同款", "博主推荐", "达人同款",
            "平替", "平价替代", "大牌质感", "白菜价好物",
            "回头客", "老顾客回购", "用过的都回购了",
            "好评如潮", "零差评", "收到都说好", "反馈超好",
        ]),
        "description": "Shopee 平台风控提醒（含东南亚口语）",
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
            # --- 新增：Lazada 东南亚口语化 ---
            "dadah", "ganja", "syabu", "pil kuda",
            "senjata api", "peluru", "bahan letupan",
            "arak", "minuman keras", "minuman beralkohol",
            "judi", "togel", "taruhan",
            "obat keras", "obat tanpa resep",
            "rokok", "tembakau", "vapor", "rokok elektronik",
            "barang tiruan", "barang kw", "imitasi",
            "逃跑", "滥用", "迷幻", "k粉", "摇头",
            "haram", "bawang", "haram dijual",
            "sulasi", "sulasi senpi", "rakitan",
            # ── 中文口语 ──
            "药丸", "胶囊", "白面", "壶", "冰",
            "冒牌", "山寨", "三无", "违禁品",
            "黑货", "水货", "走私", "海淘", "代购",
        ]),
        "description": "Lazada 平台禁售商品综合规则（含东南亚口语）",
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
            # --- 新增：Lazada 口语化 ---
            "no.1", "terbaik", "paling murah", "harga runtuh",
            "mesti beli", "wajib beli", "tak beli rugi",
            "berkesan", "paling power", "jaminan",
            "cash on delivery only", "cod saja",
            "like new", "macam original", "ori punya",
            "barang rare", "limited", "stok terhad",
            "murah gila", "separuh harga", "diskaun gila",
            "卖家保证", "卖家承诺", "无效退款",
            "harga kilang", "factory price", "borong murah",
            # ── 中文口语 ──
            "神器", "好用到哭", "一定要买", "不买后悔", "闭眼入",
            "明星同款", "网红同款", "博主推荐",
            "平替", "大牌质感", "白菜价好物",
            "回头客", "零差评", "反馈超好",
        ]),
        "description": "Lazada 平台风控提醒（含东南亚口语）",
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
