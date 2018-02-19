"""Analysis tool for iterative network analysis """

import collections
import math
from operator import itemgetter

import networkx as nx
import pylab as pl

import data_reader_module


class Model(object):
    TYPE_EVENT_COUNTER = 'event counter'
    TYPE_REAL_TIME = 'real time'

    TYPE_NODE_COUNT = 'node count'
    TYPE_EDGE_COUNT = 'edge count'
    TYPE_CONNECTED_COMPONENTS = '# weak connected cmp.'
    TYPE_DIAMETER = 'diameter'
    TYPE_AVG_SHORTEST_PATH = 'average shortest path'
    TYPE_AVG_CLUSTERING_COEFFICIENT = 'average clustering coefficient'
    TYPE_DENSITY = 'density'
    TYPE_DEGREE_ASSORTATIVITY = 'degree assortativity'

    TYPE_DIAMETER_ADAPTION = 'diameter adaption'
    TYPE_AVG_SHORTEST_PATH_ADAPTION = 'average shortest path adaption'
    TYPE_PROPORTION_OF_BIGGEST_COMPONENT = 'greatest component'

    TYPE_WEIGHTED_DIAMETER_ADAPTION = 'weighted diameter adaption'
    TYPE_WEIGHTED_AVG_SHORTEST_PATH_ADAPTION = 'weighted average shortest path adaption'
    TYPE_WEIGHTED_PROPORTION_OF_BIGGEST_COMPONENT = 'weighted biggest component'

    TYPE_EFFICIENCY = 'efficiency'
    TYPE_AVG_LOCAL_EFFICIENCY = 'average local efficiency'
    TYPE_WEIGHTED_EFFICIENCY = 'weighted efficiency'
    TYPE_WEIGHTED_AVG_LOCAL_EFFICIENCY = 'weighted average local efficiency'

    TYPE_DEGREE_DISTRIBUTION = 'degree distribution'
    TYPE_IN_DEGREE_DISTRIBUTION = 'in-degree distribution'
    TYPE_OUT_DEGREE_DISTRIBUTION = 'out-degree distribution'
    TYPE_IN_OUT_DEGREE_DISTRIBUTION = 'in-out-degree distribution'

    TYPE_WEIGHTED_DEGREE_DISTRIBUTION = 'weighted degree distribution'
    TYPE_WEIGHTED_IN_DEGREE_DISTRIBUTION = 'weighted in-degree distribution'
    TYPE_WEIGHTED_OUT_DEGREE_DISTRIBUTION = 'weighted out-degree distribution'
    TYPE_WEIGHTED_IN_OUT_DEGREE_DISTRIBUTION = 'weighted in-out-degree distribution'

    TYPE_CLUSTERING_COEFFICIENT = 'clustering coefficient'
    TYPE_DEGREE_CENTRALITY = 'degree centrality'
    TYPE_CLOSENESS_CENTRALITY = 'closeness centrality'
    TYPE_BETWEENNESS_CENTRALITY = 'betweenness centrality'
    TYPE_LOCAL_EFFICIENCY = 'local efficiency'

    TYPE_WEIGHTED_CLUSTERING_COEFFICIENT = 'weighted clustering coefficient'
    TYPE_WEIGHTED_BETWEENNESS_CENTRALITY = 'weighted betweenness centrality'
    TYPE_WEIGHTED_CLOSENESS_CENTRALITY = 'weighted closeness centrality'
    TYPE_WEIGHTED_LOCAL_EFFICIENCY = 'weighted local efficiency'

    ATTRIBUTE_INVERTED_WEIGHT = 'inverted w'
    ATTRIBUTE_WEIGHT = 'weight'

    UPDATE_EVENT_BASED = 'event'
    UPDATE_DAILY = 'daily'
    UPDATE_WEEKLY = 'weekly'

    def __init__(self, graph, graph_constructor, update_type='event', starting_properties=None):
        """
        Model including all network characteristics, graph, ...
        :param graph:
        :param starting_properties:
        :type graph: nx.Graph
        :type graph_constructor: data_reader_module.AbstractGraphConstructor
        """
        self._network_properties = {}

        self.real_time = self.add_property(self.TYPE_REAL_TIME)
        self.event_counter = self.add_property(self.TYPE_EVENT_COUNTER)
        self.time = self.real_time
        self.actual_time = 0
        self.graph = graph
        self.graph_constructor = graph_constructor
        self.update_type = update_type

        if starting_properties:
            for property_type in starting_properties:
                self.add_property(property_type)

    def add_property(self, property_type):
        if property_type in self._network_properties:
            return self._network_properties[property_type]

        if property_type == self.TYPE_EVENT_COUNTER:
            network_property = EventCounter()
        elif property_type == self.TYPE_REAL_TIME:
            network_property = RealTime(self)
        elif property_type == self.TYPE_NODE_COUNT:
            network_property = NetworkProperty(nx.Graph.number_of_nodes, [self.graph])
        elif property_type == self.TYPE_EDGE_COUNT:
            network_property = NetworkProperty(nx.Graph.number_of_edges, [self.graph])
        elif property_type == self.TYPE_CONNECTED_COMPONENTS:
            if self.graph.is_directed():
                network_property = NetworkProperty(nx.number_weakly_connected_components, [self.graph])
            else:
                network_property = NetworkProperty(nx.number_connected_components, [self.graph])
        elif property_type == self.TYPE_DIAMETER:
            network_property = NetworkProperty(nx.diameter, [self.graph])
        elif property_type == self.TYPE_AVG_SHORTEST_PATH:
            network_property = NetworkProperty(nx.average_shortest_path_length,
                                               [self.graph, self.ATTRIBUTE_INVERTED_WEIGHT])
        elif property_type == self.TYPE_DIAMETER_ADAPTION:
            network_property = DiameterAdaption(self.graph)
        elif property_type == self.TYPE_AVG_SHORTEST_PATH_ADAPTION:
            network_property = AvgShortestPathAdaption(self.graph)
        elif property_type == self.TYPE_PROPORTION_OF_BIGGEST_COMPONENT:
            network_property = ProportionOfBiggestComponent(self.graph)
        elif property_type == self.TYPE_DENSITY:
            network_property = NetworkProperty(nx.density, [self.graph])
        elif property_type == self.TYPE_DEGREE_ASSORTATIVITY:
            network_property = DegreeAssortativity(self.graph)
        elif property_type == self.TYPE_EFFICIENCY:
            network_property = Efficiency(self.graph)
        # ----- Weighted Single Valued Characteristics
        elif property_type == self.TYPE_WEIGHTED_PROPORTION_OF_BIGGEST_COMPONENT:
            network_property = ProportionOfBiggestComponent(self.graph, self.ATTRIBUTE_WEIGHT)
        elif property_type == self.TYPE_WEIGHTED_AVG_SHORTEST_PATH_ADAPTION:
            network_property = AvgShortestPathAdaption(self.graph, self.ATTRIBUTE_INVERTED_WEIGHT)
        elif property_type == self.TYPE_WEIGHTED_DIAMETER_ADAPTION:
            network_property = DiameterAdaption(self.graph, self.ATTRIBUTE_INVERTED_WEIGHT)
        elif property_type == self.TYPE_WEIGHTED_EFFICIENCY:
            network_property = Efficiency(self.graph, weight_attribute=self.ATTRIBUTE_INVERTED_WEIGHT)
        # -- handling in controller
        # elif property_type == self.TYPE_AVG_CLUSTERING_COEFFICIENT
        # elif property_type == self.TYPE_AVG_LOCAL_EFFICIENCY
        # elif property_type == self.TYPE_WEIGHTED_AVG_LOCAL_EFFICIENCY

        # ----- Distributions
        elif property_type == self.TYPE_DEGREE_DISTRIBUTION:
            network_property = DegreeDistribution(self.graph)
        elif property_type == self.TYPE_IN_DEGREE_DISTRIBUTION:
            network_property = InDegreeDistribution(self.graph)
        elif property_type == self.TYPE_OUT_DEGREE_DISTRIBUTION:
            network_property = OutDegreeDistribution(self.graph)
        elif property_type == self.TYPE_IN_OUT_DEGREE_DISTRIBUTION:
            network_property = InOutDifferenceDegreeDistribution(self.graph)
        # ----- Weighted Distributions
        elif property_type == self.TYPE_WEIGHTED_DEGREE_DISTRIBUTION:
            network_property = DegreeDistribution(self.graph, weight_attribute=self.ATTRIBUTE_WEIGHT)
        elif property_type == self.TYPE_WEIGHTED_IN_DEGREE_DISTRIBUTION:
            network_property = InDegreeDistribution(self.graph, weight_attribute=self.ATTRIBUTE_WEIGHT)
        elif property_type == self.TYPE_WEIGHTED_OUT_DEGREE_DISTRIBUTION:
            network_property = OutDegreeDistribution(self.graph, weight_attribute=self.ATTRIBUTE_WEIGHT)
        elif property_type == self.TYPE_WEIGHTED_IN_OUT_DEGREE_DISTRIBUTION:
            network_property = InOutDifferenceDegreeDistribution(self.graph, weight_attribute=self.ATTRIBUTE_WEIGHT)
        # ----- Vertex properties
        elif property_type == self.TYPE_CLUSTERING_COEFFICIENT:
            network_property = ClusteringCoefficient(self.graph)
        elif property_type == self.TYPE_WEIGHTED_CLUSTERING_COEFFICIENT:
            network_property = ClusteringCoefficient(self.graph, weight_attribute=self.ATTRIBUTE_INVERTED_WEIGHT)
        elif property_type == self.TYPE_DEGREE_CENTRALITY:
            network_property = SimpleVertexNetworkProperty(self.graph, nx.degree_centrality)
        elif property_type == self.TYPE_CLOSENESS_CENTRALITY:
            network_property = ClosenessCentrality(self.graph)
        elif property_type == self.TYPE_WEIGHTED_CLOSENESS_CENTRALITY:
            network_property = ClosenessCentrality(self.graph, weight_attribute=self.ATTRIBUTE_INVERTED_WEIGHT)
        elif property_type == self.TYPE_BETWEENNESS_CENTRALITY:
            network_property = BetweennessCentrality(self.graph)
        elif property_type == self.TYPE_WEIGHTED_BETWEENNESS_CENTRALITY:
            network_property = BetweennessCentrality(self.graph, weight_attribute=self.ATTRIBUTE_INVERTED_WEIGHT)
        elif property_type == self.TYPE_LOCAL_EFFICIENCY:
            network_property = LocalEfficiency(self.graph)
        elif property_type == self.TYPE_WEIGHTED_LOCAL_EFFICIENCY:
            network_property = LocalEfficiency(self.graph, weight_attribute=self.ATTRIBUTE_INVERTED_WEIGHT)
        else:
            raise ValueError

        self._network_properties[property_type] = network_property
        return network_property

    def update(self, only_graph_modification=False):
        if self.update_type == self.UPDATE_EVENT_BASED:
            self._update_graph()
        elif self.update_type == self.UPDATE_DAILY:
            next_day = math.floor(self.actual_time) + 1
            while self.actual_time < next_day:
                self._update_graph()
        elif self.update_type == self.UPDATE_WEEKLY:
            next_week = math.floor(self.actual_time) + 7
            while self.actual_time < next_week:
                self._update_graph()
        else:
            raise ValueError()

        if not only_graph_modification:
            self._update_properties()
        print self.actual_time
        return self.actual_time

    def _update_graph(self):
        """Update all parameters which are set for update"""
        self.actual_time = self.graph_constructor.get_graph_stepwise_projected()
        self.real_time.update_histogram_data(self.actual_time)
        self.event_counter.total_events += 1
        return self.actual_time

    def _update_properties(self):
        for network_type in self._network_properties:
            self._network_properties[network_type].update()

    def reset(self, new_constructor, delete_network_characteristics=False):
        for network_property_key in self._network_properties:
            network_property = self._network_properties[network_property_key]
            if delete_network_characteristics:
                # delete all other than time
                if not isinstance(network_property, Time):
                    del self._network_properties[network_property_key]
                else:
                    network_property.reset()
            else:
                network_property.reset()

        self.actual_time = 0
        self.graph_constructor = new_constructor

    def get_network_property_by_name(self, property_type):
        if property_type not in self._network_properties:
            raise ValueError
        return self._network_properties[property_type]

    @property
    def domain(self):
        """Return standard domain of stored attributes, i.e. the set time division"""
        return self.time.time_steps

    def remove(self, property_type):
        del self._network_properties[property_type]


