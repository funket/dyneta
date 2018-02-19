# -*- coding: utf-8 -*-
"""
Module for automatic transformation of material data into graph representation
"""

import csv
import functools
import heapq as hp
import math


@functools.total_ordering
class Order(object):
    """contains a order with all information"""
    START_TIME_NEXT = "start time next"
    FOLLOWING_NEXT = "following next"
    nextMethod = START_TIME_NEXT

    def __init__(self, order_id, machine_id, start_time, end_time):
        """Creates new order and if supplied insert first step"""
        self.order_id = int(order_id)
        self.start_time = float(start_time)
        self.last_start_time = float(start_time)
        self.end_time = float(end_time)
        self.steps = []
        self.steps.append([int(machine_id), float(start_time), float(end_time)])

    def append_step(self, machine_id, start_time, end_time):
        """Append new step"""

        # Cast Parameters to right type
        i_machine_id = int(machine_id)
        f_start_time = float(start_time)
        f_end_time = float(end_time)

        # Check order
        if self.last_start_time > f_start_time:
            raise ValueError()

        self.last_start_time = f_start_time

        # Update order start_time and end_time
        if f_end_time > self.end_time:
            self.end_time = f_end_time
        self.steps.append([i_machine_id, f_start_time, f_end_time])

    def is_order_active(self, time):
        """ Check if order is active at given time """
        return self.start_time <= time <= self.end_time

    def number_of_active_steps(self, time):
        """Return number of active steps of a order at a given time"""
        if not self.is_order_active(time):
            return 0

        i = 0
        for _, start_time, end_time in self.steps:
            if start_time <= time <= end_time:
                i += 1
        return i

    def get_next_step_index(self, step_index):
        """
        Return index of next step with taking care of different next relationships
        """
        if Order.nextMethod == Order.START_TIME_NEXT:
            if step_index < len(self.steps) - 1:
                return step_index + 1
            else:
                raise IndexError()
        elif Order.nextMethod == Order.FOLLOWING_NEXT:
            search_index = step_index + 1
            # Search next Index of a step which starts after actual step
            while search_index < len(self.steps) - 1:
                if (self.steps[step_index][2]
                        < self.steps[search_index][1]):
                    return search_index
                search_index += 1
            # else:
            raise IndexError()
        else:
            raise ValueError()

    def __len__(self):
        return len(self.steps)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.order_id == other.order_id
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return self.order_id <= other.order_id
        return NotImplemented

    def __hash__(self):
        return hash(self.order_id)


class Data(object):
    """Contain one Dataset"""

    def __init__(self, filename, keep_raw_data=False,
                 with_plausible_check=False,
                 keep_single_line_orders=False):
        self.filename = filename
        self.raw_data = []
        self.orders = []
        self.last_order = Order(-1, 0, 0, 0)
        self._number_of_lines = 0
        self.keep_raw_data = keep_raw_data
        self.with_plausible_check = with_plausible_check
        self.keep_single_line_orders = keep_single_line_orders

    def append_data(self, order_id, machine_id, start_time, end_time):
        """Append single Data line"""
        step_info = [order_id, machine_id, start_time, end_time]
        #       first plausible check
        if (self.with_plausible_check and
                not self.is_data_plausible(*step_info)):
            return

        # if demanded keep raw data
        if self.keep_raw_data:
            self.raw_data.append(*step_info)

        # distinguish adding to the same order or create a new one
        if self.last_order.order_id != int(order_id):
            # check if order only contain one line (and not the first one)
            if not self.keep_single_line_orders and len(self.last_order) == 1 and self.last_order.order_id != -1:
                self.orders.pop()
            new_order = Order(*step_info)
            self.orders.append(new_order)
            self.last_order = new_order
        else:
            self.last_order.append_step(*step_info[1:])

        self._number_of_lines += 1

    # noinspection PyUnusedLocal
    @staticmethod
    def is_data_plausible(self, order_id, machine_id, start_time, end_time):
        """ A simple check if data make sense"""
        #       check if step needed time
        return start_time < end_time

    def get_orders(self):
        return self.orders


class OrderIterator(object):
    """ Iterates stepwise over orders """

    def __init__(self, orders):
        self.orders = orders
        if len(orders) == 0:
            raise ValueError()
        self.next_candidates = []
        order_iterator = iter(orders)
        first_order = next(order_iterator)
        self._push_new_candidate(
            first_order.start_time,
            first_order,
            0,
            True,
            order_iterator)

    def _push_new_candidate(self, start_time, new_order, step_index,
                            is_last_order=False, iterator=None):
        if is_last_order:
            hp.heappush(
                self.next_candidates,
                (start_time,
                 new_order,
                 step_index,
                 is_last_order,
                 iterator)
            )
        else:
            hp.heappush(
                self.next_candidates,
                (start_time,
                 new_order,
                 step_index,
                 is_last_order)
            )

    def __iter__(self):
        return self

    def next(self):
        """Get next step"""
        #        Trivial check if finished
        if len(self.next_candidates) == 0:
            raise StopIteration()

        next_candidate = hp.heappop(self.next_candidates)

        actual_order, step_index, is_last_order = next_candidate[1:4]

        # if last order then include next from the list
        # in addition to already existing orders
        if is_last_order:
            iterator = next_candidate[4]
            try:
                next_order = next(iterator)
                self._push_new_candidate(
                    next_order.start_time,
                    next_order,
                    0,
                    True,
                    iterator)
            except StopIteration:
                pass

                #        in case not the last step of that order insert this one
        if step_index < len(actual_order.steps) - 1:
            self._push_new_candidate(
                actual_order.steps[step_index + 1][1],  # start time of next step
                actual_order,
                step_index + 1,
                False
            )

        return actual_order, step_index


