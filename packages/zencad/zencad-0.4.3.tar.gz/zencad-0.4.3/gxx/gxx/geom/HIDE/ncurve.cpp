#include "gxx/geom/ncurve.h"

namespace gxx { namespace ngeom {

	infinity_line::infinity_line(const line& l) 
	: curve(-infinity, infinity), storage(2*l.dim()), n(l.dim()) {
		location() = l.first();
		direction() = l.second() - l.first();
		direction().self_normalize();
	}

}}