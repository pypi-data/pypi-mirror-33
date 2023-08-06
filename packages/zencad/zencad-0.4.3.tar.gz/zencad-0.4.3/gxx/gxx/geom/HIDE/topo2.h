#ifndef GXX_GEOM_TOPO2_H
#define GXX_GEOM_TOPO2_H

#include <gxx/geom/geom2.h>
#include <memory>
#include <list>

namespace gxx {
	namespace topo2 {
		namespace g2 = gxx::geom2;
		
		class curve {
		private:
			std::shared_ptr<g2::curve> base;
		public:
			double bmin;
			double bmax;

			void reserve() {
				std::swap(bmin, bmax);
			}		

			g2::point start() { return base->d0(bmin); }	
			g2::point finish() { return base->d0(bmax); }

			curve(g2::point pnt1, g2::point pnt2) : base(new g2::line(pnt1, pnt2 - pnt1)), bmin(0), bmax((pnt2 - pnt1).abs()) {}
		};
		
		class vertex;
		class edge;
		class wire;

		struct vertex {
			edge* enext;
			edge* eprev;
			vertex* alternate = nullptr;

			vertex(edge* eprev, edge* enext) : eprev(eprev), enext(enext) {}
		};

		struct edge {
			curve crv;
			std::shared_ptr<vertex> vnext;
			std::shared_ptr<vertex> vprev;
			edge* enext = nullptr;
			edge* eprev = nullptr;
			wire* w;

			bool reversed = false;

			//g2::point start() const { return reversed ? crv->finish() : crv.start(); }
			//g2::point finish() const { return reversed ? crv.start() : crv.finish(); }

			void connect_next(edge& oth) {
				assert(enext == nullptr);
				assert(oth.eprev == nullptr);

				if (oth.crv.start().is_not_same(crv.finish())) 
					gxx::panic("connection error");

				vertex* v = new vertex(this, &oth);
				vnext.reset(v);
				oth.vprev = vnext;
				enext = &oth;
				oth.eprev = this;

				gxx::println("succesful connection");
			}

			void connect_prev(edge& oth) {
				oth.connect_next(*this);
			}

			edge(curve crv) : crv(crv) {}
		};

		struct wire {
			std::list<edge> edges;
			bool closed = false;

			wire(std::initializer_list<curve> lst) {
				for(auto& c : lst) {
					edges.emplace_back(c);
				}
				auto lit = edges.begin();
				auto fit = ++edges.begin();
				for(; fit != edges.end(); ++lit, ++fit) {
					lit->connect_next(*fit);					
				}
				if (edges.begin()->crv.start().is_same(edges.rbegin()->crv.finish())) {
					edges.rbegin()->connect_next(*edges.begin());
				}
			}
		};

		class figure {
			std::list<wire> outwires;
			std::list<wire> inwires;
		};

		//class segment;

		//class vertex_impl {
		//public:
		//	g2::point pnt;
		//	segment* next = nullptr;
		//	segment* prev = nullptr;
		//	vertex_impl(const g2::point& pnt) : pnt(pnt) {}
		//	void reverse() { std::swap(next, prev); }
		//};
/*
		class vertex;
		class segment;
		class contour;
		class figure;
*/
		//class vertex {
		//public:
/*			std::shared_ptr<vertex_impl> impl;
			vertex(const g2::point& pnt) : impl(new vertex_impl(pnt)) {}
			vertex(double a, double b) : vertex(g2::point(a,b)) {}
			vertex(const vertex& oth) : impl(oth.impl) {}
			vertex(vertex&& oth) : impl(std::move(oth.impl)) {}
			vertex& operator= (const vertex& oth) { impl = oth.impl; return *this; }
			g2::point loc() const { return impl->pnt; }
			void swap(vertex& oth) { std::swap(impl, oth.impl); }
			void reverse() { impl->reverse(); }
		
			void prev(segment* seg) { impl->prev = seg; }
			void next(segment* seg) { impl->next = seg; }

			segment& next() { gxx::println(impl->next); return *impl->next; }
			segment& prev() { gxx::println(impl->prev); return *impl->prev; }

			void sew(vertex& v1) {
				//impl->next = v1.impl->next;
				v1.impl = impl;
			}

			const size_t printTo(gxx::io::ostream& o) const {
				return gxx::print(impl->pnt);
			}
*/		//};

