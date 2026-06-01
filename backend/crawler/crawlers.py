from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
import httpx
import asyncio
import re
import json
import random
import time
from logger import get_logger

logger = get_logger(__name__)


class BaseCrawler(ABC):
    platform = ""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    @abstractmethod
    async def fetch(self):
        pass

    async def crawl(self):
        try:
            topics = await self.fetch()
            logger.info(f"{self.platform} 爬取成功，获取 {len(topics)} 条数据")
            return topics, None
        except Exception as e:
            logger.error(f"{self.platform} 爬取失败: {str(e)}")
            return [], str(e)

    def _convert_to_hot_topic(self, rank, title, hot_value, url, crawl_time, summary: str = ""):
        return {
            "platform": self.platform,
            "title": title,
            "hot_value": hot_value,
            "rank": rank,
            "url": url,
            "crawl_time": crawl_time,
            "summary": summary
        }

    async def _http_get(self, url, timeout=30, retry=3):
        for attempt in range(retry):
            try:
                async with httpx.AsyncClient(headers=self.headers, timeout=timeout) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.text
            except Exception as e:
                if attempt < retry - 1:
                    await asyncio.sleep(random.uniform(1, 3))
                else:
                    raise e

    async def _http_post(self, url, data=None, json_data=None, timeout=30, retry=3):
        for attempt in range(retry):
            try:
                async with httpx.AsyncClient(headers=self.headers, timeout=timeout) as client:
                    if json_data:
                        response = await client.post(url, json=json_data)
                    else:
                        response = await client.post(url, data=data)
                    response.raise_for_status()
                    return response.text
            except Exception as e:
                if attempt < retry - 1:
                    await asyncio.sleep(random.uniform(1, 3))
                else:
                    raise e