class Controller(object):
    DISPLAY_LINE_PLOT = 'line plot'
    DISPLAY_LOG_PLOT = 'log plot'
    DISPLAY_LOG_LOG_PLOT = 'log log plot'
    DISPLAY_HISTOGRAM = 'histogram'
    DISPLAY_HISTORY_LINE_PLOT = 'history line plot'
    DISPLAY_HISTORY_LOG_PLOT = 'history log plot'
    DISPLAY_HISTORY_LOG_LOG_PLOT = 'history log log plot'
    DISPLAY_VERTEX = 'vertex'

    DOMAIN_EVENT_TIME = 'event time'
    DOMAIN_REAL_TIME = 'real time'
    DOMAIN_NETWORK_PROPERTY = 'network property'

    def __init__(self, model):
        self.model = model
        self._display_order = []
        self._display_handler_by_name = {}
        self._network_type_counter = {Model.TYPE_EVENT_COUNTER: 1,
                                      Model.TYPE_REAL_TIME: 1}
        self._vertex_display = None
        self.enhanced_display = False
        self._network_type_by_name = {}

    def add_property(self, name, network_property_type, display_type='', domain_type=''):
        if name in self._display_handler_by_name:
            raise ValueError

        # Type with more then one standard display variants
        if network_property_type in [Model.TYPE_AVG_CLUSTERING_COEFFICIENT,
                                     Model.TYPE_AVG_LOCAL_EFFICIENCY,
                                     Model.TYPE_WEIGHTED_AVG_LOCAL_EFFICIENCY]:
            if network_property_type == Model.TYPE_AVG_CLUSTERING_COEFFICIENT:
                network_property_type = Model.TYPE_CLUSTERING_COEFFICIENT
            elif network_property_type == Model.TYPE_AVG_LOCAL_EFFICIENCY:
                network_property_type = Model.TYPE_LOCAL_EFFICIENCY
            elif network_property_type == Model.TYPE_WEIGHTED_AVG_LOCAL_EFFICIENCY:
                network_property_type = Model.TYPE_WEIGHTED_LOCAL_EFFICIENCY
            if not display_type:
                display_type = self.DISPLAY_LINE_PLOT

        network_property = self.model.add_property(network_property_type)

        if not display_type:
            display_type = network_property.standard_display

        if domain_type == self.DOMAIN_EVENT_TIME:
            domain_supplier = self.model.event_time
        elif domain_type == self.DOMAIN_REAL_TIME:
            domain_supplier = self.model.real_time
        elif domain_type == self.DOMAIN_NETWORK_PROPERTY or hasattr(network_property, 'domain'):
            domain_supplier = network_property
        else:
            domain_supplier = self.model

        if display_type == self.DISPLAY_LINE_PLOT:
            display_handler = LinePlot(network_property, name, domain_supplier)
        elif display_type == self.DISPLAY_LOG_PLOT:
            display_handler = LogPlot(network_property, name, domain_supplier)
        elif display_type == self.DISPLAY_LOG_LOG_PLOT:
            display_handler = LogLogPlot(network_property, name, domain_supplier)
        elif display_type == self.DISPLAY_HISTOGRAM:
            display_handler = HistogramPlot(network_property, name)
        elif display_type == self.DISPLAY_HISTORY_LINE_PLOT:
            display_handler = HistoryPlot(network_property, name, domain_supplier=domain_supplier)
        elif display_type == self.DISPLAY_HISTORY_LOG_PLOT:
            display_handler = LogHistoryPlot(network_property, name, domain_supplier=domain_supplier)
        elif display_type == self.DISPLAY_HISTORY_LOG_LOG_PLOT:
            display_handler = LogLogHistoryPlot(network_property, name, domain_supplier=domain_supplier)
        elif display_type == self.DISPLAY_VERTEX:
            display_handler = VertexDisplay(network_property, name, self.model)

            if self._vertex_display is not None:
                old_name = self._vertex_display.title
                old_network_type = self._network_type_by_name[old_name]
                del self._network_type_by_name[old_name]
                self._network_type_counter[old_network_type] -= 1
                if self._network_type_counter[old_network_type] == 0:
                    self.model.remove(old_network_type)
                    del self._network_type_counter[old_network_type]
            self._vertex_display = display_handler
            self._network_type_by_name[name] = network_property_type
            self._network_type_counter[network_property_type] = self._network_type_counter.get(network_property_type,
                                                                                               0) + 1
            return
        else:
            raise ValueError

        self._add_property(name, display_handler, network_property_type)

    def reset(self, constructor, delete_network_characteristics=False):
        self.model.reset(constructor, delete_network_characteristics)
        if delete_network_characteristics:
            self._display_order = []
            self._display_handler_by_name = {}
            self._network_type_counter = {Model.TYPE_EVENT_COUNTER: 1,
                                          Model.TYPE_REAL_TIME: 1}
            self._vertex_display = None
            self._network_type_by_name = {}

    def soft_reset(self):
        for name in self._display_order[:]:
            self.delete_characteristic_by_name(name)
        # Remove vertex characteristic
        self._vertex_display = None

    def _add_property(self, name, display_handler, network_property_type):
        self._display_order.append(name)
        self._display_handler_by_name[name] = display_handler
        self._network_type_by_name[name] = network_property_type
        self._network_type_counter[network_property_type] = self._network_type_counter.get(network_property_type, 0) + 1

    def plot(self):
        """Plot every parameter in a separate graph"""
        graphs_to_draw = len(self._display_handler_by_name)
        if graphs_to_draw > 0:
            pl.subplot(2, 1, 1)
        pl.cla()
        figure = pl.gcf()
        figure.canvas.set_window_title('Network and Property View')

        if self.enhanced_display:
            from networkx.drawing.nx_agraph import graphviz_layout
            main_graph = nx.DiGraph(self.model.graph)
            for from_node, to_node, edge_data in main_graph.edges(data=True):
                if Model.ATTRIBUTE_WEIGHT not in edge_data or edge_data[Model.ATTRIBUTE_WEIGHT] < 2:
                    main_graph.remove_edge(from_node, to_node)
            node_positions = graphviz_layout(main_graph, prog='sfdp')
        else:
            node_positions = nx.circular_layout(self.model.graph)
        # possible prog = twopi,  fdp, circo, neato, , nop, dot, sfdp.
        # not working gvcolor, wc, ccomps, tred, sccmap, acyclic, gvpr
        # nx.draw(self.model.graph, pos)
        if self._vertex_display:
            # nx.draw_circular(
            #     self.model.graph,
            #     node_color=self._vertex_display.node_color,
            #     cmap=self._vertex_display.colormap,
            #     vmin=self._vertex_display.value_min,
            #     vmax=self._vertex_display.value_max,
            #     node_size=100,
            #     arrows=False,
            # )
            # node_positions = nx.circular_layout(self.model.graph, scale=2)
            nx.draw_networkx_nodes(self.model.graph,
                                   pos=node_positions,
                                   node_color=self._vertex_display.node_color,
                                   cmap=self._vertex_display.colormap,
                                   vmin=self._vertex_display.value_min,
                                   vmax=self._vertex_display.value_max,
                                   node_size=100,
                                   )
            if self.enhanced_display:
                nx.draw_networkx_edges(self.model.graph,
                                       pos=node_positions,
                                       arrows=False
                                       )

            # axes = pl.gca()
            # axes.get_yaxis().set_visible(False)
            # axes.get_xaxis().set_visible(False)
            pl.axis('off')
        else:
            nx.draw(
                self.model.graph,
                node_size=100,
                arrows=False,
                pos=node_positions
            )
        # pl.subplot(2, 1, 2)
        # pl.cla()
        for i, name in enumerate(self._display_order):
            pl.subplot(2, graphs_to_draw, graphs_to_draw + 1 + i)
            self._display_handler_by_name[name].plot()

    def output_data(self):
        # print general information
        print ''
        print ''
        print 'Actual real-time: ' + str(self.model.actual_time)
        print 'Total events read: ' + str(self.model.event_counter.total_events)
        print ''
        print self.model.graph.nodes()
        print ''
        if self._vertex_display:
            print 'Vertex Data'
            print self._vertex_display.node_color
            print ''
        print 'Displayed Plots and Data'
        for name in self._display_order:
            print '---------------------------------------------------'
            self._display_handler_by_name[name].output_data()
        print '------------------------------------------------------------------------------------------------------'

    def user_input(self, text=''):
        """Structure view 1,2,3,4,5 or add : param type [optional : display_type : domain_type] or del : param name """
        feedback = text
        if not text:
            return feedback
        operator, options = text.split(' ', 1)

        if operator not in ['view', 'add', 'del']:
            feedback = 'please select view with e.g. ''view 1'' or add/delete param with e.g. ''add : node count''  '
        elif operator == 'view':
            feedback = self.set_view(options)
        elif operator == 'add':
            feedback = self.user_add_characteristic(options)
        elif feedback == 'del':
            feedback = self.delete_characteristic_by_name((options[1:]).strip())

        return feedback

    def set_view(self, selected_view):
        if selected_view not in ['1', '2', '3', '4', '5', 'LDIC', 'LDIC2']:
            return 'please select view with number e.g. ''view 2'''

        self.soft_reset()

        if selected_view == '1':
            self.add_property('Events/Time', Model.TYPE_EVENT_COUNTER,
                              domain_type=Controller.DOMAIN_REAL_TIME,
                              display_type=Controller.DISPLAY_LINE_PLOT)
            self.add_property('#Events', Model.TYPE_REAL_TIME)
            self.add_property('#Edges', Model.TYPE_EDGE_COUNT)
            self.add_property('#Nodes', Model.TYPE_NODE_COUNT)

        elif selected_view == '2':
            self.add_property('#Components', Model.TYPE_CONNECTED_COMPONENTS)
            self.add_property('Proportion of greatest component', Model.TYPE_PROPORTION_OF_BIGGEST_COMPONENT)
            self.add_property('Weighted Proportion of greatest component',
                              Model.TYPE_WEIGHTED_PROPORTION_OF_BIGGEST_COMPONENT)
            self.add_property('Density', Model.TYPE_DENSITY)
            self.add_property('Assortativity', Model.TYPE_DEGREE_ASSORTATIVITY)

        elif selected_view == '3':
            self.add_property('Efficiency', Model.TYPE_EFFICIENCY)
            self.add_property('Weighted Efficiency', Model.TYPE_WEIGHTED_EFFICIENCY)
            self.add_property('Avg. Local Efficiency', Model.TYPE_AVG_LOCAL_EFFICIENCY)
            self.add_property('Avg. Weighted Local Efficiency', Model.TYPE_WEIGHTED_AVG_LOCAL_EFFICIENCY)

        elif selected_view == '4':
            self.add_property('Degree', Model.TYPE_DEGREE_DISTRIBUTION)
            self.add_property('Out-Degree', Model.TYPE_OUT_DEGREE_DISTRIBUTION)
            self.add_property('In-Degree', Model.TYPE_IN_DEGREE_DISTRIBUTION)
            self.add_property('In-Out-Degree', Model.TYPE_IN_OUT_DEGREE_DISTRIBUTION)

        elif selected_view == '5':
            self.add_property('Weighted Degree', Model.TYPE_WEIGHTED_DEGREE_DISTRIBUTION)
            self.add_property('Weighted Out-Degree', Model.TYPE_WEIGHTED_OUT_DEGREE_DISTRIBUTION)
            self.add_property('Weighted In-Degree', Model.TYPE_WEIGHTED_IN_DEGREE_DISTRIBUTION)
            self.add_property('Weighted In-Out-Degree', Model.TYPE_WEIGHTED_IN_OUT_DEGREE_DISTRIBUTION)

        elif selected_view == 'LDIC':
            self.add_property('Average Shortest Path Length Adaption', Model.TYPE_AVG_SHORTEST_PATH_ADAPTION)
            self.add_property('Weighted Degree', Model.TYPE_DEGREE_DISTRIBUTION)
            self.add_property('Local Efficiency', Model.TYPE_WEIGHTED_LOCAL_EFFICIENCY)

        elif selected_view == 'LDIC2':
            self.add_property('Weighted In-Out-Degree', Model.TYPE_WEIGHTED_IN_OUT_DEGREE_DISTRIBUTION)

        return 'successfully selected view ' + selected_view

    def user_add_characteristic(self, options):
        working_options = options.split(':')
        while '' in working_options:
            working_options.remove('')

        # clear spaces
        for i, option in enumerate(working_options):
            working_options[i] = option.strip()

        if len(working_options) == 1:
            self.add_property(working_options[0], working_options[0])
        elif len(working_options) == 2:
            self.add_property(working_options[0], working_options[0], working_options[1])
        elif len(working_options) == 3:
            self.add_property(working_options[0], working_options[0], working_options[1], working_options[2])
        else:
            return 'too many '':'' options'
        return 'successfully added parameter ' + working_options[0]

    def delete_characteristic_by_name(self, name):
        self._display_order.remove(name)

        network_property_type = self._network_type_by_name[name]
        self._network_type_counter[network_property_type] -= 1
        if self._network_type_counter[network_property_type] == 0:
            self.model.remove(network_property_type)
            del self._network_type_counter[network_property_type]

        del self._display_handler_by_name[name]
        del self._network_type_by_name[name]
        return 'successfully deleted parameter ' + name


