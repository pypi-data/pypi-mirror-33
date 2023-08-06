#ifndef GXX_GEOM_GEOM2_H
#define GXX_GEOM_GEOM2_H

#include <gxx/print/stdprint.h>
#include <gxx/math/malgo2.h>
#include <gxx/math/interval.h>
#include <limits>
#include <memory>

#include <gxx/geom/sgeom2.h>
#include <gxx/exception.h>

namespace gxx { 
	class drawer2d;

namespace geom2 {
	constexpr static double infinity = std::numeric_limits<double>::infinity();
	constexpr static double precision = 0.000001;

	/*class point : public malgo2::vector2<double> {
	public: 
		point()=default;
		point(double x, double y) : malgo2::vector2<double>(x,y) {}
		point(const point& oth) : malgo2::vector2<double>(oth) {}
		point(const malgo2::vector2<double>& oth) : malgo2::vector2<double>(oth) {}
		//gxx::sgeom2::point<double> operator gxx::sgeom2::point<double> { return sgeom2::point<double>(x,y); }
	};

	class vector : public malgo2::vector2<double> {
	public:
		vector()=default;
		vector(double x, double y) : malgo2::vector2<double>(x,y) {}
		vector(const vector& oth) : malgo2::vector2<double>(oth) {}
		vector(const malgo2::vector2<double>& oth) : malgo2::vector2<double>(oth) {}
	};

	class direction : public malgo2::vector2<double> {
	public:
		direction()=default;
		direction(double x, double y, bool norm = true) : malgo2::vector2<double>(x,y) { if (norm) self_normalize(); }
		direction(const direction& oth) : malgo2::vector2<double>(oth) {}
		direction(const malgo2::vector2<double>& oth, bool norm = true) : malgo2::vector2<double>(oth) { if (norm) self_normalize(); }
	};*/

	using point = malgo::vector2<double>;
	using vector = malgo::vector2<double>;
	using direction = malgo::unit_vector2<double>;

	/*enum class curve_enum : uint8_t {
		none,
		line,
		circle
	};*/

	struct boundbox {
		gxx::math::interval<double> x;
		gxx::math::interval<double> y;

		boundbox() {};
		boundbox(double x1, double x2, double y1, double y2) : x(x1, x2), y(y1, y2) {};

		bool can_intersect(const boundbox& oth) const {
			if (x.is_intersected_with_weak(oth.x, precision) && y.is_intersected_with_weak(oth.y, precision)) gxx::println(x, y, oth.x, oth.y);
			return x.is_intersected_with_weak(oth.x, precision) && y.is_intersected_with_weak(oth.y, precision);
		}
	};

	class curve {
	public:
		virtual point d0(double t) const = 0;
		virtual vector d1(double t) const = 0;
		virtual bool is_closed() { return false; }
		virtual bool is_periodic() { return false; }
		virtual double tmin() { return 0; }
		virtual double tmax() { return 0; }
		virtual double rotation_angle() const { return 0; }
		virtual size_t printTo(gxx::io::ostream& o) const { return gxx::print_to(o, "nilcurve"); }	
		//virtual curve_enum gettype() const { return curve_enum::none; }	
		virtual void drawTo(drawer2d& cntxt) const { throw GXX_NOT_IMPLEMENTED; };

		virtual boundbox getbound(double s, double f) const { throw GXX_NOT_IMPLEMENTED; };
		virtual boundbox getbound(const math::interval<double>& t) const { return getbound(t.minimum, t.maximum); };

		virtual bool is_analityc() { return false; }
		virtual std::shared_ptr<curve> translate(double x, double y) { throw GXX_NOT_IMPLEMENTED; }
		virtual std::shared_ptr<curve> rotate(double a) { throw GXX_NOT_IMPLEMENTED; }

		//point start() const { return d0(bmin); }
		//point finish() const { return d0(bmax); }
		//vector start_d1() const { return d1(bmin); }
		//vector finish_d1() const { return d1(bmax); }

		//double bmax, bmin;
		//bool trimmed;

		//virtual bool in(double t) const { return !trimmed || ((t >= bmin) && (t <= bmax)); }
		//virtual bool is_bound(double t) const { return trimmed && (gxx::math::is_same(t, bmin, precision) || gxx::math::is_same(t, bmax, precision)); }

		//curve() {}
		//curve(double bmin, double bmax) : bmax(bmax), bmin(bmin), trimmed(true) {}
	};

	class nilcurve : public curve {
	public:
		point d0(double t) const override { return point(); }
		vector d1(double t) const override { return vector(); }
	};

