#ifndef GXX_GRAPH_H
#define GXX_GRAPH_H

#include <gxx/dlist.h>
#include <set>
#include <vector>

namespace gxx {
	namespace graph {

		class edge_head {
		public:
			dlist_head start_link;
			dlist_head finish_link;
		};

		class vertex_head {
		public:
			std::vector<edge_head*> outedges;
			std::vector<edge_head*> inedges;
		};

		template<typename Vertex, vertex_head Vertex::* vptr, typename Edge, edge_head Edge::* eptr>
		class vertex_based_graph {
		public:
			std::set<Vertex> vtxs;
		};


	}
}

#endif