class AbstractDisplay(object):
    """Abstract base class for displaying a property"""

    # class variables all titles same size
    # Size of the title for the plots
    font_size_of_title = 8

    def __init__(self, network_property, title):
        """

        :param network_property: single network property as part of the model
        :param title: the title of the diagram
        :type network_property: NetworkProperty
        :type title: str
        """
        self.network_property = network_property
        self.title = title

    def plot(self):
        raise NotImplementedError()

    def output_data(self):
        raise NotImplementedError()


class LinePlot(AbstractDisplay):
    def __init__(self, network_property, title, domain_supplier):
        super(LinePlot, self).__init__(network_property, title)
        self.domain_supplier = domain_supplier
        self._type = 'Line Plot '

    def plot(self):
        pl.cla()
        pl.title(self.title, fontsize=self.font_size_of_title)
        # if len(self.network_property.data) > 1:
        #     print self.network_property.data[len(self.network_property.data) - 1]
        pl.plot(self.domain_supplier.domain, self.network_property.data)

    def output_data(self):
        print self._type + str(self.title)
        print 'Output x/y data'
        print self.domain_supplier.domain
        print self.network_property.data


class LogPlot(LinePlot):
    def __init__(self, network_property, title, domain_supplier):
        super(LogPlot, self).__init__(network_property, title, domain_supplier)
        self._type = 'Log Plot '

    def plot(self):
        pl.title(self.title, fontsize=self.font_size_of_title)
        pl.semilogy(self.domain_supplier.domain, self.network_property.data)


