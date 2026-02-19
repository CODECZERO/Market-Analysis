import logging
import networkx as nx
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._initialize_graph()
        
    def _initialize_graph(self):
        """Initializes the graph with known relationships (Companies -> Sectors -> Commodities -> Factors)"""
        # Basic ontology
        # Factors
        self.graph.add_edge("Crude Oil", "Refining Margins", impact=0.9, type="correlated")
        self.graph.add_edge("Refining Margins", "Reliance Industries", impact=0.8, type="fundamental")
        self.graph.add_edge("US Tech Spending", "Indian IT Sector", impact=0.85, type="demand")
        self.graph.add_edge("Indian IT Sector", "TCS", impact=0.9, type="membership")
        self.graph.add_edge("Indian IT Sector", "Infosys", impact=0.9, type="membership")
        
        # Macro
        self.graph.add_edge("USD/INR", "Indian IT Sector", impact=0.6, type="currency_benefit") # IT exports gain from strong USD
        self.graph.add_edge("USD/INR", "Indian Oil Imports", impact=-0.7, type="currency_drag")
        
    def build_graph_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Constructs a subgraph of dependencies for a specific stock.
        """
        logger.info(f"🕸️ Building causal graph for {symbol}")
        
        # Normalize symbol name mapping (simplified)
        node_name = None
        if "RELIANCE" in symbol: node_name = "Reliance Industries"
        elif "TCS" in symbol: node_name = "TCS"
        elif "INFY" in symbol: node_name = "Infosys"
        
        if not node_name or node_name not in self.graph:
            # Fallback for unknown symbols (Data Visibility Fix)
            return {
                "root": symbol,
                "direct_dependencies": ["Global Market Sentiment", "Sector Trend"],
                "indirect_factors": ["USD/INR", "Interest Rates"],
                "graph_depth": 1,
                "status": "Simulated (Graph Not Built)"
            }
            
        # Find predecessors (upstream dependencies)
        upstream = list(self.graph.predecessors(node_name))
        upstream_factors = []
        
        for u in upstream:
            # Go one level deeper
            second_level = list(self.graph.predecessors(u))
            upstream_factors.extend(second_level)
            
        return {
            "root": symbol,
            "direct_dependencies": upstream,
            "indirect_factors": upstream_factors,
            "graph_depth": 2
        }
    
    def trace_impact(self, event_node: str, symbol: str) -> Dict[str, Any]:
        """
        Traces how a global event propagates through the graph to affect the stock.
        """
        # Find path from event (e.g., "Crude Oil") to symbol (e.g., "Reliance")
        # Normalize names first
        target_node = None
        if "RELIANCE" in symbol: target_node = "Reliance Industries"
        elif "TCS" in symbol: target_node = "TCS"
        
        if not target_node or event_node not in self.graph:
            return {"impact": 0, "path": []}
            
        try:
            path = nx.shortest_path(self.graph, source=event_node, target=target_node)
            # Calculate cumulative impact
            cumulative_impact = 1.0
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                edge_data = self.graph.get_edge_data(u, v)
                cumulative_impact *= edge_data.get('impact', 1.0)
                
            return {
                "event": event_node,
                "target": symbol,
                "impact_score": round(cumulative_impact, 2),
                "causal_chain": " -> ".join(path)
            }
        except nx.NetworkXNoPath:
            return {"impact": 0, "path": [], "message": "No causal link found"}
