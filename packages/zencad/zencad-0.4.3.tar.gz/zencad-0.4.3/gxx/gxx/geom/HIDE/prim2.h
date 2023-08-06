#ifndef GXX_GEOM_PRIM2_H
#define GXX_GEOM_PRIM2_H

#include <gxx/geom/topo2.h>

namespace gxx {
	namespace topo2 {
		namespace prim {
			namespace t2 = topo2;
/*
			figure triangle(g2::point pnt1, g2::point pnt2, g2::point pnt3) {
				t2::vertex v1(pnt1);
				t2::vertex v2(pnt2);
				t2::vertex v3(pnt3);
				
				t2::segment s1(v1,v2);
				t2::segment s2(v3,v2);
				t2::segment s3(v1,v3);

				t2::contour cntr{ s1, s2, s3 };
				t2::figure fig(cntr);
				return fig;
			};

			figure square(double a) {
				t2::vertex v1(g2::point(0,0));
				t2::vertex v2(g2::point(a,0));
				t2::vertex v3(g2::point(a,a));
				t2::vertex v4(g2::point(0,a));
				
				t2::segment s1(v1,v2);
				t2::segment s2(v2,v3);
				t2::segment s3(v3,v4);
				t2::segment s4(v4,v1);

				t2::contour cntr{ s1, s2, s3, s4 };
				t2::figure fig(cntr);
				return fig;
			};

			figure rectangle(double a, double b) {
				t2::vertex v1(g2::point(0,0));
				t2::vertex v2(g2::point(a,0));
				t2::vertex v3(g2::point(a,b));
				t2::vertex v4(g2::point(0,b));
				
				t2::segment s1(v1,v2);
				t2::segment s2(v2,v3);
				t2::segment s3(v3,v4);
				t2::segment s4(v4,v1);

				t2::contour cntr{ s1, s2, s3, s4 };
				t2::figure fig(cntr);
				return fig;
			};
*/		}
	}
}

#endif