class LogLogPlot(LinePlot):
    def __init__(self, network_property, title, domain_supplier):
        super(LogLogPlot, self).__init__(network_property, title, domain_supplier)
        self._type = 'LogLog Plot '

    def plot(self):
        pl.cla()
        pl.title(self.title, fontsize=self.font_size_of_title)
        pl.loglog(self.domain_supplier.domain, self.network_property.data)


class HistogramPlot(AbstractDisplay):
    def __init__(self, network_property, title):
        """

        :param network_property: single network property as part of the model
        :param title: the title of the diagram
        :type network_property: HistogramData
        :type title: str
        """
        super(HistogramPlot, self).__init__(network_property, title)
        self.network_property = network_property

    def plot(self):
        pl.cla()
        pl.title(self.title, fontsize=self.font_size_of_title)
        pl.hist(self.network_property.histogram_data,
                bins=self.network_property.bins
                )

    def output_data(self):
        print 'Histogram ' + str(self.title)
        print 'Output data/bins'
        print self.network_property.histogram_data
        print self.network_property.bins


class HistoryPlot(AbstractDisplay):
    def __init__(self, network_property, title, number_of_historical_plots=1, domain_supplier=None):
        super(HistoryPlot, self).__init__(network_property, title)
        self.histories = collections.deque()
        self.number_of_historical_plots = number_of_historical_plots
        if hasattr(network_property, 'domain') and domain_supplier is None:
            self.domain_supplier = network_property
        elif domain_supplier is not None:
            if not hasattr(domain_supplier, 'domain'):
                raise ValueError
            self.domain_supplier = domain_supplier
        else:
            raise ValueError
        self._type = 'History Line Plot'

    def plot(self):
        if len(self.network_property.data) > 0:
            self.plot_complex(self.domain_supplier.domain, self.network_property.data)

    def plot_complex(self, domain, data):
        """Plot with domain and data and history"""
        #            Plot data
        if len(self.histories) > 2 * self.number_of_historical_plots:
            self.histories.popleft()
            self.histories.popleft()
        pl.cla()
        pl.title(self.title, fontsize=self.font_size_of_title)
        self.plot_single(domain, data, '-')
        history_iterator = iter(self.histories)
        for plot_number in range(len(self.histories) / 2):
            if plot_number == 0:
                line_style = '--'
            elif plot_number == 1:
                line_style = ':'
            else:
                line_style = '-.'
            self.plot_single(history_iterator.next(), history_iterator.next(), line_style)

        self.histories.append(domain)
        self.histories.append(data)

    def plot_single(self, domain, data, line_style='-'):
        """Plot single data"""
        pl.plot(domain, data, line_style)

    def output_data(self):
        print self._type + str(self.title)
        print 'Output ' + str(self.number_of_historical_plots) + ' x/y data sets'
        for i, data in enumerate(self.histories):
            print data
            if (i + 1) % 2 == 0:
                print '---'


