#ifndef GXX_GEOM3_H
#define GXX_GEOM3_H

#include <gxx/math/malgo3.h>
#include <gxx/util/setget.h>
#include <gxx/print.h>
#include <limits>

#include <gxx/geom/geom2.h>

namespace gxx { namespace geom3 {
	constexpr static double infinity = std::numeric_limits<double>::infinity();
	constexpr static double precision = 0.00000001;

	class point : public malgo3::vector3<double> {
	public: 
		point() = default;
		point(double x, double y, double z) : malgo3::vector3<double>(x,y,z) {}
		point(const point& oth) : malgo3::vector3<double>(oth) {}
		point(const malgo3::vector3<double>& oth) : malgo3::vector3<double>(oth) {}
		double distance(const point& oth) { return sub(oth).abs(); }
	};

	class vector : public malgo3::vector3<double> {
	public:
		vector() = default;
		vector(double x, double y, double z) : malgo3::vector3<double>(x,y,z) {}
		vector(const vector& oth) : malgo3::vector3<double>(oth) {}
		vector(const malgo3::vector3<double>& oth) : malgo3::vector3<double>(oth) {}
	};

	class direction : public malgo3::vector3<double> {
	public:
		direction() : malgo3::vector3<double>(0,0,1) {};
		direction(double x, double y, double z, bool norm = true) : malgo3::vector3<double>(x,y,z) { if (norm) self_normalize(); }
		direction(const direction& oth) : malgo3::vector3<double>(oth) {}
		direction(const malgo3::vector3<double>& oth, bool norm = true) : malgo3::vector3<double>(oth) { if (norm) self_normalize(); }
	};

	class axis {
	public:
		point l;
		direction d;

		axis(point l, direction d) : l(l), d(d) {}

		CONSTREF_GETTER(loc, l);
		CONSTREF_GETTER(dir, d);
	};

	class axis2 {
	public:
		point l;
		direction n;
		direction dx;
		direction dy;
	
		axis2(point l, direction n, direction vx) : l(l), n(n) {
			//dprln("point l, direction n, direction vx");
			dy = n.vecmul(vx); 
			dx = dy.vecmul(n); 
		}

		axis2(point l, direction n) : l(l), n(n) {
			//dprln("point l, direction n");
			vector vx;

			if (n.is_same(vector(0,0,1), precision)) vx = vector(1,0,0);
			else vx = direction(0,0,1);

			dy = n.vecmul(vx); 
			dx = dy.vecmul(n); 
		}

		axis2(point a, point b, point c) : l(a) {
			//dprln("point a, point b, point c");
			//gxx::vprint(a,b,c);
			dx = direction(b-a);
			auto dpy = b-c;
			n = dx.vecmul(dpy);
			dy = direction(n.vecmul(dx));
		}

		gxx::geom2::vector project_vector(const malgo3::vector3<double>& vec) const {
			return gxx::geom2::vector(vec.sclmul(dx), vec.sclmul(dy));
		}

		gxx::geom2::point project_point(const malgo3::vector3<double>& pnt) const {
			auto vec = pnt - l;
			return gxx::geom2::vector(vec.sclmul(dx), vec.sclmul(dy));
		}

		CONSTREF_GETTER(loc, l);
		CONSTREF_GETTER(dirx, dx);
		CONSTREF_GETTER(diry, dy);

		size_t printTo(gxx::io::ostream& o) const {
			return gxx::fprint(o,"(l:{},x:{},y:{},n:{})", l, dx, dy, n);
		}
	};

	class axis3 {
	public:
		point l;
		direction dx;
		direction dy;
		direction dz;

		axis3(point l, direction n, direction vx) : l(l), dz(n) {
			dy = n.vecmul(vx); 
			dx = dy.vecmul(n); 
		}
	
		CONSTREF_GETTER(loc, l);
		CONSTREF_GETTER(dirx, dx);
		CONSTREF_GETTER(diry, dy);
		CONSTREF_GETTER(dirz, dz);

		size_t printTo(gxx::io::ostream& o) const {
			return gxx::fprint(o,"(l:{},x:{},y:{},z:{})", l, dx, dy, dz);
		}
	};

	inline point origin() { return point(0,0,0); }

	inline direction dirx() { return direction(1,0,0,false); }
	inline direction diry() { return direction(0,1,0,false); }
	inline direction dirz() { return direction(0,0,1,false); }