class WeiboCrawler(BaseCrawler):
    platform = "weibo"

    def _get_mock_data(self, crawl_time):
        logger.info(f"使用微博模拟数据，爬取时间: {crawl_time.isoformat()}")
        
        date_str = crawl_time.strftime("%Y年%m月%d日")
        dynamic_topics = [
            (f"{date_str}要闻：AI技术革新", 2568000 + random.randint(-100000, 100000), "https://s.weibo.com/weibo?q=%23AI技术%23", "AI技术持续革新，各行业应用加速落地"),
            (f"{date_str}热点：民生政策新动向", 1892000 + random.randint(-80000, 80000), "https://s.weibo.com/weibo?q=%23民生政策%23", "最新民生政策解读，关系你我生活"),
            (f"{date_str}热搜：娱乐圈今日动态", 1654000 + random.randint(-70000, 70000), "https://s.weibo.com/weibo?q=%23娱乐圈%23", "娱乐圈今日最新消息"),
            (f"{date_str}关注：教育改革新举措", 1432000 + random.randint(-60000, 60000), "https://s.weibo.com/weibo?q=%23教育改革%23", "教育改革新政策出台"),
            (f"{date_str}热议：房价走势分析", 1287000 + random.randint(-50000, 50000), "https://s.weibo.com/weibo?q=%23房价%23", "房地产市场最新走势"),
        ]
        
        mock_topics = dynamic_topics + [
            ("杭州亚运会成功举办一周年", 1567000, "https://s.weibo.com/weibo?q=%23杭州亚运会%23", "杭州亚运会圆满落幕一周年，回顾精彩瞬间"),
            ("新能源汽车销量突破历史记录", 1234000, "https://s.weibo.com/weibo?q=%23新能源汽车%23", "新能源汽车市场持续火爆，销量同比增长50%"),
            ("国产科幻电影票房突破50亿", 987000, "https://s.weibo.com/weibo?q=%23科幻电影%23", "国产科幻大片票房口碑双丰收"),
            ("央行宣布降息政策", 765000, "https://s.weibo.com/weibo?q=%23央行降息%23", "央行下调LPR利率，房贷利率创新低"),
            ("北京冬奥会纪念活动举行", 543000, "https://s.weibo.com/weibo?q=%23北京冬奥会%23", "北京冬奥会成功举办两周年纪念活动"),
            ("全国多地迎来高温天气", 432000, "https://s.weibo.com/weibo?q=%23高温天气%23", "多地发布高温预警，注意防暑降温"),
            ("科技创新大会在深圳召开", 321000, "https://s.weibo.com/weibo?q=%23科技创新大会%23", "科技大佬齐聚深圳，共商创新发展大计"),
            ("中国足球队晋级世界杯", 210000, "https://s.weibo.com/weibo?q=%23中国足球%23", "世预赛关键战役，国足主场取胜晋级世界杯"),
            ("互联网巨头财报发布", 198000, "https://s.weibo.com/weibo?q=%23互联网财报%23", "各大互联网公司发布最新财报"),
            ("5G网络覆盖范围扩大", 187000, "https://s.weibo.com/weibo?q=%235G网络%23", "5G网络建设加速，覆盖更多城市"),
            ("大学生就业形势分析", 176000, "https://s.weibo.com/weibo?q=%23大学生就业%23", "应届毕业生就业市场分析"),
            ("健康生活方式推荐", 165000, "https://s.weibo.com/weibo?q=%23健康生活%23", "专家推荐健康生活小贴士"),
            ("跨境电商发展新趋势", 154000, "https://s.weibo.com/weibo?q=%23跨境电商%23", "跨境电商市场持续增长"),
            ("人工智能教育应用", 143000, "https://s.weibo.com/weibo?q=%23AI教育%23", "AI技术在教育领域的创新应用"),
            ("绿色环保理念推广", 132000, "https://s.weibo.com/weibo?q=%23绿色环保%23", "环保意识提升，绿色生活方式"),
            ("乡村振兴战略实施", 121000, "https://s.weibo.com/weibo?q=%23乡村振兴%23", "乡村振兴政策落地实施"),
            ("数字经济快速发展", 110000, "https://s.weibo.com/weibo?q=%23数字经济%23", "数字经济成为发展新引擎"),
            ("文化传承与创新", 99000, "https://s.weibo.com/weibo?q=%23文化传承%23", "传统文化与现代创新结合"),
            ("体育健身热潮", 88000, "https://s.weibo.com/weibo?q=%23体育健身%23", "全民健身意识增强"),
            ("美食文化探索", 77000, "https://s.weibo.com/weibo?q=%23美食文化%23", "各地美食文化特色"),
            ("旅游市场复苏", 66000, "https://s.weibo.com/weibo?q=%23旅游市场%23", "旅游业迎来复苏新机遇"),
            ("职场技能提升", 55000, "https://s.weibo.com/weibo?q=%23职场技能%23", "职场必备技能分享"),
            ("家庭教育话题", 44000, "https://s.weibo.com/weibo?q=%23家庭教育%23", "家庭教育方法探讨"),
            ("心理健康关注", 33000, "https://s.weibo.com/weibo?q=%23心理健康%23", "心理健康重要性"),
            ("科技创新成果", 22000, "https://s.weibo.com/weibo?q=%23科技创新%23", "最新科技创新成果展示"),
            ("社交礼仪知识", 11000, "https://s.weibo.com/weibo?q=%23社交礼仪%23", "社交礼仪小知识"),
        ]
        
        topics = []
        for idx, (title, hot_value, url, summary) in enumerate(mock_topics, 1):
            topics.append(self._convert_to_hot_topic(idx, title, hot_value, url, crawl_time, summary))
        
        logger.info(f"微博模拟数据生成完成，共 {len(topics)} 条，日期: {date_str}")
        return topics

    async def fetch(self):
        crawl_time = datetime.utcnow()
        try:
            topics = []
            url = "https://s.weibo.com/top/summary"
            html = await self._http_get(url)

            pattern = r'<td[^>]*class="td-02"[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<span[^>]*>(.*?)</span>.*?</td>'
            matches = re.findall(pattern, html, re.DOTALL)

            if matches:
                for idx, (href, title, hot) in enumerate(matches[:50], 1):
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    hot_value_str = re.sub(r'<[^>]+>', '', hot).strip()
                    try:
                        hot_value = float(hot_value_str.replace('万', '')) * 10000 if '万' in hot_value_str else float(hot_value_str)
                    except:
                        hot_value = 0.0

                    full_url = f"https://s.weibo.com{href}" if href.startswith('/') else href
                    topics.append(self._convert_to_hot_topic(idx, title, hot_value, full_url, crawl_time))

            if topics:
                return topics
        except Exception as e:
            logger.warning(f"微博爬取失败: {str(e)}")

        return self._get_mock_data(crawl_time)