class AbstractGraphConstructor(object):
    """ Creates graph out of Data object """

    def __init__(self, data, graph, with_weight=True):
        self.data = data
        self.step_iterator = OrderIterator(data.get_orders())
        self.graph = graph
        self._with_weight = with_weight
        self._saved_data = None

    def _add_edge(self, node_text_u, node_text_v):
        """Add Edge to graph"""
        pass

    def get_graph_stepwise(self):
        """ Create graph step by step """
        #       determine next step
        try:
            actual_order, step_index = self.step_iterator.next()
        except StopIteration:
            raise StopIteration()

        node_order_text = 'O' + str(actual_order.order_id)
        node_machine_text = 'M' + str(actual_order.steps[step_index][0])
        self._add_edge(node_order_text, node_machine_text)
        return actual_order.steps[step_index][1]

    def get_graph_stepwise_projected(self, add_edge=True):
        """ Project on machines. Returns time of added edge """
        # read next steps until one has a follower (next step inside his order)
        while True:
            try:
                actual_order, step_index = self.step_iterator.next()
            except StopIteration:
                raise StopIteration()

            try:
                next_step_index = actual_order.get_next_step_index(step_index)
                break
            except IndexError:
                pass

        first_machine = 'M' + str(actual_order.steps[next_step_index][0])
        second_machine = 'M' + str(actual_order.steps[step_index][0])
        if add_edge:
            self._add_edge(first_machine, second_machine)
            return actual_order.steps[step_index][1]
        # else
        return actual_order.steps[step_index][1], (first_machine, second_machine)

    def get_full_graph(self):
        """ Read full graph using get_graph_stepwise method"""
        while True:
            try:
                self.get_graph_stepwise()
            except StopIteration:
                break

    def get_full_graph_projected(self):
        """ Read full graph using get_graph_stepwise_projected method"""
        while True:
            try:
                self.get_graph_stepwise_projected()
            except StopIteration:
                break

    def get_daily_graph(self, clear_graph=False, number_of_days=1):
        if clear_graph:
            self.graph.clear()

        # read first line and get time
        if self._saved_data is None:
            time, edge = self.get_graph_stepwise_projected(False)
        else:
            time, edge = self._saved_data
        # get "next" day via small offset and round to next integer
        #  offset needed because maybe encounter time = 1.0 but want then -> 2
        day = int(math.ceil(time + .0001 + (number_of_days - 1)))
        # no endless loop because of StopIndex from get_graph_stepwise
        while time < day:
            self._add_edge(*edge)
            time, edge = self.get_graph_stepwise_projected(False)
        else:
            self._saved_data = time, edge


class NxGraphConstructor(AbstractGraphConstructor):
    """ Constructor for Graph from NetworkX Package"""

    def __init__(self, data, graph, with_weight=True):
        super(NxGraphConstructor, self).__init__(data, graph, with_weight)

    def _add_edge(self, node_text_u, node_text_v):
        if self._with_weight:
            if self.graph.has_edge(node_text_u, node_text_v):
                self.graph[node_text_u][node_text_v]['weight'] += 1
                self.graph[node_text_u][node_text_v]['inverted w'] = 1.0 / self.graph[node_text_u][node_text_v][
                    'weight']
            else:
                self.graph.add_edge(node_text_u, node_text_v, weight=1)
                self.graph[node_text_u][node_text_v]['inverted w'] = 1
        else:
            self.graph.add_edge(node_text_u, node_text_v)


class GtGraphConstructor(AbstractGraphConstructor):
    """ Constructor for Graph from NetworkX Package"""

    def __init__(self, data, graph, with_weight=True):
        super(GtGraphConstructor, self).__init__(data, graph, with_weight)
        self._nodes = {}
        if with_weight:
            self._weights = graph.new_edge_property("double")

    def _add_edge(self, node_text_u, node_text_v):
        node_key_u = self._get_node_key(node_text_u)
        node_key_v = self._get_node_key(node_text_v)

        edge = self.graph.edge(node_key_u, node_key_v)
        if edge is None:
            edge = self.graph.add_edge(node_key_u, node_key_v)
            if self._with_weight:
                self._weights[edge] = 0
        if self._with_weight:
            self._weights[edge] += 1

    def _get_node_key(self, node_text):
        """ Return node_key from given node text """
        if node_text not in self._nodes:
            node_key = self.graph.add_vertex()
            self._nodes.update({node_text: node_key})
        else:
            node_key = self._nodes[node_text]
        return node_key


def read_data_from_file(filename):
    """Creates Data object from file"""
    data = Data(filename)
    i = 1
    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        #        Skip header
        next(reader)
        for line in reader:
            data.append_data(*line)
            i += 1
            #   if needed sort orders by start_time
    data.orders.sort(key=lambda order: order.start_time)
    return data

# Link your data
DATASETS = ['../data/a.csv']