class LogHistoryPlot(HistoryPlot):
    def __init__(self, network_property, title, number_of_historical_plots=1, domain_supplier=None):
        super(LogHistoryPlot, self).__init__(network_property, title, number_of_historical_plots, domain_supplier)
        self._type = 'History Semi-log y Plot'

    def plot_single(self, domain, data, line_style='-'):
        pl.semilogy(domain, data, line_style)


class LogLogHistoryPlot(HistoryPlot):
    def __init__(self, network_property, title, number_of_historical_plots=1, domain_supplier=None):
        super(LogLogHistoryPlot, self).__init__(network_property, title, number_of_historical_plots, domain_supplier)
        self._type = 'History LogLog Plot'

    def plot_single(self, domain, data, line_style='-'):
        pl.loglog(domain, data, line_style)


class VertexDisplay(object):
    def __init__(self, network_property, title, model, colormap='Greys',
                 value_max=1, value_min=0, relative_display=True):
        self.network_property = network_property
        self.colormap = pl.get_cmap(colormap)
        self._value_max = value_max
        self._value_min = value_min
        self.title = title
        self.relative_display = relative_display
        self.model = model

    @property
    def node_color(self):
        return self.network_property.vertex_data

    @property
    def value_max(self):
        if self.relative_display:
            return max(self.node_color)
        else:
            return self._value_max

    @property
    def value_min(self):
        if self.relative_display:
            return min(self.node_color) - .1
        else:
            return self._value_min