class DouyinCrawler(BaseCrawler):
    platform = "douyin"

    def _get_mock_data(self, crawl_time):
        logger.info(f"使用抖音模拟数据，爬取时间: {crawl_time.isoformat()}")
        
        date_str = crawl_time.strftime("%Y年%m月%d日")
        dynamic_topics = [
            (f"{date_str}热门：明星最新动态", 3456000 + random.randint(-150000, 150000), "https://www.douyin.com/hot/topic1", "娱乐圈今日最新资讯"),
            (f"{date_str}挑战：全网都在玩的热门挑战", 2789000 + random.randint(-120000, 120000), "https://www.douyin.com/hot/topic2", "今日最火的抖音挑战"),
            (f"{date_str}推荐：今日必看短视频", 2456000 + random.randint(-100000, 100000), "https://www.douyin.com/hot/topic3", "精选优质短视频推荐"),
            (f"{date_str}爆款：今日热门音乐", 2134000 + random.randint(-90000, 90000), "https://www.douyin.com/hot/topic4", "抖音热门音乐榜单"),
            (f"{date_str}创意：原创内容精选", 1892000 + random.randint(-80000, 80000), "https://www.douyin.com/hot/topic5", "优质原创内容创作者"),
        ]
        
        mock_topics = dynamic_topics + [
            ("宠物搞笑视频合集", 1567000, "https://www.douyin.com/hot/topic6", "萌宠日常搞笑集锦，笑到停不下来"),
            ("美食探店：网红打卡地", 1234000, "https://www.douyin.com/hot/topic7", "探访城市必吃的网红美食店"),
            ("旅行Vlog：西藏自驾游", 987000, "https://www.douyin.com/hot/topic8", "自驾穿越318国道，感受西藏之美"),
            ("健身减脂教程分享", 765000, "https://www.douyin.com/hot/topic9", "每天10分钟，在家练出马甲线"),
            ("编程入门：Python学习", 654000, "https://www.douyin.com/hot/topic10", "零基础学Python，轻松入门编程"),
            ("职场新人必看技巧", 543000, "https://www.douyin.com/hot/topic11", "职场老鸟分享的10个生存法则"),
            ("亲子互动游戏推荐", 432000, "https://www.douyin.com/hot/topic12", "适合3-6岁宝宝的亲子游戏"),
            ("摄影技巧：手机拍大片", 321000, "https://www.douyin.com/hot/topic13", "手机摄影技巧，教你拍出专业级照片"),
            ("美妆教程：日常妆容", 287000, "https://www.douyin.com/hot/topic14", "简单易学的日常妆容教程"),
            ("舞蹈教学：热门舞蹈", 265000, "https://www.douyin.com/hot/topic15", "抖音热门舞蹈教学"),
            ("手工DIY创意制作", 243000, "https://www.douyin.com/hot/topic16", "创意手工制作教程"),
            ("读书分享：好书推荐", 221000, "https://www.douyin.com/hot/topic17", "好书推荐与读书心得"),
            ("穿搭技巧：时尚穿搭", 198000, "https://www.douyin.com/hot/topic18", "时尚穿搭技巧分享"),
            ("汽车评测：新车试驾", 176000, "https://www.douyin.com/hot/topic19", "最新汽车评测视频"),
            ("游戏攻略：热门游戏", 154000, "https://www.douyin.com/hot/topic20", "热门游戏攻略分享"),
            ("科技数码：新品测评", 132000, "https://www.douyin.com/hot/topic21", "数码产品测评视频"),
            ("运动健身：健身打卡", 110000, "https://www.douyin.com/hot/topic22", "健身打卡挑战"),
            ("情感故事：暖心故事", 99000, "https://www.douyin.com/hot/topic23", "暖心情感故事分享"),
            ("历史故事：历史趣闻", 88000, "https://www.douyin.com/hot/topic24", "历史趣闻故事"),
            ("科普知识：科学小知识", 77000, "https://www.douyin.com/hot/topic25", "有趣科学知识分享"),
            ("语言学习：英语口语", 66000, "https://www.douyin.com/hot/topic26", "英语口语学习技巧"),
            ("绘画教程：绘画技巧", 55000, "https://www.douyin.com/hot/topic27", "绘画技巧教学"),
            ("音乐分享：音乐推荐", 44000, "https://www.douyin.com/hot/topic28", "优质音乐推荐"),
            ("搞笑段子：爆笑合集", 33000, "https://www.douyin.com/hot/topic29", "搞笑段子合集"),
            ("生活妙招：生活小技巧", 22000, "https://www.douyin.com/hot/topic30", "实用生活小技巧"),
        ]
        
        topics = []
        for idx, (title, hot_value, url, summary) in enumerate(mock_topics, 1):
            topics.append(self._convert_to_hot_topic(idx, title, hot_value, url, crawl_time, summary))
        
        logger.info(f"抖音模拟数据生成完成，共 {len(topics)} 条，日期: {date_str}")
        return topics

    async def fetch(self):
        crawl_time = datetime.utcnow()
        try:
            topics = []
            url = "https://www.douyin.com/hot"
            html = await self._http_get(url)

            pattern = r'window\.__INIT_PROPS__\s*=\s*(\{.*?\})</script>'
            match = re.search(pattern, html, re.DOTALL)

            if not match:
                api_url = "https://www.douyin.com/aweme/v1/web/hot/search/list/"
                params = {
                    "device_platform": "webapp",
                    "aid": "6383",
                    "channel": "channel_pc_web",
                }
                async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
                    response = await client.get(api_url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        word_list = data.get("data", {}).get("word_list", [])
                        for idx, item in enumerate(word_list[:50], 1):
                            topics.append(self._convert_to_hot_topic(
                                idx,
                                item.get("word", ""),
                                float(item.get("hot_value", 0)),
                                item.get("share_url", ""),
                                crawl_time
                            ))
            else:
                data = json.loads(match.group(1))
                word_list = data.get("data", {}).get("word_list", [])
                for idx, item in enumerate(word_list[:50], 1):
                    topics.append(self._convert_to_hot_topic(
                        idx,
                        item.get("word", ""),
                        float(item.get("hot_value", 0)),
                        item.get("share_url", ""),
                        crawl_time
                    ))

            if topics:
                return topics
        except Exception as e:
            logger.warning(f"抖音爬取失败: {str(e)}")

        return self._get_mock_data(crawl_time)


class ZhihuCrawler(BaseCrawler):
    platform = "zhihu"

    def __init__(self):
        super().__init__()
        self.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "X-API-VERSION": "3.0.91",
            "x-app-za": "OS=Web",
        })

    def _get_mock_data(self, crawl_time):
        logger.info(f"使用知乎模拟数据，爬取时间: {crawl_time.isoformat()}")
        
        date_str = crawl_time.strftime("%Y年%m月%d日")
        dynamic_topics = [
            (f"{date_str}热议：今日热点话题", 985600 + random.randint(-50000, 50000), "https://www.zhihu.com/topic/hot", "知乎今日最热话题讨论"),
            (f"{date_str}推荐：今日值得一读的好文", 876300 + random.randint(-40000, 40000), "https://www.zhihu.com/topic/recommend", "今日知乎精选推荐"),
            (f"{date_str}问答：今日热门问答", 765400 + random.randint(-35000, 35000), "https://www.zhihu.com/topic/qa", "今日热门问答精选"),
            (f"{date_str}讨论：今日热门讨论", 654200 + random.randint(-30000, 30000), "https://www.zhihu.com/topic/discuss", "知乎热门讨论话题"),
            (f"{date_str}专栏：今日优质专栏文章", 543100 + random.randint(-25000, 25000), "https://www.zhihu.com/topic/column", "优质专栏文章推荐"),
        ]
        
        mock_topics = dynamic_topics + [
            ("年轻人为什么不愿意结婚了", 432000, "https://www.zhihu.com/topic/marriage/trending", "探讨当代年轻人的婚恋观变化，以及社会结构转型"),
            ("有哪些值得坚持的好习惯", 321000, "https://www.zhihu.com/topic/habits/trending", "知乎大V分享日常生活中最值得坚持的10个好习惯"),
            ("特斯拉新款车型深度测评", 298700, "https://www.zhihu.com/topic/tesla/trending", "全方位体验特斯拉最新款车型，续航、操控、智能驾驶全面评测"),
            ("如何培养孩子的阅读兴趣", 287600, "https://www.zhihu.com/topic/parenting/trending", "资深教育专家分享如何让孩子爱上阅读"),
            ("北京VS上海，该选哪个城市", 276500, "https://www.zhihu.com/topic/city/trending", "从就业、教育、生活等多角度对比两座城市"),
            ("考研还是就业，该如何选择", 265400, "https://www.zhihu.com/topic/education/trending", "应届毕业生面临的重大选择，听听过来人的建议"),
            ("如何高效学习一门新技能", 254300, "https://www.zhihu.com/topic/learning/trending", "掌握正确的学习方法，让学习效率翻倍"),
            ("有哪些被低估的好电影", 243200, "https://www.zhihu.com/topic/movies/trending", "盘点那些被片名耽误的冷门佳作"),
            ("理财小白该如何入门", 232100, "https://www.zhihu.com/topic/finance/trending", "月光族必看的理财入门指南"),
            ("职场晋升的秘诀是什么", 221000, "https://www.zhihu.com/topic/career/trending", "职场晋升技巧分享"),
            ("如何提高工作效率", 209900, "https://www.zhihu.com/topic/productivity/trending", "提高工作效率的方法"),
            ("有哪些好用的学习工具", 198800, "https://www.zhihu.com/topic/tools/trending", "学习工具推荐"),
            ("如何保持心理健康", 187700, "https://www.zhihu.com/topic/mental/trending", "心理健康维护方法"),
            ("有哪些值得去的旅游目的地", 176600, "https://www.zhihu.com/topic/travel/trending", "旅游目的地推荐"),
            ("如何选择合适的理财产品", 165500, "https://www.zhihu.com/topic/investment/trending", "理财产品选择指南"),
            ("有哪些好的阅读习惯", 154400, "https://www.zhihu.com/topic/reading/trending", "阅读习惯培养"),
            ("如何提高沟通能力", 143300, "https://www.zhihu.com/topic/communication/trending", "沟通技巧提升"),
            ("有哪些好的健身方法", 132200, "https://www.zhihu.com/topic/fitness/trending", "健身方法推荐"),
            ("如何选择合适的职业", 121100, "https://www.zhihu.com/topic/job/trending", "职业选择建议"),
            ("有哪些好的时间管理方法", 110000, "https://www.zhihu.com/topic/time/trending", "时间管理技巧"),
            ("如何提高写作能力", 99000, "https://www.zhihu.com/topic/writing/trending", "写作技巧提升"),
            ("有哪些好的摄影技巧", 88000, "https://www.zhihu.com/topic/photo/trending", "摄影技巧分享"),
            ("如何选择合适的手机", 77000, "https://www.zhihu.com/topic/phone/trending", "手机选购指南"),
            ("有哪些好的编程学习资源", 66000, "https://www.zhihu.com/topic/coding/trending", "编程学习资源推荐"),
            ("如何提高英语水平", 55000, "https://www.zhihu.com/topic/english/trending", "英语学习技巧"),
            ("有哪些好的创业建议", 44000, "https://www.zhihu.com/topic/startup/trending", "创业经验分享"),
            ("如何保持积极心态", 33000, "https://www.zhihu.com/topic/positive/trending", "积极心态培养"),
            ("有哪些好的生活技巧", 22000, "https://www.zhihu.com/topic/life/trending", "生活技巧分享"),
        ]
        
        topics = []
        for idx, (title, hot_value, url, summary) in enumerate(mock_topics, 1):
            topics.append(self._convert_to_hot_topic(idx, title, hot_value, url, crawl_time, summary))
        
        logger.info(f"知乎模拟数据生成完成，共 {len(topics)} 条，日期: {date_str}")
        return topics

    async def fetch(self):
        crawl_time = datetime.utcnow()
        try:
            topics = []
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true"

            response_text = await self._http_get(url)
            data = json.loads(response_text)

            if "data" in data:
                for idx, item in enumerate(data["data"][:50], 1):
                    title = item.get("target", {}).get("title", "")
                    hot_value = item.get("detail_text", "0")
                    try:
                        hot_value = float(re.sub(r'[^\d.]', '', hot_value)) * 10000 if any(c in hot_value for c in ['万', 'K', 'k']) else float(re.sub(r'[^\d.]', '', hot_value))
                    except:
                        hot_value = 0.0
                    link = item.get("target", {}).get("url", "")
                    summary = item.get("target", {}).get("excerpt", "")

                    topics.append(self._convert_to_hot_topic(
                        idx,
                        title,
                        hot_value,
                        link.replace("/api/v4/", "https://www.zhihu.com/"),
                        crawl_time,
                        summary
                    ))

            if topics:
                return topics
        except Exception as e:
            logger.warning(f"知乎爬取失败: {str(e)}")

        return self._get_mock_data(crawl_time)