	inline axis Ox() { return axis(origin(), direction(1,0,0)); }	
	inline axis Oy() { return axis(origin(), direction(0,1,0)); }
	inline axis Oz() { return axis(origin(), direction(0,0,1)); }

	inline axis2 Oxy() { return axis2(origin(), direction(0,0,1), direction(1,0,0)); }
	inline axis2 Oyz() { return axis2(origin(), direction(1,0,0), direction(0,1,0)); }
	inline axis2 Ozx() { return axis2(origin(), direction(0,1,0), direction(0,0,1)); }
	/*inline axis2 Oyx() { return axis2(origin(), direction(0,0,1), direction(0,1,0)); }
	inline axis2 Ozy() { return axis2(origin(), direction(1,0,0), direction(0,0,1)); }
	inline axis2 Oxz() { return axis2(origin(), direction(0,1,0), direction(1,0,0)); }*/
	
	inline axis3 Oxyz() { return axis3(origin(), direction(0,0,1), direction(1,0,0)); }

	class transform {
		malgo3::matrix3<double> rot;
		malgo3::vector3<double> trs;
		double scl;

		transform() : scl(1), trs(0,0,0), rot(malgo3::matrix3<double>::identity()) {};
		//transform(const matrix3<T>& mat, const vector3<T>& vec, T scl) : rotate(mat), translate(vec), scl(scl) {}

		malgo3::vector3<double> doit(const malgo3::vector3<double>& a) {
			return rot.dot(a.scale(scl)).add(trs);
		}
	};

