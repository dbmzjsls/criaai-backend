"""
种子脚本：初始化产品向量嵌入数据
运行方式:
  uv run python scripts/seed_embeddings.py          # 追加模式
  uv run python scripts/seed_embeddings.py --reset  # 重置模式

为常用跨境电商产品生成向量嵌入，使 RAG 检索有数据可查。
"""
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.database import SessionLocal
from models.embedding import ProductEmbedding
from utils.embeddings import embedding_service

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

# ============================================================
# 内置产品目录 — 覆盖主流跨境电商品类
# 每个产品有: product_id, category, name(用于生成嵌入的文本)
# ============================================================
PRODUCTS = [
    # ── 服装 / Apparel ──
    ("BR-APP-001", "clothing", "Men's Cotton Casual T-Shirt Short Sleeve Solid Color"),
    ("BR-APP-002", "clothing", "Women's Summer Floral Dress Beach Party Sundress"),
    ("BR-APP-003", "clothing", "Unisex Hoodie Sweatshirt Fleece Pullover Streetwear"),
    ("BR-APP-004", "clothing", "Men's Slim Fit Dress Shirt Business Formal Long Sleeve"),
    ("BR-APP-005", "clothing", "Women's Yoga Pants High Waist Leggings Fitness Workout"),
    ("BR-APP-006", "clothing", "Kids Cartoon Pajamas Set Cotton Sleepwear Boys Girls"),
    ("BR-APP-007", "clothing", "Men's Cargo Shorts Casual Loose Fit Multi-Pocket Summer"),
    ("BR-APP-008", "clothing", "Women's Blazer Jacket Office Work Business Professional"),
    ("BR-APP-009", "clothing", "Baby Romper Bodysuit Infant One-Piece Cotton Newborn"),
    ("BR-APP-010", "clothing", "Men's Sports Jacket Windbreaker Outdoor Running Hiking"),

    # ── 鞋类 / Shoes ──
    ("BR-SHO-001", "shoes", "Men's Running Shoes Lightweight Breathable Athletic Sneakers"),
    ("BR-SHO-002", "shoes", "Women's High Heels Stiletto Party Wedding Dress Pumps"),
    ("BR-SHO-003", "shoes", "Unisex Flip Flops Beach Sandals Summer Outdoor Slippers"),
    ("BR-SHO-004", "shoes", "Men's Leather Oxford Shoes Business Formal Dress Office"),
    ("BR-SHO-005", "shoes", "Women's Flat Ballet Shoes Comfort Casual Work Office"),
    ("BR-SHO-006", "shoes", "Kids LED Light Up Sneakers Boys Girls Athletic Sports"),
    ("BR-SHO-007", "shoes", "Men's Hiking Boots Waterproof Outdoor Trekking Camping"),
    ("BR-SHO-008", "shoes", "Women's Platform Sneakers Chunky Dad Shoes Street Style"),

    # ── 箱包 / Bags ──
    ("BR-BAG-001", "bags", "Women's Leather Handbag Shoulder Bag Tote Purse Designer"),
    ("BR-BAG-002", "bags", "Men's Backpack Travel Laptop Bag College School Business"),
    ("BR-BAG-003", "bags", "Luggage Set Hard Shell Suitcase Travel Trolley 3-Piece"),
    ("BR-BAG-004", "bags", "Women's Crossbody Bag Small Messenger Purse Phone Wallet"),
    ("BR-BAG-005", "bags", "Men's Wallet Leather Slim Bifold Card Holder RFID Blocking"),
    ("BR-BAG-006", "bags", "Canvas Tote Bag Shopping Grocery Reusable Shoulder Eco Bag"),

    # ── 珠宝手表 / Jewelry & Watches ──
    ("BR-JWL-001", "jewelry_watches", "Women's Crystal Necklace Pendant Luxury Fashion Jewelry"),
    ("BR-JWL-002", "jewelry_watches", "Men's Stainless Steel Watch Analog Quartz Business Casual"),
    ("BR-JWL-003", "jewelry_watches", "Sterling Silver Earrings Stud Hoop Women's Gift Box"),
    ("BR-JWL-004", "jewelry_watches", "Smart Watch Fitness Tracker Heart Rate Monitor Waterproof"),
    ("BR-JWL-005", "jewelry_watches", "Gold Plated Bracelet Bangle Women's Fashion Accessory"),
    ("BR-JWL-006", "jewelry_watches", "Men's Titanium Ring Wedding Band Engagement 8mm"),

    # ── 美妆 / Beauty ──
    ("BR-BTY-001", "beauty", "Lipstick Set Matte Liquid Long Lasting 12 Colors Makeup Kit"),
    ("BR-BTY-002", "beauty", "Face Serum Hyaluronic Acid Anti-Aging Moisturizing 30ml"),
    ("BR-BTY-003", "beauty", "Eyeshadow Palette 35 Colors Nude Matte Shimmer Professional"),
    ("BR-BTY-004", "beauty", "Electric Hair Straightener Flat Iron Ceramic Anti-Frizz"),
    ("BR-BTY-005", "beauty", "Nail Polish Set Gel UV LED Quick Dry 24 Colors Manicure"),
    ("BR-BTY-006", "beauty", "Men's Beard Grooming Kit Trimmer Shaver Electric Razor Set"),
    ("BR-BTY-007", "beauty", "Sunscreen SPF 50+ Face Cream Moisturizing UV Protection 50ml"),

    # ── 电子产品 / Electronics ──
    ("BR-ELC-001", "electronics", "Wireless Bluetooth Headphones Noise Cancelling HiFi Stereo"),
    ("BR-ELC-002", "electronics", "Portable Power Bank 20000mAh Fast Charging USB-C Phone"),
    ("BR-ELC-003", "electronics", "USB-C Hub Adapter 7-in-1 HDMI SD Card Reader Laptop"),
    ("BR-ELC-004", "electronics", "Wireless Charger Pad Fast Qi Charging iPhone Samsung"),
    ("BR-ELC-005", "electronics", "Bluetooth Speaker Portable Waterproof Outdoor Sound Bass"),
    ("BR-ELC-006", "electronics", "Phone Case Silicone Shockproof Protective Cover for iPhone"),
    ("BR-ELC-007", "electronics", "Car Phone Holder Magnetic Dashboard GPS Mount Universal"),
    ("BR-ELC-008", "electronics", "Webcam 1080P HD USB Computer Camera with Microphone PC"),

    # ── 手机配件 / Phone Accessories ──
    ("BR-PHN-001", "phone_accessories", "iPhone Tempered Glass Screen Protector 9H HD 2-Pack"),
    ("BR-PHN-002", "phone_accessories", "USB-C Fast Charging Cable 2M Nylon Braided Data Sync"),
    ("BR-PHN-003", "phone_accessories", "Phone Ring Holder Kickstand Magnetic Car Mount Grip"),
    ("BR-PHN-004", "phone_accessories", "AirPods Pro Case Cover Silicone Protective Shockproof"),

    # ── 家居 / Home ──
    ("BR-HOM-001", "home", "LED Desk Lamp Eye-Caring Reading Table Light Touch Dimming"),
    ("BR-HOM-002", "home", "Memory Foam Pillow Orthopedic Neck Support Sleep Bedding"),
    ("BR-HOM-003", "home", "Non-Stick Cooking Pan Fry Pan Granite Coating 28cm Kitchen"),
    ("BR-HOM-004", "home", "Cotton Bed Sheet Set Queen Size 4-Piece Soft Breathable"),
    ("BR-HOM-005", "home", "Robot Vacuum Cleaner Smart Auto Charging Mopping 3000Pa"),
    ("BR-HOM-006", "home", "Essential Oil Diffuser Aroma Humidifier 300ml Ultrasonic LED"),
    ("BR-HOM-007", "home", "Blackout Curtains Thermal Insulated Window Drapes 2-Panel"),
    ("BR-HOM-008", "home", "Silicone Kitchen Utensil Set Cooking Tools 12-Piece Spatula"),

    # ── 厨房 / Kitchen ──
    ("BR-KIT-001", "kitchen", "Electric Coffee Grinder Burr Mill 14 Settings Espresso Drip"),
    ("BR-KIT-002", "kitchen", "Portable Blender Personal Smoothie Maker USB Rechargeable"),
    ("BR-KIT-003", "kitchen", "Stainless Steel Water Bottle Insulated Thermos 750ml Hot Cold"),
    ("BR-KIT-004", "kitchen", "Knife Set Chef Kitchen Cutlery 6-Piece Stainless Steel Block"),
    ("BR-KIT-005", "kitchen", "Electric Kettle Temperature Control 1.7L Stainless Fast Boil"),

    # ── 母婴 / Baby & Kids ──
    ("BR-BBY-001", "baby_kids", "Baby Diapers Disposable Ultra Soft Size M 80 Count Hypoallergenic"),
    ("BR-BBY-002", "baby_kids", "Baby Stroller Lightweight Foldable Travel Umbrella 5-Point Harness"),
    ("BR-BBY-003", "baby_kids", "Kids Educational Toys Building Blocks STEM Learning Set 100pcs"),
    ("BR-BBY-004", "baby_kids", "Baby Monitor Camera Wireless WiFi Night Vision Two-Way Audio"),
    ("BR-BBY-005", "baby_kids", "Toddler Sippy Cup Spill-Proof Straw Baby Training 300ml BPA-Free"),

    # ── 运动户外 / Sports & Outdoors ──
    ("BR-SPT-001", "sports_outdoors", "Yoga Mat Non-Slip Exercise Fitness Gym Workout 6mm Thick"),
    ("BR-SPT-002", "sports_outdoors", "Resistance Bands Set Exercise Workout Pull Up Stretch 5 Levels"),
    ("BR-SPT-003", "sports_outdoors", "Camping Tent 4-Person Waterproof Outdoor Family Hiking Shelter"),
    ("BR-SPT-004", "sports_outdoors", "Fishing Rod Carbon Fiber Spinning Travel Telescopic Portable"),
    ("BR-SPT-005", "sports_outdoors", "Dumbbell Set Adjustable Weight Home Gym Fitness 20kg Pair"),
    ("BR-SPT-006", "sports_outdoors", "Ski Goggles Snowboard Anti-Fog UV Protection OTG Winter Sports"),

    # ── 宠物 / Pet Supplies ──
    ("BR-PET-001", "pet_supplies", "Dog Bed Orthopedic Memory Foam Washable Medium Large Soft"),
    ("BR-PET-002", "pet_supplies", "Cat Scratching Post Tower Tree House Condo Furniture Sisal"),
    ("BR-PET-003", "pet_supplies", "Dog Leash Set Hands-Free Waist Running Reflective Adjustable"),
    ("BR-PET-004", "pet_supplies", "Pet Grooming Brush Self-Cleaning Slicker Deshedding Cat Dog"),
    ("BR-PET-005", "pet_supplies", "Automatic Pet Feeder Food Dispenser Timer Programmable 4L"),

    # ── 健康 / Health ──
    ("BR-HLT-001", "health", "Vitamin C Supplement 1000mg Immune Support 120 Tablets"),
    ("BR-HLT-002", "health", "Digital Thermometer Infrared Forehead Non-Contact Baby Adult"),
    ("BR-HLT-003", "health", "Protein Powder Whey Isolate Chocolate Vanilla 2lb Muscle Recovery"),
    ("BR-HLT-004", "health", "First Aid Kit Medical Emergency Survival Travel Home Office 100pcs"),
    ("BR-HLT-005", "health", "Posture Corrector Back Support Brace Adjustable Men Women Pain Relief"),

    # ── 办公 / Office ──
    ("BR-OFC-001", "office", "Notebook A5 Leather Journal Diary Planner Refillable Travel"),
    ("BR-OFC-002", "office", "Gel Pens Set 24 Colors Fine Point Smooth Writing School Office"),
    ("BR-OFC-003", "office", "Monitor Stand Riser Wood Desk Organizer Ergonomic Height Adjustable"),
    ("BR-OFC-004", "office", "Sticky Notes Set Colorful Memo Pad Self-Adhesive 12 Pack 100 Sheets"),

    # ── 汽车 / Automotive ──
    ("BR-AUT-001", "automotive", "Car Air Freshener Perfume Vent Clip Long Lasting 6-Pack"),
    ("BR-AUT-002", "automotive", "Car Seat Cover Set Leather Waterproof Universal Fit Front Rear"),
    ("BR-AUT-003", "automotive", "Dash Cam 4K Front Rear Dual Camera Night Vision Parking Monitor"),
    ("BR-AUT-004", "automotive", "Car Vacuum Cleaner Portable Handheld 8000Pa Cordless Wet Dry"),

    # ── 园艺 / Garden ──
    ("BR-GRD-001", "garden", "LED Grow Light Full Spectrum 100W Indoor Plant Veg Bloom"),
    ("BR-GRD-002", "garden", "Garden Hose Expandable 50ft Flexible Water Pipe Spray Nozzle"),
    ("BR-GRD-003", "garden", "Plant Pots Set Ceramic Succulent Cactus Flower Indoor Decorative"),
    ("BR-GRD-004", "garden", "Garden Tools Set Stainless Steel Heavy Duty 8-Piece Ergonomic"),

    # ── 玩具 / Toys ──
    ("BR-TOY-001", "toys", "RC Car Remote Control 4WD Off-Road Monster Truck Rechargeable"),
    ("BR-TOY-002", "toys", "Board Game Family Strategy Card Party Night Fun Adults Kids"),
    ("BR-TOY-003", "toys", "Puzzle 1000 Pieces Jigsaw Landscape Scenery Adults Teens Educational"),
    ("BR-TOY-004", "toys", "Action Figure Set Anime Superhero Collectible 6-Pack Gift Box"),
]


