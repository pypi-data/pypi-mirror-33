import scrapy


class ApptItem(scrapy.Item):
    complex_name = scrapy.Field()
    complex_id = scrapy.Field()
    complex_url = scrapy.Field()
    complex_wall_type = scrapy.Field()
    addr = scrapy.Field()

    house_id = scrapy.Field()
    house_name = scrapy.Field()
    house_url = scrapy.Field()
    house_deadline = scrapy.Field()
    house_max_floor = scrapy.Field()

    id = scrapy.Field()
    floor = scrapy.Field()
    room_count = scrapy.Field()
    square = scrapy.Field()
    price = scrapy.Field()
    is_studio = scrapy.Field()
    plan_url = scrapy.Field()
    is_apartment = scrapy.Field()
    has_finishing = scrapy.Field()