class NetworkProperty(object):
    """Basic class of a network property as part of the model"""

    def __init__(self, update_function=NotImplemented,
                 update_function_parameter=None):
        """Initialize all needed attributes"""

        # Field for storing the data
        self.data = []

        # in each iteration the update function is called with the update function parameters
        self.update_function = update_function
        self.update_function_parameter = []

        if update_function_parameter is None:
            update_function_parameter = []
        self.update_function_parameter.extend(update_function_parameter)

        self.standard_display = Controller.DISPLAY_LINE_PLOT

    def update(self):
        """Call of saved update function with known parameters"""
        self.data.append(
            self.update_function(*self.update_function_parameter)
        )

    def reset(self):
        self.data = []


class HistogramData(NetworkProperty):
    def __init__(self, update_function=NotImplemented,
                 update_function_parameter=None):
        super(HistogramData, self).__init__(update_function, update_function_parameter)
        self._min_value = 0
        self._max_value = 0
        self.standard_display = Controller.DISPLAY_HISTOGRAM

    @property
    def histogram_data(self):
        raise NotImplementedError()

    @property
    def bins(self):
        return abs(int(math.ceil(self._max_value)) - int(math.floor(self._min_value))) + 1


class Time(NetworkProperty):
    def _increment(self, timer):
        raise NotImplementedError()

    @property
    def min_value(self):
        raise NotImplementedError()

    @property
    def max_value(self):
        raise NotImplementedError()

    @property
    def time_steps(self):
        return self.data

    @property
    def domain(self):
        return self.data


class EventCounter(Time):
    def __init__(self, start_step=0):
        super(EventCounter, self).__init__(EventCounter._increment, [self])
        self._start_step = start_step
        self._actual_step = 0
        # This can be different from self._actual_step due to reading daily or weekly
        self.total_events = 0

        self.standard_display = Controller.DISPLAY_LINE_PLOT

    def _increment(self, timer=1):
        self._actual_step += timer
        return self._actual_step

    @property
    def min_value(self):
        return self._start_step

    @property
    def max_value(self):
        return self._actual_step

    def reset(self):
        super(EventCounter, self).reset()
        self.total_events = 0


class RealTime(Time, HistogramData):
    def __init__(self, model, start_time=0):
        update_function_parameter = [self, model]
        super(RealTime, self).__init__(RealTime._increment, update_function_parameter)
        self.start_time = start_time
        self._next_time = start_time
        self._histogram_data = []
        del self._min_value
        del self._max_value

    def _increment(self, timer):
        self._next_time = timer.actual_time
        return self._next_time

    @property
    def min_value(self):
        return self.start_time

    @property
    def max_value(self):
        return self._next_time

    def update_histogram_data(self, actual_time):
        self._histogram_data.append(actual_time)

    @property
    def histogram_data(self):
        return self._histogram_data

    @property
    def bins(self):
        return range(int(math.floor(self.start_time)), int(math.ceil(self._next_time)) + 1)

    def reset(self):
        super(RealTime, self).reset()
        self._histogram_data = []


class DegreeAssortativity(NetworkProperty):
    """Parameter subclass for own handling of nx.degree_assortativity() call"""

    def __init__(self, graph):
        super(DegreeAssortativity, self).__init__(DegreeAssortativity.update_data,
                                                  [graph])

    @staticmethod
    def update_data(graph):
        """Own handling of data call"""
        #        needed because of error when no edge exists
        if graph.number_of_edges() > 2:
            return nx.degree_assortativity_coefficient(graph, weight='weight')
        else:
            return 0


class DistributionProperty(HistogramData):
    def __init__(self, update_function=NotImplemented,
                 update_function_parameter=None,
                 calculate_accumulated_distribution=True,
                 complementary_accumulated=True):
        super(DistributionProperty, self).__init__(update_function, update_function_parameter)
        self.domain = []
        self.standard_display = Controller.DISPLAY_HISTORY_LINE_PLOT
        self._histogram_data = []
        self._min_value = 0
        self._iter_function = self._data_iter
        self.calculate_accumulated_distribution = calculate_accumulated_distribution
        self.complementary_accumulated = complementary_accumulated
        self.history = {}
        self.counter = 0
        self.save_history = True

    def update_data(self, graph):
        n = graph.number_of_nodes()
        if n > 0:
            self._histogram_data = self._get_histogram(graph)
            data = [float(x) / n for x in self._histogram_data]

            if self.calculate_accumulated_distribution:
                actual_value = 0
                accumulated_distribution = []
                for value in data:
                    actual_value += value
                    accumulated_distribution.append(actual_value)
                if self.complementary_accumulated:
                    data[0] = 1
                    accumulated_distribution.pop()
                    for i, value in enumerate(accumulated_distribution):
                        data[i + 1] = 1 - value

            return data, range(len(data))

    def _get_histogram(self, graph):
        """
        Calculate the histogram frequencies from a given data set and iteration function.
        This implementation is an extension of the function nx.degree_histogram to the general case.
        :param graph: calculate the histogram for this graph
        :return: A list of frequencies indexed by their values
        """

        data_sequence = list(self._iter_function(graph))

        # if wanted save complete information
        if self.save_history:
            self.history[self.counter] = data_sequence
            self.counter += 1

        self._max_value = max(data_sequence) + 1
        frequencies = [0 for _ in range(self._max_value)]
        for data in data_sequence:
            frequencies[data] += 1
        return frequencies

    def _data_iter(self, graph):
        raise NotImplementedError()

    @property
    def histogram_data(self):
        return self._histogram_data

    def update(self):
        self.data, self.domain = self.update_function(*self.update_function_parameter)

    def reset(self):
        super(DistributionProperty, self).reset()
        self._histogram_data = []
        self.domain = []
        if self.save_history:
            print(self.history)
        self.history = {}
        self.counter = 0


