#include <gxx/rabbit/intersect2.h>
#include <typeinfo>
#include <typeindex>
#include <map>

namespace rabbit {	
	struct crvcrv_analytic_intresult {
		std::vector<double> apnts;
		std::vector<double> bpnts;
		std::vector<point2> pnts;
		bool same = false;
		
		double offset;
		bool revdir;

		bool have_points() const {
			return !apnts.empty(); 
		}	

		crvcrv_analytic_intresult(bool b) : same(b) {} 
		crvcrv_analytic_intresult(bool b, double offset, bool revdir) : same(b), offset(offset), revdir(revdir) {} 
		crvcrv_analytic_intresult(const std::initializer_list<double>& ap, const std::initializer_list<double>& bp, const std::initializer_list<point2>& p) : apnts(ap), bpnts(bp), pnts(p) {}
	
		crvcrv_analytic_intresult& swap_curves() {
			std::swap(apnts, bpnts);
			return *this;
		}

		bool empty() {
			return apnts.empty() && bpnts.empty() && same == false;
		}

		size_t printTo(gxx::io::ostream& o) const {
			if (have_points()) {
				gxx::fprint_to(o, "pnts:(a:{}, b:{}, r:{}) ", apnts, bpnts, pnts);
			}
			if (same) {
				gxx::fprint_to(o, "same curve -> off:{} rev:{}", offset, revdir);
			}

			return 1;
		}
	};

	using analytic_intsignature = crvcrv_analytic_intresult(*)(const curve2&, const curve2&); 	

	crvcrv_analytic_intresult line_line_intersection(const curve2& acrv, const curve2& bcrv) {
		const auto& a = static_cast<const gxx::geom2::line&>(acrv);
		const auto& b = static_cast<const gxx::geom2::line&>(bcrv);

		point l12 = a.l - b.l;
		double dd = a.d.crossmul(b.d);

		if (gxx::math::early_zero(dd, rabbit::precision)) {
			if (l12.early_zero() || gxx::math::is_same(l12.x / a.d.x, l12.y / a.d.y, rabbit::precision)) {
				return crvcrv_analytic_intresult(true, l12.sclmul(b.d), a.d.is_not_same(b.d));
			}
			else {
				return crvcrv_analytic_intresult(false);
			}
		}
		
		double t1 = b.d.crossmul(l12) / dd;
		double t2 = a.d.crossmul(l12) / dd;

		auto apnt = acrv.d0(t1);
		auto bpnt = bcrv.d0(t2);
		assert(apnt.is_same(bpnt));
		
		return crvcrv_analytic_intresult({t1}, {t2}, {apnt});
	}

	crvcrv_analytic_intresult circle_circle_intersection(const curve2& acrv, const curve2& bcrv) {
		gxx::println("circ circ intersect");
		const auto& a = static_cast<const gxx::geom2::circle&>(acrv);
		const auto& b = static_cast<const gxx::geom2::circle&>(bcrv);

		PANIC_TRACED();
	}


	/*crvcrv_analytic_intresult intersect_line2_circle2(const line& a, const circle& b, intresult_common& com, intresult_parts& ares, intresult_parts& bres) {
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
	}*/



	std::map<std::pair<std::type_index, std::type_index>, analytic_intsignature> intsmap {
		{std::pair<std::type_index, std::type_index>(typeid(gxx::geom2::line), typeid(gxx::geom2::line)), line_line_intersection}, 
		{std::pair<std::type_index, std::type_index>(typeid(gxx::geom2::circle), typeid(gxx::geom2::circle)), circle_circle_intersection}, 
	};

	crvcrv_analytic_intresult analytic_curve_curve_intersection(const curve2& acrv, const curve2& bcrv) {
		std::type_index atype = typeid(acrv); 
		std::type_index btype = typeid(bcrv);

		auto it = intsmap.find(std::pair<std::type_index, std::type_index>(atype, btype));
		if (it != intsmap.end()) { return it->second(acrv, bcrv); } 

		it = intsmap.find(std::pair<std::type_index, std::type_index>(btype, atype));
		if (it != intsmap.end()) { return it->second(bcrv, acrv).swap_curves(); }

		PANIC_TRACED();
	}

