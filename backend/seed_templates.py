"""运行一次：python seed_templates.py 插入美容行业模板"""
import asyncio
from app.database import async_session
from app.models.template import Template

TEMPLATES = [
    {
        "name": "美容推荐-产品介绍",
        "industry": "美容美发",
        "config": {
            "scene": "indoor_bright",
            "camera": "medium_shot",
            "duration_range": [15, 30],
            "style": "professional_beauty",
            "resolution": "1080p",
            "aspect_ratio": "9:16",
        },
    },
    {
        "name": "美容教程-护肤步骤",
        "industry": "美容美发",
        "config": {
            "scene": "studio_setup",
            "camera": "close_up",
            "duration_range": [30, 60],
            "style": "tutorial",
            "resolution": "1080p",
            "aspect_ratio": "9:16",
        },
    },
    {
        "name": "美容活动-促销推广",
        "industry": "美容美发",
        "config": {
            "scene": "shop_environment",
            "camera": "medium_shot",
            "duration_range": [15, 30],
            "style": "promotional",
            "resolution": "1080p",
            "aspect_ratio": "9:16",
        },
    },
]


async def seed():
    async with async_session() as db:
        for t in TEMPLATES:
            template = Template(**t)
            db.add(template)
        await db.commit()
        print(f"Seeded {len(TEMPLATES)} templates.")


async def seed_plans():
    from app.models.plan import Plan
    plans = [
        Plan(name="基础版", monthly_price=99.00, credits_per_month=300,
             features={"avatars": 1, "video_length": 30, "resolution": "720p"}),
        Plan(name="专业版", monthly_price=299.00, credits_per_month=1000,
             features={"avatars": 3, "video_length": 60, "resolution": "1080p"}),
        Plan(name="企业版", monthly_price=999.00, credits_per_month=5000,
             features={"avatars": 10, "video_length": 120, "resolution": "1080p", "priority_support": True}),
    ]
    async with async_session() as db:
        for p in plans:
            db.add(p)
        await db.commit()
    print(f"Seeded {len(plans)} plans.")


if __name__ == "__main__":
    asyncio.run(seed())
    asyncio.run(seed_plans())
