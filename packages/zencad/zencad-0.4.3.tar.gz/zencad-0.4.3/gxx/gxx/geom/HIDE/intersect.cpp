#include <gxx/geom/intersect.h>

namespace gxx { namespace geom3 {


	/*intersect_curve_curve_s intersect_infline_infline(const line& l1, const line& l2) {
		auto& loc1 = l1.loc();
		auto& loc2 = l2.loc();
		auto& dir1 = l1.dir();
		auto& dir2 = l2.dir();
	}*/

	/*intersect_curve_curve_s intersect_line_curve(const line& l, const curve& crv) {
		if (typeid(crv) == typeid(line)) { return intersect_line_line(l, crv); }
		gxx::panic("undefined curves type");
	}

	intersect_curve_curve_s intersect_curve_curve(const curve& crv1, const curve& crv2) {
		//if (typeid(crv1) == typeid(line) && typeid(crv2) == typeid(line)) { return intersect_line_line(crv1, crv2); }
		if (typeid(crv1) == typeid(line)) { return intersect_line_curve(crv1, crv2); }
		if (typeid(crv2) == typeid(line)) { return intersect_line_curve(crv1, crv2); }

		gxx::panic("undefined curves type");
	};*/

}}