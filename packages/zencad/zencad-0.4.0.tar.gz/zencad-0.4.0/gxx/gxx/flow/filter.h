#ifndef GXX_VIEW_FILTER_H
#define GXX_VIEW_FILTER_H

#include <gxx/generator.h>
#include <gxx/debug/dprint.h>
//#include <gxx/util/signature.h>

namespace gxx {
	namespace flow {
		template <typename F, typename C>
		class filter_view : public gxx::generator<typename C::value_type, filter_view<F,C>> {
			const C& c;
			const F& f;
			bool inited;

			decltype(c.begin()) it;
			decltype(c.end()) eit;			
		public:
			filter_view(const F& f, const C& c) : f(f), c(c), it(c.begin()), eit(c.end()) {
				if (it == eit) return;
				if (!f(*it)) next();
			}
		
			decltype(auto) value() {
				return *it;
			}

			void next() {
				while(it != eit) {
					++it;
					if (f(*it)) break;
				}
			}

			bool have() {
				return it != eit;
			}
		};

		template <typename F>
		struct filter_fabric_view {
			const F& f;
			filter_fabric_view(const F& f) : f(f) {};			
		};

		template <typename F>
		auto filter(const F& f) {
			return filter_fabric_view<F>(f);
		}

		template <typename F, typename C>
		auto operator | (const C& c, const filter_fabric_view<F>& fabric) {
			return filter_view<F,C>(fabric.f, c);
		}
	}
}

#endif