#ifndef GXX_RABBIT_INTERSET2_H
#define GXX_RABBIT_INTERSET2_H

#include <gxx/rabbit/topo2.h>
#include <gxx/dlist.h>

#include <algorithm>
#include <list>

namespace rabbit {
	static constexpr double precision = 0.00000001;

	struct tpoint {
		double a;
		double b;
		point2 r;

		tpoint(double a, double b, point2 r) : a(a), b(b), r(r) {}

		size_t printTo(gxx::io::ostream& o) const {
			gxx::fprint_to(o, "(a:{}, b:{}, r:{}) ", a, b, r);
		}
	};

	struct ipoint {
		double a;
		double b;
		point2 r;

		//dlist_head alnk;
		//dlist_head blnk;
		ipoint* anext;
		ipoint* bnext;

		bool a_righter_than_b;
		bool used;

		trim2* at;
		trim2* bt;

		ipoint(double a, double b, point2 r, bool righter) : a(a), b(b), r(r), a_righter_than_b(righter), at(at), bt(bt) {}

		size_t printTo(gxx::io::ostream& o) const {
			gxx::fprint_to(o, "(a:{}, b:{}, r:{}) ", a, b, r);
		}
	};

	struct trim_trim_intersection_result {
		//Точки пересечения.
		std::vector<tpoint> pnts;

		//Интервал пересечения.
				//TODO
		rabbit::interval aint;
		rabbit::interval bint;	
		rabbit::trim2 trm;

		bool have_points() const {
			return !pnts.empty(); 
		}	

		bool is_interval() const {
			return ((bool)aint) && ((bool)bint); 
		}	

		bool have_intervals() const {
			return ((bool)aint) && ((bool)bint); 
		}	

		bool empty() const {
			return pnts.empty() && is_interval() == false;
		}		

		size_t printTo(gxx::io::ostream& o) const {
			if (have_points()) {
				gxx::fprint_to(o, "pnts:{}", pnts);
			}
			if (have_intervals()) {
				//TODO
				gxx::fprint_to(o, "ints:(a:{}, b:{}) ", aint, bint);
			}

			if (empty()) { gxx::print("have not intersection"); }

			return 1;
		}
	};

	inline bool is_a_righter_than_b(const trim2& a, const trim2& b, const tpoint& p) {
		//gxx::println("is_a_righter_than_b");
		auto d1res = a.d1(p.a).evalrot(b.d1(p.b));
		if (! gxx::math::early_zero(d1res, rabbit::precision)) {
			return d1res > 0;
		}
		else PANIC_TRACED();		
	}

	inline bool is_a_righter_than_b(const trim2& a1, const trim2& a2, const trim2& b1, const trim2& b2, const tpoint& tp) {
		//gxx::println("is_a_righter_than_b_2");
		vector2 dir_a1;
		vector2 dir_a2;
		vector2 dir_b1;
		vector2 dir_b2;

		//GXX_PRINT(&a1 == &a2);
		//GXX_PRINT(&b1 == &b2);

		if (&a1 == &a2) { dir_a1 = dir_a2 = a1.d1(tp.a); } else { dir_a1 = a1.d1(1); dir_a2 = a2.d1(0); }
		if (&b1 == &b2) { dir_b1 = dir_b2 = b1.d1(tp.b); } else { dir_b1 = b1.d1(1); dir_b2 = b2.d1(0); }

		//auto d1res_1 = a.d1(p.a).evalrot(b.d1(p.b));
		//auto d1res_2 = a.d1(p.a).evalrot(b.d1(p.b));
		
		//GXX_PRINT(dir_a1);
		//GXX_PRINT(dir_a2);
		//GXX_PRINT(dir_b1);
		//GXX_PRINT(dir_b2);

		//auto arot = dir_a1.evalrot(dir_a2) + M_PI;
		auto rot1 = dir_a1.evalrot(dir_b1);
		auto rot2 = dir_a2.evalrot(dir_b2);

		//GXX_PRINT(rot1);
		//GXX_PRINT(rot2);

		assert((rot1 < 0 && rot2 < 0) || (rot1 > 0 && rot2 > 0));

		return(rot1 > 0);		
	}

	struct loop_loop_intersection_result {
		std::list<ipoint> ipnts;
		
		size_t printTo(gxx::io::ostream& o) const {
			return gxx::print_to(o, ipnts);
		}

