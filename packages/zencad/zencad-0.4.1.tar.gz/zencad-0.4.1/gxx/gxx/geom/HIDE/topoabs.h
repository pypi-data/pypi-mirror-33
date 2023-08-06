#ifndef GXX_TOPOABS_H
#define GXX_TOPOABS_H

#include <gxx/geom/curve2.h>
#include <gxx/geom/curve3.h>
#include <gxx/geom/surface3.h>

namespace gxx {
	namespace topo {
		/*enum class curve3_enum : uint8_t {
			none,
			line
		};

		enum class curve2_enum : uint8_t {
			none,
			line
		};

		enum class surface_enum : uint8_t {
			none,
			plane
		};

		class curve2;
		class curve3;
		class surface;

		/*struct line2_params {
			geom2::point l;
			geom2::direction d;
		};

		struct line3_params {
			geom3::point l;
			geom3::direction d;
		};

		struct plane_params {
			geom3::axis2 ax2;
		};*/

		/*class curve2 {
		public:
			curve2_enum type;
			union {
				gxx::curve2::line ln;
			};
			double tmin = 0, tmax = 0;

			curve2(){}

			curve2(const gxx::curve2::line& ctr) {
				ln = ctr;
				type = curve2_enum::line;
			}
			
			curve2(const curve2& oth){
				copy(oth);
			}
			
			curve2(const gxx::geom2::point& pnt, const gxx::geom2::vector& vec) {
				ln.l = pnt;
				ln.d = gxx::geom2::direction(vec);
				tmax = vec.abs();
				type = curve2_enum::line;
			}

			~curve2(){}

			curve2& operator=(curve2&& oth) {
				invalidate();
				move(std::move(oth));
			}

			void copy(const curve2& oth) {
				type = oth.type;
				switch(oth.type) {
					case curve2_enum::line:
						ln = oth.ln;
						return;
					default: gxx::panic("copy: undefined curve2");
				}
			}

			void move(curve2&& oth) {
				type = oth.type;
				switch(oth.type) {
					case curve2_enum::line:
						ln = oth.ln;
						return;
					default: gxx::panic("move: undefined curve2");
				}
			}

			void invalidate() {}
		};

		class curve3 {
		public:
			curve3_enum type;
			union {
				char stub;
				gxx::curve3::line ln;
			};
			double tmin = 0, tmax = 0;

			gxx::curve3::line& as_line() { return ln; }
			const gxx::curve3::line& as_line() const { return ln; }

			/*curve3(const gxx::curve3::line& ctr) {
				ln.l = ctr.loc();
				ln.d = ctr.dir();
				type = curve3_enum::line;
			}*/

		/*	gxx::curve3::curve& abstract() { return *reinterpret_cast<gxx::curve3::curve*>(&stub); }
			const gxx::curve3::curve& abstract() const { return *reinterpret_cast<const gxx::curve3::curve*>(&stub); }

			curve3(const gxx::geom3::point& pnt1, const gxx::geom3::point& pnt2) {
				ln.l = pnt1;
				auto vec = pnt2 - pnt1;
				ln.d = geom3::direction(vec);
				tmax = vec.abs();
				type = curve3_enum::line;
			}

			size_t printTo(gxx::io::ostream& o) const {
				return abstract().printTo(o);
			}

			const char* strtype() const {
				switch (type) {
					case curve3_enum::line: return "line";
					default: return "undefined curve3";
				}
			}

			curve2 project_line_to(const surface& surf);
			curve2 project_to(const surface& surf);

			~curve3(){}
		};

		class surface {
		public:
			surface_enum type;
			union {
				char stub;
				gxx::surf3::plane pln;
			};

			surf3::plane& as_plane() { return pln; }
			const surf3::plane& as_plane() const { return pln; }

			gxx::surf3::surface& abstract() { return *reinterpret_cast<gxx::surf3::surface*>(&stub); }
			const gxx::surf3::surface& abstract() const { return *reinterpret_cast<const gxx::surf3::surface*>(&stub); }

			//double vmin, vmax, umin, umax;

			surface(const gxx::surf3::plane& ctr) {
				pln.ax2 = ctr.pos();
				type = surface_enum::plane;
			}

			surface(const surface& oth) {
				switch(oth.type) {
					case surface_enum::plane:
						pln = oth.pln;
						type = surface_enum::plane;
					default: gxx::panic("surface: undefined surface");
				}
			}

			size_t printTo(gxx::io::ostream& o) const {
				return abstract().printTo(o);
			}

			~surface(){}
		};*/
	}
}

#endif