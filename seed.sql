
-- Seed plans
INSERT INTO plans (id, name, monthly_price, credits_per_month, features) VALUES
  (gen_random_uuid(), ''基础版'', 99.00, 300, ''{"avatars": 1, "video_length": 30, "resolution": "720p"}''),
  (gen_random_uuid(), ''专业版'', 299.00, 1000, ''{"avatars": 3, "video_length": 60, "resolution": "1080p"}''),
  (gen_random_uuid(), ''企业版'', 999.00, 5000, ''{"avatars": 10, "video_length": 120, "resolution": "1080p", "priority_support": true}'');

-- Seed templates (beauty industry)
INSERT INTO templates (id, name, industry, config) VALUES
  (gen_random_uuid(), ''美容推荐-产品介绍'', ''美容美发'', ''{"scene": "indoor_bright", "camera": "medium_shot", "duration_range": [15, 30], "style": "professional_beauty", "resolution": "1080p", "aspect_ratio": "9:16"}''),
  (gen_random_uuid(), ''美容教程-护肤步骤'', ''美容美发'', ''{"scene": "studio_setup", "camera": "close_up", "duration_range": [30, 60], "style": "tutorial", "resolution": "1080p", "aspect_ratio": "9:16"}''),
  (gen_random_uuid(), ''美容活动-促销推广'', ''美容美发'', ''{"scene": "shop_environment", "camera": "medium_shot", "duration_range": [15, 30], "style": "promotional", "resolution": "1080p", "aspect_ratio": "9:16"}'');