class DegreeDistribution(DistributionProperty):
    def __init__(self, graph, weight_attribute='', use_complementary_accumulated_distribution=True):
        super(DegreeDistribution, self).__init__(DegreeDistribution.update_data, [self, graph], True,
                                                 use_complementary_accumulated_distribution)
        self.weight_attribute = weight_attribute
        self.standard_display = Controller.DISPLAY_LOG_LOG_PLOT

    def _data_iter(self, graph):
        if isinstance(graph, nx.DiGraph):
            if self.weight_attribute:
                for node in graph.nodes():
                    yield sum(data.get(self.weight_attribute, 1) for data in graph.pred[node].values()) \
                          + sum(data.get(self.weight_attribute, 1) for data in graph.succ[node].values())
            else:
                for node in graph.nodes():
                    yield len(graph.pred[node]) + len(graph.succ[node])
        else:
            if self.weight_attribute:
                for _, degree in graph.degree_iter(weight=self.weight_attribute):
                    yield degree
            else:
                for _, degree in graph.degree():
                    yield degree


class InDegreeDistribution(DegreeDistribution):
    def _data_iter(self, graph):
        if self.weight_attribute:
            for _, degree in graph.in_degree(weight=self.weight_attribute):
                yield degree
        else:
            for _, degree in graph.in_degree():
                yield degree


class OutDegreeDistribution(DegreeDistribution):
    def _data_iter(self, graph):
        if self.weight_attribute:
            for _, degree in graph.out_degree(weight=self.weight_attribute):
                yield degree
        else:
            for _, degree in graph.out_degree():
                yield degree


class InOutDifferenceDegreeDistribution(HistogramData):
    def __init__(self, graph, weight_attribute=''):
        if not isinstance(graph, nx.DiGraph):
            raise TypeError()
        super(InOutDifferenceDegreeDistribution, self).__init__(InOutDifferenceDegreeDistribution.update_data,
                                                                [self, graph])
        self._iter_function = self._data_iter
        self._min_value = 0
        self.weight_attribute = weight_attribute
        self.without_outlier = False

    def update_data(self, graph):
        self._min_value = min(self._iter_function(graph))
        self._max_value = max(self._iter_function(graph))
        self.data = list(self._iter_function(graph))
        if self.without_outlier:
            self.data.remove(self._min_value)
            self.data.remove(self._max_value)
            self._min_value = min(self.data)
            self._max_value = max(self.data)

    def _data_iter(self, graph):
        if self.weight_attribute:
            for node in graph.nodes():
                yield sum(data.get(self.weight_attribute, 1) for data in graph.pred[node].values()) \
                      - sum(data.get(self.weight_attribute, 1) for data in graph.succ[node].values())
        else:
            for node in graph.nodes():
                yield len(graph.pred[node]) - len(graph.succ[node])

    @property
    def histogram_data(self):
        return self.data


class VertexNetworkProperty(NetworkProperty):
    def __init__(self, update_function=NotImplemented,
                 update_function_parameter=None):
        super(VertexNetworkProperty, self).__init__(update_function, update_function_parameter)
        self._vertex_data = {}
        self._vertex_data_flatten = []
        self.min_value = -.1
        self.max_value = 1
        self.relative_display = True
        self.qualitative_display = False
        self.number_of_qualitative_steps = 10

        self.standard_display = Controller.DISPLAY_VERTEX

    def update(self):
        self._vertex_data = self.update_function(*self.update_function_parameter)
        self.aggregate_update()
        if self.relative_display and not self.qualitative_display:
            self.min_value = min(self._vertex_data_flatten)
            self.max_value = max(self._vertex_data_flatten)

    def aggregate_update(self):
        pass

    def _flatten_vertex_data(self, data, graph):
        self._vertex_data_flatten = [data[node] for node in graph.nodes()]

    @property
    def vertex_data(self):
        if self.qualitative_display:
            length = float(len(self._vertex_data_flatten))
            actual_step = 0.0
            last_value = 0
            self.min_value = -.1
            self.max_value = 1
            for number_of_entries_read, (position, value) in \
                    enumerate(sorted(enumerate(self._vertex_data_flatten), key=itemgetter(1))):
                if (number_of_entries_read / length > (actual_step + 1) / self.number_of_qualitative_steps) \
                        and value != last_value:
                    actual_step += 1
                self._vertex_data_flatten[position] = actual_step / self.number_of_qualitative_steps
                last_value = value
        return self._vertex_data_flatten


class SimpleVertexNetworkProperty(VertexNetworkProperty):
    def __init__(self, graph, vertex_data_function):
        super(SimpleVertexNetworkProperty, self).__init__(SimpleVertexNetworkProperty.update_data, [self, graph])
        self.vertex_data_function = vertex_data_function

    def update_data(self, graph):
        data = self.vertex_data_function(graph)
        self._flatten_vertex_data(data, graph)
        return data


class ClusteringCoefficient(VertexNetworkProperty):
    def __init__(self, graph, weight_attribute=''):
        super(ClusteringCoefficient, self).__init__(ClusteringCoefficient.update_data, [self, graph])
        self.weight_attribute = weight_attribute

    def update_data(self, graph):
        if self.weight_attribute:
            data = nx.clustering(graph, weight=self.weight_attribute)
        else:
            data = nx.clustering(graph)
        self._flatten_vertex_data(data, graph)
        return data

    def aggregate_update(self):
        self.data.append(sum(self._vertex_data.values()) / float(len(self._vertex_data)))


class ClosenessCentrality(VertexNetworkProperty):
    def __init__(self, graph, weight_attribute=''):
        super(ClosenessCentrality, self).__init__(ClosenessCentrality.update_data, [self, graph])
        self.weight_attribute = weight_attribute

    def update_data(self, graph):
        if self.weight_attribute:
            data = nx.closeness_centrality(graph, distance=self.weight_attribute)
        else:
            data = nx.closeness_centrality(graph)
        self._flatten_vertex_data(data, graph)
        return data