		void try_add_bound_point(double alparam, double blparam, const tpoint& tp, const trim2& at1, const trim2& at2, const trim2& bt1, const trim2& bt2) {
			auto aparam = &at1 != &at2 ? alparam : alparam + tp.a; 
			auto bparam = &bt1 != &bt2 ? blparam : blparam + tp.b; 

			bool righter_than = rabbit::is_a_righter_than_b(at1, at2, bt1, bt2, tp);
			
			ipnts.emplace_back(alparam + tp.a, blparam + tp.b, tp.r, righter_than);
		}

		void add_point(int alparam, int blparam, const tpoint& tp, const trim2& at, const trim2& bt) {
			assert(at.d0(tp.a).is_same(tp.r) && bt.d0(tp.b).is_same(tp.r));
			bool righter_than = rabbit::is_a_righter_than_b(at, bt, tp);
			ipnts.emplace_back(alparam + tp.a, blparam + tp.b, tp.r, righter_than);
		}

		bool empty() {
			return ipnts.empty();
		}
	};

	trim_trim_intersection_result trim_trim_intersection(const trim2& a, const trim2& b);
	loop_loop_intersection_result loop_loop_intersection(const loop2& a, const loop2& b);
	
	std::pair<loop2, loop2> loop_loop_combine(const loop2& a, const loop2& b);

