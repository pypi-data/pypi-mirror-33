#ifndef GXX_RABBIT_FIGURE_H
#define GXX_RABBIT_FIGURE_H

#include <gxx/rabbit/topo2.h>

namespace rabbit {
	namespace figure {
		loop2 rectangle(double x, double y) {
			rabbit::point pnts[] = {
				{0, 0},
				{x, 0},
				{x, y},
				{0, y},
			};

			return loop2 {
				rabbit::line2(pnts[0], pnts[1]),
				rabbit::line2(pnts[1], pnts[2]),
				rabbit::line2(pnts[2], pnts[3]),
				rabbit::line2(pnts[3], pnts[0]),
			};
		}

		loop2 square(double a) {
			rabbit::point pnts[] = {
				{0, 0},
				{a, 0},
				{a, a},
				{0, a},
			};

			return loop2 {
				rabbit::line2(pnts[0], pnts[1]),
				rabbit::line2(pnts[1], pnts[2]),
				rabbit::line2(pnts[2], pnts[3]),
				rabbit::line2(pnts[3], pnts[0]),
			};
		}

		loop2 triangle(rabbit::point a, rabbit::point b, rabbit::point c) {
			if (vector2(b - a).evalrot(vector2(c - a)) > 0) {
				return loop2 { line2(a,b),line2(b,c),line2(c,a) };
			} else {
				return loop2 { line2(a,c),line2(c,b),line2(b,a) };
			}
		}

		loop2 ngon(double rad, int n, point center = point(0,0)) {
			assert(n > 2);
			loop2 ret;

			point pnts[n];

			for (int i = 0; i < n; ++i) {
				double a = M_PI * 2 / n * i;
				pnts[i] = point(rad*cos(a), rad*sin(a)) + center;
			}

			for (int i = 0; i < n - 1; ++i) {
				ret.edges.emplace_back(rabbit::line2(pnts[i], pnts[i+1]));
			}
			ret.edges.emplace_back(rabbit::line2(pnts[n-1], pnts[0]));

			return ret;
		}

		loop2 circle(double rad, point center = point(0,0)) {
			//return loop2 { rabbit::circle2(rad) };
			//gxx::println("TODO:CIRCLE CURVE");
			return ngon(rad, 40, center);
		}

		loop2 bline(point pnt1, point pnt2, double rad) {
			auto diff = pnt2 - pnt1;
			auto c1 = rabbit::figure::circle(rad, rabbit::point(0,0));
			auto c2 = rabbit::figure::circle(rad, rabbit::point(diff.abs(),0));
			auto r = rabbit::figure::rectangle(diff.abs(), rad*2).translate(0,-rad);
		
			auto l = loop_loop_combine(c1, r);
			l = loop_loop_combine(l.first, c2);
		
			rabbit::loop2 res = l.first.rotate(diff.argument()).translate(pnt1.x, pnt1.y);
			return res;
		}
	}
} 

#endif