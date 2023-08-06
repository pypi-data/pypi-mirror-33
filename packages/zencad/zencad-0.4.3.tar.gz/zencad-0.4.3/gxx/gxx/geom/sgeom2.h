#ifndef GXX_GEOM_SGEOM2_H
#define GXX_GEOM_SGEOM2_H

namespace gxx {
	namespace sgeom2 {
		template <typename T>
		struct point {
			T x, y;
			point(T x, T y) : x(x), y(y) {}
		};

		template <typename T>
		struct line {
			T x1, x2, y1, y2;
			line(T x1, T y1, T x2, T y2) : x1(x1), x2(x2), y1(y1), y2(y2) {}
			line(point<T> pnt1, point<T> pnt2) : x1(pnt1.x), x2(pnt2.x), y1(pnt1.y), y2(pnt2.y) {}	
			line(malgo::vector2<T> pnt1, malgo::vector2<T> pnt2) : x1(pnt1.x), x2(pnt2.x), y1(pnt1.y), y2(pnt2.y) {}			
		};

		template <typename T>
		struct arc {
			T x, y, w, h, a1, a2;
			arc(T x, T y, T w, T h, T a1, T a2) : x(x), y(y), w(w), h(h), a1(a1), a2(a2) {}			
		};
	}
}

#endif