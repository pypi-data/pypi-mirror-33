#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import unittest
from GLXCurses import Container
from GLXCurses import Adjustment
from GLXCurses import Box
from GLXCurses.Utils import glxc_type
from GLXCurses.Utils import is_valid_id


# Unittest
class TestBin(unittest.TestCase):
    # Test
    def test_type(self):
        """Test Container type"""
        self.assertTrue(glxc_type(Container()))

    def test_add(self):
        """Test Container.add()"""
        container = Container()
        # Test add method for None parameter
        # Create a child
        child1 = Container()
        child2 = Container()
        # Add the child
        container.add(child1)
        # We must have the child inside the child list
        self.assertEqual(container._get_child()['widget'], child1)
        # Add the child
        container.add(child2)
        # We must have the child inside the child list
        self.assertEqual(container._get_child()['widget'], child2)
        # Test type error
        self.assertRaises(TypeError, container.add, int())
        self.assertRaises(TypeError, container.add)

    def test_remove(self):
        """Test Container.remove()"""
        # create our tested container
        container = Container()

        # Create a child
        child1 = Container()
        child2 = Box()

        # Add the child and test
        container.add(child1)
        self.assertEqual(container._get_child()['widget'], child1)

        # remove and test
        container.remove(child1)
        self.assertEqual(container._get_child(), None)

        # Add the child and test
        container.add(child2)
        self.assertEqual(container._get_child()['widget'], child2)

        child2.pack_start(child1)
        self.assertEqual(child2.get_children()[0]['widget'], child1)

        # remove and test
        child2.remove(child1)
        self.assertEqual(len(child2.get_children()), 0)

        # we still have the child 2
        self.assertEqual(container._get_child()['widget'], child2)

        # we remove child 2
        container.remove(child2)
        self.assertEqual(container._get_child(), None)

        # Test type error
        self.assertRaises(TypeError, container.remove, int())
        self.assertRaises(TypeError, container.remove)
        self.assertRaises(TypeError, container.remove, child2, int())

    def test_add_with_properties(self):
        """Test Container.add_with_property()"""
        container = Container()
        # Create a child
        child1 = Container()
        # prepare a property
        child_properties = {
            'position': 0,
            'Galaxie': 42
        }
        # Add the child
        container.add_with_properties(child1, properties=child_properties)
        # We must have the child inside the child list
        self.assertEqual(container._get_child()['widget'], child1)
        self.assertEqual(container._get_child()['properties']['Galaxie'], 42)
        # Test type error
        self.assertRaises(TypeError, container.add_with_properties, int())
        self.assertRaises(TypeError, container.add_with_properties, child1, int())

    def test_get_children(self):
        """Test Container.get_children()"""
        # prepare container
        container = Container()
        # it's a list
        self.assertEqual(type(container.get_children()), type(list()))
        # prepare a children
        box1 = Box()
        box2 = Box()

        box1.pack_start(box2)
        self.assertEqual(box1.get_children()[0]['widget'], box2)

    def test_set_get_focus_vadjustment(self):
        """Test Container.set_focus_vadjustment() and Container.get_focus_vadjustment()"""
        # prepare container
        container = Container()
        # prepare children
        adjustment = Adjustment()
        box = Box()
        # set
        container.set_focus_vadjustment(adjustment=adjustment)
        # get
        self.assertEqual(container.get_focus_vadjustment()['widget'], adjustment)
        self.assertTrue(is_valid_id(container.get_focus_vadjustment()['id']))
        self.assertEqual(type(container.get_focus_vadjustment()['properties']), type(dict()))
        # set None
        container.set_focus_vadjustment(adjustment=None)
        # get None
        self.assertEqual(container.get_focus_vadjustment(), None)
        # test raise
        self.assertRaises(TypeError, container.set_focus_vadjustment, int())
        self.assertRaises(TypeError, container.set_focus_vadjustment, box)

    def test_set_get_focus_hadjustment(self):
        """Test Container.set_focus_hadjustment() and Container.get_focus_hadjustment()"""
        # prepare container
        container = Container()
        # prepare children
        adjustment = Adjustment()
        box = Box()
        # set
        container.set_focus_hadjustment(adjustment=adjustment)
        # get
        self.assertEqual(container.get_focus_hadjustment()['widget'], adjustment)
        self.assertTrue(is_valid_id(container.get_focus_hadjustment()['id']))
        self.assertEqual(type(container.get_focus_hadjustment()['properties']), type(dict()))
        # set None
        container.set_focus_hadjustment(adjustment=None)
        # get None
        self.assertEqual(container.get_focus_hadjustment(), None)
        # test raise
        self.assertRaises(TypeError, container.set_focus_hadjustment, int())
        self.assertRaises(TypeError, container.set_focus_hadjustment, box)

    def test_child_type(self):
        """Test Container.child-type"""
        # create our tested container
        container = Container()

        # child
        box1 = Box()
        box2 = Box()

        cont1 = Container()
        cont2 = Container()

        # The container haven't it self as child then waiting -1
        self.assertEqual(container.child_type(container), -1)

        container.add(box1)
        # when it work normally
        self.assertEqual(container.child_type(box1), 'GLXCurses.Box')

        box1.pack_start(cont1)
        # when it work normally
        self.assertEqual(box1.child_type(cont1), 'GLXCurses.Container')

        cont1.add(box2)
        # cont1 have no more child space
        self.assertEqual(box1.child_type(cont1), None)

        # yes it work
        box2.pack_start(cont2)
        self.assertEqual(box2.child_type(cont2), 'GLXCurses.Container')
        self.assertEqual(box2.child_type(cont1), -1)
        # change for a single child
        ###########################
        # create our tested container
        container = Container()

        # child
        box1 = Box()
        box2 = Box()

        cont1 = Container()
        cont2 = Container()

        # The container haven't it self as child then waiting -1
        self.assertEqual(container.child_type(container), -1)

        container.add(cont1)
        # when it work normally
        self.assertEqual(container.child_type(cont1), 'GLXCurses.Container')
        self.assertEqual(container.child_type(cont2), -1)

        cont1.add(box1)
        # Should have no space
        self.assertEqual(container.child_type(cont1), None)

        box1.pack_start(box2)
        self.assertEqual(cont1.child_type(box1), 'GLXCurses.Box')

    def test_child_get(self):
        """Test Container.child_get()"""
        # Use Container as main container (single child)
        # create our tested container
        container = Container()

        # Create a child
        child1 = Container()
        child2 = Container()

        # Add the child and test
        container.add(child1)
        self.assertEqual(container._get_child()['widget'], child1)

        # check if we receive a dict type
        self.assertEqual(type(container.child_get(child1)), type(dict()))

        self.assertEqual(container.child_get(child1), container._get_child()['properties'])

        # return None if child is not found
        self.assertEqual(None, container.child_get(child2))

        # Use Box as main container (multiple child)
        # create our tested container
        container_to_test = Box()

        # Create a child
        child_to_test1 = Container()
        child_to_test2 = Container()
        child_to_test3 = Container()

        # Add the child and test
        container_to_test.pack_start(child_to_test2)
        container_to_test.pack_start(child_to_test1)
        self.assertEqual(container_to_test.get_children()[0]['widget'], child_to_test1)
        self.assertEqual(
            container_to_test.get_children()[0]['properties'],
            container_to_test.child_get(child_to_test1)
        )
        # return None if child is not found
        self.assertEqual(None, container_to_test.child_get(child_to_test3))

        # check if we receive a dict type
        self.assertEqual(type(container_to_test.child_get(child_to_test1)), type(dict()))

        # Test type error
        self.assertRaises(TypeError, container.child_get, int())
        self.assertRaises(TypeError, container.child_get)

    def test_child_set(self):
        """Test Container.child_set()"""
        # Use Container as main container (single child)
        # create our tested container
        container = Container()

        # Create a child
        child1 = Container()
        child2 = Container()

        # Add the child and test
        container.add(child1)
        added_properties = {'Galaxie': 42.42}

        # use child set
        old_properties = container._get_child()['properties']
        container.child_set(child1, added_properties)
        new_properties = container._get_child()['properties']

        # check result
        self.assertGreater(len(new_properties), len(old_properties))
        self.assertEqual(
            type(float()),
            type(container._get_child()['properties']['Galaxie'])
        )

        # Use Box as main container (multiple child)
        # create our tested container
        container_to_test = Box()

        # Create a child
        child_to_test1 = Container()

        # Add the child and test
        container_to_test.pack_start(child_to_test1)

        old_properties = container_to_test.get_children()[0]['properties']
        container_to_test.child_set(child_to_test1, added_properties)
        new_properties = container_to_test.get_children()[0]['properties']

        # check result
        self.assertGreater(len(new_properties), len(old_properties))
        self.assertEqual(
            type(float()),
            type(container._get_child()['properties']['Galaxie'])
        )

        # raise error
        self.assertRaises(TypeError, container.child_set, int())
        self.assertRaises(TypeError, container.child_set)
        self.assertRaises(TypeError, container.child_set, child2, int())
        self.assertRaises(TypeError, container.child_set, child2)

    def test_child_set_property(self):
        """Test Container.child_set_property()"""
        # Use Container as main container (single child)
        # create our tested container
        container = Container()

        # Create a child
        child1 = Container()
        child2 = Container()

        # Add the child and test
        container.add(child1)

        # use child set
        old_properties = container._get_child()['properties']
        container.child_set_property(child1, property_name='Galaxie', value=42.42)
        new_properties = container._get_child()['properties']

        # check result
        self.assertGreater(len(new_properties), len(old_properties))
        self.assertEqual(
            type(float()),
            type(container._get_child()['properties']['Galaxie'])
        )

        # Use Box as main container (multiple child)
        # create our tested container
        container_to_test = Box()

        # Create a child
        child_to_test1 = Container()

        # Add the child and test
        container_to_test.pack_start(child_to_test1)

        old_properties = container_to_test.get_children()[0]['properties']
        container_to_test.child_set_property(child_to_test1, property_name='Galaxie', value=42.42)
        new_properties = container_to_test.get_children()[0]['properties']

        # check result
        self.assertGreater(len(new_properties), len(old_properties))
        self.assertEqual(
            type(float()),
            type(container._get_child()['properties']['Galaxie'])
        )

        # check raise
        self.assertRaises(TypeError, container.child_set_property, int())
        self.assertRaises(TypeError, container.child_set_property)
        self.assertRaises(TypeError, container.child_set_property, child2, int())
        self.assertRaises(TypeError, container.child_set_property, child2)
        self.assertRaises(TypeError, container.child_set_property, child2, 'Galaxie', None)
        self.assertRaises(TypeError, container.child_set_property, child2, 'Galaxie')

    def test_child_get_property(self):
        """Test Container.child_get_property()"""
        # Use Container as main container (single child)
        # create our tested container
        container = Container()

        # Create a child
        child1 = Container()

        # Add the child and test
        container.add(child1)

        # use child set
        container.child_set_property(child1, property_name='Galaxie', value=42.00)
        old_properties = container.child_get_property(child1, 'Galaxie')
        container.child_set_property(child1, property_name='Galaxie', value=42.42)
        new_properties = container.child_get_property(child1, 'Galaxie')

        # check result
        self.assertGreater(new_properties, old_properties)
        self.assertEqual(
            type(float()),
            type(container.child_get_property(child1, 'Galaxie'))
        )

        # Use Box as main container (multiple child)
        # create our tested container
        container_to_test = Box()

        # Create a child
        child_to_test1 = Container()

        # Add the child and test
        container_to_test.pack_start(child_to_test1)

        container_to_test.child_set_property(child_to_test1, property_name='Galaxie', value=42.00)
        old_properties = container_to_test.child_get_property(child_to_test1, 'Galaxie')
        container_to_test.child_set_property(child_to_test1, property_name='Galaxie', value=42.42)
        new_properties = container_to_test.child_get_property(child_to_test1, 'Galaxie')

        # check result
        self.assertGreater(new_properties, old_properties)
        self.assertEqual(
            type(float()),
            type(container_to_test.child_get_property(child_to_test1, 'Galaxie'))
        )

        # check raise
        self.assertRaises(TypeError, container.child_get_property, int())
        self.assertRaises(TypeError, container.child_get_property)