	trim_trim_intersection_result trim_trim_intersection(const trim2& a, const trim2& b) {
		trim_trim_intersection_result res;
		//if (!a.box.can_intersect(b.box)) return res;

		//gxx::println(a);
		//gxx::println(b);

		if (a.crv->is_analityc() && b.crv->is_analityc()) {
			//Пересечение кривых аналитического класса.
			auto crvres = analytic_curve_curve_intersection(*a.crv, *b.crv);
			
			if (crvres.empty()) return res;
			if (crvres.same) {
				gxx::panic("TODO same curves");

				//Кривые совпадают.
				//Ищем интервал B в системе координат A.
				/*auto bint_asystem = b.tparam.offset(crvres.offset);
				if (crvres.revdir) bint_asystem = bint_asystem.reverse();
				
				auto intersect = a.tparam.simple_intersect(bint_asystem);
				if (intersect) {
					res.aint = intersect;

					//Обратное преобразование.
					res.bint = crvres.revdir ? intersect.reverse() : intersect;
					res.bint = res.bint.offset( crvres.offset );
					res.trm = trim2(a.crv, res.aint.minimum, res.aint.maximum); 

					//ASSERTATION
					auto trm2 = trim2(b.crv, res.bint.minimum, res.bint.maximum); 
					if (!crvres.revdir) {
						assert(trm2.start().is_same(res.trm.start()));
						assert(trm2.finish().is_same(res.trm.finish()));
					} else {
						assert(trm2.start().is_same(res.trm.finish()));
						assert(trm2.finish().is_same(res.trm.start()));						
					}
				}*/
			} else {
				//Копируем точки пересечения.
				size_t sz = crvres.pnts.size();
				res.pnts.reserve(sz);

				for (int i = 0; i < sz; ++i) {
					if (a.tparam.in_weak(crvres.apnts[i], rabbit::precision) && b.tparam.in_weak(crvres.bpnts[i], rabbit::precision)) {
						//gxx::println("H", crvres.apnts[i]);
						res.pnts.emplace_back(a.tparam.to_proc(crvres.apnts[i]), b.tparam.to_proc(crvres.bpnts[i]), crvres.pnts[i]);
						//gxx::println("E", crvres.apnts[i]);
					}
				}

				res.pnts.shrink_to_fit();
			}

			return res;
		} else {
			PANIC_TRACED();
		}
	}

	bool __is_really_intersected(
		const malgo::vector2<double>& avin,
		const malgo::vector2<double>& bvin,
		const malgo::vector2<double>& avout,
		const malgo::vector2<double>& bvout
	) {
		auto m1 = avin.crossmul(bvin);
		auto m2 = avout.crossmul(bvout);
		return (m1 < 0 && m2 > 0) || (m1 > 0 && m2 < 0);
	}

	bool is_really_intersected(const trim2& ain, const trim2& bin, const trim2& aout, const trim2& bout) {
		auto vaout = aout.crv->d1(aout.tparam.start());
		auto vain = ain.crv->d1(ain.tparam.finish());
		auto vbout = bout.crv->d1(bout.tparam.start());
		auto vbin = bin.crv->d1(bin.tparam.finish());
		return __is_really_intersected(vain, vaout, vbin, vbout);
	}

	bool is_really_intersected(const trim2& a, double param, const trim2& bin, const trim2& bout) {
		auto vaio = a.crv->d1(param);
		auto vbout = bout.crv->d1(bout.tparam.start());
		auto vbin = bin.crv->d1(bin.tparam.finish());
		return __is_really_intersected(vaio, vaio, vbin, vbout);
	}

