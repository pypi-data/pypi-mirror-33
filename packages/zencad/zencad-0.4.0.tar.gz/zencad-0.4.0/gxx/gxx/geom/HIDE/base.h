#ifndef GXX_GEOM_BASE_H
#define GXX_GEOM_BASE_H

/*#include <gxx/print.h>
#include <gxx/util/setget.h>
#include <gxx/math/vectorN.h>

namespace gxx {
	namespace geom3d {
		
		class point;
		class vector;
		class direction;

		class vector {
		public:
			gxx::math::vector3 raw;

		public:
			vector(float x, float y, float z);
			vector(const math::vector3& oth);
			vector(const point& spnt, const point& epnt);
			vector(const direction& dir, float length);

			//float abs() { return eval_abs(); }

			vector translate(const geom3d::vector& vect) { raw.self_add(vect.raw); }
			vector rotateX(float angle) { raw.self_rotateX(angle); }
			vector rotateY(float angle) { raw.self_rotateY(angle); }
			vector rotateZ(float angle) { raw.self_rotateZ(angle); }
			vector scale(float scl) { raw.self_scale(scl); }

			vector translated(const geom3d::vector& vect) { return vector(raw.add(vect.raw)); }
			vector rotatedX(float angle) { return vector(raw.rotateX(angle)); }
			vector rotatedY(float angle) { return vector(raw.rotateY(angle)); }
			vector rotatedZ(float angle) { return vector(raw.rotateZ(angle)); }
			vector scaled(float scl) { return vector(raw.scale(scl)); }
		};

		class point {
		public:
			gxx::math::vector3 raw;

		public:
			point(float x, float y, float z);
			point(const math::vector3& oth);

			void translate(const geom3d::vector& vect) { raw.self_add(vect.raw); }
			void rotateX(float angle) { raw.self_rotateX(angle); }
			void rotateY(float angle) { raw.self_rotateY(angle); }
			void rotateZ(float angle) { raw.self_rotateZ(angle); }

			point translated(const geom3d::vector& vect) { return point(raw.add(vect.raw)); }
			point rotatedX(float angle) { return point(raw.rotateX(angle)); }
			point rotatedY(float angle) { return point(raw.rotateY(angle)); }
			point rotatedZ(float angle) { return point(raw.rotateZ(angle)); }

			float distance(const point& oth) {
				return oth.raw.sub(raw).abs();
			}
		};

		class direction {
		public:
			gxx::math::vector3 raw;

		public:
			direction(float x, float y, float z) : raw(x,y,z) { raw.self_normalize(); }
			direction(const math::vector3& oth) : direction(oth.x, oth.y, oth.z) {};
			direction(const geom3d::vector& oth) : direction(oth.raw) {};
		};

		class axis {
		public:
			point 	pnt;
			direction dir;

		public:
			const point& get_location() const { return pnt; }
			const direction& get_direction() const { return dir; }

			axis(const point& vrx, const direction& dir);
		};
/*
		class axis2 {
			point origin;

		};

*/
/*		class line {
		public:
			axis 	ax;

		public:
			const point& 		get_location() const { return ax.get_location(); }
			const direction& 	get_direction() const { return ax.get_direction(); }
			const axis& 		get_position() const { return ax; }

			line(const point& pnt, const direction& dir) : ax(pnt,dir) {}
			line(const axis& ax) : ax(ax) {}

			float distance(const point& pnt) {
				const auto& dir = ax.get_direction().raw;				
				auto pntsub = pnt.raw.sub(ax.pnt.raw);
				//gxx::fprintln("pntsub: {}", pntsub);

				return dir.vecmul(pntsub).abs();
			}

			float distance(const line& oth) {
				const auto& dir1 = ax.get_direction().raw;
				const auto& dir2 = oth.ax.get_direction().raw;
				const auto& pnt1 = ax.get_location().raw;
				const auto& pnt2 = oth.ax.get_location().raw;
				auto pntsub = pnt1.sub(pnt2);
				
				if (dir1.is_equal(dir2)) {
					//Прямые паралельны.
					return dir1.vecmul(pntsub).abs();
				} 
				
				else {
					//Прямые скрещиваются.
					auto normal = dir1.vecmul(dir2);
					normal.self_normalize();
					return fabsf(normal.scalar_mul(pntsub));
				}
			}
		};
/*




		inline vector vector_multiply(const vector& a, const vector& b) {
			return vector(a.coord_cross_mul(b));
		}*/
//	}
//}

#endif