		//Сегмент объединен с реализацией, т.к. на сегмент может ссылаться только один контур.
/*		class segment {
		public:
			vertex v1, v2;
			std::shared_ptr<curve2> crv;
			bool reversed = false;

			//segment(const segment&) = delete;

			//segment(const g2::line& l) : crv(new g2::line(l)), v1(l.start()), v2(l.finish()) {}
			segment(vertex& v1, vertex& v2) : v1(v1), v2(v2), crv(new g2::line(v1.loc(), v2.loc())) { 
				check_critical();
			}

			void check_critical() {
				if (v1.loc().is_not_same(crvstart()) || v2.loc().is_not_same(crvfinish())) {
					gxx::vprintln("v1.loc():", v1.loc());
					gxx::vprintln("v2.loc():", v2.loc());
					gxx::vprintln("crv->start():", reversed ? crv->finish() : crv->start());
					gxx::vprintln("crv->finish():", reversed ? crv->start() : crv->finish());
					gxx::panic("segment check failure");
				}
			}

			void reverse() {
				reversed = !reversed;
				v1.swap(v2);
			}

			g2::point crvstart() const { return reversed ? crv->finish() : crv->start(); }
			g2::point crvfinish() const { return reversed ? crv->start() : crv->finish(); }

			g2::vector start_d1() const { return reversed ? -crv->finish_d1() : crv->start_d1(); }
			g2::vector finish_d1() const { return reversed ? -crv->start_d1() : crv->finish_d1(); }

			double rotation_angle() const { return reversed ? -crv->rotation_angle() : crv->rotation_angle(); }

			g2::point start() const { return v1.loc(); }
			g2::point finish() const { return v2.loc(); }

			vertex& prev() { return v1; }
			vertex& next() { return v2; }

			void orient_vertexs() {
				gxx::println("orientvertexs");

				gxx::println(this);
				gxx::println(crv.get());
				v1.next(this); v2.prev(this);
				gxx::println(crv.get());
			} 

			const size_t printTo(gxx::io::ostream& o) const {
				gxx::vprintln("HERE", crv.get());
				gxx::vprintln("HERE", v2.impl.get());
				gxx::vprintln("HERE", v1.impl.get());
				//return gxx::print(*crv);
			}
		};

		class contour {
		public:
			std::vector<segment> segs;
			bool reversed = false;
			bool closed = false;

			void orient_segments() {
				if (segs.size() == 1) return;
				auto f = segs[0].finish();
				if (f.is_not_same(segs[1].start()) && f.is_not_same(segs[1].finish())) segs[0].reverse();
				for (int i = 1; i < segs.size(); ++i) {
					if (segs[i].start().is_not_same(segs[i-1].finish())) segs[i].reverse();
					//if (segs[i].start().is_not_same(segs[i-1].finish())) gxx::panic("broken contour");
				}
				if (segs[segs.size()-1].finish().is_same(segs[0].start())) closed = true;
			}

			void sew_vertexs() {
				for (int i = 0; i < segs.size() - 1; ++i) {
					segs[i].v2.sew(segs[i+1].v1);
				}
				if (closed) segs[segs.size()-1].v2.sew(segs[0].v1);
				for (auto& a: segs) a.orient_vertexs();
			}

			void check_segment_connection_critical(const segment& s1, const segment& s2) const {
				if (s2.start().is_not_same(s1.finish())) {
					gxx::vprintln("s1.start():", s1.start());
					gxx::vprintln("s1.finish():", s1.finish());
					gxx::vprintln("s2.start():", s2.start());
					gxx::vprintln("s2.finish():", s2.finish());
					gxx::panic("contour conection error");
				}
			}

			void check_closed_critical() const {
				if (closed == false) gxx::panic("contour isn't closed");
			}

			void check_critical() {
				for (int i = 0; i < segs.size() - 1; ++i) {
					check_segment_connection_critical(segs[i], segs[i+1]);
				}
				if (closed) check_segment_connection_critical(segs[segs.size()-1], segs[0]);
				for (auto & s: segs) {
					s.check_critical();
				}
			}

			bool cycle_orientation() const {
				double sum = 0;
				g2::vector last = segs[segs.size() - 1].finish_d1();
				for (int i = 0; i < segs.size(); ++i) {
					sum += segs[i].rotation_angle();
					sum += last.evalrot(segs[i].start_d1());
					last = segs[i].finish_d1();
				}
				if (gxx::math::is_same(sum, - 2 * M_PI, g2::precision)) return false;
				if (gxx::math::is_same(sum,   2 * M_PI, g2::precision)) return true;
				gxx::panic("strange cycle");
			}

			contour(const std::initializer_list<segment>& segs) : segs(segs) {
				orient_segments();
				check_critical();
				sew_vertexs();
				check_critical();
			}

			void reverse() {
				for(auto& e : segs) {
					e.reverse();
				}
			}

			std::set<vertex_impl*> list_of_vertex() {
				std::set<vertex_impl*> ret;
				for (auto& s : segs) {
					ret.insert(s.v1.impl.get());
					ret.insert(s.v2.impl.get());
				}
				return ret;
			}
		};

		class figure {
		public:
			std::vector<contour> conts;
			figure(const contour& cntr) : conts{cntr} {
				cntr.check_closed_critical();
				if (!cntr.cycle_orientation()) conts[0].reverse();
			}			
		};

		inline figure fuse(const figure& a, const figure& b) {
			figure droub_a = a;
			figure droub_b = b;
		}*/
	}
}

#endif