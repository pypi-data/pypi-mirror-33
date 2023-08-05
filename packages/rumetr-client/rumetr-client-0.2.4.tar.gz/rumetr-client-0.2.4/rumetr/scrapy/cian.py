from scrapy.spiders import XMLFeedSpider

from rumetr.scrapy import ApptItem as Item


class CianFeedSpider(XMLFeedSpider):
    """Base Spider to parse cian feed"""
    name = 'spider'
    itertag = 'offer'
    iterator = 'xml'
    # field complex_names must be overriden in child class 
    complex_names = dict()

    def parse_node(self, response, node):
        yield Item(
            complex_id=node.xpath('residential_complex/@id')[0].extract(),
            complex_name=self.get_complex_name_by_id(node.xpath('residential_complex/@id')[0].extract()),
            addr= self.get_address(node),

            house_id=node.xpath('residential_complex/@korpusid')[0].extract(),
            house_name=node.xpath('address/@house_str')[0].extract(),

            id=node.xpath('id/text()')[0].extract(),
            floor=node.xpath('floor/text()')[0].extract(),
            room_count=node.xpath('rooms_num/text()')[0].extract(),
            square=node.xpath('area/@total')[0].extract(),
            price=node.xpath('price/text()')[0].extract(),
        )

    def get_address(self, node):
        city = node.xpath('address/@locality')[0].extract()
        street = node.xpath('address/@street')[0].extract()
        house_str = node.xpath('address/@house_str')[0].extract()
        return ', '.join(x for x in [city, street, house_str])

    def get_complex_name_by_id(self, complex_id):
        try:
            return self.complex_names[complex_id]
        except KeyError:
            raise Exception('There is no complex_name in dictionary which matches id {}'.format(complex_id))