	/*void curve_curve_intersection(const curve2&, const curve2&, std::vector<double>&, std::vector<double>&, const interval&, const interval&);

	class boolean_algorithm_2d {
		const face2& a;
		const face2& b;

		enum edge_classify : uint8_t {
			True,
			False,
			NotInfomation
		};

		class lvertex;
		class ledge {
		public:
			lvertex* vstart;
			lvertex* vfinish;

			const curve2* crv;
			double start;
			double finish;

			edge_classify aleft = NotInfomation;
			edge_classify aright = NotInfomation;
			edge_classify bleft = NotInfomation;
			edge_classify bright = NotInfomation;

			ledge(lvertex* s, lvertex* f, const trim2& tr, edge_classify al, edge_classify ar, edge_classify bl, edge_classify br) : 
				vstart(s), vfinish(f), crv(tr.crv.get()), start(tr.tstart), finish(tr.tfinish), aleft(al), aright(ar), bleft(bl), bright(br) {}
		
			ledge(lvertex* s, lvertex* f, const curve2* crv, double ts, double tf, edge_classify al, edge_classify ar, edge_classify bl, edge_classify br) : 
				vstart(s), vfinish(f), crv(crv), start(ts), finish(tf), aleft(al), aright(ar), bleft(bl), bright(br) {}
		};

		class lvertex {
		public:
			std::vector<ledge*> inedges;
			std::vector<ledge*> outedges;
		};

		std::map<const trim2*, std::vector<double>> apntsmap;
		std::map<const trim2*, std::vector<double>> bpntsmap;

		struct smallzone : public malgo2::vector2<double> {
			bool operator < (const malgo2::vector2<double>& pnt) const {
				return (x < (pnt.x - gxx::geom2::precision)) || (y < (pnt.y - gxx::geom2::precision));
			}
			smallzone(const malgo2::vector2<double>& oth) : malgo2::vector2<double>(oth) {}
		};

		std::map<smallzone, lvertex> locvtxs;
		std::vector<ledge> locedgs;

		bool evaluate_intersect_stage = false;
		bool generate_local_graph_stage = false;

	public:
		boolean_algorithm_2d(const face2& a, const face2& b) : a(a), b(b) {}
	
		void evaluate_intersection() {
			for (const loop2& al : a.loops) {
				for (const loop2& bl : b.loops) {
					for (const trim2& at : al.edges) {
						for (const trim2& bt : bl.edges) {
							auto& apoints = apntsmap[&at];
							auto& bpoints = bpntsmap[&bt];
							curve_curve_intersection(*at.crv, *bt.crv, apoints, bpoints, at.interval(), bt.interval());
						}
					}
				}	
			}
			evaluate_intersect_stage = true;
		}

		static bool edge_compare(const ledge* a, const ledge* b) {	
			gxx::println("HERE");

			gxx::println(a->start);
			gxx::println(a->finish);
			gxx::println(*(a->crv));
			gxx::println(b->start);
			gxx::println(b->finish);	
			gxx::println(*(b->crv));		

			auto ad1 = a->crv->d1(a->start);
			auto bd1 = b->crv->d1(b->start);

			if (ad1.is_same(bd1)) gxx::println("EQ");
			if (ad1.argument() < bd1.argument()) gxx::println("MORE");
			else gxx::println("LESS");
		}

		void generate_local_data() {
			assert(evaluate_intersect_stage);

			//Индексация геометрии контура А. 
			for (const loop2& l : a.loops) {	
				for (const trim2& t : l.edges) {
					std::vector<double>& intsvec = apntsmap[&t];
					if (!intsvec.empty()) {
						intsvec.push_back(t.tstart);
						intsvec.push_back(t.tfinish);
						std::sort(intsvec.begin(), intsvec.end());
						gxx::println(intsvec);
						for (int i = 0; i < intsvec.size() - 1; ++i) {
							lvertex* vstart = &locvtxs[smallzone(t.crv->d0(intsvec[i]))];
							lvertex* vfinish = &locvtxs[smallzone(t.crv->d0(intsvec[i+1]))];
							if (vstart != vfinish) {
								locedgs.emplace_back(vstart, vfinish, t.crv.get(), intsvec[i], intsvec[i+1], True, False, NotInfomation, NotInfomation);
								ledge* e = &locedgs[locedgs.size() - 1]; 
								vfinish->inedges.push_back(e);
								vstart->outedges.push_back(e);
								gxx::println(intsvec[i], intsvec[i+1]);
							}
						}
					} else {
						lvertex* vstart = &locvtxs[smallzone(t.start())];
						lvertex* vfinish = &locvtxs[smallzone(t.finish())];
						locedgs.emplace_back(vstart, vfinish, t, True, False, NotInfomation, NotInfomation);
						ledge* e = &locedgs[locedgs.size() - 1]; 
						vfinish->inedges.push_back(e);
						vstart->outedges.push_back(e);
					} 
				}
			}

			//Индексация геометрии контура Б.
			for (const loop2& l : b.loops) {	
				for (const trim2& t : l.edges) {
					std::vector<double>& intsvec = bpntsmap[&t];
					if (!intsvec.empty()) {
						intsvec.push_back(t.tstart);
						intsvec.push_back(t.tfinish);
						std::sort(intsvec.begin(), intsvec.end());
						gxx::println(intsvec);
						for (int i = 0; i < intsvec.size() - 1; ++i) {
							lvertex* vstart = &locvtxs[smallzone(t.crv->d0(intsvec[i]))];
							lvertex* vfinish = &locvtxs[smallzone(t.crv->d0(intsvec[i+1]))];
							if (vstart != vfinish) {
								locedgs.emplace_back(vstart, vfinish, t.crv.get(), intsvec[i], intsvec[i+1], True, False, NotInfomation, NotInfomation);
								ledge* e = &locedgs[locedgs.size() - 1]; 
								vfinish->inedges.push_back(e);
								vstart->outedges.push_back(e);
								gxx::println(intsvec[i], intsvec[i+1]);
							}
						}
					} else {
						lvertex* vstart = &locvtxs[smallzone(t.start())];
						lvertex* vfinish = &locvtxs[smallzone(t.finish())];
						locedgs.emplace_back(vstart, vfinish, t, NotInfomation, NotInfomation, True, False);
						ledge* e = &locedgs[locedgs.size() - 1]; 
						vfinish->inedges.push_back(e);
						vstart->outedges.push_back(e);
					} 
				}
			}

			for (auto& lv: locvtxs) {
				gxx::println(lv.first);
			}

			//Сортировка ребер относительно вершин
			for (auto& pairlv : locvtxs) {
				auto& lv = pairlv.second;

				GXX_PRINT(pairlv.first);
				GXX_PRINT(lv.inedges.size());
				GXX_PRINT(lv.outedges.size());

				gxx::println("sort");
				std::sort(lv.inedges.begin(), lv.inedges.end(), edge_compare);
				std::sort(lv.outedges.begin(), lv.outedges.end(), edge_compare);
			}
			
			for (const auto& le : locedgs) {

			}

			//generate_local_graph_stage = true;
		}

		void print_intersection() {
			gxx::println("ALOOP:");
			for (auto p : apntsmap) {
				gxx::println(*p.first->crv);
				for (auto v : p.second) {
					gxx::fprintln("\t{} -> {}", v, p.first->crv->d0(v));
				}
			}

			gxx::println("BLOOP:");
			for (auto p : bpntsmap) {
				gxx::println(*p.first->crv);
				for (auto v : p.second) {
					gxx::fprintln("\t{} -> {}", v, p.first->crv->d0(v));
				}
			}
		}
	};*/

}

#endif