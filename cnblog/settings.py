# -*- coding: utf-8 -*-

# Scrapy settings for cnblog project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'cnblog'

SPIDER_MODULES = ['cnblog.spiders']
NEWSPIDER_MODULE = 'cnblog.spiders'
DOWNLOAD_DELAY = 0.25

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'cnblog (+http://www.yourdomain.com)'