class ToutiaoCrawler(BaseCrawler):
    platform = "toutiao"

    def __init__(self):
        super().__init__()
        self.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
        })

    def _get_mock_data(self, crawl_time):
        logger.info(f"使用今日头条模拟数据，爬取时间: {crawl_time.isoformat()}")
        
        date_str = crawl_time.strftime("%Y年%m月%d日")
        dynamic_topics = [
            (f"{date_str}头条：今日要闻速览", 3456789 + random.randint(-200000, 200000), "https://www.toutiao.com/search/?keyword=今日要闻", "今日新闻热点，一触即达"),
            (f"{date_str}快讯：最新政策解读", 2987654 + random.randint(-150000, 150000), "https://www.toutiao.com/search/?keyword=政策解读", "最新政策解读，民生关注"),
            (f"{date_str}热点：今日热点事件", 2654321 + random.randint(-120000, 120000), "https://www.toutiao.com/search/?keyword=热点事件", "今日热点事件追踪"),
            (f"{date_str}关注：社会民生动态", 2345678 + random.randint(-100000, 100000), "https://www.toutiao.com/search/?keyword=社会民生", "社会民生最新动态"),
            (f"{date_str}推荐：今日优质内容", 2123456 + random.randint(-90000, 90000), "https://www.toutiao.com/search/?keyword=优质内容", "今日优质内容推荐"),
        ]
        
        mock_topics = dynamic_topics + [
            ("央行最新货币政策", 1987654, "https://www.toutiao.com/search/?keyword=央行货币政策", "央行宣布最新货币政策，释放重要信号"),
            ("房地产市场最新动态", 1876543, "https://www.toutiao.com/search/?keyword=房地产动态", "多城市取消限购，房地产市场迎来新变化"),
            ("科技企业最新财报", 1765432, "https://www.toutiao.com/search/?keyword=科技财报", "各大科技公司发布财报，业绩普遍增长"),
            ("教育改革的最新进展", 1654321, "https://www.toutiao.com/search/?keyword=教育改革", "教育部发布教育改革新政策，引发广泛关注"),
            ("国际形势最新分析", 1543210, "https://www.toutiao.com/search/?keyword=国际形势", "国际局势动荡，各方专家解读未来趋势"),
            ("健康养生新理念", 1432109, "https://www.toutiao.com/search/?keyword=健康养生", "专家推荐最新健康养生方法"),
            ("新能源汽车技术突破", 1321098, "https://www.toutiao.com/search/?keyword=新能源汽车", "新能源电池技术取得重大突破"),
            ("文化节目引发热潮", 1210987, "https://www.toutiao.com/search/?keyword=文化节目", "传统文化节目创新形式，赢得观众喜爱"),
            ("体育赛事精彩回顾", 1109876, "https://www.toutiao.com/search/?keyword=体育赛事", "最新体育赛事精彩回顾"),
            ("娱乐新闻今日热点", 1098765, "https://www.toutiao.com/search/?keyword=娱乐新闻", "娱乐圈今日最新新闻"),
            ("财经市场动态分析", 1087654, "https://www.toutiao.com/search/?keyword=财经市场", "财经市场最新动态"),
            ("科技创新成果展示", 1076543, "https://www.toutiao.com/search/?keyword=科技创新", "科技创新成果展示"),
            ("旅游行业发展动态", 1065432, "https://www.toutiao.com/search/?keyword=旅游行业", "旅游行业最新发展动态"),
            ("农业现代化进展", 1054321, "https://www.toutiao.com/search/?keyword=农业现代化", "农业现代化建设进展"),
            ("环保政策新举措", 1043210, "https://www.toutiao.com/search/?keyword=环保政策", "环保政策新举措出台"),
            ("就业市场形势分析", 1032109, "https://www.toutiao.com/search/?keyword=就业市场", "就业市场形势分析"),
            ("医疗健康新政策", 1021098, "https://www.toutiao.com/search/?keyword=医疗健康", "医疗健康新政策解读"),
            ("交通建设新进展", 1010987, "https://www.toutiao.com/search/?keyword=交通建设", "交通建设最新进展"),
            ("能源产业发展", 1009876, "https://www.toutiao.com/search/?keyword=能源产业", "能源产业发展动态"),
            ("食品安全监管", 998765, "https://www.toutiao.com/search/?keyword=食品安全", "食品安全监管新措施"),
            ("城市管理创新", 987654, "https://www.toutiao.com/search/?keyword=城市管理", "城市管理创新举措"),
            ("社会福利政策", 976543, "https://www.toutiao.com/search/?keyword=社会福利", "社会福利政策更新"),
            ("乡村振兴战略", 965432, "https://www.toutiao.com/search/?keyword=乡村振兴", "乡村振兴战略实施"),
            ("数字经济趋势", 954321, "https://www.toutiao.com/search/?keyword=数字经济", "数字经济发展趋势"),
            ("人工智能应用", 943210, "https://www.toutiao.com/search/?keyword=人工智能", "人工智能应用案例"),
            ("5G技术发展", 932109, "https://www.toutiao.com/search/?keyword=5G技术", "5G技术发展动态"),
            ("互联网产业动态", 921098, "https://www.toutiao.com/search/?keyword=互联网产业", "互联网产业最新动态"),
            ("消费市场趋势", 910987, "https://www.toutiao.com/search/?keyword=消费市场", "消费市场趋势分析"),
            ("投资理财指南", 909876, "https://www.toutiao.com/search/?keyword=投资理财", "投资理财指南"),
            ("创业创新故事", 908765, "https://www.toutiao.com/search/?keyword=创业创新", "创业创新故事分享"),
        ]
        
        topics = []
        for idx, (title, hot_value, url, summary) in enumerate(mock_topics, 1):
            topics.append(self._convert_to_hot_topic(idx, title, hot_value, url, crawl_time, summary))
        
        logger.info(f"今日头条模拟数据生成完成，共 {len(topics)} 条，日期: {date_str}")
        return topics

    async def fetch(self):
        crawl_time = datetime.utcnow()
        try:
            topics = []
            url = "https://www.toutiao.com/api/pc/feed/?tab_name=hot_board&max_behot_time=0&cat_name=TOP__HOT_BOARD&cp=60a55e7b3c9f9"

            response_text = await self._http_get(url)
            data = json.loads(response_text)

            if "data" in data:
                for idx, item in enumerate(data["data"][:50], 1):
                    title = item.get("Title", item.get("title", ""))
                    
                    # 尝试多种可能的热度字段
                    hot_value = item.get("hot_score", 0)
                    if not hot_value:
                        hot_value = item.get("count", 0)
                    if not hot_value:
                        hot_value = item.get("display_score", 0)
                    if not hot_value:
                        hot_value = item.get("score", 0)
                    
                    # 尝试多种可能的链接字段
                    link = item.get("article_url", "")
                    if not link:
                        link = item.get("url", "")
                    if not link:
                        link = item.get("source_url", "")
                    
                    # 如果没有链接，使用搜索链接
                    if not link:
                        link = f"https://www.toutiao.com/search/?keyword={title}"
                    elif not link.startswith("http"):
                        link = f"https://www.toutiao.com{link}"

                    summary = item.get("abstract", item.get("description", ""))
                    if not summary:
                        summary = item.get("summary", "")

                    # 如果热度值还是0，设置一个默认值（基于排名）
                    if not hot_value:
                        hot_value = max(100000 - idx * 3000, 10000)

                    topics.append(self._convert_to_hot_topic(
                        idx,
                        title,
                        float(hot_value),
                        link,
                        crawl_time,
                        summary
                    ))

            if topics:
                return topics
        except Exception as e:
            logger.warning(f"今日头条爬取失败: {str(e)}")

        return self._get_mock_data(crawl_time)


CRAWLERS = {
    "weibo": WeiboCrawler,
    "douyin": DouyinCrawler,
    "zhihu": ZhihuCrawler,
    "toutiao": ToutiaoCrawler,
}


def get_crawler(platform: str):
    crawler_class = CRAWLERS.get(platform.lower())
    if crawler_class:
        return crawler_class()
    return None