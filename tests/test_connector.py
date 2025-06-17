from .base_class import VisuscriptTestCase
from visuscript.connector import Edges, ElementsAlreadyConnectedError, ElementsNotConnectedError
from visuscript.element import Circle
class TestEdges(VisuscriptTestCase):

    def test_connecting(self):

        edges = Edges()

        circles = [Circle(5) for _ in range(4)]


        edges.connect(circles[0], circles[1])
        edges.connect(circles[1], circles[2])
        edges.connect(circles[3], circles[2])

        self.assertFalse(edges.connected(circles[0], circles[0]))
        self.assertFalse(edges.connected(circles[1], circles[1]))
        self.assertFalse(edges.connected(circles[2], circles[2]))
        self.assertFalse(edges.connected(circles[3], circles[3]))


        self.assertTrue(edges.connected(circles[0], circles[1]))
        self.assertTrue(edges.connected(circles[1], circles[0]))

        self.assertTrue(edges.connected(circles[1], circles[2]))
        self.assertTrue(edges.connected(circles[2], circles[1]))

        self.assertTrue(edges.connected(circles[3], circles[2]))
        self.assertTrue(edges.connected(circles[2], circles[3]))

        self.assertFalse(edges.connected(circles[0], circles[2]))
        self.assertFalse(edges.connected(circles[2], circles[0]))

        self.assertFalse(edges.connected(circles[0], circles[3]))
        self.assertFalse(edges.connected(circles[3], circles[0]))

        self.assertFalse(edges.connected(circles[1], circles[3]))
        self.assertFalse(edges.connected(circles[3], circles[1]))

        


    def test_connecting_errors(self):

        edges = Edges()

        circles = [Circle(5) for _ in range(4)]


        edges.connect(circles[0], circles[1])
        edges.connect(circles[1], circles[2])
        edges.connect(circles[3], circles[2])

        self.assertRaises(ElementsAlreadyConnectedError,
                          lambda: edges.connect(circles[0], circles[1]))
        self.assertRaises(ElementsAlreadyConnectedError,
                          lambda: edges.connect(circles[1], circles[0]))
        
        edges.get_edge(circles[0], circles[1])
        edges.get_edge(circles[1], circles[0])

        self.assertRaises(ElementsNotConnectedError,
                          lambda: edges.get_edge(circles[0], circles[3])
                          )
        self.assertRaises(ElementsNotConnectedError,
                          lambda: edges.get_edge(circles[3], circles[0])
                          )
        
    
    def test_connect_by_rule(self):

        edges = Edges()

        circles = [Circle(5) for _ in range(7)]

        circles[0].previous = None

        circles[1].previous = circles[0]
        circles[2].previous = circles[0]

        circles[3].previous = circles[1]
        circles[4].previous = circles[1]
        circles[5].previous = circles[2]
        circles[6].previous = circles[2]

        edges.connect(circles[0], circles[3])

        rule = lambda e1, e2: e2.previous is e1

        edges.connect_by_rule(rule, circles)

        self.assertTrue(edges.connected(circles[0], circles[1]))
        self.assertTrue(edges.connected(circles[2], circles[0]))

        self.assertTrue(edges.connected(circles[1], circles[3]))
        self.assertTrue(edges.connected(circles[4], circles[1]))

        self.assertTrue(edges.connected(circles[5], circles[2]))
        self.assertTrue(edges.connected(circles[2], circles[6]))

        self.assertFalse(edges.connected(circles[0], circles[3]))
        self.assertFalse(edges.connected(circles[1], circles[6]))
        self.assertFalse(edges.connected(circles[6], circles[1]))


    def test_connect_by_rule_animation(self):

        edges = Edges()

        circles = [Circle(5) for _ in range(7)]

        circles[0].previous = None

        circles[1].previous = circles[0]
        circles[2].previous = circles[0]

        circles[3].previous = circles[1]
        circles[4].previous = circles[1]
        circles[5].previous = circles[2]
        circles[6].previous = circles[2]

        edges.connect(circles[0], circles[3]).finish()
        line_to_fade_away = edges.get_edge(circles[0], circles[3])

        rule = lambda e1, e2: e2.previous is e1
        animation = edges.connect_by_rule(rule, circles)
        self.assertEqual(line_to_fade_away.opacity, 1)

        fade_in_lines = [
            edges.get_edge(circles[0], circles[1]),
            edges.get_edge(circles[0], circles[2]),
            edges.get_edge(circles[1], circles[3]),
            edges.get_edge(circles[1], circles[4]),
            edges.get_edge(circles[2], circles[5]),
            edges.get_edge(circles[2], circles[6]),
        ]

        self.assertEqual(len(list(edges.lines_iter())), 6)
        for line in fade_in_lines:
            self.assertEqual(line.opacity, 0)

    
        animation.finish()
        self.assertEqual(line_to_fade_away.opacity, 0)

        self.assertEqual(len(list(edges.lines_iter())), 6)
        for line in fade_in_lines:
            self.assertEqual(line.opacity, 1)





        