def seed_embeddings(reset: bool = False):
    """导入产品嵌入数据"""
    db = SessionLocal()
    try:
        if reset:
            deleted = db.query(ProductEmbedding).delete()
            db.commit()
            logger.info(f"已清除旧嵌入: {deleted} 条")

        # 查重：跳过已存在的 product_id
        existing_ids = set(
            r[0] for r in db.query(ProductEmbedding.product_id).all()
        )

        new_products = [p for p in PRODUCTS if p[0] not in existing_ids]
        if not new_products:
            logger.info(f"所有 {len(PRODUCTS)} 个产品已存在，无需导入")
            return

        logger.info(f"准备导入 {len(new_products)} 个产品 (总计 {len(PRODUCTS)}，已存在 {len(PRODUCTS) - len(new_products)})")

        texts = [p[2] for p in new_products]
        logger.info("正在生成嵌入向量，请稍候...")
        embeddings = embedding_service.embed_batch(texts, batch_size=10)

        count = 0
        for (product_id, category, text), vector in zip(new_products, embeddings):
            db.add(ProductEmbedding(
                product_id=product_id,
                category=category,
                text=text,
                embedding=vector,
                extra_data={"category": category, "source": "built_in_seed"},
            ))
            count += 1
            if count % 10 == 0:
                db.flush()
                logger.info(f"已写入: {count}/{len(new_products)}")

        db.commit()
        logger.info(f"导入完成: {count} 条")

    finally:
        db.close()


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    seed_embeddings(reset)

    # 验证
    db = SessionLocal()
    try:
        total = db.query(ProductEmbedding).count()
        logger.info(f"product_embeddings 表当前共: {total} 条")
        if total > 0:
            sample = db.query(ProductEmbedding).first()
            logger.info(f"示例: {sample.product_id} | {sample.category} | {sample.text[:60]}...")
    finally:
        db.close()