	/*using curve2 = gxx::geom2::curve; 
	using line2 = gxx::geom2::line; 
	using point2 = gxx::geom2::point; 
	using direction2 = gxx::geom2::direction; 
	using vector2 = gxx::geom2::vector; 

	enum class curve_enum : uint8_t {
		none,
		line
	};

	enum class surface_enum : uint8_t {
		none,
		plane
	};

	

	class basic_curve {
	public:
		double bmax, bmin;
		virtual point d0(double t) const = 0;
		virtual vector d1(double t) const = 0;
		virtual bool is_closed() { return false; }
		virtual bool is_periodic() { return false; }
		virtual double tmin() { return 0; }
		virtual double tmax() { return 0; }
		virtual ~basic_curve() {}
		virtual curve_enum gettype() const { return curve_enum::none; }

		virtual size_t printTo(gxx::io::ostream& o) const {
			return gxx::print("curve3");
		}; 

		basic_curve() : bmax(tmax()), bmin(tmin()) {}
		basic_curve(double bmin, double bmax) : bmax(bmax), bmin(bmin) {}
	};

	class nilcurve : public basic_curve {
		point d0(double t) const override { return point(); }
		vector d1(double t) const override { return vector(); }
	};

	class line : public basic_curve {
	public:
		point l;
		direction d;

		ACCESSOR(loc, l);
		ACCESSOR(dir, d);

		line(point l, direction d) : l(l), d(d) {}
		line(point l1, point l2) : l(l1), d(l2 - l1), basic_curve(0, (l2 - l1).abs()) {}
		line(point l, vector v) : l(l), d(v), basic_curve(0, v.abs()) {}

		vector vec() const {
			return d0(bmax) - l;
		}

		point d0(double t) const override {
			return point(l.x + d.x * t, l.y + d.y * t, l.z + d.z * t);
		}

		vector d1(double t) const override {
			return d;
		}

		double tmin() override { return - geom3::infinity; }
		double tmax() override { return   geom3::infinity; }

		size_t printTo(gxx::io::ostream& o) const override {
			return gxx::fprint("line(l:{},d:{},bmin:{},bmax:{})",l,d,bmin,bmax);
		} 

		virtual curve_enum gettype() const { return curve_enum::line; }
	};


	class curve {
	public:
		//curve_enum type;
		union {
			nilcurve nil;
			line ln;
		};
		double tmin = 0, tmax = 0;

		line& as_line() { return ln; }
		const line& as_line() const { return ln; }

		basic_curve& abstract() { return *static_cast<basic_curve*>(&ln); }
		const basic_curve& abstract() const { return *static_cast<const basic_curve*>(&ln); }

		curve() {
			new (&nil) nilcurve();
		}

		curve(const point& pnt1, const point& pnt2) {
			new (&ln) line(pnt1, pnt2);
		}

		size_t printTo(gxx::io::ostream& o) const {
			return abstract().printTo(o);
		}

		const char* strtype() const {
			switch (abstract().gettype()) {
				case curve_enum::none: return "none";
				case curve_enum::line: return "line";
				default: return "undefined curve3";
			}
		}

		curve_enum gettype() const { return abstract().gettype(); }

		//curve2 project_line_to(const surface& surf);
		//curve2 project_to(const surface& surf);

		~curve(){}
	};









	class basic_surface {
	public:
		virtual point d0(double v, double u) const = 0; 
		virtual bool is_v_closed() { return false; }
		virtual bool is_v_periodic() { return false; }
		virtual bool is_u_closed() { return false; }
		virtual bool is_u_periodic() { return false; }
		virtual double vmin() { return 0; }
		virtual double vmax() { return 0; }
		virtual double umin() { return 0; }
		virtual double umax() { return 0; }
		virtual curve2 projection(const curve& crv) const { return curve2(); }
		virtual ~basic_surface() {}
		virtual size_t printTo(gxx::io::ostream& o) const { return gxx::print("surface"); }
		virtual surface_enum gettype() const { return surface_enum::none; }
	};


	class nilsurf : public basic_surface {
		point d0(double v, double u) const override { return point(); }
		//vector d1(double t) const override { return vector(); }
	};

	class cylinder : public basic_surface {
	public:
		double r;
		double h;
		axis3 ax3;

		cylinder(double r, double h, const axis3& ax3) : r(r), h(h), ax3(ax3) {}

		point d0(double v, double u) const override {
			double c = r * cos(v);
			double s = r * sin(v);
			double w = h * u;
			return point(
				ax3.l.x + ax3.dx.x * c + ax3.dy.x * s + ax3.dz.x * w,
				ax3.l.y + ax3.dx.y * c + ax3.dy.y * s + ax3.dz.y * w,
				ax3.l.z + ax3.dx.z * c + ax3.dy.z * s + ax3.dz.z * w
			);
		}
	};

	class sphere : public basic_surface {
	public:
		double r;
		axis3 ax3;

		sphere(double r, double h, const axis3& ax3) : r(r), ax3(ax3) {}

		point d0(double v, double u) const override {
			double a = r * cos(v) * cos(u);
			double b = r * sin(v) * cos(u);
			double c = r * sin(u);
			return point(
				ax3.l.x + ax3.dx.x * a + ax3.dy.x * b + ax3.dz.x * c,
				ax3.l.y + ax3.dx.y * a + ax3.dy.y * b + ax3.dz.y * c,
				ax3.l.z + ax3.dx.z * a + ax3.dy.z * b + ax3.dz.z * c
			);
		}
	};

	class plane : public basic_surface {
	public:
		axis2 ax2;

		ACCESSOR(pos, ax2);

		plane(const axis2& ax2) : ax2(ax2) {}

		point d0(double v, double u) const override {
			return point(ax2.loc() + ax2.dirx().scale(v) + ax2.diry().scale(u));				
		} 

		curve2 projection(const curve& crv) const override;// { 
		//	gxx::println("projection to plane");
		//	return line2(point2(0,0), direction2(0,1));
		//}

		virtual surface_enum gettype() const { return surface_enum::plane; }
	};




	class surface {
	public:
		//surface_enum type;
		union {
			nilsurf nil;
			plane pln;
		};

		plane& as_plane() { return pln; }
		const plane& as_plane() const { return pln; }

		basic_surface& abstract() { return *static_cast<basic_surface*>(&pln); }
		const basic_surface& abstract() const { return *static_cast<const basic_surface*>(&pln); }

		surface(const plane& ctr) {
			new (&pln) plane(ctr);
		}

		surface(const axis2& ctr) {
			new (&pln) plane(ctr);
		}

		surface(const surface& oth) {
			switch(oth.gettype()) {
				case surface_enum::none: new (&nil) nilsurf(); return;
				case surface_enum::plane: new (&pln) plane(oth.pln); return;
				default: gxx::panic("surface: undefined surface");
			}
		}

		curve2 projection(const curve& crv) const {				
			return abstract().projection(crv);
		}

		size_t printTo(gxx::io::ostream& o) const {
			return abstract().printTo(o);
		}

		~surface(){}

		surface_enum gettype() const { return abstract().gettype(); }
	};*/

}}

#endif