	class line : public curve {
	public:
		point l;
		direction d;
		double angle;
		line(const point& l, const direction& v) : l(l), d(v), angle(atan2(v.y, v.x)) {}
		//line(const point& l1, const point& l2) : l(l1), d(l2-l1), curve(0, (l2-l1).abs()) { angle = atan2(d.y, d.x); }
		point d0(double t) const override { return point(l.x + d.x * t, l.y + d.y * t); }
		double rev_d0(point pnt) const { return (pnt-l).sclmul(d); }
		vector d1(double t) const override { return d; }
		double tmin() override { return - geom2::infinity; }
		double tmax() override { return   geom2::infinity; }
		//curve_enum gettype() const override { return curve_enum::line; }	
		size_t printTo(gxx::io::ostream& o) const override { return gxx::fprint("line(l:{},d:{})",l,d); } 
		//void drawTo(drawer2d& cntxt) const override;

		double distance(point pnt) const {
			auto l21 = pnt - l;
			return std::fabs(l21.crossmul(d));
		}

		direction normal() const { 
			return direction(-sin(angle), cos(angle)); 
		}

		virtual boundbox getbound(double s, double f) const { 
			auto pnt1 = d0(s);
			auto pnt2 = d0(f);
			if (pnt1.x > pnt2.x) std::swap(pnt1.x, pnt2.x);
			if (pnt1.y > pnt2.y) std::swap(pnt1.y, pnt2.y);
			return boundbox{pnt1.x, pnt2.x, pnt1.y, pnt2.y};
		}

		bool is_analityc() override { return true; }

		std::shared_ptr<curve> translate(double x, double y) { 
			return std::shared_ptr<curve>(new line(l + vector(x,y), d));
		}

		std::shared_ptr<curve> rotate(double a) { 
			return std::shared_ptr<curve>(new line(l.rotate(a), d.rotate(a)));
		}
	};

	class circle : public curve {
	public:
		point l;
		double r;
		double sp;
		direction dirx;
		ACCESSOR(center, l);
		ACCESSOR(radius, r);
		circle(double r, const point& l, const direction& d = direction(1,0,false)) : l(l), dirx(d), r(r), sp(atan2(d.y, d.x)) {}
		point d0(double t) const override { auto c = cos(t+sp); auto s = sin(t+sp); return point(l.x + c*r, l.y + s*r); }
		vector d1(double t) const override { gxx::panic("circle"); }
		double tmax() override { return 2 * M_PI; }
		//curve_enum gettype() const override { return curve_enum::circle; }	
		size_t printTo(gxx::io::ostream& o) const override { return gxx::fprint("circle(r:{},c:{},v:{})",r,l,dirx); } 
		double sparam() { return atan2(dirx.x, dirx.y); }
		//void drawTo(drawer2d& cntxt) const override;
		
		bool is_analityc() override { return true; }

