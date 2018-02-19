import random as rd

import matplotlib

matplotlib.use('TkAgg')
# import order needed like described in pycxsimulator
# noinspection PyPep8
import networkx as nx
# noinspection PyPep8
import data_reader_module
# noinspection PyPep8
import network_analysis as neta

# initialize Random
rd.seed()


class Main(object):
    """Holder class for the main central functions"""

    def __init__(self):
        self._graph = nx.DiGraph()

        self.data = data_reader_module.read_data_from_file(data_reader_module.DATASETS[0])
        self.constructor = data_reader_module.NxGraphConstructor(self.data, self._graph)

        self.model = neta.Model(self._graph, self.constructor)
        self.controller = neta.Controller(self.model)
        self.parameter_setters = [self.controller.user_input]
        self._first_display = True

    def initialize(self):
        """Initialize all objects"""

        self._graph.clear()

        self.constructor = data_reader_module.NxGraphConstructor(self.data, self._graph)
        self.controller.reset(self.constructor)
        actual_time = self.model.update(only_graph_modification=True)
        self.model.real_time.start_time = actual_time

        # if skip_first_day:
        while actual_time <= 0:
            actual_time = self.model.update(only_graph_modification=True)
        self.model.real_time.start_time = actual_time

        if self._first_display:
            self._first_display = False
            # Simply comment in or out properties to show on start

            # ---- Update type
            # self.model.update_type = neta.Model.UPDATE_EVENT_BASED
            self.model.update_type = neta.Model.UPDATE_DAILY
            # self.model.update_type = neta.Model.UPDATE_WEEKLY

            # ---- Standard Properties
            # self.controller.add_property('Events/Time', neta.Model.TYPE_EVENT_COUNTER,
            #                              domain_type=neta.Controller.DOMAIN_REAL_TIME,
            #                              display_type=neta.Controller.DISPLAY_LINE_PLOT)
            self.controller.add_property('#Events', neta.Model.TYPE_REAL_TIME)
            # self.controller.add_property('#Edges', neta.Model.TYPE_EDGE_COUNT)
            # self.controller.add_property('#Nodes', neta.Model.TYPE_NODE_COUNT)

            # ---- Connections
            # self.controller.add_property('#Components', neta.Model.TYPE_CONNECTED_COMPONENTS)
            # self.controller.add_property('Proportion of greatest component',
            #                              neta.Model.TYPE_PROPORTION_OF_BIGGEST_COMPONENT)
            self.controller.add_property('Weighted Proportion of greatest component',
                                         neta.Model.TYPE_WEIGHTED_PROPORTION_OF_BIGGEST_COMPONENT)
            # self.controller.add_property('Density', neta.Model.TYPE_DENSITY)
            # self.controller.add_property('Assortativity', neta.Model.TYPE_DEGREE_ASSORTATIVITY)
            # self.controller.add_property('Efficiency', neta.Model.TYPE_EFFICIENCY)
            # self.controller.add_property('Weighted Efficiency', neta.Model.TYPE_WEIGHTED_EFFICIENCY)
            # self.controller.add_property('Avg. Local Efficiency', neta.Model.TYPE_AVG_LOCAL_EFFICIENCY)
            # self.controller.add_property('Avg. Weighted Local Efficiency',
            #                              neta.Model.TYPE_WEIGHTED_AVG_LOCAL_EFFICIENCY)

            # ---- Degree Distributions
            # self.controller.add_property('Degree', neta.Model.TYPE_DEGREE_DISTRIBUTION)
            # self.controller.add_property('Out-Degree', neta.Model.TYPE_OUT_DEGREE_DISTRIBUTION)
            # self.controller.add_property('In-Degree', neta.Model.TYPE_IN_DEGREE_DISTRIBUTION)
            # self.controller.add_property('In-Out-Degree', neta.Model.TYPE_IN_OUT_DEGREE_DISTRIBUTION)

            # ---- Weighted Degree Distributions
            # self.controller.add_property('Weighted Degree', neta.Model.TYPE_WEIGHTED_DEGREE_DISTRIBUTION)
            # self.controller.add_property('Weighted Out-Degree', neta.Model.TYPE_WEIGHTED_OUT_DEGREE_DISTRIBUTION)
            # self.controller.add_property('Weighted In-Degree', neta.Model.TYPE_WEIGHTED_IN_DEGREE_DISTRIBUTION)
            # self.controller.add_property('Weighted In-Out-Degree',
            #                              neta.Model.TYPE_WEIGHTED_IN_OUT_DEGREE_DISTRIBUTION)

            # ---- Vertex Properties
            # - only one at a time possible
            # self.controller.add_property('Degree Centrality', neta.Model.TYPE_DEGREE_CENTRALITY)
            # self.controller.add_property('Closeness Centrality', neta.Model.TYPE_CLOSENESS_CENTRALITY)
            # self.controller.add_property('Betweenness centrality', neta.Model.TYPE_BETWEENNESS_CENTRALITY)
            # self.controller.add_property('Local Efficiency', neta.Model.TYPE_LOCAL_EFFICIENCY)

            # ---- Weighted Vertex Properties
            # self.controller.add_property('Weighted Local Efficiency', neta.Model.TYPE_WEIGHTED_LOCAL_EFFICIENCY)
            # self.controller.add_property('Weighted Betweenness Centrality',
            #                               neta.Model.TYPE_WEIGHTED_BETWEENNESS_CENTRALITY)
            # self.controller.add_property('Weighted Closeness Centrality',
            #                              neta.Model.TYPE_WEIGHTED_CLOSENESS_CENTRALITY)

            # --------- only for connected graphs
            # self.controller.add_property('Diameter', neta.Model.TYPE_DIAMETER)
            # self.controller.add_property('L', neta.Model.TYPE_AVG_SHORTEST_PATH)

            # --------- Adaptions taking the maximal subgraph
            # self.controller.add_property('Diameter Adaption', neta.Model.TYPE_DIAMETER_ADAPTION)
            # self.controller.add_property('L Adaption', neta.Model.TYPE_AVG_SHORTEST_PATH_ADAPTION)
            # self.controller.add_property('Weighted Diameter Adaption', neta.Model.TYPE_WEIGHTED_DIAMETER_ADAPTION)
            # self.controller.add_property('Weighted L Adaption', neta.Model.TYPE_WEIGHTED_AVG_SHORTEST_PATH_ADAPTION)

            # --------- only for undirected graphs
            # self.controller.add_property('Clustering Coefficient', neta.Model.TYPE_CLUSTERING_COEFFICIENT)
            # self.controller.add_property('Clustering Coefficient', neta.Model.TYPE_WEIGHTED_CLUSTERING_COEFFICIENT)
            # self.controller.add_property('C', neta.Model.TYPE_AVG_CLUSTERING_COEFFICIENT)

        # at least some points for the lines
        self.model.update()
        self.model.update()
        self.model.update()

        # while actual_time <= 7.5:
        #     actual_time = self.model.update(only_graph_modification=False)

    def observe(self):
        """Observe the model and update the GUI"""
        self.controller.plot()

    def update(self):
        """Keep everything moving"""
        self.model.update()

    def output_data(self):
        self.controller.output_data()


import pycxsimulator

starter = Main()
pycxsimulator.GUI(
    title='Control View',
    parameterSetters=starter.parameter_setters,
    outputFunction=starter.output_data
).start(func=[starter.initialize, starter.observe, starter.update])