	loop_loop_intersection_result loop_loop_intersection(const loop2& a, const loop2& b) {
		loop_loop_intersection_result ret;

		const trim2* alt = &a.edges[a.edges.size()-1];
		const trim2* blt = &b.edges[b.edges.size()-1];

		for(int ai = 0; ai < a.edges.size(); ++ai) {
			const auto& at = a.edges[ai];
			
			for(int bi = 0; bi < b.edges.size(); ++bi) {
				const auto& bt = b.edges[bi];

				auto ttres = trim_trim_intersection(at, bt);
				//gxx::println(ai, bi, ttres);

				for (int i = 0; i < ttres.pnts.size(); ++i) {
					tpoint ip = ttres.pnts[i];

					bool afinish = gxx::math::is_same(1.0, ip.a, rabbit::precision);
					bool bfinish = gxx::math::is_same(1.0, ip.b, rabbit::precision);
					bool astart = gxx::math::is_same(0.0, ip.a, rabbit::precision);
					bool bstart = gxx::math::is_same(0.0, ip.b, rabbit::precision);

					if (afinish || bfinish)  {
						
					} else if (astart || bstart) {
						if (astart && bstart) {
							ret.try_add_bound_point(ai, bi, ttres.pnts[i], at, *alt, bt, *blt);
						} else if (astart) {
							ret.try_add_bound_point(ai, bi, ttres.pnts[i], at, *alt, bt, bt);
						} else {
							ret.try_add_bound_point(ai, bi, ttres.pnts[i], at, at, bt, *blt);
						}
					} 
					else {
						ret.add_point(ai, bi, ttres.pnts[i], at, bt);
					}

				}				
				blt = &bt;
			};
			//gxx::println();
			alt = &at;  
		};

		return ret;
	}

	void add_loop_part(loop2& formed, const loop2& donor, double tstrt, double tstop) {
		int strim = tstrt;
		int ftrim = tstop;

		tstrt -= strim;
		tstop -= ftrim;

		int num = strim;

		if (strim == ftrim && strim < ftrim) {
			formed.edges.emplace_back(donor.edges[strim], tstrt, tstop);
			//gxx::println();
			return;
		}


		//gxx::println("strt", donor.edges.size());
		formed.edges.emplace_back(donor.edges[num++], tstrt, 1);
		if (num == donor.edges.size()) num = 0;
		while(num != ftrim) {
			//gxx::println(num);
			//gxx::println("iter");
			formed.edges.emplace_back(donor.edges[num++], 0, 1);
			if (num == donor.edges.size()) num = 0;
		}
		//gxx::println("fin");
		formed.edges.emplace_back(donor.edges[num], 0, tstop);
	}

	std::pair<loop2, loop2> loop_loop_combine(const loop2& a, const loop2& b) {
		//gxx::println("loop_loop_combine");
		auto llints = loop_loop_intersection(a,b);

		if (llints.empty()) {
			return std::make_pair(a,b);
		}

		std::vector<ipoint*> asorted;
		std::vector<ipoint*> bsorted;

		for (auto& i : llints.ipnts) {
			//GXX_PRINT(i);
			asorted.push_back(&i);
			bsorted.push_back(&i);
		}

		std::sort(asorted.begin(), asorted.end(), [](const ipoint* a, const ipoint* b) { return a->a < b->a; }); 
		std::sort(bsorted.begin(), bsorted.end(), [](const ipoint* a, const ipoint* b) { return a->b < b->b; });

		for (int i = 0; i < asorted.size() - 1; ++i) {
			asorted[i]->anext = asorted[i+1];
		}
		asorted[asorted.size() - 1]->anext = asorted[0];

		for (int i = 0; i < bsorted.size() - 1; ++i) {
			bsorted[i]->bnext = bsorted[i+1];
		}
		bsorted[bsorted.size() - 1]->bnext = bsorted[0];

		ipoint* start = asorted[0];
		ipoint* it = start;
		//gxx::fprintln("start by: {}", *it);

		std::pair<loop2,loop2> ret;
		do {
			if (it->a_righter_than_b) {
				//gxx::fprintln("step by A to: {}", *it);
				add_loop_part(ret.first, a, it->a, it->anext->a);
				it = it->anext;
			} else {
				//gxx::fprintln("step by B to: {}", *it);
				add_loop_part(ret.first, b, it->b, it->bnext->b);
				it = it->bnext;
			}
		} while(it != start);	

		//gxx::println(ret);	
		//for (auto& t: ret.first.edges) {
		//	gxx::println(t.finish());
		//}

		if (!ret.first.edges.empty()) ret.first.check_closed();
		if (!ret.second.edges.empty()) ret.second.check_closed();

		return ret;
	}
}