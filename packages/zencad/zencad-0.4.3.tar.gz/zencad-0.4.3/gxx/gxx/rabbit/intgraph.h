#ifndef GXX_RABBIT_INTGRAPH_H
#define GXX_RABBIT_INTGRAPH_H

namespace rabbit {
	struct intpart;

	struct lpart {
		loop* lp;
		int snum;
		int fnum;
		double spar;
		double fpar;

		intpart * next;
	};

	struct intpnt {
		std::vector<lpart> inputs;
		std::vector<lpart> outputs;
	};
}

#endif