		std::shared_ptr<curve> translate(double x, double y) { 
			return std::shared_ptr<curve>(new circle(r, l + vector(x,y), dirx));
		}
	};
/*
	struct intersection_point2d {
		double value;
		bool bound;
		intersection_point2d(double a, bool bound = false) : value(a), bound(bound) {}
		operator double() { return value; }
		size_t printTo(gxx::io::ostream& o) const {
			return gxx::fprint("({},tan:{})", value, bound);
		}
	};

	struct intersection_point {
		point value;
		bool tangent;
		intersection_point(point a, bool tangent = false) : value(a), tangent(tangent) {}
		operator point() { return value; }
		size_t printTo(gxx::io::ostream& o) const {
			return gxx::fprint("({},tan:{})", value, tangent);
		}
	};

	struct interval {
		double start;
		double finish;
		interval(double start, double finish) : start(start), finish(finish) {}
		size_t printTo(gxx::io::ostream& o) const {
			return gxx::fprint("({},{})", start, finish);
		}
	};

	class intresult_parts {
	public:
		std::vector<intersection_point2d> points;
		std::vector<interval> intervals;
	public:
		size_t printTo(gxx::io::ostream& o) const {
			return gxx::fprint("(pnts:{}, ints:{})", points, intervals);
		}
	};

	class intresult_common {
	public:
		std::vector<intersection_point> points;
	public:	
		size_t printTo(gxx::io::ostream& o) const {
			return gxx::fprint("(pnts:{})", points);
		}
	};

	class intresult {
	public:
		intresult_common common;
		intresult_parts first;	
		intresult_parts second;
	};

	
	inline void intersect_line2_line2(const line& a, const line& b, intresult_common& com, intresult_parts& ares, intresult_parts& bres) {
		point l12 = a.l - b.l;
		double dd = a.d.crossmul(b.d);

		if (gxx::math::early_zero(dd, precision)) {
			if (gxx::math::early_zero(l12.crossmul(a.d), precision)) {
				//прямые совпадают
				gxx::println("same");
				if (!a.trimmed && !b.trimmed) {
					ares.intervals.emplace_back(-infinity, infinity);
					bres.intervals.emplace_back(-infinity, infinity);
				}
				else {
					gxx::panic("undef");
				}
			}
			else {
				gxx::println("not intersect");
				//нет пересечений
			}
		}
		else {
			gxx::println("one point");
			//одна точка пересечения
			double t1 = b.d.crossmul(l12) / dd;
			double t2 = a.d.crossmul(l12) / dd;
			if (a.in(t1) && b.in(t2)) {
				ares.points.emplace_back(t1, a.is_bound(t1));
				bres.points.emplace_back(t2, b.is_bound(t1));
				com.points.emplace_back(a.d0(t1));
			}
		}

		return;
	}

	inline void intersect_line2_circle2(const line& a, const circle& b, intresult_common& com, intresult_parts& ares, intresult_parts& bres) {
		auto linenorm = a.normal();
		auto distance = linenorm.sclmul(a.l - b.l);
		auto r = b.radius();
		
		if (distance < 0) { linenorm.self_reverse(); distance = -distance; }
				
		if (gxx::math::is_same(distance, r, precision)) {
			auto t1 = a.d.sclmul(b.l-a.l);
			auto t2 = -b.sp + atan2(linenorm.y, linenorm.x); 
			
			if (a.in(t1) && b.in(t2)) {
				ares.points.emplace_back(t1);
				bres.points.emplace_back(t2);
				com.points.emplace_back(a.d0(t1), true);
			}
			
			return;
		}

		if (distance > r) {
			return;
		}

		auto cos_diff_angle = distance / r;
		auto diff_angle = acos(cos_diff_angle);
		auto t2 = -b.sp + atan2(linenorm.y, linenorm.x); 

		auto t21 = t2 - diff_angle;
		auto pnt1 = b.d0(t21);
		auto t11 = a.rev_d0(pnt1);

		auto t22 = t2 + diff_angle;
		auto pnt2 = b.d0(t22);
		auto t12 = a.rev_d0(pnt2);

		if (a.in(t11) && b.in(t21)) {
			ares.points.emplace_back(t11, a.is_bound(t11));
			bres.points.emplace_back(t21, b.is_bound(t21));
			com.points.emplace_back(pnt1);
		}

		if (a.in(t12) && b.in(t22)) {
			ares.points.emplace_back(t12, a.is_bound(t12));
			bres.points.emplace_back(t22, b.is_bound(t22));
			com.points.emplace_back(pnt2);
		}
		return;
	}


	inline void intersect_circle2_circle2(const circle& a, const circle& b, intresult_common& com, intresult_parts& ares, intresult_parts& bres) {
		gxx::println("circ circ intersect");
	}

	inline void intersect_line2_curve2(const line& a, const curve& b, intresult_common& com, intresult_parts& ares, intresult_parts& bres) {
		if (typeid(b) == typeid(line)) { intersect_line2_line2(a, static_cast<const line&>(b), com, ares, bres); return; }
		if (typeid(b) == typeid(circle)) { intersect_line2_circle2(a, static_cast<const circle&>(b), com, ares, bres); return; }
		gxx::panic("undefined curve");
	}

	inline void intersect_circle2_curve2(const circle& a, const curve& b, intresult_common& com, intresult_parts& ares, intresult_parts& bres) {
		if (typeid(b) == typeid(circle)) { intersect_circle2_circle2(a, static_cast<const circle&>(b), com, ares, bres); return; }
		gxx::panic("undefined curve");
	}

	inline intresult intersect_curve2_curve2(const curve& a, const curve& b) {
		intresult res;
		if (typeid(a) == typeid(line)) { intersect_line2_curve2(static_cast<const line&>(a), b, res.common, res.first, res.second); return res; }
		if (typeid(b) == typeid(line)) { intersect_line2_curve2(static_cast<const line&>(b), a, res.common, res.second, res.first); return res; }
		if (typeid(a) == typeid(circle)) { intersect_circle2_curve2(static_cast<const circle&>(a), b, res.common, res.first, res.second); return res; }
		if (typeid(b) == typeid(circle)) { intersect_circle2_curve2(static_cast<const circle&>(b), a, res.common, res.second, res.first); return res; }
		gxx::panic("undefined curve");
		return res;
	}

	inline intresult operator ^ (const curve& a, const curve& b) {
		return intersect_curve2_curve2(a, b);
	}*/
}}

#endif