#ifndef GXX_GEOM_CURVE3_H
#define GXX_GEOM_CURVE3_H

#include <gxx/geom/geom3.h>
#include <math.h>

namespace gxx { namespace curve3 {
	using namespace gxx::geom3;

	class curve {
	public:
		virtual point d0(double t) = 0;
		virtual bool is_closed() { return false; }
		virtual bool is_periodic() { return false; }
		virtual double tmin() { return 0; }
		virtual double tmax() { return 0; }
		virtual ~curve() {}

		virtual size_t printTo(gxx::io::ostream& o) const {
			return gxx::print("curve3");
		}; 
	};

	class line : public curve {
	public:
		point l;
		direction d;

		ACCESSOR(loc, l);
		ACCESSOR(dir, d);

		line(point l, direction d) : l(l), d(d) {}
		line(point l1, point l2) : l(l1), d(l2 - l1) {}

		point d0(double t) override {
			return point(l.x + d.x * t, l.y + d.y * t, l.z + d.z * t);
		}

		double tmin() override { return - geom3::infinity; }
		double tmax() override { return   geom3::infinity; }

		size_t printTo(gxx::io::ostream& o) const override {
			return gxx::fprint("line(l:{},d:{})",l,d);
		} 
	};

	/*class circle : public curve {
	public:
		double r;
		axis2 ax2;

		circle(double r, const axis2& ax2) : r(r), ax2(ax2) {}

		point d0(double t) override {
			auto& pl = ax2.l;
			auto& dx = ax2.dx;
			auto& dy = ax2.dy;
			double s = sin(t) * r;
			double c = cos(t) * r;
			return point(
				pl.x + c * dx.x + s * dy.x, 
				pl.y + c * dx.y + s * dy.y, 
				pl.z + c * dx.z + s * dy.z
			);
		}
	};*/

	/*class elipse : public curve {
	public:
		double xr;
		double yr;
		axis2 ax2;

		elipse(double xr, double yr, const axis2& ax2) : xr(xr), yr(yr), ax2(ax2) {}

		point d0(double t) override {
			auto& pl = ax2.l;
			auto& dx = ax2.dx;
			auto& dy = ax2.dy;
			double s = sin(t) * yr;
			double c = cos(t) * xr;
			return point(
				pl.x + c * dx.x + s * dy.x, 
				pl.y + c * dx.y + s * dy.y, 
				pl.z + c * dx.z + s * dy.z
			);
		}
	};*/

	/*class line : public bounded_curve {
	public:
		point a;
		direction d;

		line(point pnt1, point pnt2) : a(pnt1), d(pnt2.sub(pnt1)), bounded_curve(0, 1, false, false) {}

		point d0(double t) override {
			return point(a.x + d.x * t, a.y + d.y * t, a.z + d.z * t);
		}
	};*/

}}

#endif