import unittest

from urlymath.parse.parse import *


class TestElements(unittest.TestCase):
    def test_protocol(self):
        url = parse('')
        protocol = Protocol(url, 'https')
        self.assertEqual(protocol.parsed_element, ['https'])
        self.assertEqual(protocol.dressed_element, 'https://')

    def test_subdomain(self):
        url = parse('')
        subdomain = SubDomain(url, 'www')
        self.assertEqual(subdomain.parsed_element, ['www'])
        self.assertEqual(subdomain.dressed_element, 'www.')

    def test_sld(self):
        url = parse('')
        sld = SecondLevelDomain(url, 'example')
        self.assertEqual(sld.parsed_element, ['example'])
        self.assertEqual(sld.dressed_element, 'example.')

    def test_tld(self):
        url = parse('')
        tld = TopLevelDomain(url, 'co.kr')
        self.assertEqual(tld.parsed_element, ['co.kr'])
        self.assertEqual(tld.dressed_element, 'co.kr')
        # get country of origin
        self.assertEqual(tld.country, 'Korea, Republic of')

    def test_port(self):
        url = parse('')
        port = Port(url, '80')
        self.assertEqual(port.parsed_element, ['80'])
        self.assertEqual(port.dressed_element, ':80')

    def test_path(self):
        url = parse('')
        path = Path(url, 'path1/path2')
        self.assertEqual(path.parsed_element, ['path1', 'path2'])
        self.assertEqual(path.dressed_element, '/path1/path2')
        # add elements to the path hierarchy
        path.append('path3')  # with no leading slash
        self.assertEqual(path, 'path1/path2/path3')
        path.append('/path4')  # with leading slash
        self.assertEqual(path, 'path1/path2/path3/path4')
        path.append('path5/path6')  # double!
        self.assertEqual(path, 'path1/path2/path3/path4/path5/path6')
        self.assertEqual(path.parsed_element, ['path1', 'path2', 'path3', 'path4', 'path5', 'path6'])

    def test_file(self):
        url = parse('')
        file = File(url, 'page.php')
        self.assertEqual(file.parsed_element, ('page', 'php'))
        self.assertEqual(file.dressed_element, '/page.php')
        # get filename and extension
        self.assertEqual(file.filename, 'page')
        self.assertEqual(file.ext, 'php')

    def test_query(self):
        url = parse('')
        query = Query(url, '?query1=one&query2=&query3=three')
        self.assertEqual(query.parsed_element, [('query1', 'one'), ('query2', ''), ('query3', 'three')])
        self.assertEqual(query.dressed_element, '?query1=one&query2=&query3=three')
        # add elements to the query
        query.append('query4=')  # with no leading question mark and blank value
        self.assertEqual(query, '?query1=one&query2=&query3=three&query4=')
        query.append('query5=')  # with no leading question mark and blank value
        self.assertEqual(query, '?query1=one&query2=&query3=three&query4=&query5=')
        query.append('?query6=six')  # with leading question mark
        self.assertEqual(query, '?query1=one&query2=&query3=three&query4=&query5=&query6=six')
        query.append('query7=seven&query8=eight')  # double!
        self.assertEqual(query, '?query1=one&query2=&query3=three&query4=&query5=&query6=six&query7=seven&query8=eight')
        with self.assertRaises(NonSensicalUrlStructure):
            query.append('')  # quits!
        self.assertEqual(query, '?query1=one&query2=&query3=three&query4=&query5=&query6=six&query7=seven&query8=eight')
        self.assertEqual(
            query.parsed_element, [
                ('query1', 'one'), ('query2', ''),
                ('query3', 'three'), ('query4', ''),
                ('query5', ''), ('query6', 'six'),
                ('query7', 'seven'), ('query8', 'eight')
            ]
        )

    def test_fragments(self):
        url = parse('')
        fragments = FragmentElement(url, '#frag1&frag2')
        self.assertEqual(fragments.parsed_element, ['frag1', 'frag2'])
        self.assertEqual(fragments.dressed_element, '#frag1&frag2')
        # add elements to the path hierarchy
        fragments.append('frag3')  # with no leading hash
        self.assertEqual(fragments, '#frag1&frag2&frag3')
        fragments.append('#frag4')  # with leading hash
        self.assertEqual(fragments, '#frag1&frag2&frag3&frag4')
        fragments.append('frag5&frag6')  # double!
        self.assertEqual(fragments, '#frag1&frag2&frag3&frag4&frag5&frag6')
        self.assertEqual(fragments.parsed_element, ['frag1', 'frag2', 'frag3', 'frag4', 'frag5', 'frag6'])


class TestParse(unittest.TestCase):
    def test_parse(self):
        url = parse("http://www.example.co.kr:80/path1/path2/file.php?query1=one&query2=two#frag1&frag2")
        self.assertEqual(url, "http://www.example.co.kr:80/path1/path2/file.php?query1=one&query2=two#frag1&frag2")
        self.assertEqual(url.query, '?query1=one&query2=two')
        self.assertEqual(url - url.query, "http://www.example.co.kr:80/path1/path2/file.php#frag1&frag2")


if __name__ == '__main__':
    unittest.main()