class BetweennessCentrality(VertexNetworkProperty):
    def __init__(self, graph, weight_attribute=''):
        super(BetweennessCentrality, self).__init__(BetweennessCentrality.update_data, [self, graph])
        self.weight_attribute = weight_attribute

    def update_data(self, graph):
        if self.weight_attribute:
            data = nx.closeness_centrality(graph, distance=self.weight_attribute)
        else:
            data = nx.closeness_centrality(graph)
        self._flatten_vertex_data(data, graph)
        return data


class MaximumSubgraphProperty(NetworkProperty):
    def __init__(self, update_function=NotImplemented, update_function_parameter=None, weight_attribute=''):
        super(MaximumSubgraphProperty, self).__init__(update_function, update_function_parameter)
        self.weight_attribute = weight_attribute

    def _find_maximum_subgraph(self, graph):
        if graph.is_directed():
            components_iter = nx.strongly_connected_component_subgraphs
        else:
            components_iter = nx.connected_component_subgraphs

        maximum_value = 0
        maximum_subgraph = graph
        for subgraph in components_iter(graph):
            if self.weight_attribute:
                value = subgraph.size(weight=self.weight_attribute)
            else:
                value = subgraph.size()
            if value > maximum_value:
                maximum_value = value
                maximum_subgraph = subgraph
        return maximum_subgraph


class DiameterAdaption(MaximumSubgraphProperty):
    def __init__(self, graph, weight_attribute=''):
        super(DiameterAdaption, self).__init__(DiameterAdaption.update_data, [self, graph], weight_attribute)

    def update_data(self, graph):
        maximum_subgraph = self._find_maximum_subgraph(graph)
        if self.weight_attribute:
            return max([max(path_length) for path_length in
                        [nodes.values() for nodes in
                         nx.shortest_path_length(maximum_subgraph, weight=self.weight_attribute).values()]])

        return max([max(path_length) for path_length in
                    [nodes.values() for nodes in nx.shortest_path_length(graph).values()]])


class AvgShortestPathAdaption(MaximumSubgraphProperty):
    def __init__(self, graph, weight_attribute=''):
        super(AvgShortestPathAdaption, self).__init__(
            AvgShortestPathAdaption.update_data, [self, graph], weight_attribute)

    def update_data(self, graph):
        maximum_subgraph = self._find_maximum_subgraph(graph)
        if self.weight_attribute:
            return nx.average_shortest_path_length(maximum_subgraph, self.weight_attribute)
        return nx.average_shortest_path_length(maximum_subgraph)


class EfficiencyAdaption(MaximumSubgraphProperty):
    def __init__(self, graph, weight_attribute=''):
        super(EfficiencyAdaption, self).__init__(EfficiencyAdaption.update_data, [self, graph], weight_attribute)
        self.efficiency = Efficiency(graph, weight_attribute)

    def update_data(self, graph):
        maximum_subgraph = self._find_maximum_subgraph(graph)
        return self.efficiency.update_data(maximum_subgraph)


class AvgClusteringCoefficientAdaption(MaximumSubgraphProperty):
    def __init__(self, graph, weight_attribute=''):
        super(AvgClusteringCoefficientAdaption, self).__init__(
            AvgClusteringCoefficientAdaption.update_data, [self, graph])
        self.weight_attribute = weight_attribute

    def update_data(self, graph):
        maximum_subgraph = self._find_maximum_subgraph(graph)
        if self.weight_attribute:
            return nx.average_clustering(maximum_subgraph, weight=self.weight_attribute)
        return nx.average_clustering(maximum_subgraph)


class Efficiency(NetworkProperty):
    def __init__(self, graph, weight_attribute=''):
        super(Efficiency, self).__init__(Efficiency.update_data, [self, graph])
        self.weight_attribute = weight_attribute

    def update_data(self, graph):

        normalization = 1.0 / (graph.number_of_nodes() * graph.number_of_nodes())
        if self.weight_attribute:
            return normalization * reduce(self._inverse_sum, [reduce(self._inverse_sum, path_length) for path_length in
                                                              [nodes.values() for nodes in
                                                               dict(nx.shortest_path_length(graph,
                                                                                            weight=self.weight_attribute
                                                                                            )).values()
                                                               ]])
        return normalization * reduce(self._inverse_sum, [reduce(self._inverse_sum, path_length) for path_length in
                                                          [nodes.values() for nodes in
                                                           dict(nx.shortest_path_length(graph)).values()]])

    @staticmethod
    def _inverse_sum(x, y):
        try:
            return x + 1.0 / y
        except ZeroDivisionError:
            return x


class LocalEfficiency(VertexNetworkProperty):
    def __init__(self, graph, weight_attribute=''):
        super(LocalEfficiency, self).__init__(LocalEfficiency.update_data, [self, graph])
        self.efficiency = Efficiency(graph, weight_attribute)
        # self.relative_display = False
        # self.max_value = .7

    def update_data(self, graph):
        self._vertex_data_flatten = []
        vertex_data = {}
        for node in graph.nodes:
            if graph.is_directed():
                neighbors = set(graph.predecessors(node)).union(graph.successors(node))
            else:
                neighbors = graph.neighbors_iter(node)
            sub_graph = graph.subgraph(neighbors)
            local_efficiency = self.efficiency.update_data(sub_graph)
            vertex_data[node] = local_efficiency
            self._vertex_data_flatten.append(local_efficiency)
        return vertex_data

    def aggregate_update(self):
        self.data.append(sum(self._vertex_data_flatten) / float(len(self._vertex_data_flatten)))


class ProportionOfBiggestComponent(NetworkProperty):
    def __init__(self, graph, weight_attribute='', strong_component=True):
        super(ProportionOfBiggestComponent, self).__init__(ProportionOfBiggestComponent.update_data, [self, graph])
        self.strong_component = strong_component
        self.weight_attribute = weight_attribute

    def update_data(self, graph):
        if graph.is_directed():
            if self.strong_component:
                components_iter = nx.strongly_connected_component_subgraphs
            else:
                components_iter = nx.weakly_connected_component_subgraphs
        else:
            components_iter = nx.connected_component_subgraphs

        maximum_value = 0
        for subgraph in components_iter(graph):
            if self.weight_attribute:
                maximum_value = max(subgraph.size(self.weight_attribute), maximum_value)
            else:
                maximum_value = max(subgraph.size(), maximum_value)

        if self.weight_attribute:
            result = float(maximum_value) / graph.size(self.weight_attribute)
        else:
            result = float(maximum_value) / graph.size()
        return result
